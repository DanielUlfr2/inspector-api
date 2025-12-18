import logging
import asyncio
from src.services.balena_service import BalenaService
from src.repositories.fleet_repo import FleetRepository
from src.repositories.info_devices_repo import InfoDevicesRepository
from src.repositories.history_repo import HistoryRepository
from src.utils.transaction_manager import TransactionManager, ScriptIds, TransactionStatus

logger = logging.getLogger(__name__)

class ConfigurationSyncService:
    
    MAX_CONCURRENT_TASKS = 5

    # =========================================================================
    # 1. SINCRONIZACIÓN MAESTRA (CRON JOB)
    # =========================================================================
    @classmethod
    async def sync_all_variables(cls):
        """
        Proceso MAESTRO con AUDITORÍA:
        1. Inicia Transacción Global (AUTO).
        2. Compara y Audita variables de flotas.
        3. Compara y Audita variables de equipos (en paralelo).
        """
        # ID CORRECTO: AUTOMATIC_COLLECTION_VARS_INSPECTOR
        script_id = ScriptIds.AUTO_VARS_SYNC
        
        logger.info(f"🔧 INICIANDO SYNC DE VARIABLES (Auditoría Activada)...")

        if not BalenaService.login():
            logger.error("🛑 Abortado: Fallo login Balena.")
            return False

        # Iniciamos transacción global
        historic_id = await TransactionManager.start_transaction(script_id, user="SYSTEM", role="SYSTEM")
        
        try:
            # --- FASE 1: FLOTAS ---
            raw_fleets = BalenaService.get_fleets()
            
            for f in raw_fleets:
                fleet_id_db = f.get("app_name") 
                slug_balena = f.get("slug")
                
                if fleet_id_db and slug_balena:
                    await cls.sync_fleet_variables(slug_balena, fleet_id_db, historic_id_override=historic_id)

            # --- FASE 2: DISPOSITIVOS ---
            all_uuids = await InfoDevicesRepository.get_all_uuids() 
            
            if all_uuids:
                semaphore = asyncio.Semaphore(cls.MAX_CONCURRENT_TASKS)
                tasks = []
                for uuid in all_uuids:
                    tasks.append(cls._worker_sync_device(uuid, historic_id, semaphore))
                await asyncio.gather(*tasks)

            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, "Sync Variables Finalizado")
            return True

        except Exception as e:
            logger.error(f"❌ Error Critical Vars Sync: {e}")
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, str(e))
            return False

    @classmethod
    async def _worker_sync_device(cls, uuid, historic_id, semaphore):
        async with semaphore:
            await cls.sync_device_variables(uuid, historic_id_override=historic_id)

    # =========================================================================
    # 2. LÓGICA DE COMPARACIÓN (SYNC / DIFF)
    # =========================================================================
    
    @classmethod
    async def sync_fleet_variables(cls, fleet_slug_balena: str, fleet_id_db: str = None, historic_id_override: int = None):
        if not fleet_id_db:
             raw_fleets = BalenaService.get_fleets()
             fleet_id_db = next((f.get("app_name") for f in raw_fleets if f.get("slug") == fleet_slug_balena), None)
             if not fleet_id_db: return False

        historic_id = historic_id_override
        should_close_transaction = False
        
        # ID CORRECTO: MANUAL_COLLECTION_VARS_INSPECTOR (Si se invoca solo)
        script_id = ScriptIds.MANUAL_VARS_SYNC

        if not historic_id:
            historic_id = await TransactionManager.start_transaction(script_id, user="SYSTEM", role="SYSTEM")
            should_close_transaction = True

        try:
            vars_list = BalenaService.get_fleet_vars(fleet_slug_balena)
            remote_vars = {v['name']: v['value'] for v in vars_list} if vars_list else {}
            local_vars = await FleetRepository.get_variables_dict(fleet_id_db)

            # 1. Nuevas y Actualizadas
            for name, r_val in remote_vars.items():
                l_val = local_vars.get(name)
                
                if l_val is None: # CREATE
                    await FleetRepository.upsert_variable(fleet_id_db, name, r_val)
                    await HistoryRepository.log_variable_audit(historic_id, 'FLEET', fleet_id_db, name, 'CREATE', None, r_val)
                
                elif str(l_val) != str(r_val): # UPDATE
                    await FleetRepository.upsert_variable(fleet_id_db, name, r_val)
                    await HistoryRepository.log_variable_audit(historic_id, 'FLEET', fleet_id_db, name, 'UPDATE', l_val, r_val)

            # 2. Eliminadas
            for name, l_val in local_vars.items():
                if name not in remote_vars: # DELETE
                    await FleetRepository.delete_variable(fleet_id_db, name)
                    await HistoryRepository.log_variable_audit(historic_id, 'FLEET', fleet_id_db, name, 'DELETE', l_val, None)

            if should_close_transaction:
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Vars Sync {fleet_id_db} OK")
            return True

        except Exception as e:
            if should_close_transaction:
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, str(e))
            return False

    @classmethod
    async def sync_device_variables(cls, uuid: str, historic_id_override: int = None):
        historic_id = historic_id_override
        should_close_transaction = False
        
        # ID CORRECTO: MANUAL_COLLECTION_VARS_INSPECTOR
        script_id = ScriptIds.MANUAL_VARS_SYNC

        if not historic_id:
            historic_id = await TransactionManager.start_transaction(script_id, user="SYSTEM", role="SYSTEM")
            should_close_transaction = True

        try:
            vars_list = BalenaService.get_device_vars(uuid)
            remote_vars = {v['name']: v['value'] for v in vars_list} if vars_list else {}
            local_vars = await InfoDevicesRepository.get_variables_dict(uuid)

            for name, r_val in remote_vars.items():
                l_val = local_vars.get(name)
                if l_val is None:
                    await InfoDevicesRepository.upsert_variable(uuid, name, r_val)
                    await HistoryRepository.log_variable_audit(historic_id, 'DEVICE', uuid, name, 'CREATE', None, r_val)
                elif str(l_val) != str(r_val):
                    await InfoDevicesRepository.upsert_variable(uuid, name, r_val)
                    await HistoryRepository.log_variable_audit(historic_id, 'DEVICE', uuid, name, 'UPDATE', l_val, r_val)

            for name, l_val in local_vars.items():
                if name not in remote_vars:
                    await InfoDevicesRepository.delete_variable(uuid, name)
                    await HistoryRepository.log_variable_audit(historic_id, 'DEVICE', uuid, name, 'DELETE', l_val, None)

            if should_close_transaction:
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Vars Sync {uuid} OK")
            return True

        except Exception as e:
            if should_close_transaction:
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, str(e))
            return False

    # =========================================================================
    # 4. CREACIÓN MANUAL (CORREGIDA ✅)
    # Usa: MANUAL_SET_VAR_INSPECTOR
    # =========================================================================

    @classmethod
    async def create_fleet_variable(cls, fleet_identifier: str, key: str, value: str, user: str = "SYSTEM", role: str = "SYSTEM"):
        logger.info(f"🔧 Set Variable Flota: {key} en {fleet_identifier} por {user}")
        
        # 👇 ID CORRECTO: MANUAL_SET_VAR_INSPECTOR
        script_id = ScriptIds.MANUAL_SET_VAR 
        
        historic_id = await TransactionManager.start_transaction(script_id, user=user, role=role)

        if not BalenaService.login(): 
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Login Balena Fallido")
            return {"success": False, "message": "Fallo Login Balena"}

        # 1. Balena Cloud
        success = await asyncio.to_thread(BalenaService.set_fleet_variable, fleet_identifier, key, value)
        
        if not success:
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Balena rechazó la variable")
            return {"success": False, "message": "Balena Cloud rechazó la variable."}

        # 2. BD Local y Auditoría Correcta
        try:
            # A. Obtener valor actual para definir acción
            current_vars = await FleetRepository.get_variables_dict(fleet_identifier)
            old_val = current_vars.get(key)
            
            # 👇 CORRECCIÓN CLAVE: Usamos 'UPDATE' o 'CREATE' válidos
            action = "UPDATE" if old_val is not None else "CREATE"

            # B. Upsert BD
            await FleetRepository.upsert_variable(fleet_identifier, key, value)
            
            # C. Auditoría
            if historic_id:
                await HistoryRepository.log_variable_audit(
                    historic_id, 
                    'FLEET', 
                    fleet_identifier, 
                    key, 
                    action,    # <--- Ahora sí es válido ('CREATE'/'UPDATE')
                    old_val, 
                    value
                )
                
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Var {key} establecida.")
            return {"success": True, "message": "Variable establecida correctamente"}

        except Exception as e:
            logger.error(f"❌ Error BD: {e}")
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, str(e))
            return {"success": False, "message": f"Error interno BD: {e}"}

    @classmethod
    async def create_device_variable(cls, uuid: str, key: str, value: str, user: str = "SYSTEM", role: str = "SYSTEM"):
        logger.info(f"🔧 Set Variable Device: {key} en {uuid} por {user}")
        
        # 👇 ID CORRECTO: MANUAL_SET_VAR_INSPECTOR
        script_id = ScriptIds.MANUAL_SET_VAR
        
        historic_id = await TransactionManager.start_transaction(script_id, user=user, role=role)

        if not BalenaService.login(): 
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Login Balena Fallido")
            return {"success": False, "message": "Fallo Login Balena"}

        # 1. Balena
        success = await asyncio.to_thread(BalenaService.set_device_variable, uuid, key, value)
        
        if not success:
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Balena rechazó la variable")
            return {"success": False, "message": "Balena Cloud rechazó la variable."}

        try:
            # A. Obtener valor actual para definir acción
            current_vars = await InfoDevicesRepository.get_variables_dict(uuid)
            old_val = current_vars.get(key)
            
            # 👇 CORRECCIÓN CLAVE: Usamos 'UPDATE' o 'CREATE' válidos
            action = "UPDATE" if old_val is not None else "CREATE"

            # B. Upsert BD
            await InfoDevicesRepository.upsert_variable(uuid, key, value)
            
            # C. Auditoría
            if historic_id:
                await HistoryRepository.log_variable_audit(
                    historic_id, 
                    'DEVICE', 
                    uuid, 
                    key, 
                    action,  # <--- Ahora sí es válido ('CREATE'/'UPDATE')
                    old_val, 
                    value
                )

            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Var {key} establecida.")
            return {"success": True, "message": "Variable establecida correctamente"}

        except Exception as e:
            logger.error(f"❌ Error BD: {e}")
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, str(e))
            return {"success": False, "message": f"Error interno BD: {e}"}


    # =========================================================================
    # 5. ELIMINACIÓN MANUAL (CON AUDITORÍA) 🗑️
    # =========================================================================

    @classmethod
    async def delete_fleet_variable(cls, fleet_identifier: str, key: str, user: str, role: str):
        logger.info(f"🗑️ Eliminando variable {key} en flota {fleet_identifier} por {user}")
        
        script_id = ScriptIds.MANUAL_SET_VAR # Usamos el mismo script de gestión de vars
        historic_id = await TransactionManager.start_transaction(script_id, user=user, role=role)

        if not BalenaService.login():
             await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Login Fallido")
             return {"success": False, "message": "Login Balena falló"}

        # 1. Guardar valor actual para la auditoría (El "Old Value")
        current_vars = await FleetRepository.get_variables_dict(fleet_identifier)
        old_val = current_vars.get(key)

        if old_val is None:
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, "Variable no existía")
            return {"success": True, "message": "La variable no existía, nada que borrar."}

        # 2. Borrar en Balena
        success = await asyncio.to_thread(BalenaService.remove_fleet_variable, fleet_identifier, key)
        if not success:
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Balena Error")
            return {"success": False, "message": "Error al eliminar en Balena Cloud"}

        try:
            # 3. Borrar en BD Local
            await FleetRepository.delete_variable(fleet_identifier, key)

            # 4. Auditoría (Action=DELETE, Old=Valor, New=NULL)
            if historic_id:
                await HistoryRepository.log_variable_audit(
                    historic_id, 'FLEET', fleet_identifier, key, 'DELETE', old_val, None
                )

            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Var {key} eliminada")
            return {"success": True, "message": "Variable eliminada correctamente"}

        except Exception as e:
            logger.error(f"❌ Error BD Delete: {e}")
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, str(e))
            return {"success": False, "message": f"Error BD: {e}"}

    @classmethod
    async def delete_device_variable(cls, uuid: str, key: str, user: str, role: str):
        logger.info(f"🗑️ Eliminando variable {key} en dispositivo {uuid} por {user}")
        
        script_id = ScriptIds.MANUAL_SET_VAR
        historic_id = await TransactionManager.start_transaction(script_id, user=user, role=role)

        if not BalenaService.login(): return {"success": False, "message": "Login Balena falló"}

        # 1. Snapshot valor viejo
        current_vars = await InfoDevicesRepository.get_variables_dict(uuid)
        old_val = current_vars.get(key)

        if old_val is None:
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, "Variable no existía")
            return {"success": True, "message": "La variable no existía."}

        # 2. Balena
        success = await asyncio.to_thread(BalenaService.remove_device_variable, uuid, key)
        if not success:
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, "Balena Error")
            return {"success": False, "message": "Error al eliminar en Balena Cloud"}

        try:
            # 3. BD Local
            await InfoDevicesRepository.delete_variable(uuid, key)

            # 4. Auditoría
            if historic_id:
                await HistoryRepository.log_variable_audit(
                    historic_id, 'DEVICE', uuid, key, 'DELETE', old_val, None
                )

            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.COMPLETO, f"Var {key} eliminada")
            return {"success": True, "message": "Variable eliminada correctamente"}

        except Exception as e:
            logger.error(f"❌ Error BD Delete: {e}")
            await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, str(e))
            return {"success": False, "message": f"Error BD: {e}"}