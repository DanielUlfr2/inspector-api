"""
Endpoints para monitoreo y gestión del cache avanzado
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import Dict, Any
import datetime

from app.services.cache import cache
from app.services.registro_cache_service import registro_cache_service
from app.services.deps import require_admin

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/cache/stats",
    summary="Estadísticas del cache",
    description="Devuelve estadísticas detalladas del sistema de cache. Requiere autenticación: solo admin."
)
async def get_cache_stats(user=Depends(require_admin)):
    """Endpoint para obtener estadísticas del cache"""
    try:
        stats = registro_cache_service.get_cache_stats()
        return {
            "message": "Estadísticas del cache obtenidas exitosamente",
            "stats": stats,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del cache: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas del cache")


@router.post(
    "/cache/clear",
    summary="Limpiar cache",
    description="Limpia todo el cache del sistema. Requiere autenticación: solo admin."
)
async def clear_cache(user=Depends(require_admin)):
    """Endpoint para limpiar todo el cache"""
    try:
        # Limpiar cache general
        cache.clear()
        
        # Limpiar cache específico de registros
        registro_cache_service.invalidate_registro_cache()
        registro_cache_service.invalidate_estadisticas_cache()
        
        return {
            "message": "Cache limpiado exitosamente",
            "cleared_at": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error al limpiar cache: {e}")
        raise HTTPException(status_code=500, detail="Error al limpiar cache")


@router.post(
    "/cache/cleanup",
    summary="Limpiar entradas expiradas",
    description="Limpia automáticamente las entradas expiradas del cache. Requiere autenticación: solo admin."
)
async def cleanup_expired_cache(user=Depends(require_admin)):
    """Endpoint para limpiar entradas expiradas del cache"""
    try:
        # Limpiar entradas expiradas del cache general
        expired_count = cache.cleanup_expired()
        
        return {
            "message": "Limpieza de cache completada",
            "expired_entries_removed": expired_count,
            "cleaned_at": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error al limpiar entradas expiradas: {e}")
        raise HTTPException(status_code=500, detail="Error al limpiar entradas expiradas")


@router.post(
    "/cache/invalidate/registros",
    summary="Invalidar cache de registros",
    description="Invalida específicamente el cache relacionado con registros. Requiere autenticación: solo admin."
)
async def invalidate_registros_cache(user=Depends(require_admin)):
    """Endpoint para invalidar cache de registros"""
    try:
        invalidated = registro_cache_service.invalidate_registro_cache()
        
        return {
            "message": "Cache de registros invalidado exitosamente",
            "invalidated_entries": invalidated,
            "invalidated_at": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error al invalidar cache de registros: {e}")
        raise HTTPException(status_code=500, detail="Error al invalidar cache de registros")


@router.post(
    "/cache/invalidate/estadisticas",
    summary="Invalidar cache de estadísticas",
    description="Invalida específicamente el cache relacionado con estadísticas. Requiere autenticación: solo admin."
)
async def invalidate_estadisticas_cache(user=Depends(require_admin)):
    """Endpoint para invalidar cache de estadísticas"""
    try:
        invalidated = registro_cache_service.invalidate_estadisticas_cache()
        
        return {
            "message": "Cache de estadísticas invalidado exitosamente",
            "invalidated_entries": invalidated,
            "invalidated_at": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error al invalidar cache de estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error al invalidar cache de estadísticas")


@router.get(
    "/cache/health",
    summary="Estado de salud del cache",
    description="Verifica el estado de salud del sistema de cache. Requiere autenticación: solo admin."
)
async def cache_health_check(user=Depends(require_admin)):
    """Endpoint para verificar la salud del cache"""
    try:
        stats = registro_cache_service.get_cache_stats()
        
        # Calcular métricas de salud
        total_requests = stats.get('total_requests', 0)
        hit_rate = float(stats.get('hit_rate', '0%').replace('%', ''))
        
        health_status = "healthy"
        if hit_rate < 50:
            health_status = "warning"
        if hit_rate < 20:
            health_status = "critical"
        
        return {
            "status": health_status,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "cache_size": stats.get('cache_size', 0),
            "checked_at": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en health check del cache: {e}")
        return {
            "status": "error",
            "error": str(e),
            "checked_at": datetime.datetime.utcnow().isoformat()
        } 