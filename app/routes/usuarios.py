from fastapi import APIRouter, HTTPException, Depends, Path, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.connection import get_async_session
from app.db.models import Usuario, HistorialUsuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate, HistorialUsuarioOut
from app.services.auth import hash_password
from app.services.deps import require_admin, require_user_or_admin, get_current_user
from datetime import datetime
import os
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.responses import FileResponse
import logging
from pydantic import BaseModel

router = APIRouter()

FOTOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'fotos')
os.makedirs(FOTOS_DIR, exist_ok=True)

class ResetPasswordRequest(BaseModel):
    new_password: str

@router.post(
    "/usuarios/",
    response_model=UsuarioOut,
    summary="Crear usuario",
    description="Crea un nuevo usuario. Solo el primer usuario es admin automáticamente. El resto requiere permisos de admin."
)
async def crear_usuario(
    datos: UsuarioCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    # Validar unicidad de username y email
    result = await session.execute(select(Usuario).where((Usuario.username == datos.username) | (Usuario.email == datos.email)))
    existente = result.scalar_one_or_none()
    if existente:
        raise HTTPException(status_code=400, detail="El username o email ya está registrado")

    # Si es el primer usuario, forzar admin
    result = await session.execute(select(Usuario))
    usuarios_existentes = result.scalars().all()
    rol = datos.rol
    if not usuarios_existentes:
        rol = "admin"

    nuevo_usuario = Usuario(
        username=datos.username,
        email=datos.email,
        password_hash=hash_password(datos.password),
        rol=rol,
        foto_perfil=datos.foto_perfil,
        fecha_creacion=datetime.utcnow().isoformat()
    )
    session.add(nuevo_usuario)
    await session.commit()
    await session.refresh(nuevo_usuario)
    
    # Registrar en historial después de obtener el ID
    await registrar_cambio_usuario(
        session=session,
        usuario_id=nuevo_usuario.id,
        admin_username=user["sub"],
        accion="creacion",
        descripcion=f"Usuario creado con rol {rol}"
    )
    
    await session.commit()
    
    return nuevo_usuario

@router.get(
    "/usuarios/",
    response_model=list[UsuarioOut],
    summary="Listar usuarios",
    description="Devuelve la lista de todos los usuarios activos. Requiere autenticación: usuario o admin."
)
async def listar_usuarios(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_user_or_admin)
):
    result = await session.execute(select(Usuario).where(Usuario.activo == True))
    return result.scalars().all()

@router.get(
    "/usuarios/todos",
    response_model=list[UsuarioOut],
    summary="Listar todos los usuarios (incluyendo deshabilitados)",
    description="Devuelve la lista de todos los usuarios, incluyendo los deshabilitados. Requiere autenticación: admin."
)
async def listar_todos_usuarios(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    result = await session.execute(select(Usuario))
    return result.scalars().all()

@router.get(
    "/usuarios/{id}",
    response_model=UsuarioOut,
    summary="Obtener usuario por ID",
    description="Devuelve los datos de un usuario específico por su ID. Requiere autenticación: usuario o admin."
)
async def obtener_usuario_por_id(
    id: int = Path(..., description="ID del usuario a consultar"),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_user_or_admin)
):
    result = await session.execute(select(Usuario).where(Usuario.id == id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put(
    "/usuarios/{id}",
    response_model=UsuarioOut,
    summary="Actualizar usuario",
    description="Actualiza los datos de un usuario. Solo admin puede actualizar cualquier usuario. Requiere autenticación: admin."
)
async def actualizar_usuario(
    id: int,
    datos: UsuarioUpdate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    logging.info(f"Actualizando usuario ID={id} con datos: {datos}")
    
    result = await session.execute(select(Usuario).where(Usuario.id == id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Registrar cambios en historial
    cambios = []
    for key, value in datos.dict(exclude_unset=True).items():
        valor_anterior = getattr(usuario, key)
        if str(valor_anterior) != str(value):
            cambios.append({
                "campo": key,
                "valor_anterior": str(valor_anterior),
                "valor_nuevo": str(value)
            })
    
    logging.info(f"Cambios detectados: {cambios}")
    
    # Aplicar cambios
    for key, value in datos.dict(exclude_unset=True).items():
        setattr(usuario, key, value)
    
    # Registrar cada cambio en el historial
    for cambio in cambios:
        try:
            await registrar_cambio_usuario(
                session=session,
                usuario_id=usuario.id,
                admin_username=user["sub"],
                accion="edicion",
                campo=cambio["campo"],
                valor_anterior=cambio["valor_anterior"],
                valor_nuevo=cambio["valor_nuevo"],
                descripcion=f"Campo {cambio['campo']} modificado"
            )
        except Exception as e:
            logging.error(f"Error al registrar cambio en historial: {e}")
    
    await session.commit()
    await session.refresh(usuario)
    
    logging.info(f"Usuario actualizado exitosamente: {usuario.username}")
    
    return usuario

@router.delete(
    "/usuarios/{id}",
    response_model=dict,
    summary="Eliminar usuario",
    description="Elimina un usuario por ID. Solo admin puede eliminar usuarios. Requiere autenticación: admin."
)
async def eliminar_usuario(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    result = await session.execute(select(Usuario).where(Usuario.id == id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Registrar en historial antes de eliminar
    await registrar_cambio_usuario(
        session=session,
        usuario_id=usuario.id,
        admin_username=user["sub"],
        accion="eliminacion",
        descripcion=f"Usuario {usuario.username} eliminado"
    )
    
    await session.delete(usuario)
    await session.commit()
    return {"mensaje": f"Usuario con ID={id} eliminado exitosamente"}

@router.put(
    "/usuarios/{id}/toggle-activo",
    response_model=UsuarioOut,
    summary="Activar/desactivar usuario",
    description="Cambia el estado activo/inactivo de un usuario. Requiere autenticación: admin."
)
async def toggle_usuario_activo(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    result = await session.execute(select(Usuario).where(Usuario.id == id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    estado_anterior = usuario.activo
    usuario.activo = not usuario.activo
    
    # Registrar en historial
    accion = "activacion" if usuario.activo else "desactivacion"
    descripcion = f"Usuario {'activado' if usuario.activo else 'deshabilitado'}"
    
    await registrar_cambio_usuario(
        session=session,
        usuario_id=usuario.id,
        admin_username=user["sub"],
        accion=accion,
        campo="activo",
        valor_anterior=str(estado_anterior),
        valor_nuevo=str(usuario.activo),
        descripcion=descripcion
    )
    
    await session.commit()
    await session.refresh(usuario)
    
    return usuario

@router.post(
    "/usuarios/{id}/foto",
    summary="Subir o actualizar foto de perfil",
    description="Permite subir o actualizar la foto de perfil del usuario. El propio usuario o un admin pueden hacerlo. Requiere autenticación: usuario o admin."
)
async def subir_foto_perfil(
    id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(get_current_user)
):
    # Permitir solo al propio usuario o admin
    if user["rol"] != "admin" and user["id"] != id:
        raise HTTPException(status_code=403, detail="No tienes permisos para cambiar esta foto de perfil")
    result = await session.execute(select(Usuario).where(Usuario.id == id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Guardar archivo
    ext = os.path.splitext(file.filename)[1]
    filename = f"usuario_{id}{ext}"
    filepath = os.path.join(FOTOS_DIR, filename)

    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    # Actualizar campo foto_perfil
    usuario.foto_perfil = f"/static/fotos/{filename}"
    await session.commit()
    await session.refresh(usuario)
    
    # Devolver respuesta con campo "foto" unificado
    return {
        "message": "Foto de perfil actualizada correctamente",
        "foto": usuario.foto_perfil,
        "user": {
            "id": usuario.id,
            "username": usuario.username,
            "email": usuario.email,
            "rol": usuario.rol,
            "foto": usuario.foto_perfil
        }
    }

@router.get(
    "/usuarios/{id}/foto",
    summary="Obtener foto de perfil",
    description="Devuelve la imagen de la foto de perfil del usuario si existe. No requiere autenticación."
)
async def obtener_foto_perfil(
    id: int,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Usuario).where(Usuario.id == id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not usuario.foto_perfil:
        default_path = os.path.join(FOTOS_DIR, "default.png")
        if os.path.exists(default_path):
            return FileResponse(default_path, media_type="image/png")
        else:
            raise HTTPException(status_code=404, detail="El usuario no tiene foto de perfil")
    foto_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), usuario.foto_perfil.lstrip("/"))
    logging.warning(f"Intentando servir foto de perfil: {foto_path}")
    if not os.path.exists(foto_path):
        logging.error(f"Archivo de foto de perfil no encontrado: {foto_path}")
        raise HTTPException(status_code=404, detail="Archivo de foto de perfil no encontrado")
    ext = os.path.splitext(foto_path)[1].lower()
    mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    return FileResponse(foto_path, media_type=mime) 

@router.post(
    "/usuarios/{id}/restablecer-contrasena",
    summary="Restablecer contraseña de usuario (admin)",
    description="Permite a un admin restablecer la contraseña de cualquier usuario. Requiere autenticación: admin.",
)
async def restablecer_contrasena_usuario(
    id: int,
    datos: ResetPasswordRequest,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    result = await session.execute(select(Usuario).where(Usuario.id == id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if len(datos.new_password) < 8:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 8 caracteres")
    
    usuario.password_hash = hash_password(datos.new_password)
    
    # Registrar en historial
    await registrar_cambio_usuario(
        session=session,
        usuario_id=usuario.id,
        admin_username=user["sub"],
        accion="restablecer_password",
        descripcion="Contraseña restablecida por administrador"
    )
    
    await session.commit()
    
    return {"mensaje": f"Contraseña restablecida para el usuario con ID={id}"} 

@router.get(
    "/usuarios/{id}/historial",
    summary="Obtener historial de cambios de un usuario",
    description="Devuelve el historial de cambios realizados sobre un usuario específico. Requiere autenticación: admin."
)
async def obtener_historial_usuario(
    id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    # Verificar que el usuario existe
    result = await session.execute(select(Usuario).where(Usuario.id == id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener historial ordenado por fecha descendente
    result = await session.execute(
        select(HistorialUsuario)
        .where(HistorialUsuario.usuario_id == id)
        .order_by(HistorialUsuario.fecha.desc())
    )
    historial = result.scalars().all()
    
    # Convertir datetime a string para cada registro
    historial_convertido = []
    for record in historial:
        record_dict = {
            "id": record.id,
            "usuario_id": record.usuario_id,
            "fecha": record.fecha.isoformat() if record.fecha else None,
            "admin_que_realizo_cambio": record.admin_que_realizo_cambio,
            "accion": record.accion,
            "campo": record.campo,
            "valor_anterior": record.valor_anterior,
            "valor_nuevo": record.valor_nuevo,
            "descripcion": record.descripcion
        }
        historial_convertido.append(record_dict)
    
    return historial_convertido

# Función auxiliar para registrar cambios en el historial
async def registrar_cambio_usuario(
    session: AsyncSession,
    usuario_id: int,
    admin_username: str,
    accion: str,
    campo: str = None,
    valor_anterior: str = None,
    valor_nuevo: str = None,
    descripcion: str = None
):
    historial = HistorialUsuario(
        usuario_id=usuario_id,
        admin_que_realizo_cambio=admin_username,
        accion=accion,
        campo=campo,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        descripcion=descripcion
    )
    session.add(historial)
    # No hacer commit aquí, se hará en el endpoint principal 