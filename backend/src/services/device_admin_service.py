import logging
from fastapi.concurrency import run_in_threadpool
from asgiref.sync import async_to_sync
from src.services.balena_service import BalenaService
from src.repositories.provisioning_repo import ProvisioningRepository
from src.repositories.info_devices_repo import InfoDevicesRepository
from src.repositories.history_repo import HistoryRepository
from src.utils.transaction_manager import TransactionManager, ScriptIds, TransactionStatus
from src.api.v1.schemas.provisioning_schema import ProvisioningRequest
from src.api.v1.schemas.device_action_schema import DeviceNoteRequest

logger = logging.getLogger(__name__)

class DeviceAdminService:

    SCRIPT_MAP = {
        "reboot": ScriptIds.MANUAL_REBOOT,
        "restart": ScriptIds.MANUAL_RESTART,
        "shutdown": ScriptIds.MANUAL_SHUTDOWN,
        "rename": ScriptIds.MANUAL_RENAME,
        "move": ScriptIds.MANUAL_MOVE_FLEET,
        "note": ScriptIds.MANUAL_SET_NOTE
    }

    # ==========================================
    # 1. PROVISIONING
    # ==========================================
    @classmethod
    async def provision_device(cls, uuid: str, data: ProvisioningRequest, user: str = "SYSTEM", role: str = "SYSTEM"):
        logger.info(f"🚀 Iniciando Provisioning para {uuid} por {user}...")

        if not BalenaService.login():
            return {"success": False, "message": "Fallo Login Balena"}

        rename_ok = BalenaService.rename_device(uuid, data.new_device_name)
        if not rename_ok:
            return {"success": False, "message": "Error al renombrar en Balena Cloud."}

        try:
            await ProvisioningRepository.create_service_and_link_device(uuid, data)
        except Exception as e:
            logger.error(f"⚠️ Desincronización BD: {e}")
            return {"success": False, "message": f"Error guardando en BD: {str(e)}"}

        return {"success": True, "message": "Dispositivo aprovisionado correctamente."}

    # ==========================================
    # 2. ACCIONES DE PODER (Reboot, Restart, Shutdown)
    # ==========================================
    @classmethod
    async def execute_power_action(cls, uuid: str, action: str, user: str = "SYSTEM", role: str = "SYSTEM"):
        logger.info(f"⚡ Solicitud '{action}' en {uuid} por {user}")
        
        script_id = cls.SCRIPT_MAP.get(action, "DEFAULT")
        snapshot = await InfoDevicesRepository.get_device_by_uuid(uuid)
        if not snapshot: snapshot = {}

        # PASAMOS USER Y ROLE AQUÍ 👇
        historic_id = await TransactionManager.start_transaction(script_id, user=user, role=role)

        if historic_id:
            await HistoryRepository.log_device_snapshot(historic_id, uuid, TransactionStatus.EN_PROGRESO, snapshot)

        if not await run_in_threadpool(BalenaService.login):
            if historic_id:
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Fallo Login Balena")
            return {"success": False, "message": "Fallo Login Balena CLI"}

        success = False
        if action == "reboot": success = await run_in_threadpool(BalenaService.reboot_device, uuid)
        elif action == "restart": success = await run_in_threadpool(BalenaService.restart_device, uuid)
        elif action == "shutdown": success = await run_in_threadpool(BalenaService.shutdown_device, uuid)
        
        status = TransactionStatus.COMPLETO if success else TransactionStatus.FALLIDO
        msg = f"Comando {action} ejecutado." if success else f"Error ejecutando {action} en Balena."
        
        if historic_id:
            await TransactionManager.finish_transaction(historic_id, script_id, status, msg)

        return {"success": success, "message": msg}

    @classmethod
    def monitor_power_action(
        cls, uuid: str, action: str, user: str = "SYSTEM", role: str = "SYSTEM"
    ):
        """
        Generador Simplificado que:
        1. Inicia transacción
        2. Ejecuta Balena CLI (que espera a 'done')
        3. Reporta éxito/fallo basado en el exit code del CLI
        """
        logger.info(f"⚡ Ejecutando '{action}' en {uuid} por {user}")
        
        script_id = cls.SCRIPT_MAP.get(action, "DEFAULT")
        
        snapshot = async_to_sync(InfoDevicesRepository.get_device_by_uuid)(uuid) or {}
        historic_id = async_to_sync(TransactionManager.start_transaction)(
            script_id, user=user, role=role
        )
        
        if historic_id:
            async_to_sync(HistoryRepository.log_device_snapshot)(
                historic_id, uuid, TransactionStatus.EN_PROGRESO, snapshot
            )

        try:
            # 1. Login Balena
            if not BalenaService.login():
                msg = "Fallo Login Balena CLI"
                if historic_id:
                     async_to_sync(TransactionManager.finish_transaction)(
                         historic_id, script_id, TransactionStatus.FALLIDO, msg
                     )
                yield {"status": "failed", "message": msg}
                return

            # 2. Reportar In inicio (Feedback visual inicial)
            yield {
                "status": "in_progress", 
                "step": "executing", 
                "message": f"Ejecutando {action} en Balena (esperando confirmación)..."
            }

            # 3. Ejecutar acción (El CLI bloqueará hasta que termine o falle)
            import time
            start_time = time.time()
            action_success = False
            
            if action == "reboot":
                action_success = BalenaService.reboot_device(uuid)
            elif action == "restart":
                action_success = BalenaService.restart_device(uuid)
            elif action == "shutdown":
                action_success = BalenaService.shutdown_device(uuid)
            else:
                yield {"status": "failed", "message": f"Acción {action} no soportada"}
                return
            
            elapsed = time.time() - start_time

            # 4. Evaluar resultado del CLI
            if action_success:
                msg = f"{action.capitalize()} ejecutado exitosamente."
                
                if historic_id:
                    async_to_sync(TransactionManager.finish_transaction)(
                        historic_id, script_id, TransactionStatus.COMPLETO, msg
                    )
                
                yield {
                    "status": "completed", 
                    "step": "done", 
                    "message": msg,
                    "elapsed": elapsed
                }
            else:
                msg = f"Error: Balena CLI falló al ejecutar {action}."
                
                if historic_id:
                    async_to_sync(TransactionManager.finish_transaction)(
                        historic_id, script_id, TransactionStatus.FALLIDO, msg
                    )
                
                yield {"status": "failed", "message": msg}
        
        except Exception as e:
            logger.error(f"❌ Error en monitor_power_action: {e}")
            if historic_id:
                async_to_sync(TransactionManager.finish_transaction)(
                    historic_id, script_id, TransactionStatus.FALLIDO, f"Error: {e}"
                )
            yield {"status": "failed", "message": str(e)}



    # ==========================================
    # 3. GESTIÓN DE NOTAS
    # ==========================================
    @classmethod
    async def set_note(cls, uuid: str, data: DeviceNoteRequest, user: str = "SYSTEM", role: str = "SYSTEM"):
        logger.info(f"📝 Nota en {uuid} por {user}")
        
        script_id = cls.SCRIPT_MAP["note"]
        snapshot = await InfoDevicesRepository.get_device_by_uuid(uuid) or {}
        
        # PASAMOS USER Y ROLE AQUÍ 👇
        historic_id = await TransactionManager.start_transaction(script_id, user=user, role=role)
        if historic_id:
            await HistoryRepository.log_device_snapshot(historic_id, uuid, TransactionStatus.EN_PROGRESO, snapshot)

        if not BalenaService.login():
            if historic_id: await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Fallo Login")
            return {"success": False, "message": "Fallo Login"}

        if BalenaService.set_device_note(uuid, data.note):
            try:
                await InfoDevicesRepository.update_device_note(uuid, data.note)
                if historic_id: 
                    await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Nota: {data.note}")
                return {"success": True, "message": "Nota guardada correctamente."}
            except Exception as e:
                if historic_id: 
                    await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Balena OK, BD Error: {e}")
                return {"success": True, "message": "Nota en Balena OK, error en BD local."}
        
        if historic_id: await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Error Balena API")
        return {"success": False, "message": "Error al guardar nota en Balena."}

    # ==========================================
    # 4. MOVER DE FLOTA
    # ==========================================
    @classmethod
    async def move_device_to_fleet(cls, uuid: str, target_fleet_identifier: str, user: str = "SYSTEM", role: str = "SYSTEM"):
        """
        Mueve un dispositivo de flota.
        Maneja la discrepancia entre ID Local (ej: 'andina_2') y Slug Balena (ej: 'admin/andina_2').
        """
        logger.info(f"🚚 Moviendo {uuid} -> Solicitado: '{target_fleet_identifier}' por {user}")
        
        script_id = cls.SCRIPT_MAP["move"]
        snapshot = await InfoDevicesRepository.get_device_by_uuid(uuid) or {}
        
        # 1. Resolver Fleet ID Local vs Balena Slug
        # Intentamos obtener la flota asumiendo que el identifier es el ID primero
        fleet_id_local = target_fleet_identifier
        balena_target = target_fleet_identifier

        # Verificamos si existe en BD para obtener el slug correcto para Balena
        try:
            from src.repositories.fleet_repo import FleetRepository
            fleet_info = await FleetRepository.get_by_id(target_fleet_identifier)
            
            if fleet_info:
                # Es un ID local válido (ej: 'andina_2')
                fleet_id_local = fleet_info['id']
                balena_target = fleet_info['slug'] # Usamos el slug real para Balena (ej: 'admin/andina_2')
                logger.info(f"✅ Flota resuelta: Local='{fleet_id_local}', Balena='{balena_target}'")
            else:
                # Si no lo encontramos por ID, podría ser que nos enviaron el slug directamente?
                # Por ahora asumimos que lo que envian es lo que usaremos, pero logueamos advertencia.
                logger.warning(f"⚠️ Flota '{target_fleet_identifier}' no encontrada en BD local. Se intentará usar tal cual.")
        
        except Exception as e:
            logger.error(f"⚠️ Error resolviendo flota: {e}")

        # Pasamos USER Y ROLE AQUÍ 👇
        historic_id = await TransactionManager.start_transaction(script_id, user=user, role=role)
        if historic_id:
             await HistoryRepository.log_device_snapshot(historic_id, uuid, TransactionStatus.EN_PROGRESO, snapshot)

        if not BalenaService.login():
            if historic_id: await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Fallo Login")
            return {"success": False, "message": "Fallo Login"}

        # 2. Mover en Balena con el SLUG
        if BalenaService.move_device(uuid, balena_target):
            try:
                # 3. Mover en BD Local con el ID LOCAL
                await InfoDevicesRepository.update_device_fleet(uuid, fleet_id_local)
                
                # Bonus: Actualizar variables si es necesario (sync parcial)
                # ...
                
            except Exception as e:
                logger.error(f"⚠️ Balena moved OK but DB update failed: {e}")
                # No retornamos False porque en Balena SÍ se movió.
                if historic_id:
                     await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Balena OK. Error BD: {e}")
                return {"success": True, "message": f"Movido en Balena, error en BD: {e}"}
                
            if historic_id: 
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Movido a {fleet_id_local}")
            return {"success": True, "message": "Dispositivo movido correctamente."}
        
        if historic_id: 
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Balena rechazó movimiento")
        return {"success": False, "message": "Error moviendo en Balena."}

    # ==========================================
    # 5. ELIMINAR DISPOSITIVO
    # ==========================================
    @classmethod
    async def remove_device(cls, uuid: str, user: str = "SYSTEM", role: str = "SYSTEM"):
        logger.info(f"🗑️ Eliminando dispositivo {uuid} solicitador por {user}...")

        script_id = ScriptIds.MANUAL_DELETE_INSPECTOR
        snapshot = await InfoDevicesRepository.get_device_by_uuid(uuid) or {}

        # 1. Iniciar Transacción
        historic_id = await TransactionManager.start_transaction(script_id, user=user, role=role)
        if historic_id:
            await HistoryRepository.log_device_snapshot(historic_id, uuid, TransactionStatus.EN_PROGRESO, snapshot)

        # 2. Login Balena
        if not BalenaService.login():
            if historic_id: await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Fallo Login Balena")
            return {"success": False, "message": "Fallo Login Balena"}

        # 3. Eliminar de Balena
        balena_success = await run_in_threadpool(BalenaService.remove_device, uuid)
        
        if not balena_success:
            if historic_id: await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Error eliminando en Balena")
            return {"success": False, "message": "Error eliminando en Balena Cloud. Operación abortada."}

        # 4. Eliminar de DB Local
        try:
            db_success = await InfoDevicesRepository.delete_device(uuid)
            status = TransactionStatus.COMPLETO if db_success else TransactionStatus.FALLIDO
            msg = "Dispositivo eliminado correctamente." if db_success else "Eliminado de Balena, pero error en BD local."
            
            if historic_id: 
                await TransactionManager.finish_transaction(historic_id, script_id, status, msg)
            
            return {"success": db_success, "message": msg}

        except Exception as e:
            if historic_id: 
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, f"Error DB: {e}")
            return {"success": False, "message": f"Error eliminando de BD: {e}"}
