from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, text
import logging

from app.db.connection import get_async_session
from app.db.models import Registro, Base, HistorialCambio
from app.schemas.registro import RegistroCreate, RegistroUpdate, RegistroOut
from app.services.cache import cache
from app.services.registro_cache_service import registro_cache_service
from app.services.deps import require_admin, require_user_or_admin
from app.services.validation import validate_single_registro, ValidationError
from app.schemas.respuesta import TotalRegistrosResponse
from fastapi.responses import StreamingResponse
import csv
import io
from fastapi import File, UploadFile
from typing import List, Union
from sqlalchemy import cast, String
from sqlalchemy import case
from sqlalchemy import or_, and_
import datetime
import json
from sqlalchemy import desc

# Configuración básica del logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.put(
    "/registros/{id}",
    response_model=RegistroOut,
    summary="Actualizar registro",
    description="Actualiza los datos de un registro existente por su ID. Requiere autenticación: solo admin."
)
async def actualizar_registro(
    datos: RegistroUpdate,
    id: int = Path(..., description="ID del registro a actualizar"),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    logger.info(f"PUT recibido para ID={id}")
    logger.info(f"Datos recibidos: {datos}")

    try:
        query = select(Registro).where(Registro.id == id)
        result = await session.execute(query)
        registro = result.scalar_one_or_none()

        if not registro:
            raise HTTPException(
                status_code=404, 
                detail="ERROR Registro no encontrado: No existe un registro con el ID especificado para actualizar. Verifica el ID e intenta nuevamente."
            )

        # Preparar datos para validación (combinar datos existentes con nuevos)
        registro_data = {
            "numero_inspector": registro.numero_inspector,
            "uuid": registro.uuid,
            "nombre": registro.nombre,
            "observaciones": registro.observaciones,
            "status": registro.status,
            "region": registro.region,
            "flota": registro.flota,
            "encargado": registro.encargado,
            "celular": registro.celular,
            "correo": registro.correo,
            "direccion": registro.direccion,
            "uso": registro.uso,
            "departamento": registro.departamento,
            "ciudad": registro.ciudad,
            "tecnologia": registro.tecnologia,
            "cmts_olt": registro.cmts_olt,
            "id_servicio": registro.id_servicio,
            "mac_sn": registro.mac_sn
        }
        
        # Actualizar con nuevos datos
        update_data = datos.dict(exclude_unset=True)
        registro_data.update(update_data)

        # Validar el registro actualizado
        is_valid, errors, tipos_error = await validate_single_registro(session, registro_data, exclude_id=id)
        
        if not is_valid:
            error_message = "; ".join(errors)
            logger.error(f"Validación fallida al actualizar registro ID={id}: {error_message}")
            raise HTTPException(
                status_code=400, 
                detail=f"ERROR Error de validación: No se puede actualizar el registro. {error_message}"
            )

        # Guardar cambios y registrar historial
        cambios = []
        for key, nuevo_valor in update_data.items():
            valor_anterior = getattr(registro, key, None)
            if str(valor_anterior) != str(nuevo_valor):
                cambios.append({
                    "campo": key,
                    "valor_anterior": valor_anterior,
                    "valor_nuevo": nuevo_valor
                })

        # Registrar cambios en el historial
        for cambio in cambios:
            historial = HistorialCambio(
                registro_id=registro.id,
                numero_inspector=registro.numero_inspector,
                fecha=datetime.datetime.utcnow(),
                usuario=user["sub"] if isinstance(user, dict) and "sub" in user else str(user),
                accion="edicion",
                campo=cambio["campo"],
                valor_anterior=str(cambio["valor_anterior"]) if cambio["valor_anterior"] is not None else None,
                valor_nuevo=str(cambio["valor_nuevo"]) if cambio["valor_nuevo"] is not None else None,
                descripcion=f"Cambio en campo '{cambio['campo']}'"
            )
            session.add(historial)

        # Aplicar cambios al registro
        for key, value in update_data.items():
            setattr(registro, key, value)

        await session.commit()
        await session.refresh(registro)
        logger.info(f"Registro ID={id} actualizado correctamente.")
        
        # Invalidar cache de registros usando el servicio avanzado
        registro_cache_service.invalidate_registro_cache(id)
        logger.info("Cache invalidated after update")
        
        return registro

    except HTTPException:
        raise
    except IntegrityError as ie:
        logger.error(f"Error de integridad en la base de datos al actualizar: {ie}")
        raise HTTPException(
            status_code=409, 
            detail="ERROR Conflicto de datos: Ya existe un registro con los mismos datos únicos (número de inspector o nombre). Verifica que no estés duplicando información."
        )
    except SQLAlchemyError as se:
        logger.error(f"Error de base de datos al actualizar: {se}")
        raise HTTPException(
            status_code=500, 
            detail="ERROR Error de base de datos: No se pudo actualizar el registro debido a un problema técnico. Contacta al administrador si el problema persiste."
        )
    except Exception as e:
        logger.error(f"Error inesperado al actualizar el registro ID={id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="ERROR Error interno del servidor: Ocurrió un problema inesperado al actualizar el registro. Intenta nuevamente o contacta al administrador."
        )


@router.post(
    "/registros",
    response_model=RegistroOut,
    summary="Crear registro",
    description="Crea un nuevo registro en la base de datos. Requiere autenticación: solo admin."
)
async def crear_registro(
    datos: RegistroCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    logger.info("POST recibido para crear nuevo registro")
    logger.info(f"Datos recibidos: {datos}")

    try:
        # Validar el registro antes de crearlo
        registro_data = datos.dict()
        is_valid, errors, tipos_error = await validate_single_registro(session, registro_data)
        
        if not is_valid:
            logger.warning(
                f"[VALIDACIÓN] Error al crear registro. Campos inválidos o faltantes: {errors} | Datos recibidos: {registro_data}"
            )
            # Si errors es una lista de dicts, devuélvela tal cual, si es lista de strings, conviértela
            detail = errors
            raise HTTPException(
                status_code=400,
                detail=detail
            )
        
        nuevo_registro = Registro(**registro_data)
        session.add(nuevo_registro)
        await session.commit()
        await session.refresh(nuevo_registro)
        logger.info(f"Registro creado con ID={nuevo_registro.id}")
        
        # Registrar creación en el historial
        historial = HistorialCambio(
            registro_id=nuevo_registro.id,
            numero_inspector=nuevo_registro.numero_inspector,
            fecha=datetime.datetime.utcnow(),
            usuario=user["sub"] if isinstance(user, dict) and "sub" in user else str(user),
            accion="creacion",
            campo=None,
            valor_anterior=None,
            valor_nuevo=None,
            descripcion=f"Registro creado: {nuevo_registro.nombre}"
        )
        session.add(historial)
        await session.commit()
        
        # Invalidar cache de registros usando el servicio avanzado
        registro_cache_service.invalidate_registro_cache()
        logger.info("Cache invalidated after create")
        
        return nuevo_registro

    except HTTPException:
        raise
    except IntegrityError as ie:
        logger.error(f"Error de integridad en la base de datos al crear: {ie}")
        raise HTTPException(
            status_code=409, 
            detail="ERROR Conflicto de datos: Ya existe un registro con los mismos datos únicos (número de inspector o nombre). Verifica que no estés duplicando información."
        )
    except SQLAlchemyError as se:
        logger.error(f"Error de base de datos al crear: {se}")
        raise HTTPException(
            status_code=500, 
            detail="ERROR Error de base de datos: No se pudo crear el registro debido a un problema técnico. Contacta al administrador si el problema persiste."
        )
    except Exception as e:
        logger.error(f"Error inesperado al crear el registro: {e}")
        raise HTTPException(
            status_code=500, 
            detail="ERROR Error interno del servidor: Ocurrió un problema inesperado al procesar tu solicitud. Intenta nuevamente o contacta al administrador."
        )


@router.get(
    "/registros/total",
    response_model=TotalRegistrosResponse,
    summary="Total de registros",
    description="Devuelve el número total de registros en la base de datos. Requiere autenticación: usuario o admin."
)
async def contar_registros(
    numero_inspector: str = Query(None),
    uuid: str = Query(None),
    nombre: str = Query(None),
    observaciones: str = Query(None),
    status: str = Query(None),
    region: str = Query(None),
    flota: str = Query(None),
    encargado: str = Query(None),
    celular: str = Query(None),
    correo: str = Query(None),
    direccion: str = Query(None),
    uso: str = Query(None),
    departamento: str = Query(None),
    ciudad: str = Query(None),
    tecnologia: str = Query(None),
    cmts_olt: str = Query(None),
    id_servicio: str = Query(None),
    mac_sn: str = Query(None),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_user_or_admin)
):
    try:
        # Usar el servicio de cache avanzado
        result = await registro_cache_service.get_cached_total_registros(
            session,
            numero_inspector=numero_inspector,
            uuid=uuid,
            nombre=nombre,
            observaciones=observaciones,
            status=status,
            region=region,
            flota=flota,
            encargado=encargado,
            celular=celular,
            correo=correo,
            direccion=direccion,
            uso=uso,
            departamento=departamento,
            ciudad=ciudad,
            tecnologia=tecnologia,
            cmts_olt=cmts_olt,
            id_servicio=id_servicio,
            mac_sn=mac_sn
        )
        
        if result is None:
            raise HTTPException(status_code=500, detail="Error en conteo de registros")
        
        logger.info(f"Conteo de registros exitoso. Total: {result['total']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al contar registros: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error en conteo de registros")


@router.get(
    "/registros",
    response_model=List[RegistroOut],
    summary="Filtrar y ordenar registros",
    description="Devuelve una lista paginada de registros, permitiendo filtrar por cualquier columna y ordenar por cualquier campo. Requiere autenticación: usuario o admin."
)
async def listar_registros(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("id"),
    sort_dir: str = Query("asc"),
    numero_inspector: str = Query(None),
    uuid: str = Query(None),
    nombre: str = Query(None),
    observaciones: str = Query(None),
    status: str = Query(None),
    region: str = Query(None),
    flota: str = Query(None),
    encargado: str = Query(None),
    celular: str = Query(None),
    correo: str = Query(None),
    direccion: str = Query(None),
    uso: str = Query(None),
    departamento: str = Query(None),
    ciudad: str = Query(None),
    tecnologia: str = Query(None),
    cmts_olt: str = Query(None),
    id_servicio: str = Query(None),
    mac_sn: str = Query(None),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_user_or_admin)
):
    try:
        # Usar el servicio de cache avanzado
        registros = await registro_cache_service.get_cached_registros_list(
            session,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir,
            numero_inspector=numero_inspector,
            uuid=uuid,
            nombre=nombre,
            observaciones=observaciones,
            status=status,
            region=region,
            flota=flota,
            encargado=encargado,
            celular=celular,
            correo=correo,
            direccion=direccion,
            uso=uso,
            departamento=departamento,
            ciudad=ciudad,
            tecnologia=tecnologia,
            cmts_olt=cmts_olt,
            id_servicio=id_servicio,
            mac_sn=mac_sn
        )
        
        if registros is None:
            raise HTTPException(status_code=500, detail="Error al obtener registros")
        
        return registros
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al listar registros: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener registros")


@router.get(
    "/registros/{numero_inspector}/historial",
    summary="Obtener historial de registro",
    description="Devuelve el historial de cambios de un registro según el número de inspector. Requiere autenticación: solo admin."
)
async def obtener_historial_registro(
    numero_inspector: int = Path(..., description="Número del inspector"),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    try:
        # Usar el servicio de cache avanzado
        historial = await registro_cache_service.get_cached_historial(
            session, numero_inspector
        )
        
        if historial is None:
            raise HTTPException(status_code=500, detail="Error al obtener historial")
        
        return historial
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener historial para inspector {numero_inspector}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")


@router.get(
    "/registros/{id}",
    response_model=RegistroOut,
    summary="Obtener registro por ID",
    description="Devuelve los datos de un registro específico por su ID. Requiere autenticación: usuario o admin."
)
async def obtener_registro_por_id(
    id: int = Path(..., description="ID del registro a consultar"),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_user_or_admin)
):
    logger.info(f"GET recibido para consultar ID={id}")
    try:
        # Usar el servicio de cache avanzado
        registro = await registro_cache_service.get_cached_registro_by_id(session, id)
        
        if not registro:
            raise HTTPException(
                status_code=404, 
                detail="ERROR Registro no encontrado: No existe un registro con el ID especificado. Verifica el ID e intenta nuevamente."
            )
        
        return registro
        
    except HTTPException:
        raise
    except SQLAlchemyError as se:
        logger.error(f"Error de base de datos al obtener: {se}")
        raise HTTPException(
            status_code=500, 
            detail="ERROR Error de base de datos: No se pudo obtener el registro debido a un problema técnico. Contacta al administrador si el problema persiste."
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener el registro ID={id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="ERROR Error interno del servidor: Ocurrió un problema inesperado al obtener el registro. Intenta nuevamente o contacta al administrador."
        )


@router.delete(
    "/registros/{id}",
    response_model=dict,
    summary="Eliminar registro",
    description="Elimina un registro de la base de datos por su ID. Requiere autenticación: solo admin."
)
async def eliminar_registro(
    id: int = Path(..., description="ID del registro a eliminar"),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    logger.info(f"DELETE recibido para ID={id}")

    try:
        result = await session.execute(select(Registro).where(Registro.id == id))
        registro = result.scalar_one_or_none()

        if not registro:
            raise HTTPException(
                status_code=404, 
                detail="ERROR Registro no encontrado: No existe un registro con el ID especificado para eliminar. Verifica el ID e inténtalo nuevamente."
            )

        # Registrar eliminación en el historial
        historial = HistorialCambio(
            registro_id=registro.id,
            numero_inspector=registro.numero_inspector,
            fecha=datetime.datetime.utcnow(),
            usuario=user["sub"] if isinstance(user, dict) and "sub" in user else str(user),
            accion="eliminacion",
            campo=None,
            valor_anterior=json.dumps(registro.as_dict(), ensure_ascii=False),
            valor_nuevo=None,
            descripcion="Registro eliminado"
        )
        session.add(historial)

        await session.delete(registro)
        await session.commit()
        logger.info(f"Registro ID={id} eliminado correctamente.")
        
        # Invalidar cache usando el servicio avanzado
        registro_cache_service.invalidate_registro_cache(id)
        logger.info("Cache invalidated after delete")
        
        return {"mensaje": f"Registro con ID={id} eliminado exitosamente"}

    except HTTPException:
        raise
    except SQLAlchemyError as se:
        logger.error(f"Error de base de datos al eliminar: {se}")
        raise HTTPException(
            status_code=500, 
            detail="ERROR Error de base de datos: No se pudo eliminar el registro debido a un problema técnico. Contacta al administrador si el problema persiste."
        )
    except Exception as e:
        logger.error(f"Error inesperado al eliminar el registro ID={id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="ERROR Error interno del servidor: Ocurrió un problema inesperado al eliminar el registro. Intenta nuevamente o contacta al administrador."
        )


@router.get(
    "/registros/unique_values",
    summary="Valores únicos de columna",
    description="Devuelve los valores únicos de una columna de registros, opcionalmente filtrados por texto. Requiere autenticación: usuario o admin."
)
async def unique_values(
    col: Union[str, list] = Query(..., min_length=1),
    search: str = Query('', min_length=0),
    session: AsyncSession = Depends(get_async_session)
):
    # Si col es lista, toma el primer valor
    if isinstance(col, list):
        col = col[0]
    
    logging.info(f"[unique_values] col: '{col}', search: '{search}'")
    
    try:
        # Usar el servicio de cache avanzado
        result = await registro_cache_service.get_cached_unique_values(
            session, col, search
        )
        
        if result is None:
            raise HTTPException(status_code=400, detail=f"Columna no permitida: '{col}'")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener valores únicos para columna {col}: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener valores únicos")


@router.get(
    "/cache/stats",
    summary="Estadísticas del cache",
    description="Devuelve estadísticas del sistema de cache. Requiere autenticación: solo admin."
)
async def get_cache_stats(user=Depends(require_admin)):
    """Endpoint para obtener estadísticas del cache"""
    try:
        stats = registro_cache_service.get_cache_stats()
        return {
            "message": "Estadísticas del cache obtenidas exitosamente",
            "stats": stats
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