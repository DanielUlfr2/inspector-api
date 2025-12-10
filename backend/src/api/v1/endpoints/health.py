import logging
import redis.asyncio as redis
from fastapi import APIRouter, HTTPException
from databases.postgres_connector import PostgresConnector
from src.core.config import settings

router = APIRouter()
logger = logging.getLogger("health_check")

@router.get("/", status_code=200)
async def health_check():
    """
    Verifica la conectividad con Postgres y Redis.
    Retorna 200 OK si todo está bien.
    Retorna 503 Service Unavailable si falla alguno crítico.
    """
    health_status = {
        "status": "ok",
        "services": {
            "postgres": "unknown",
            "redis": "unknown"
        }
    }
    
    # 1. VERIFICAR POSTGRES
    conn = None
    try:
        conn = await PostgresConnector.get_connection()
        # Consulta ligera para verificar que la DB responde
        await conn.fetchval("SELECT 1")
        health_status["services"]["postgres"] = "online"
    except Exception as e:
        logger.error(f"Fallo Health Check Postgres: {e}")
        health_status["services"]["postgres"] = "offline"
        health_status["status"] = "error"
    finally:
        if conn:
            await PostgresConnector.release_connection(conn)

    # 2. VERIFICAR REDIS
    try:
        # Creamos una conexión temporal solo para el check
        # (Idealmente deberías tener un RedisConnector similar al de Postgres, 
        # pero para este ejemplo lo hacemos directo)
        r = redis.from_url(
            f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            encoding="utf-8", 
            decode_responses=True
        )
        if await r.ping():
            health_status["services"]["redis"] = "online"
        await r.close()
    except Exception as e:
        logger.error(f"Fallo Health Check Redis: {e}")
        health_status["services"]["redis"] = "offline"
        health_status["status"] = "error"

    # Si algún servicio crítico falla, cambiamos el código de respuesta HTTP
    if health_status["status"] == "error":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status