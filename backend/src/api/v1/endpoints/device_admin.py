from fastapi import APIRouter, HTTPException, Header
from src.services.device_admin_service import DeviceAdminService
from src.api.v1.schemas.provisioning_schema import ProvisioningRequest
from src.api.v1.schemas.device_action_schema import DeviceNoteRequest, DeviceMoveRequest

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

@router.post("/{uuid}/reboot")
async def reboot_device_endpoint(
    uuid: str, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    result = await DeviceAdminService.execute_power_action(uuid, "reboot", user=x_user_id, role=x_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/{uuid}/restart")
async def restart_container_endpoint(
    uuid: str, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    result = await DeviceAdminService.execute_power_action(uuid, "restart", user=x_user_id, role=x_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/{uuid}/shutdown")
async def shutdown_device_endpoint(
    uuid: str, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    result = await DeviceAdminService.execute_power_action(uuid, "shutdown", user=x_user_id, role=x_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

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