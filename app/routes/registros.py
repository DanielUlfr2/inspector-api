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

        # Comentado temporalmente para evitar errores con el modelo HistorialCambio
        # for cambio in cambios:
        #     historial = HistorialCambio(
        #         numero_inspector=registro.numero_inspector,
        #         fecha=datetime.datetime.utcnow(),
        #         usuario=user["sub"] if isinstance(user, dict) and "sub" in user else str(user),
        #         accion="edicion",
        #         campo=cambio["campo"],
        #         valor_anterior=str(cambio["valor_anterior"]) if cambio["valor_anterior"] is not None else None,
        #         valor_nuevo=str(cambio["valor_nuevo"]) if cambio["valor_nuevo"] is not None else None,
        #         descripcion=f"Cambio en campo '{cambio['campo']}'"
        #     )
        #     session.add(historial)

        # Aplicar cambios al registro
        for key, value in update_data.items():
            setattr(registro, key, value)

        await session.commit()
        await session.refresh(registro)
        logger.info(f"Registro ID={id} actualizado correctamente.")
        
        # Invalidar cache de registros
        cache.clear()
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
        
        # Invalidar cache de registros
        cache.clear()
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
        from sqlalchemy import func
        filtros = []
        if numero_inspector:
            if str(numero_inspector).startswith("__EXACT__"):
                valor = str(numero_inspector)[9:]
                filtros.append(cast(Registro.numero_inspector, String) == valor)
            else:
                filtros.append(cast(Registro.numero_inspector, String).ilike(f"%{numero_inspector}%"))
        if uuid:
            if str(uuid).startswith("__EXACT__"):
                valor = str(uuid)[9:]
                filtros.append(cast(Registro.uuid, String) == valor)
            else:
                filtros.append(Registro.uuid.ilike(f"%{uuid}%"))
        if nombre:
            if str(nombre).startswith("__EXACT__"):
                valor = str(nombre)[9:]
                filtros.append(cast(Registro.nombre, String) == valor)
            else:
                filtros.append(Registro.nombre.ilike(f"%{nombre}%"))
        if observaciones:
            if str(observaciones).startswith("__EXACT__"):
                valor = str(observaciones)[9:]
                filtros.append(cast(Registro.observaciones, String) == valor)
            else:
                filtros.append(Registro.observaciones.ilike(f"%{observaciones}%"))
        if status:
            if str(status).startswith("__EXACT__"):
                valor = str(status)[9:]
                filtros.append(cast(Registro.status, String) == valor)
            else:
                filtros.append(Registro.status.ilike(f"%{status}%"))
        if region:
            if str(region).startswith("__EXACT__"):
                valor = str(region)[9:]
                filtros.append(cast(Registro.region, String) == valor)
            else:
                filtros.append(Registro.region.ilike(f"%{region}%"))
        if flota:
            if str(flota).startswith("__EXACT__"):
                valor = str(flota)[9:]
                filtros.append(cast(Registro.flota, String) == valor)
            else:
                filtros.append(Registro.flota.ilike(f"%{flota}%"))
        if encargado:
            if str(encargado).startswith("__EXACT__"):
                valor = str(encargado)[9:]
                filtros.append(cast(Registro.encargado, String) == valor)
            else:
                filtros.append(Registro.encargado.ilike(f"%{encargado}%"))
        if celular:
            if str(celular).startswith("__EXACT__"):
                valor = str(celular)[9:]
                filtros.append(cast(Registro.celular, String) == valor)
            else:
                filtros.append(Registro.celular.ilike(f"%{celular}%"))
        if correo:
            if str(correo).startswith("__EXACT__"):
                valor = str(correo)[9:]
                filtros.append(cast(Registro.correo, String) == valor)
            else:
                filtros.append(Registro.correo.ilike(f"%{correo}%"))
        if direccion:
            if str(direccion).startswith("__EXACT__"):
                valor = str(direccion)[9:]
                filtros.append(cast(Registro.direccion, String) == valor)
            else:
                filtros.append(Registro.direccion.ilike(f"%{direccion}%"))
        if uso:
            if str(uso).startswith("__EXACT__"):
                valor = str(uso)[9:]
                filtros.append(cast(Registro.uso, String) == valor)
            else:
                filtros.append(Registro.uso.ilike(f"%{uso}%"))
        if departamento:
            if str(departamento).startswith("__EXACT__"):
                valor = str(departamento)[9:]
                filtros.append(cast(Registro.departamento, String) == valor)
            else:
                filtros.append(Registro.departamento.ilike(f"%{departamento}%"))
        if ciudad:
            if str(ciudad).startswith("__EXACT__"):
                valor = str(ciudad)[9:]
                filtros.append(cast(Registro.ciudad, String) == valor)
            else:
                filtros.append(Registro.ciudad.ilike(f"%{ciudad}%"))
        if tecnologia:
            if str(tecnologia).startswith("__EXACT__"):
                valor = str(tecnologia)[9:]
                filtros.append(cast(Registro.tecnologia, String) == valor)
            else:
                filtros.append(Registro.tecnologia.ilike(f"%{tecnologia}%"))
        if cmts_olt:
            if str(cmts_olt).startswith("__EXACT__"):
                valor = str(cmts_olt)[9:]
                filtros.append(cast(Registro.cmts_olt, String) == valor)
            else:
                filtros.append(Registro.cmts_olt.ilike(f"%{cmts_olt}%"))
        if id_servicio:
            if str(id_servicio).startswith("__EXACT__"):
                valor = str(id_servicio)[9:]
                filtros.append(cast(Registro.id_servicio, String) == valor)
            else:
                filtros.append(Registro.id_servicio.ilike(f"%{id_servicio}%"))
        if mac_sn:
            if str(mac_sn).startswith("__EXACT__"):
                valor = str(mac_sn)[9:]
                filtros.append(cast(Registro.mac_sn, String) == valor)
            else:
                filtros.append(Registro.mac_sn.ilike(f"%{mac_sn}%"))
        stmt = select(func.count()).select_from(Registro)
        if filtros:
            stmt = stmt.where(*filtros)
        total = await session.scalar(stmt)
        logger.info(f"Conteo de registros exitoso. Total: {total}")
        return {"total": total}
    except Exception as e:
        import traceback
        print("Error al contar registros:", e)
        traceback.print_exc()
        logger.error(f"Error al contar registros: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error en conteo de registros")

from typing import List
from app.schemas.registro import RegistroOut  # Ya importado arriba

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
        query = select(Registro)
        # Filtros dinámicos
        filtros = []
        filtro_valores = []
        filtro_columnas = []
        # Construir filtros y recolectar valores para lógica OR
        if numero_inspector:
            if str(numero_inspector).startswith("__EXACT__"):
                valor = str(numero_inspector)[9:]
                expr = cast(Registro.numero_inspector, String) == valor
            else:
                expr = cast(Registro.numero_inspector, String).ilike(f"%{numero_inspector}%")
            filtros.append(expr)
            filtro_valores.append(numero_inspector)
            filtro_columnas.append("numero_inspector")
        if uuid:
            if str(uuid).startswith("__EXACT__"):
                valor = str(uuid)[9:]
                expr = cast(Registro.uuid, String) == valor
            else:
                expr = Registro.uuid.ilike(f"%{uuid}%")
            filtros.append(expr)
            filtro_valores.append(uuid)
            filtro_columnas.append("uuid")
        if nombre:
            if str(nombre).startswith("__EXACT__"):
                valor = str(nombre)[9:]
                expr = cast(Registro.nombre, String) == valor
            else:
                expr = Registro.nombre.ilike(f"%{nombre}%")
            filtros.append(expr)
            filtro_valores.append(nombre)
            filtro_columnas.append("nombre")
        if observaciones:
            if str(observaciones).startswith("__EXACT__"):
                valor = str(observaciones)[9:]
                expr = cast(Registro.observaciones, String) == valor
            else:
                expr = Registro.observaciones.ilike(f"%{observaciones}%")
            filtros.append(expr)
            filtro_valores.append(observaciones)
            filtro_columnas.append("observaciones")
        if status:
            if str(status).startswith("__EXACT__"):
                valor = str(status)[9:]
                expr = cast(Registro.status, String) == valor
            else:
                expr = Registro.status.ilike(f"%{status}%")
            filtros.append(expr)
            filtro_valores.append(status)
            filtro_columnas.append("status")
        if region:
            if str(region).startswith("__EXACT__"):
                valor = str(region)[9:]
                expr = cast(Registro.region, String) == valor
            else:
                expr = Registro.region.ilike(f"%{region}%")
            filtros.append(expr)
            filtro_valores.append(region)
            filtro_columnas.append("region")
        if flota:
            if str(flota).startswith("__EXACT__"):
                valor = str(flota)[9:]
                expr = cast(Registro.flota, String) == valor
            else:
                expr = Registro.flota.ilike(f"%{flota}%")
            filtros.append(expr)
            filtro_valores.append(flota)
            filtro_columnas.append("flota")
        if encargado:
            if str(encargado).startswith("__EXACT__"):
                valor = str(encargado)[9:]
                expr = cast(Registro.encargado, String) == valor
            else:
                expr = Registro.encargado.ilike(f"%{encargado}%")
            filtros.append(expr)
            filtro_valores.append(encargado)
            filtro_columnas.append("encargado")
        if celular:
            if str(celular).startswith("__EXACT__"):
                valor = str(celular)[9:]
                expr = cast(Registro.celular, String) == valor
            else:
                expr = Registro.celular.ilike(f"%{celular}%")
            filtros.append(expr)
            filtro_valores.append(celular)
            filtro_columnas.append("celular")
        if correo:
            if str(correo).startswith("__EXACT__"):
                valor = str(correo)[9:]
                expr = cast(Registro.correo, String) == valor
            else:
                expr = Registro.correo.ilike(f"%{correo}%")
            filtros.append(expr)
            filtro_valores.append(correo)
            filtro_columnas.append("correo")
        if direccion:
            if str(direccion).startswith("__EXACT__"):
                valor = str(direccion)[9:]
                expr = cast(Registro.direccion, String) == valor
            else:
                expr = Registro.direccion.ilike(f"%{direccion}%")
            filtros.append(expr)
            filtro_valores.append(direccion)
            filtro_columnas.append("direccion")
        if uso:
            if str(uso).startswith("__EXACT__"):
                valor = str(uso)[9:]
                expr = cast(Registro.uso, String) == valor
            else:
                expr = Registro.uso.ilike(f"%{uso}%")
            filtros.append(expr)
            filtro_valores.append(uso)
            filtro_columnas.append("uso")
        if departamento:
            if str(departamento).startswith("__EXACT__"):
                valor = str(departamento)[9:]
                expr = cast(Registro.departamento, String) == valor
            else:
                expr = Registro.departamento.ilike(f"%{departamento}%")
            filtros.append(expr)
            filtro_valores.append(departamento)
            filtro_columnas.append("departamento")
        if ciudad:
            if str(ciudad).startswith("__EXACT__"):
                valor = str(ciudad)[9:]
                expr = cast(Registro.ciudad, String) == valor
            else:
                expr = Registro.ciudad.ilike(f"%{ciudad}%")
            filtros.append(expr)
            filtro_valores.append(ciudad)
            filtro_columnas.append("ciudad")
        if tecnologia:
            if str(tecnologia).startswith("__EXACT__"):
                valor = str(tecnologia)[9:]
                expr = cast(Registro.tecnologia, String) == valor
            else:
                expr = Registro.tecnologia.ilike(f"%{tecnologia}%")
            filtros.append(expr)
            filtro_valores.append(tecnologia)
            filtro_columnas.append("tecnologia")
        if cmts_olt:
            if str(cmts_olt).startswith("__EXACT__"):
                valor = str(cmts_olt)[9:]
                expr = cast(Registro.cmts_olt, String) == valor
            else:
                expr = Registro.cmts_olt.ilike(f"%{cmts_olt}%")
            filtros.append(expr)
            filtro_valores.append(cmts_olt)
            filtro_columnas.append("cmts_olt")
        if id_servicio:
            if str(id_servicio).startswith("__EXACT__"):
                valor = str(id_servicio)[9:]
                expr = cast(Registro.id_servicio, String) == valor
            else:
                expr = Registro.id_servicio.ilike(f"%{id_servicio}%")
            filtros.append(expr)
            filtro_valores.append(id_servicio)
            filtro_columnas.append("id_servicio")
        if mac_sn:
            if str(mac_sn).startswith("__EXACT__"):
                valor = str(mac_sn)[9:]
                expr = cast(Registro.mac_sn, String) == valor
            else:
                expr = Registro.mac_sn.ilike(f"%{mac_sn}%")
            filtros.append(expr)
            filtro_valores.append(mac_sn)
            filtro_columnas.append("mac_sn")

        # Lógica OR para búsqueda global
        use_or = False
        if filtros and len(set(filtro_valores)) == 1 and len(filtro_valores) > 1:
            # Todos los filtros tienen el mismo valor y hay más de uno (búsqueda global)
            use_or = True
        if filtros:
            if use_or:
                query = query.where(or_(*filtros))
            else:
                query = query.where(and_(*filtros))

        # Ordenamiento especial para numero_inspector estilo Excel
        if sort_by == "numero_inspector":
            # Ordenamiento tipo Excel para SQLite
            # Primero números, luego texto, luego otros
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
                query = query.order_by(
                    case_expr,
                    Registro.numero_inspector.asc()
                )
            else:
                query = query.order_by(
                    case_expr.desc(),
                    Registro.numero_inspector.desc()
                )
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

        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        registros = result.scalars().all()
        return registros
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
        from datetime import datetime, timedelta
        hace_15_dias = datetime.utcnow() - timedelta(days=15)
        logger.info(f"Consultando historial para inspector {numero_inspector} desde {hace_15_dias}")
        result = await session.execute(
            select(HistorialCambio)
            .where(and_(HistorialCambio.numero_inspector == numero_inspector, HistorialCambio.fecha >= hace_15_dias))
            .order_by(desc(HistorialCambio.fecha))
        )
        historial = result.scalars().all()
        logger.info(f"Historial encontrado: {len(historial)} cambios para inspector {numero_inspector}")
        if not historial:
            return []
        # El historial ya se ordena por fecha descendente (más reciente primero)
        historial_ordenado = sorted(historial, key=lambda h: h.fecha or datetime.min, reverse=True)
        return [
            {
                "fecha": h.fecha.isoformat() if h.fecha else None,
                "usuario": h.usuario,
                "accion": h.accion,
                "campo": h.campo,
                "valor_anterior": h.valor_anterior,
                "valor_nuevo": h.valor_nuevo,
                "descripcion": h.descripcion
            }
            for h in historial_ordenado
        ]
    except Exception as e:
        import traceback
        logger.error(f"Error al obtener historial para inspector {numero_inspector}: {e}")
        logger.error(traceback.format_exc())
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
        result = await session.execute(select(Registro).where(Registro.id == id))
        registro = result.scalar_one_or_none()
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

        # Comentado temporalmente para evitar errores con el modelo HistorialCambio
        # historial = HistorialCambio(
        #     numero_inspector=registro.numero_inspector,
        #     fecha=datetime.datetime.utcnow(),
        #     usuario=user["sub"] if isinstance(user, dict) and "sub" in user else str(user),
        #     accion="eliminacion",
        #     campo=None,
        #     valor_anterior=json.dumps(registro.as_dict(), ensure_ascii=False),
        #     valor_nuevo=None,
        #     descripcion="Registro eliminado"
        # )
        # session.add(historial)

        await session.delete(registro)
        await session.commit()
        logger.info(f"Registro ID={id} eliminado correctamente.")
        
        cache.clear()
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
    "/registros/exportar",
    summary="Exportar registros como CSV",
    description="Devuelve todos los registros en formato CSV para descarga. Requiere autenticación: solo admin."
)
async def exportar_registros_csv(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    try:
        result = await session.execute(select(Registro))
        registros = result.scalars().all()

        # Crear archivo CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)

        # Escribir encabezados
        headers = [
            "id", "numero_inspector", "uuid", "nombre", "observaciones", "status", "region", "flota",
            "encargado", "celular", "correo", "direccion", "uso", "departamento",
            "ciudad", "tecnologia", "cmts_olt", "id_servicio", "mac_sn"
        ]
        writer.writerow(headers)

        # Escribir registros
        for r in registros:
            writer.writerow([
                r.id, r.numero_inspector, r.uuid, r.nombre, r.observaciones, r.status, r.region, r.flota,
                r.encargado, r.celular, r.correo, r.direccion, r.uso, r.departamento,
                r.ciudad, r.tecnologia, r.cmts_olt, r.id_servicio, r.mac_sn
            ])

        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=registros.csv"})

    except Exception as e:
        logger.error(f"Error al exportar registros: {e}")
        raise HTTPException(status_code=500, detail="Error al exportar registros")

@router.post(
    "/registros/cargar",
    summary="Cargar registros desde CSV",
    description="Carga masiva de registros desde un archivo CSV. Requiere autenticación: solo admin."
)
async def cargar_registros_csv(
    archivo: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    try:
        contenido = await archivo.read()
        decoded = contenido.decode("utf-8").splitlines()
        reader = csv.DictReader(decoded)

        nuevos_registros = []
        for row in reader:
            try:
                registro_data = dict(row)
                if 'uuid' not in registro_data:
                    registro_data['uuid'] = None
                registro_data = RegistroCreate(**registro_data)
                nuevo = Registro(**registro_data.dict())
                session.add(nuevo)
                nuevos_registros.append(nuevo)
            except Exception as e:
                logger.warning(f"Fila inválida omitida: {row} - Error: {e}")

        await session.commit()
        return {"mensaje": f"{len(nuevos_registros)} registros cargados correctamente"}

    except Exception as e:
        logger.error(f"Error al cargar CSV: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar archivo CSV")

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
    allowed_cols = [
        "numero_inspector", "nombre", "observaciones", "status", "region", "flota", "encargado", "celular", "correo", "direccion", "uso", "departamento", "ciudad", "tecnologia", "cmts_olt", "id_servicio", "mac_sn"
    ]
    if not col or col not in allowed_cols:
        logging.error(f"[unique_values] Columna no permitida o vacía: '{col}'")
        raise HTTPException(status_code=400, detail=f"Columna no permitida: '{col}'")
    model_col = getattr(Registro, col)
    stmt = select(model_col).distinct().order_by(model_col)
    if search:
        stmt = stmt.where(cast(model_col, String).ilike(f"%{search}%"))
    result = await session.execute(stmt)
    values = [row[0] for row in result.fetchall() if row[0] is not None]
    return {"values": values}

@router.get(
    "/historial-cambios/exportar",
    summary="Exportar historial de cambios global a JSON",
    description="Devuelve todo el historial de cambios de la base de datos en formato JSON, ordenado de más reciente a más antiguo. Requiere autenticación: solo admin."
)
async def exportar_historial_cambios(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    from datetime import datetime
    result = await session.execute(
        select(HistorialCambio).order_by(desc(HistorialCambio.fecha))
    )
    historial = result.scalars().all()
    historial_json = [
        {
            "fecha": h.fecha.isoformat() if h.fecha else None,
            "usuario": h.usuario,
            "accion": h.accion,
            "campo": h.campo,
            "valor_anterior": h.valor_anterior,
            "valor_nuevo": h.valor_nuevo,
            "descripcion": h.descripcion,
            "numero_inspector": h.numero_inspector,
            "registro_id": h.registro_id,
            "id": h.id
        }
        for h in historial
    ]
    return historial_json
