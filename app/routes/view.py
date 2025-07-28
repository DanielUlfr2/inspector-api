from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func, cast, String
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import logging

from app.db.connection import get_async_session
from app.db.models import Registro
from app.schemas.registro import RegistroListResponse
from app.services.cache import cache


# Configuración básica del logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/registros", response_model=RegistroListResponse)
async def listar_registros(
    busqueda: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    ciudad: Optional[str] = Query(None),
    tecnologia: Optional[str] = Query(None),
    flota: Optional[str] = Query(None),
    uso: Optional[str] = Query(None),
    mac_sn: Optional[str] = Query(None),
    id_servicio: Optional[str] = Query(None),
    skip: int = Query(0, ge=0, le=1000),
    limit: int = Query(100, ge=1, le=1000),

    session: AsyncSession = Depends(get_async_session)
):
    try:
        logger.info(f"GET /registros | Filtros: busqueda={busqueda}, region={region}, ciudad={ciudad}, tecnologia={tecnologia}, flota={flota}, uso={uso}, mac_sn={mac_sn}, id_servicio={id_servicio}, skip={skip}, limit={limit}")
        
        # Crear clave de cache basada en los parámetros
        cache_key = f"registros:{busqueda}:{region}:{ciudad}:{tecnologia}:{flota}:{uso}:{mac_sn}:{id_servicio}:{skip}:{limit}"
        
        # Intentar obtener del cache primero
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for key: {cache_key}")
            return cached_result
        
        # Si no está en cache, ejecutar la consulta
        logger.info(f"Cache miss for key: {cache_key}, executing query")
        
        # Optimización: Seleccionar solo las columnas necesarias para mejorar rendimiento
        query = select(
            Registro.id,
            Registro.numero_inspector,
            Registro.uuid,
            Registro.nombre,
            Registro.observaciones,
            Registro.status,
            Registro.region,
            Registro.flota,
            Registro.encargado,
            Registro.celular,
            Registro.correo,
            Registro.direccion,
            Registro.uso,
            Registro.departamento,
            Registro.ciudad,
            Registro.tecnologia,
            Registro.cmts_olt,
            Registro.id_servicio,
            Registro.mac_sn
        )

        if busqueda:
            like_filter = f"%{busqueda.lower()}%"
            query = query.where(
                or_(
                    func.lower(Registro.nombre).like(like_filter),
                    func.lower(Registro.region).like(like_filter),
                    func.lower(Registro.ciudad).like(like_filter),
                    func.lower(Registro.tecnologia).like(like_filter),
                    func.lower(Registro.flota).like(like_filter),
                    func.lower(Registro.uso).like(like_filter),
                    func.lower(Registro.mac_sn).like(like_filter),
                    func.lower(cast(Registro.id_servicio, String)).like(like_filter),
                )
            )

        if region:
            query = query.where(func.lower(Registro.region) == region.lower())
        if ciudad:
            query = query.where(func.lower(Registro.ciudad) == ciudad.lower())
        if tecnologia:
            query = query.where(func.lower(Registro.tecnologia) == tecnologia.lower())
        if flota:
            query = query.where(func.lower(Registro.flota) == flota.lower())
        if uso:
            query = query.where(func.lower(Registro.uso) == uso.lower())
        if mac_sn:
            query = query.where(func.lower(Registro.mac_sn) == mac_sn.lower())
        if id_servicio:
            query = query.where(func.lower(cast(Registro.id_servicio, String)) == id_servicio.lower())

        # Optimización: Conteo total más eficiente usando la misma consulta filtrada
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(total_query)
        total_records = total_result.scalar()

        # Aplicar paginación
        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        registros = result.all()  # Cambiado de scalars().all() a all() porque ahora seleccionamos columnas específicas

        logger.info(f"Registros encontrados: {len(registros)} (total: {total_records})")
        

        
        result = {"total_records": total_records, "registros": registros}
        
        # Guardar en cache
        cache.set(cache_key, result, ttl=300)
        
        return result
    except HTTPException:
        raise
    except SQLAlchemyError as se:
        logger.error(f"Error de base de datos en listar_registros: {se}")
        raise HTTPException(status_code=500, detail="Error de base de datos al listar los registros")
    except Exception as e:
        logger.error(f"Error inesperado en listar_registros: {e}")
        raise HTTPException(status_code=500, detail="Error interno al listar los registros")
