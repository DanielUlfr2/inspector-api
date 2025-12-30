#device_admin.py
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Depends
from src.services.device_admin_service import DeviceAdminService
from src.services.balena_service import BalenaService
from src.api.v1.schemas.provisioning_schema import ProvisioningRequest
from src.api.v1.schemas.device_action_schema import DeviceNoteRequest, DeviceMoveRequest
from fastapi.responses import StreamingResponse
from src.core.security import require_roles

router = APIRouter()

@router.post("/{uuid}/provision")
async def provision_device_endpoint(
    uuid: str, 
    request: ProvisioningRequest,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    result = await DeviceAdminService.provision_device(uuid, request, user=x_user_id, role=x_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/{uuid}/reboot", status_code=200)
async def reboot_device_endpoint(
    uuid: str, 
    background_tasks: BackgroundTasks,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Reinicia el dispositivo (OS) en segundo plano.
    """
    background_tasks.add_task(DeviceAdminService.execute_power_action, uuid, "reboot", user=x_user_id, role=x_role)
    return {"success": True, "message": "Reinicio de sistema iniciado. Verifique el historial."}

@router.post("/{uuid}/restart", status_code=200)
async def restart_container_endpoint(
    uuid: str, 
    background_tasks: BackgroundTasks,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Reinicia la aplicación (Contenedor) en segundo plano.
    """
    background_tasks.add_task(DeviceAdminService.execute_power_action, uuid, "restart", user=x_user_id, role=x_role)
    return {"success": True, "message": "Reinicio de aplicación iniciado. Verifique el historial."}

@router.post("/{uuid}/shutdown", status_code=200)
async def shutdown_device_endpoint(
    uuid: str, 
    background_tasks: BackgroundTasks,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Apaga el dispositivo en segundo plano.
    """
    background_tasks.add_task(DeviceAdminService.execute_power_action, uuid, "shutdown", user=x_user_id, role=x_role)
    return {"success": True, "message": "Apagado iniciado. Verifique el historial."}

@router.put("/{uuid}/note")
async def set_device_note_endpoint(
    uuid: str, 
    request: DeviceNoteRequest, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    result = await DeviceAdminService.set_note(uuid, request, user=x_user_id, role=x_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/{uuid}/move")
async def move_device_endpoint(
    uuid: str, 
    request: DeviceMoveRequest, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    result = await DeviceAdminService.move_device_to_fleet(uuid, request.target_fleet, user=x_user_id, role=x_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# --- Endpoint antiguo de Provision (Recomendado: Eliminar si ya usas el de arriba con {uuid}) ---
@router.post("/provision")
async def provision_device(
    request: ProvisioningRequest, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    if not request.uuid:
        raise HTTPException(status_code=400, detail="El UUID es obligatorio")

    result = await DeviceAdminService.provision_device(request.uuid, request, user=x_user_id, role=x_role)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

@router.get("/{uuid}/logs")
async def get_device_logs_stream(
    uuid: str,
    # Ahora coincide con el nombre en security.py
    user_data=Depends(require_roles(["Inspector_admin", "Inspector_operator"]))
):
    """
    Streaming en tiempo real de los logs del dispositivo.
    Bypass: Frontend -> Backend (Puerto 5000)
    """
    log_generator = BalenaService.stream_device_logs(uuid)
    
    headers = {
        "X-Accel-Buffering": "no",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
    
    return StreamingResponse(log_generator, media_type="text/event-stream", headers=headers)