import asyncio
from src.core.celery_app import celery_app
from src.utils.transaction_manager import ScriptIds
from src.services.inventory_sync import InventorySyncService
from src.services.configuration_sync import ConfigurationSyncService # Asumiendo que este existe o existirá
from asgiref.sync import async_to_sync
from src.core.logger import logger

# ==============================================================================
# TAREA 1: SINCRONIZACIÓN DE INVENTARIO (Dispositivos, Flotas, Estados)
# ==============================================================================
@celery_app.task(name="tasks.run_automatic_sync")
def task_run_automatic_sync(is_manual=False):
    """
    Ejecuta la sincronización masiva. 
    La auditoría (TransactionManager) y la lógica están DENTRO del Servicio.
    """
    # Solo determinamos el ID para loguear en consola, no para la BD aquí
    script_name = "MANUAL" if is_manual else "AUTO"
    logger.info(f"📨 WORKER: Iniciando Sync Inventario ({script_name})...")
    
    # Llamamos directamente al servicio. Él se encarga de abrir/cerrar transacciones.
    # is_manual no se pasa a sync_all porque el ScriptId lo definimos dentro del servicio 
    # (O puedes modificar sync_all para recibir el script_id si quieres diferenciarlo).
    async_to_sync(InventorySyncService.sync_all)()
    
    return f"Inventory Sync Completed"

# ==============================================================================
# TAREA 2: SINCRONIZACIÓN DE CONFIGURACIÓN (Variables)
# ==============================================================================
@celery_app.task(name="tasks.run_configuration_sync")
def task_run_configuration_sync(is_manual=False):
    """
    Ejecuta la sincronización de variables.
    """
    logger.info(f"📨 WORKER: Iniciando Sync Configuración...")

    # Lo ideal es que ConfigurationSyncService siga el mismo patrón que InventorySyncService
    # y maneje su propia transacción internamente.
    async_to_sync(ConfigurationSyncService.sync_all_variables)()
    
    return f"Config Sync Done"

# ==============================================================================
# TAREAS PUNTUALES (Disparadas por nuevos dispositivos/flotas)
# ==============================================================================

# Nota: Estas tareas asumen que los métodos existen en el servicio.
# Si aún no los creas en ConfigurationSyncService, coméntalas para que no de error al arrancar.

@celery_app.task(name="tasks.sync_single_fleet_vars")
def task_sync_single_fleet_vars(fleet_slug: str):
    logger.info(f"📨 WORKER: Sync Variables Flota -> {fleet_slug}")
    async_to_sync(ConfigurationSyncService.sync_fleet_variables)(fleet_slug)
    return f"Fleet Vars {fleet_slug} synced"

@celery_app.task(name="tasks.sync_single_device_vars")
def task_sync_single_device_vars(uuid: str):
    logger.info(f"📨 WORKER: Sync Variables Dispositivo -> {uuid}")
    async_to_sync(ConfigurationSyncService.sync_device_variables)(uuid)
    return f"Device Vars {uuid} synced"

# ==============================================================================
# TAREAS DE REINICIO DE DISPOSITIVOS
# ==============================================================================

@celery_app.task(name="tasks.restart_single_device", bind=True)
def task_restart_single_device(self, uuid: str, action: str, user: str = "SYSTEM", role: str = "SYSTEM"):
    """
    Reinicia un dispositivo individual (restart/reboot/shutdown).
    Valida el estado antes de ejecutar Y verifica que se completó.
    
    Estados de Celery:
    - PENDING: Tarea encolada (estado por defecto)
    - STARTED: Comando enviado, esperando confirmación
    - SUCCESS: Reinicio confirmado exitosamente
    - FAILURE: Error o timeout
    """
    from src.services.device_admin_service import DeviceAdminService
    from src.repositories.info_devices_repo import InfoDevicesRepository
    from src.utils.deviceStatus import get_device_real_status
    
    logger.info(f"🔄 WORKER: Reiniciando {uuid} (acción: {action}) por {user}")
    
    
    # Actualizar estado a STARTED (IN_PROGRESS)
    self.update_state(
        state='STARTED',
        meta={
            'status': 'in_progress',
            'step': 'init',
            'message': f'Iniciando secuencia de {action}...',
            'uuid': uuid,
            'action': action
        }
    )
    
    # Validar estado del dispositivo (opcional - comentado para permitir intentos forzados)
    try:
        device = async_to_sync(InfoDevicesRepository.get_device_by_uuid)(uuid)
        if not device:
            err_msg = "Dispositivo no encontrado en base de datos"
            logger.warning(f"⚠️ {err_msg}")
            raise Exception(err_msg)
        
        # Ejecutar acción CON MONITOREO (Consumir generador)
        final_result = None
        
        # Iteramos sobre el generador síncrono monitor_power_action
        for update in DeviceAdminService.monitor_power_action(uuid, action, user, role):
            # Loguear para debug
            if update.get("status") == "in_progress":
                logger.info(f"🔄 [{uuid}] Step: {update.get('step')} - {update.get('message')}")
            
            # Guardamos el último update
            final_result = update
            
            # Actualizar estado de Celery en tiempo real
            # IMPORTANTE: update_state es lo que permite al frontend ver el progreso
            self.update_state(
                state='STARTED',
                meta={
                    'status': update.get('status'),
                    'step': update.get('step'),
                    'message': update.get('message'),
                    'elapsed_time': update.get('elapsed'),
                    'uuid': uuid,
                    'action': action,
                    'details': update.get('details') # Puede venir en completed
                }
            )

        # Evaluar resultado final
        if final_result and final_result.get("status") == "completed":
            return {
                "status": "completed",
                "message": final_result.get("message"),
                "elapsed_time": final_result.get("elapsed"),
                "uuid": uuid,
                "action": action,
                "details": final_result.get("details")
            }
        else:
            # FAILURE - Timeout o error
            error_msg = final_result.get("message", "Error desconocido") if final_result else "No hubo respuesta del monitor"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)

        
    except Exception as e:
        logger.error(f"❌ Error reiniciando {uuid}: {e}")
        raise  # Esto marcará la tarea como FAILURE


@celery_app.task(name="tasks.restart_bulk_devices")
def task_restart_bulk_devices(uuids: list, action: str, user: str = "SYSTEM", role: str = "SYSTEM"):
    """
    Reinicia múltiples dispositivos en lotes (chunks de 10).
    Filtra automáticamente dispositivos offline/reducidos.
    """
    from src.repositories.info_devices_repo import InfoDevicesRepository
    from src.utils.deviceStatus import get_device_real_status
    
    logger.info(f"🔄 WORKER: Reinicio masivo de {len(uuids)} dispositivos por {user}")
    
    # Filtrar dispositivos válidos
    valid_uuids = []
    excluded_count = 0
    
    try:
        for uuid in uuids:
            device = async_to_sync(InfoDevicesRepository.get_device_by_uuid)(uuid)
            if device and get_device_real_status(device) == "operativo":
                valid_uuids.append(uuid)
            else:
                excluded_count += 1
        
        logger.info(f"✅ {len(valid_uuids)} dispositivos válidos, {excluded_count} excluidos")
        
        # Procesar en chunks de 10
        chunk_size = 10
        results = []
        
        for i in range(0, len(valid_uuids), chunk_size):
            chunk = valid_uuids[i:i + chunk_size]
            logger.info(f"📦 Procesando chunk {i//chunk_size + 1} ({len(chunk)} dispositivos)")
            
            # Disparar tareas individuales para cada dispositivo del chunk
            for uuid in chunk:
                task_restart_single_device.delay(uuid, action, user, role)
            
            results.append(f"Chunk {i//chunk_size + 1} encolado")
        
        return {
            "success": True,
            "total": len(uuids),
            "valid": len(valid_uuids),
            "excluded": excluded_count,
            "chunks": len(results)
        }
        
    except Exception as e:
        logger.error(f"❌ Error en reinicio masivo: {e}")
        return {"success": False, "message": str(e)}

@celery_app.task(name="tasks.run_automatic_restart")
def task_run_automatic_restart(is_manual: bool = False):
    """
    Tarea programada para reinicio automático diario (5 AM).
    Solo reinicia dispositivos operativos.
    """
    from src.repositories.info_devices_repo import InfoDevicesRepository
    from src.utils.deviceStatus import get_device_real_status
    from src.utils.transaction_manager import ScriptIds, TransactionManager, TransactionStatus
    
    script_name = "MANUAL" if is_manual else "AUTO"
    logger.info(f"🌅 WORKER: Iniciando Reinicio Automático ({script_name})...")
    
    script_id = ScriptIds.AUTO_RESTART if not is_manual else ScriptIds.MANUAL_RESTART
    
    try:
        # Obtener todos los dispositivos
        all_devices = async_to_sync(InfoDevicesRepository.get_all_devices)()
        
        # Filtrar solo operativos
        operational_devices = [
            d for d in all_devices 
            if get_device_real_status(d) == "operativo"
        ]
        
        logger.info(f"📊 Total: {len(all_devices)}, Operativos: {len(operational_devices)}")
        
        if not operational_devices:
            logger.warning("⚠️ No hay dispositivos operativos para reiniciar")
            return {"success": True, "message": "No hay dispositivos operativos"}
        
        # Iniciar transacción de auditoría
        historic_id = async_to_sync(TransactionManager.start_transaction)(
            script_id, 
            user="SYSTEM_CRON", 
            role="SYSTEM"
        )
        
        # Ejecutar reinicio masivo
        uuids = [d["uuidinspector"] for d in operational_devices]
        result = task_restart_bulk_devices(uuids, "restart", "SYSTEM_CRON", "SYSTEM")
        
        # Finalizar transacción
        if historic_id:
            status = TransactionStatus.COMPLETO if result.get("success") else TransactionStatus.FALLIDO
            msg = f"Reiniciados {result.get('valid', 0)} de {result.get('total', 0)} dispositivos"
            async_to_sync(TransactionManager.finish_transaction)(historic_id, script_id, status, msg)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error en reinicio automático: {e}")
        return {"success": False, "message": str(e)}

# --- NOTA SOBRE TAREAS DE INVENTARIO INDIVIDUAL ---
# En el InventorySyncService actual NO definimos 'sync_device_by_uuid' ni 'sync_fleet_by_slug'.
# Solo definimos 'sync_all'. 
# Por tanto, he REMOVIDO esas tareas aquí para evitar errores de "AttributeError".
# Si las necesitas, debemos crear esos métodos en el servicio primero.