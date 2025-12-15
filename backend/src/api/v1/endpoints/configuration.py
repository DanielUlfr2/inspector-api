from fastapi import APIRouter, HTTPException, status
from src.worker.tasks import task_run_configuration_sync
from src.utils.transaction_manager import TransactionManager, TransactionStatus, ScriptIds

router = APIRouter()

@router.post("/sync", status_code=202)
async def sync_all_configuration():
    """
    Dispara la recolección COMPLETA de variables (Flotas y Equipos).
    """
    script_id = ScriptIds.MANUAL_VARS_SYNC

    current_status = await TransactionManager.get_current_status(script_id)
    if current_status == TransactionStatus.EN_PROGRESO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="⚠️ Ya se están sincronizando las variables."
        )

    task = task_run_configuration_sync.delay(is_manual=True)
    
    return {
        "message": "Sincronización de Configuración encolada 📦",
        "task_id": task.id,
        "monitor_status": "Revisa script MANUAL_COLLECTION_VARS_INSPECTOR"
    }