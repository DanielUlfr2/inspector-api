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

# --- NOTA SOBRE TAREAS DE INVENTARIO INDIVIDUAL ---
# En el InventorySyncService actual NO definimos 'sync_device_by_uuid' ni 'sync_fleet_by_slug'.
# Solo definimos 'sync_all'. 
# Por tanto, he REMOVIDO esas tareas aquí para evitar errores de "AttributeError".
# Si las necesitas, debemos crear esos métodos en el servicio primero.