from fastapi import APIRouter, HTTPException, status
from src.worker.tasks import task_run_automatic_sync
from src.utils.transaction_manager import TransactionManager, TransactionStatus, ScriptIds

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