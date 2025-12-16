from fastapi import APIRouter, HTTPException
from src.services.device_admin_service import DeviceAdminService
from src.api.v1.schemas.provisioning_schema import ProvisioningRequest

router = APIRouter()

@router.post("/{uuid}/provision")
async def provision_device_endpoint(uuid: str, request: ProvisioningRequest):
    """
    Recibe el formulario de legalización y ejecuta el aprovisionamiento.
    """
    result = await DeviceAdminService.provision_device(uuid, request)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result