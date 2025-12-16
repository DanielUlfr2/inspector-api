from fastapi import APIRouter
from src.api.v1.endpoints import health, info_devices, sync, configuration, catalogs, device_admin

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(configuration.router, prefix="/configuration", tags=["configuration"])
api_router.include_router(info_devices.router, prefix="/infodevices", tags=["Info Devices"])
api_router.include_router(catalogs.router, prefix="/catalogs", tags=["Catalogs"])
api_router.include_router(device_admin.router, prefix="/admin", tags=["Admin"]) 