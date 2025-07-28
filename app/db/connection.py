import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker
from fastapi import Depends, HTTPException
from sqlalchemy.exc import OperationalError
# import asyncpg  # Comentado porque estamos usando SQLite

from app.config import DATABASE_URL

# Configuración básica del logger
logger = logging.getLogger(__name__)

# Crear motor de base de datos
try:
    engine = create_async_engine(DATABASE_URL, echo=True)
    logger.info("Motor de base de datos creado correctamente.")
except Exception as e:
    logger.error(f"Error al crear el motor de base de datos: {e}")
    raise

# Crear session factory
try:
    async_session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    logger.info("Session factory creada correctamente.")
except Exception as e:
    logger.error(f"Error al crear la session factory: {e}")
    raise

# Dependencia para FastAPI
async def get_async_session() -> AsyncSession:
    try:
        async with async_session_factory() as session:
            logger.info("Sesión asíncrona obtenida correctamente.")
            yield session
    except OperationalError as oe:
        logger.error(f"Error de conexión a la base de datos: {oe}")
        raise HTTPException(status_code=503, detail="Base de datos no disponible. Intenta más tarde.")
    # except asyncpg.exceptions.ConnectionDoesNotExistError as ce:
    #     logger.error(f"Conexión perdida con la base de datos: {ce}")
    #     raise HTTPException(status_code=503, detail="Conexión perdida con la base de datos.")
    except Exception as e:
        logger.error(f"Error inesperado al obtener la sesión: {e}")
        raise HTTPException(status_code=500, detail="Error interno al obtener la sesión de base de datos.")
