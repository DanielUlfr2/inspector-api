import logging
from src.services.balena_service import BalenaService
from src.repositories.provisioning_repo import ProvisioningRepository
from src.repositories.info_devices_repo import InfoDevicesRepository
from src.repositories.history_repo import HistoryRepository
from src.utils.transaction_manager import TransactionManager, ScriptIds, TransactionStatus
from src.api.v1.schemas.provisioning_schema import ProvisioningRequest
from src.api.v1.schemas.device_action_schema import DeviceNoteRequest

logger = logging.getLogger(__name__)

class DeviceAdminService:

    # Mapeo: Acción del Frontend -> ID del Script en BD
    SCRIPT_MAP = {
        "reboot": ScriptIds.MANUAL_REBOOT,
        "restart": ScriptIds.MANUAL_RESTART,
        "shutdown": ScriptIds.MANUAL_SHUTDOWN,
        "rename": ScriptIds.MANUAL_RENAME,
        "move": ScriptIds.MANUAL_MOVE_FLEET,
        "note": ScriptIds.MANUAL_SET_VAR
    }

    # ==========================================
    # 1. PROVISIONING (Tu código existente)
    # ==========================================
    @classmethod
    async def provision_device(cls, uuid: str, data: ProvisioningRequest):
        """
        Flujo Completo:
        1. Renombrar en Balena (Nube).
        2. Guardar en PostgreSQL (Local).
        """
        logger.info(f"🚀 Iniciando Provisioning para {uuid}...")

        # A. Login Balena
        if not BalenaService.login():
            return {"success": False, "message": "Fallo Login Balena"}

        # B. Renombrar en Balena
        rename_ok = BalenaService.rename_device(uuid, data.new_device_name)
        if not rename_ok:
            return {"success": False, "message": "Error al renombrar en Balena Cloud. Revise conexión."}

        # C. Guardar en Base de Datos
        try:
            await ProvisioningRepository.create_service_and_link_device(uuid, data)
        except Exception as e:
            logger.error(f"⚠️ Desincronización: Balena renombró OK, pero BD falló: {e}")
            return {"success": False, "message": f"Error guardando en BD: {str(e)}"}

        return {"success": True, "message": "Dispositivo aprovisionado correctamente."}

    # ==========================================
    # 2. ACCIONES DE PODER (Reboot, Restart, Shutdown)
    # ==========================================
    @classmethod
    async def execute_power_action(cls, uuid: str, action: str):
        logger.info(f"⚡ Solicitud '{action}' en {uuid}")
        
        # 1. Definir Script ID
        script_id = cls.SCRIPT_MAP.get(action, "DEFAULT")
        
        # 2. Obtener Snapshot (Foto del equipo ANTES de la acción)
        snapshot = await InfoDevicesRepository.get_device_by_uuid(uuid)
        if not snapshot: snapshot = {}

        # 3. Iniciar Transacción (Crea registro Padre en HistoricScriptTransaction)
        historic_id = await TransactionManager.start_transaction(script_id)

        # 4. Guardar Snapshot (Crea registro Hijo en StatusInspectorHistory)
        if historic_id:
            await HistoryRepository.log_device_snapshot(historic_id, uuid, TransactionStatus.EN_PROGRESO, snapshot)

        # 5. Validar Login
        if not BalenaService.login():
            if historic_id:
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Fallo Login Balena")
            return {"success": False, "message": "Fallo Login Balena CLI"}

        # 6. Ejecutar Acción en Balena
        success = False
        if action == "reboot": success = BalenaService.reboot_device(uuid)
        elif action == "restart": success = BalenaService.restart_device(uuid)
        elif action == "shutdown": success = BalenaService.shutdown_device(uuid)
        
        # 7. Cerrar Transacción
        status = TransactionStatus.COMPLETO if success else TransactionStatus.FALLIDO
        msg = f"Comando {action} ejecutado." if success else f"Error ejecutando {action} en Balena."
        
        if historic_id:
            await TransactionManager.finish_transaction(historic_id, script_id, status, msg)

        return {"success": success, "message": msg}

    # ==========================================
    # 3. GESTIÓN DE NOTAS
    # ==========================================
    @classmethod
    async def set_note(cls, uuid: str, data: DeviceNoteRequest):
        logger.info(f"📝 Asignando nota a {uuid}")
        
        script_id = cls.SCRIPT_MAP["note"]
        snapshot = await InfoDevicesRepository.get_device_by_uuid(uuid) or {}
        
        # Inicio Auditoría
        historic_id = await TransactionManager.start_transaction(script_id)
        if historic_id:
            await HistoryRepository.log_device_snapshot(historic_id, uuid, TransactionStatus.EN_PROGRESO, snapshot)

        if not BalenaService.login():
            if historic_id: await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Fallo Login")
            return {"success": False, "message": "Fallo Login"}

        # Ejecución
        if BalenaService.set_device_note(uuid, data.note):
            try:
                # Actualizamos BD Local inmediatamente
                await InfoDevicesRepository.update_device_note(uuid, data.note)
                
                if historic_id: 
                    await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Nota: {data.note}")
                return {"success": True, "message": "Nota guardada correctamente."}
            except Exception as e:
                # Si falla BD local pero Balena funcionó
                if historic_id: 
                    await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Balena OK, BD Error: {e}")
                return {"success": True, "message": "Nota en Balena OK, error en BD local."}
        
        # Si falló Balena
        if historic_id: await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Error Balena API")
        return {"success": False, "message": "Error al guardar nota en Balena."}

    # ==========================================
    # 4. MOVER DE FLOTA
    # ==========================================
    @classmethod
    async def move_device_to_fleet(cls, uuid: str, target_fleet_slug: str):
        logger.info(f"🚚 Moviendo {uuid} -> {target_fleet_slug}")
        
        script_id = cls.SCRIPT_MAP["move"]
        snapshot = await InfoDevicesRepository.get_device_by_uuid(uuid) or {}
        
        # Inicio Auditoría
        historic_id = await TransactionManager.start_transaction(script_id)
        if historic_id:
             await HistoryRepository.log_device_snapshot(historic_id, uuid, TransactionStatus.EN_PROGRESO, snapshot)

        if not BalenaService.login():
            if historic_id: await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Fallo Login")
            return {"success": False, "message": "Fallo Login"}

        if BalenaService.move_device(uuid, target_fleet_slug):
            # Nota: Aquí podríamos actualizar la BD local si tuvieras el método update_device_fleet.
            # Por ahora confiamos en que el Sync Service detectará el cambio de flota después.
            
            if historic_id: 
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Movido a {target_fleet_slug}")
            return {"success": True, "message": "Dispositivo movido correctamente."}
        
        if historic_id: 
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Balena rechazó movimiento")
        return {"success": False, "message": "Error moviendo en Balena."}