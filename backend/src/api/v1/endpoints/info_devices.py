from fastapi import APIRouter, HTTPException
from typing import List
from src.services.info_devices_service import InfoDevicesService
from src.models.info_devices import DeviceInfoSchema

router = APIRouter()

@router.get("", response_model=List[DeviceInfoSchema])
async def read_info_devices():
    """
    Obtiene el listado de dispositivos (Sondas) desde la BD Real.
    """
    devices = await InfoDevicesService.get_device_list()
    return devices