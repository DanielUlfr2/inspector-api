"""
🔐 Servicios de Autenticación - Inspector API

Este módulo contiene toda la lógica de autenticación y autorización del sistema,
incluyendo hash de contraseñas, generación de tokens JWT y validación de usuarios.

Funcionalidades principales:
- Hash y verificación de contraseñas con bcrypt
- Generación y validación de tokens JWT
- Autenticación de usuarios mediante tokens
- Gestión de sesiones seguras

Autor: Daniel Bermúdez
Versión: 1.0.0
"""

from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.connection import get_async_session
from app.db.models import Usuario
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Configuración de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de seguridad HTTP Bearer
security = HTTPBearer()

def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando bcrypt.
    
    Args:
        password (str): Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password (str): Contraseña en texto plano
        hashed_password (str): Hash de la contraseña
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso con los datos proporcionados.
    
    Args:
        data (dict): Datos a incluir en el token (ej: username, rol)
        expires_delta (Optional[timedelta]): Tiempo de expiración personalizado
        
    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT de acceso.
    
    Args:
        token (str): Token JWT a decodificar
        
    Returns:
        dict: Payload del token decodificado
        
    Raises:
        ValueError: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado")
    except jwt.PyJWTError:
        raise ValueError("Token inválido")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> Usuario:
    """
    Obtiene el usuario actual basado en el token JWT.
    
    Esta función se usa como dependencia en endpoints protegidos para
    autenticar automáticamente al usuario y obtener su información.
    
    Args:
        credentials (HTTPAuthorizationCredentials): Credenciales del token Bearer
        session (AsyncSession): Sesión de base de datos
        
    Returns:
        Usuario: Objeto del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido, expirado o el usuario no existe
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await session.execute(
        select(Usuario).where(Usuario.username == username)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user 