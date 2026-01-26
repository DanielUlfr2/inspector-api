from fastapi import APIRouter, HTTPException, status
from src.worker.tasks import task_run_automatic_sync
from src.utils.transaction_manager import TransactionManager, TransactionStatus, ScriptIds
from src.services.inventory_sync import InventorySyncService

router = APIRouter()

@router.post("/inventory", status_code=202)
async def sync_inventory():
    """
    Encola la tarea de sincronización SOLO si no hay una en curso.
    """
    script_id = ScriptIds.MANUAL_SYNC

    # 1. VERIFICACIÓN
    current_status = await TransactionManager.get_current_status(script_id)
    
    if current_status == TransactionStatus.EN_PROGRESO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"⚠️ Ya existe una sincronización en curso."
        )

    # 2. ENCOLADO
    task = task_run_automatic_sync.delay(is_manual=True)
    
    return {
        "message": "Sincronización encolada correctamente 🚀",
        "task_id": task.id,
        "monitor_status": "Revisa la tabla ScriptTransaction"
    }

@router.post("/inventory/fleet/{fleet_id}")
async def sync_fleet_inventory(fleet_id: str):
    """
    Sincroniza solo una flota específica con Balena Cloud.
    Más rápido que sincronizar todo el inventario.
    
    Args:
        fleet_id: ID de la flota (app_name)
        
    Returns:
        Resultado de la sincronización con número de dispositivos
    """
    # Verificar si hay una sincronización en progreso
    script_id = ScriptIds.MANUAL_SYNC
    current_status = await TransactionManager.get_current_status(script_id)
    
    if current_status == TransactionStatus.EN_PROGRESO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="⚠️ Ya existe una sincronización en curso. Espera a que termine."
        )
    
    try:
        # Ejecutar sincronización directamente (no en cola)
        result = await InventorySyncService.sync_single_fleet(fleet_id, user="API", role="operator")
        return result
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sincronizando flota: {error_msg}"
        )
