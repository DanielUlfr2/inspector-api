from fastapi import APIRouter
from src.api.v1.endpoints import health, info_devices, sync, configuration

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(configuration.router, prefix="/configuration", tags=["configuration"])
# CAMBIO AQUÍ: De /inspector a /infodevices
api_router.include_router(info_devices.router, prefix="/infodevices", tags=["Info Devices"])