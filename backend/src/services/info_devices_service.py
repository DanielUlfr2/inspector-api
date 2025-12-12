from typing import List
from src.repositories.info_devices_repo import InfoDevicesRepository
from src.models.info_devices import DeviceInfoSchema

class InfoDevicesService:
    
    @staticmethod
    async def get_device_list() -> List[DeviceInfoSchema]:
        # Aquí podrías filtrar por usuario o rol en el futuro
        return await InfoDevicesRepository.get_all_devices()