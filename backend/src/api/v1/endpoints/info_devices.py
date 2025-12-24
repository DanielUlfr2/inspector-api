from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from src.services.info_devices_service import InfoDevicesService
from src.models.info_devices import DeviceInfoSchema, DeviceDetailSchema
from src.repositories.info_devices_repo import InfoDevicesRepository

router = APIRouter()

# --- LISTADO GENERAL ---
@router.get("", response_model=List[DeviceInfoSchema])
async def read_info_devices():
    """
    Obtiene el listado de dispositivos (Sondas) desde la BD Real.
    """
    devices = await InfoDevicesService.get_device_list()
    return devices

# --- HISTORIAL PARA GRÁFICAS ---
@router.get("/{uuid}/history")
async def get_device_history(
    uuid: str,
    start_date: Optional[datetime] = Query(None, description="Fecha inicio (ISO)"),
    end_date: Optional[datetime] = Query(None, description="Fecha fin (ISO)")
):
    """
    Retorna los puntos para las gráficas del Dashboard (CPU, RAM, Temp, etc).
    Si no se envían fechas, retorna las últimas 24 horas por defecto.
    """
    # Lógica por defecto: Últimas 24 horas si no especifica
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(hours=24)

    history_data = await InfoDevicesRepository.get_device_history_range(uuid, start_date, end_date)
    
    if history_data is None:
        return [] # Retornamos lista vacía en vez de error si no hay datos
        
    return history_data

@router.get("/{uuid}", response_model=DeviceDetailSchema)
async def get_device_detail(uuid: str):
    """
    Obtiene la ficha técnica completa de un dispositivo específico.
    Incluye nombres de estatus y servicio.
    """
    device = await InfoDevicesRepository.get_device_detail_full(uuid)
    
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        
    return device