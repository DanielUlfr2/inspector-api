from fastapi import APIRouter
from src.api.v1.endpoints import health, inspector

api_router = APIRouter()

# La ruta quedará accesible en: /api/v1/health
api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(inspector.router, prefix="/inspector", tags=["inspector"])