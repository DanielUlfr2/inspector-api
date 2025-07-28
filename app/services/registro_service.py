"""
Servicio para operaciones CRUD de registros
"""
import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.db.models import Registro

logger = logging.getLogger(__name__)


class RegistroService:
    """Servicio para operaciones con registros"""
    
    async def create_registro(
        self, session: AsyncSession, registro_data: dict
    ) -> Optional[Registro]:
        """Crear un nuevo registro"""
        try:
            registro = Registro(**registro_data)
            session.add(registro)
            await session.commit()
            await session.refresh(registro)
            logger.info(f"Registro creado con ID: {registro.id}")
            return registro
        except Exception as e:
            logger.error(f"Error al crear registro: {e}")
            await session.rollback()
            return None
    
    async def get_registro_by_id(
        self, session: AsyncSession, registro_id: int
    ) -> Optional[Registro]:
        """Obtener registro por ID"""
        try:
            result = await session.execute(
                select(Registro).where(Registro.id == registro_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error al obtener registro {registro_id}: {e}")
            return None
    
    async def get_all_registros(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Registro]:
        """Obtener todos los registros con paginación"""
        try:
            result = await session.execute(
                select(Registro).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error al obtener registros: {e}")
            return []
    
    async def update_registro(
        self, session: AsyncSession, registro_id: int, update_data: dict
    ) -> Optional[Registro]:
        """Actualizar un registro"""
        try:
            result = await session.execute(
                update(Registro)
                .where(Registro.id == registro_id)
                .values(**update_data)
            )
            await session.commit()
            
            if result.rowcount > 0:
                return await self.get_registro_by_id(session, registro_id)
            return None
        except Exception as e:
            logger.error(f"Error al actualizar registro {registro_id}: {e}")
            await session.rollback()
            return None
    
    async def delete_registro(
        self, session: AsyncSession, registro_id: int
    ) -> bool:
        """Eliminar un registro"""
        try:
            result = await session.execute(
                delete(Registro).where(Registro.id == registro_id)
            )
            await session.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Error al eliminar registro {registro_id}: {e}")
            await session.rollback()
            return False


# Instancia global del servicio
registro_service = RegistroService() 