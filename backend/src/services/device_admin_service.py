import logging
from fastapi.concurrency import run_in_threadpool
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
    async def move_device_to_fleet(cls, uuid: str, target_fleet_slug: str, user: str = "SYSTEM", role: str = "SYSTEM"):
        logger.info(f"🚚 Moviendo {uuid} -> {target_fleet_slug} por {user}")
        
        script_id = cls.SCRIPT_MAP["move"]
        snapshot = await InfoDevicesRepository.get_device_by_uuid(uuid) or {}
        
        # PASAMOS USER Y ROLE AQUÍ 👇
        historic_id = await TransactionManager.start_transaction(script_id, user=user, role=role)
        if historic_id:
             await HistoryRepository.log_device_snapshot(historic_id, uuid, TransactionStatus.EN_PROGRESO, snapshot)

        if not BalenaService.login():
            if historic_id: await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Fallo Login")
            return {"success": False, "message": "Fallo Login"}

        if BalenaService.move_device(uuid, target_fleet_slug):
            try:
                await InfoDevicesRepository.update_device_fleet(uuid, target_fleet_slug)
            except Exception as e:
                logger.error(f"⚠️ Balena moved OK but DB update failed: {e}")
                
            if historic_id: 
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Movido a {target_fleet_slug}")
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
