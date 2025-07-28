from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.connection import get_async_session
from app.db.models import Usuario
from app.services.auth import (
    verify_password, create_access_token, get_current_user, hash_password
)
from pydantic import BaseModel, EmailStr
import os
import shutil
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["autenticación"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    nombre: str
    apellido: str
    rol: str = "user"


class EditProfileRequest(BaseModel):
    nombre: str
    email: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post(
    "/register", 
    summary="Registrar usuario", 
    description="Crea un nuevo usuario en el sistema"
)
async def register(
    user_data: RegisterRequest,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Verificar si el username ya existe
        result = await session.execute(
            select(Usuario).where(Usuario.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400, 
                detail="El nombre de usuario ya está en uso"
            )
        
        # Verificar si el email ya existe
        result = await session.execute(
            select(Usuario).where(Usuario.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400, 
                detail="El correo electrónico ya está en uso"
            )
        
        # Crear nuevo usuario
        hashed_password = hash_password(user_data.password)
        nuevo_usuario = Usuario(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            nombre=user_data.nombre,
            apellido=user_data.apellido,
            rol=user_data.rol,
            fecha_creacion=datetime.now().isoformat(),
            activo=True
        )
        
        session.add(nuevo_usuario)
        await session.commit()
        await session.refresh(nuevo_usuario)
        
        return {
            "message": "Usuario registrado correctamente",
            "id": nuevo_usuario.id,
            "username": nuevo_usuario.username,
            "email": nuevo_usuario.email,
            "rol": nuevo_usuario.rol
        }
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Error al registrar el usuario"
        )


@router.get(
    "/me", 
    summary="Obtener usuario actual", 
    description="Obtiene la información del usuario autenticado"
)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "rol": current_user.rol,
        "foto": current_user.foto_perfil,
        "activo": current_user.activo
    }


@router.post(
    "/login", 
    summary="Iniciar sesión", 
    description="Autentica al usuario y devuelve un JWT con los datos y rol. Usar este token para acceder a los endpoints protegidos."
)
async def login(
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    # Detectar si viene como form-data (OAuth2) o JSON (frontend)
    if request.headers.get("content-type", "").startswith(
        "application/x-www-form-urlencoded"
    ):
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
    else:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")

    # Buscar usuario por username o email
    result = await session.execute(
        select(Usuario).where(
            (Usuario.username == username) | (Usuario.email == username)
        )
    )
    usuario = result.scalar_one_or_none()
    if not usuario or not verify_password(password, usuario.password_hash):
        raise HTTPException(
            status_code=401, 
            detail="Credenciales incorrectas"
        )
    
    # Verificar que el usuario esté activo
    if not usuario.activo:
        raise HTTPException(
            status_code=401, 
            detail="Usuario deshabilitado"
        )

    token_data = {
        "sub": usuario.username,
        "id": usuario.id,
        "rol": usuario.rol,
        "email": usuario.email
    }
    access_token = create_access_token(token_data)
    
    # Devolver token e información del usuario
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": usuario.id,
            "username": usuario.username,
            "email": usuario.email,
            "rol": usuario.rol,
            "foto": usuario.foto_perfil
        }
    }

@router.put("/editar-perfil", summary="Editar perfil", description="Actualiza la información básica del perfil del usuario")
async def editar_perfil(
    profile_data: EditProfileRequest,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Verificar si el email ya está en uso por otro usuario
        if profile_data.email != current_user.email:
            result = await session.execute(
                select(Usuario).where(Usuario.email == profile_data.email)
            )
            existing_user = result.scalar_one_or_none()
            if existing_user:
                raise HTTPException(status_code=400, detail="El correo electrónico ya está en uso")
        
        # Actualizar datos del usuario
        current_user.username = profile_data.nombre
        current_user.email = profile_data.email
        
        await session.commit()
        
        return {
            "message": "Perfil actualizado correctamente",
            "user": {
                "username": current_user.username,
                "email": current_user.email,
                "rol": current_user.rol,
                "foto": current_user.foto_perfil
            }
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar el perfil")

@router.post("/cambiar-contraseña", summary="Cambiar contraseña", description="Cambia la contraseña del usuario actual")
async def cambiar_contraseña(
    password_data: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Verificar contraseña actual
        if not verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
        
        # Verificar que la nueva contraseña sea diferente
        if password_data.current_password == password_data.new_password:
            raise HTTPException(status_code=400, detail="La nueva contraseña debe ser diferente a la actual")
        
        # Validar longitud de la nueva contraseña
        if len(password_data.new_password) < 8:
            raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 8 caracteres")
        
        # Hashear y guardar nueva contraseña
        current_user.password_hash = hash_password(password_data.new_password)
        await session.commit()
        
        return {"message": "Contraseña actualizada correctamente"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error al cambiar la contraseña")

@router.post("/cambiar-foto", summary="Cambiar foto de perfil", description="Sube y actualiza la foto de perfil del usuario")
async def cambiar_foto(
    foto: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Validar tipo de archivo
        if not foto.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
        # Validar tamaño (máximo 5MB)
        if foto.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="La imagen debe ser menor a 5MB")
        
        # Crear directorio de fotos si no existe
        fotos_dir = "app/static/fotos"
        os.makedirs(fotos_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(foto.filename)[1]
        filename = f"usuario_{current_user.id}_{timestamp}{file_extension}"
        file_path = os.path.join(fotos_dir, filename)
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        
        # Actualizar ruta en la base de datos
        foto_url = f"/static/fotos/{filename}"
        current_user.foto_perfil = foto_url
        await session.commit()
        
        return {
            "message": "Foto de perfil actualizada correctamente",
            "foto": foto_url
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error al actualizar la foto de perfil") 