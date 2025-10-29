"""
Servicio especializado para cache de registros
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, cast, String, desc
from sqlalchemy import case

from app.db.models import Registro, HistorialCambio
from app.services.cache import cache, generate_cache_key, save_to_cache, TTL_CONFIG
from app.schemas.respuesta import TotalRegistrosResponse

logger = logging.getLogger(__name__)


class RegistroCacheService:
    """Servicio especializado para cache de operaciones con registros"""
    
    @staticmethod
    def _build_filters(**filters) -> List:
        """Construye filtros para consultas de registros"""
        filter_list = []
        for field, value in filters.items():
            if value is not None:
                if str(value).startswith("__EXACT__"):
                    valor = str(value)[9:]
                    expr = cast(getattr(Registro, field), String) == valor
                else:
                    expr = cast(getattr(Registro, field), String).ilike(f"%{value}%")
                filter_list.append(expr)
        return filter_list
    
    @staticmethod
    async def get_cached_total_registros(
        session: AsyncSession, 
        **filters
    ) -> Optional[TotalRegistrosResponse]:
        """
        Obtiene el total de registros desde cache o base de datos
        """
        # Generar clave de cache
        cache_key = generate_cache_key("total_registros", **filters)
        
        # Intentar obtener del cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for total registros with filters: {filters}")
            return cached_result
        
        # Si no está en cache, calcular desde BD
        try:
            filter_list = RegistroCacheService._build_filters(**filters)
            stmt = select(func.count()).select_from(Registro)
            
            if filter_list:
                stmt = stmt.where(and_(*filter_list))
            
            total = await session.scalar(stmt)
            result = {"total": total}
            
            # Guardar en cache
            save_to_cache("total_registros", result, TTL_CONFIG['estadisticas'], **filters)
            logger.info(f"Calculated and cached total registros: {total}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating total registros: {e}")
            return None
    
    @staticmethod
    async def get_cached_registros_list(
        session: AsyncSession,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "id",
        sort_dir: str = "asc",
        **filters
    ) -> Optional[List[Registro]]:
        """
        Obtiene lista de registros desde cache o base de datos
        """
        # Generar clave de cache
        cache_key = generate_cache_key(
            "registros_lista", 
            limit=limit, 
            offset=offset, 
            sort_by=sort_by, 
            sort_dir=sort_dir,
            **filters
        )
        
        # Intentar obtener del cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for registros list with params: limit={limit}, offset={offset}")
            return cached_result
        
        # Si no está en cache, consultar BD
        try:
            query = select(Registro)
            filter_list = RegistroCacheService._build_filters(**filters)
            
            # Aplicar filtros
            if filter_list:
                # Lógica OR para búsqueda global
                use_or = False
                if len(filter_list) > 1:
                    # Verificar si todos los filtros tienen el mismo valor (búsqueda global)
                    filter_values = [f for f in filters.values() if f is not None]
                    if len(set(filter_values)) == 1 and len(filter_values) > 1:
                        use_or = True
                
                if use_or:
                    query = query.where(or_(*filter_list))
                else:
                    query = query.where(and_(*filter_list))
            
            # Aplicar ordenamiento
            if sort_by == "numero_inspector":
                # Ordenamiento especial tipo Excel
                case_expr = case(
                    (Registro.numero_inspector.cast(String).like('0%'), 1),
                    (Registro.numero_inspector.cast(String).like('1%'), 1),
                    (Registro.numero_inspector.cast(String).like('2%'), 1),
                    (Registro.numero_inspector.cast(String).like('3%'), 1),
                    (Registro.numero_inspector.cast(String).like('4%'), 1),
                    (Registro.numero_inspector.cast(String).like('5%'), 1),
                    (Registro.numero_inspector.cast(String).like('6%'), 1),
                    (Registro.numero_inspector.cast(String).like('7%'), 1),
                    (Registro.numero_inspector.cast(String).like('8%'), 1),
                    (Registro.numero_inspector.cast(String).like('9%'), 1),
                    else_=2
                )
                
                if sort_dir == "asc":
                    query = query.order_by(case_expr, Registro.numero_inspector.asc())
                else:
                    query = query.order_by(case_expr.desc(), Registro.numero_inspector.desc())
            else:
                # Ordenamiento genérico
                col = getattr(Registro, sort_by, None)
                if col is not None:
                    if sort_dir == "asc":
                        query = query.order_by(col.asc())
                    else:
                        query = query.order_by(col.desc())
                else:
                    query = query.order_by(Registro.id.asc())
            
            # Aplicar paginación
            query = query.offset(offset).limit(limit)
            
            result = await session.execute(query)
            registros = result.scalars().all()
            
            # Guardar en cache
            save_to_cache(
                "registros_lista", 
                registros, 
                TTL_CONFIG['registros_lista'],
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_dir=sort_dir,
                **filters
            )
            
            logger.info(f"Retrieved and cached {len(registros)} registros")
            return registros
            
        except Exception as e:
            logger.error(f"Error retrieving registros list: {e}")
            return None
    
    @staticmethod
    async def get_cached_registro_by_id(
        session: AsyncSession,
        registro_id: int
    ) -> Optional[Registro]:
        """
        Obtiene un registro individual desde cache o base de datos
        """
        # Generar clave de cache
        cache_key = generate_cache_key("registro_individual", id=registro_id)
        
        # Intentar obtener del cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for registro ID: {registro_id}")
            return cached_result
        
        # Si no está en cache, consultar BD
        try:
            result = await session.execute(
                select(Registro).where(Registro.id == registro_id)
            )
            registro = result.scalar_one_or_none()
            
            if registro:
                # Guardar en cache
                save_to_cache("registro_individual", registro, TTL_CONFIG['registro_individual'], id=registro_id)
                logger.info(f"Retrieved and cached registro ID: {registro_id}")
            
            return registro
            
        except Exception as e:
            logger.error(f"Error retrieving registro {registro_id}: {e}")
            return None
    
    @staticmethod
    async def get_cached_historial(
        session: AsyncSession,
        numero_inspector: int,
        days_back: int = 15
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene historial de cambios desde cache o base de datos
        """
        # Generar clave de cache
        cache_key = generate_cache_key("historial", numero_inspector=numero_inspector, days=days_back)
        
        # Intentar obtener del cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for historial inspector: {numero_inspector}")
            return cached_result
        
        # Si no está en cache, consultar BD
        try:
            from datetime import datetime, timedelta
            hace_dias = datetime.utcnow() - timedelta(days=days_back)
            
            result = await session.execute(
                select(HistorialCambio)
                .where(and_(
                    HistorialCambio.numero_inspector == numero_inspector,
                    HistorialCambio.fecha >= hace_dias
                ))
                .order_by(desc(HistorialCambio.fecha))
            )
            historial = result.scalars().all()
            
            # Convertir a formato JSON
            historial_json = [
                {
                    "fecha": h.fecha.isoformat() if h.fecha else None,
                    "usuario": h.usuario,
                    "accion": h.accion,
                    "campo": h.campo,
                    "valor_anterior": h.valor_anterior,
                    "valor_nuevo": h.valor_nuevo,
                    "descripcion": h.descripcion
                }
                for h in historial
            ]
            
            # Guardar en cache
            save_to_cache(
                "historial", 
                historial_json, 
                TTL_CONFIG['historial'],
                numero_inspector=numero_inspector,
                days=days_back
            )
            
            logger.info(f"Retrieved and cached {len(historial_json)} historial entries")
            return historial_json
            
        except Exception as e:
            logger.error(f"Error retrieving historial for inspector {numero_inspector}: {e}")
            return None
    
    @staticmethod
    async def get_cached_unique_values(
        session: AsyncSession,
        column: str,
        search: str = ""
    ) -> Optional[Dict[str, List[str]]]:
        """
        Obtiene valores únicos de una columna desde cache o base de datos
        """
        # Generar clave de cache
        cache_key = generate_cache_key("valores_unicos", column=column, search=search)
        
        # Intentar obtener del cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Cache hit for unique values column: {column}")
            return cached_result
        
        # Si no está en cache, consultar BD
        try:
            allowed_cols = [
                "numero_inspector", "nombre", "observaciones", "status", "region", 
                "flota", "encargado", "celular", "correo", "direccion", "uso", 
                "departamento", "ciudad", "tecnologia", "cmts_olt", "id_servicio", "mac_sn"
            ]
            
            if column not in allowed_cols:
                logger.error(f"Invalid column for unique values: {column}")
                return None
            
            model_col = getattr(Registro, column)
            stmt = select(model_col).distinct().order_by(model_col)
            
            if search:
                stmt = stmt.where(cast(model_col, String).ilike(f"%{search}%"))
            
            result = await session.execute(stmt)
            values = [row[0] for row in result.fetchall() if row[0] is not None]
            
            result_dict = {"values": values}
            
            # Guardar en cache
            save_to_cache(
                "valores_unicos", 
                result_dict, 
                TTL_CONFIG['valores_unicos'],
                column=column,
                search=search
            )
            
            logger.info(f"Retrieved and cached {len(values)} unique values for column: {column}")
            return result_dict
            
        except Exception as e:
            logger.error(f"Error retrieving unique values for column {column}: {e}")
            return None
    
    @staticmethod
    def invalidate_registro_cache(registro_id: int = None):
        """
        Invalida cache relacionado con registros
        """
        if registro_id:
            # Invalidar cache específico del registro
            cache.invalidate_by_pattern(f"registro_individual:id={registro_id}")
            logger.info(f"Invalidated cache for registro ID: {registro_id}")
        
        # Invalidar cache general de registros
        invalidated = cache.invalidate_registros()
        logger.info(f"Invalidated {invalidated} registro-related cache entries")
    
    @staticmethod
    def invalidate_estadisticas_cache():
        """
        Invalida cache relacionado con estadísticas
        """
        invalidated = cache.invalidate_estadisticas()
        logger.info(f"Invalidated {invalidated} estadisticas-related cache entries")
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache
        """
        return cache.get_stats()


# Instancia global del servicio de cache de registros
registro_cache_service = RegistroCacheService() 