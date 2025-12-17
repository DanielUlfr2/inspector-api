from fastapi import APIRouter, HTTPException, Body
from src.services.fleet_admin_service import FleetAdminService
from src.api.v1.schemas.fleet_schema import FleetCreateRequest, FleetRenameRequest

router = APIRouter()

# --- 1. CATALOGO DE DISPOSITIVOS ---
@router.get("/supported-devices")
async def get_supported_devices():
    """Retorna lista para el dropdown 'Tipo de Dispositivo'"""
    # Reutilizamos el repo directamente o a través del servicio
    from src.repositories.fleet_repo import FleetRepository
    return await FleetRepository.get_all_device_types()

# --- 2. CREAR FLOTA ---
@router.post("/", status_code=201)
async def create_fleet(request: FleetCreateRequest):
    result = await FleetAdminService.create_fleet(request)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# --- 3. RENOMBRAR FLOTA ---
@router.put("/{fleet_name}/rename")
async def rename_fleet(fleet_name: str, request: FleetRenameRequest):
    result = await FleetAdminService.rename_fleet(fleet_name, request.new_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# --- 4. ELIMINAR FLOTA ---
@router.delete("/{fleet_name}")
async def delete_fleet(fleet_name: str):
    result = await FleetAdminService.delete_fleet(fleet_name)
    
    if not result["success"]:
        # Si el error es por flota llena, usamos 409 Conflict
        if result.get("error_code") == "FLEET_NOT_EMPTY":
            raise HTTPException(status_code=409, detail=result["message"])
        
        # Cualquier otro error
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result