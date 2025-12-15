from fastapi import APIRouter, HTTPException, status
from src.worker.tasks import task_run_configuration_sync
from src.utils.transaction_manager import TransactionManager, TransactionStatus, ScriptIds
from pydantic import BaseModel
from src.services.configuration_sync import ConfigurationSyncService

router = APIRouter()

class VariableInput(BaseModel):
    name: str
    value: str

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

@router.post("/fleet/{slug:path}/variable", status_code=201)
async def set_fleet_variable(slug: str, var: VariableInput):
    """
    Crea o actualiza una variable de flota.
    Recibe: {"name": "WIFI", "value": "123"}
    """
    # Llamamos al servicio coordinador
    success = await ConfigurationSyncService.create_fleet_variable(slug, var.name, var.value)
    
    if not success:
        raise HTTPException(status_code=500, detail="Fallo al crear variable en Balena cloud")
    
    return {"message": "Variable creada/actualizada correctamente", "data": var}

@router.post("/device/{uuid}/variable", status_code=201)
async def set_device_variable(uuid: str, var: VariableInput):
    """
    Crea o actualiza una variable de dispositivo.
    Recibe: {"name": "WIFI", "value": "123"}
    """
    # Llamamos al servicio coordinador
    success = await ConfigurationSyncService.create_device_variable(uuid, var.name, var.value)
    
    if not success:
        raise HTTPException(status_code=500, detail="Fallo al crear variable en Balena cloud")
    
    return {"message": "Variable creada/actualizada correctamente", "data": var}