from fastapi import APIRouter
from src.api.v1.endpoints import health

api_router = APIRouter()

# La ruta quedará accesible en: /api/v1/health
api_router.include_router(health.router, prefix="/health", tags=["system"])