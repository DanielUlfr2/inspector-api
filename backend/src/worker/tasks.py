import asyncio
from src.core.celery_app import celery_app
from src.utils.transaction_manager import TransactionManager, TransactionStatus, ScriptIds
from src.services.inventory_sync import InventorySyncService
from asgiref.sync import async_to_sync
from src.core.logger import logger
from src.services.configuration_sync import ConfigurationSyncService
# Tarea 1: Sincronización Automática
@celery_app.task(name="tasks.run_automatic_sync")
def task_run_automatic_sync(is_manual=False):
    
    script_id = ScriptIds.MANUAL_SYNC if is_manual else ScriptIds.AUTO_SYNC
    logger.info(f"📨 WORKER RECIBIÓ TAREA: {script_id} | Manual: {is_manual}")
    
    async def _process():
        await TransactionManager.start_transaction(script_id)
        try:
            # Llamada simple, sin argumentos raros
            result = await InventorySyncService.sync_all()
            
            if result is False: 
                 raise Exception("Fallo en la lógica de sincronización (Ver logs)")

            await TransactionManager.finish_transaction(
                script_id, TransactionStatus.COMPLETO, "Sincronización finalizada correctamente."
            )
        except Exception as e:
            logger.error(f"❌ ERROR CRÍTICO EN TAREA {script_id}: {str(e)}", exc_info=True)
            await TransactionManager.finish_transaction(
                script_id, TransactionStatus.FALLIDO, f"Error crítico: {str(e)}"
            )

    async_to_sync(_process)()
    return f"Sync {script_id} completed"

# Tarea 2: Tareas puntuales (Las mantenemos porque son útiles y no estorban)
@celery_app.task(name="tasks.sync_single_device")
def task_sync_single_device(uuid: str):
    logger.info(f"📨 TAREA PUNTUAL: Sync Device {uuid}")
    async_to_sync(InventorySyncService.sync_device_by_uuid)(uuid) # Ojo: Asegurate de tener este método en InventorySyncService o bórrala de aquí si también quieres quitarla.
    # SI QUIERES LIMPIEZA TOTAL, borra estas tareas puntuales también por ahora.
    return f"Device {uuid} synced"

@celery_app.task(name="tasks.sync_single_fleet")
def task_sync_single_fleet(fleet_slug: str):
    logger.info(f"📨 TAREA PUNTUAL: Sync Fleet {fleet_slug}")
    async_to_sync(InventorySyncService.sync_fleet_by_slug)(fleet_slug)
    return f"Fleet {fleet_slug} synced"

@celery_app.task(name="tasks.run_configuration_sync")
def task_run_configuration_sync(is_manual=False):
    
    # Usamos los IDs que definimos para Variables
    script_id = ScriptIds.MANUAL_VARS_SYNC if is_manual else ScriptIds.AUTO_VARS_SYNC
    logger.info(f"📨 WORKER TAREA CONFIG: {script_id}")
    
    async def _process():
        await TransactionManager.start_transaction(script_id)
        try:
            # Llamamos al servicio DE CONFIGURACIÓN
            result = await ConfigurationSyncService.sync_all_variables()
            
            if result is False: raise Exception("Fallo en sync de variables")

            await TransactionManager.finish_transaction(
                script_id, TransactionStatus.COMPLETO, "Configuración actualizada."
            )
        except Exception as e:
            logger.error(f"❌ Error Config: {e}")
            await TransactionManager.finish_transaction(
                script_id, TransactionStatus.FALLIDO, f"Error: {str(e)}"
            )

    async_to_sync(_process)()
    return f"Config Sync {script_id} done"