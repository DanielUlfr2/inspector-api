from fastapi import APIRouter, HTTPException, status, Header
from src.worker.tasks import task_run_configuration_sync
from src.utils.transaction_manager import TransactionManager, TransactionStatus, ScriptIds
from src.services.configuration_sync import ConfigurationSyncService
from src.api.v1.schemas.variable_schema import VariableRequest

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

@router.get("/fleet/{slug:path}/variables")
async def get_fleet_variables(slug: str):
    """
    Obtiene todas las variables de una flota específica.
    """
    result = await ConfigurationSyncService.get_fleet_variables(slug)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return {
        "fleet_id": slug,
        "variables": result["variables"]
    }

@router.post("/fleet/{slug:path}/variable", status_code=201)
async def set_fleet_variable(
    slug: str, 
    var: VariableRequest,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), # 👇 CAPTURA USUARIO
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Crea o actualiza una variable de flota.
    """
    result = await ConfigurationSyncService.create_fleet_variable(
        fleet_identifier=slug, 
        key=var.name, 
        value=var.value,
        user=x_user_id, 
        role=x_role
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return {"message": result["message"], "data": var}

@router.post("/device/{uuid}/variable", status_code=201)
async def set_device_variable(
    uuid: str, 
    var: VariableRequest,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), # 👇 CAPTURA USUARIO
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Crea o actualiza una variable de dispositivo.
    """
    result = await ConfigurationSyncService.create_device_variable(
        uuid=uuid, 
        key=var.name, 
        value=var.value,
        user=x_user_id, 
        role=x_role
    )
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return {"message": result["message"], "data": var}

@router.get("/device/{uuid}/variables")
async def get_device_variables(uuid: str):
    """
    Obtiene todas las variables de un dispositivo específico.
    """
    result = await ConfigurationSyncService.get_device_variables(uuid)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return {
        "device_uuid": uuid,
        "variables": result["variables"]
    }

@router.delete("/fleet/{slug:path}/variable/{key}", status_code=200)
async def delete_fleet_variable(
    slug: str, 
    key: str,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Elimina una variable de flota.
    """
    result = await ConfigurationSyncService.delete_fleet_variable(slug, key, x_user_id, x_role)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

@router.delete("/device/{uuid}/variable/{key}", status_code=200)
async def delete_device_variable(
    uuid: str, 
    key: str,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Elimina una variable de dispositivo.
    """
    result = await ConfigurationSyncService.delete_device_variable(uuid, key, x_user_id, x_role)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result