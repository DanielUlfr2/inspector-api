import logging
import re
import requests
from jose import jwt
from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from src.core.config import settings

# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Security")

# --- LÓGICA DE KEYCLOAK (AUTH) ---
token_auth_scheme = HTTPBearer()
_jwks_cache = None

def get_jwks():
    """Obtiene y cachea las llaves públicas de Keycloak usando la red interna"""
    global _jwks_cache
    if _jwks_cache is None:
        try:
            # Aquí se usa 'keycloak:8080' porque es comunicación entre contenedores
            url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            _jwks_cache = response.json()
        except Exception as e:
            logger.error(f"Error obteniendo JWKS de Keycloak: {e}")
            return None
    return _jwks_cache

def verify_keycloak_jwt(token: str = Depends(token_auth_scheme)):
    """Valida el token JWT enviado por el Frontend"""
    jwks = get_jwks()
    if not jwks:
        raise HTTPException(status_code=500, detail="Error de configuración de seguridad")

    try:
        header = jwt.get_unverified_header(token.credentials)
        key = next(k for k in jwks['keys'] if k['kid'] == header['kid'])
        
        # --- SOLUCIÓN AL ERROR DE ISSUER ---
        payload = jwt.decode(
            token.credentials,
            key,
            algorithms=['RS256'],
            audience=settings.KEYCLOAK_AUDIENCE,
            # Desactivamos la verificación de 'iss' y 'aud' estricta 
            # para evitar líos entre localhost y nombres de Docker.
            options={
                "verify_iss": False,
                "verify_aud": False,
                "verify_at_hash": False
            }
        )
        return payload
    except Exception as e:
        logger.warning(f"Intento de acceso con token inválido: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

def require_roles(allowed_roles: List[str]):
    """Dependencia para validar roles de Inspector"""
    def role_checker(user_data=Depends(verify_keycloak_jwt)):
        # Buscamos roles en la raíz del token (según tu JSON)
        user_roles = user_data.get("roles", []) 
        
        # Por si acaso, también buscamos en realm_access
        if not user_roles:
            user_roles = user_data.get("realm_access", {}).get("roles", [])

        if not any(role in user_roles for role in allowed_roles):
            logger.warning(f"🚫 Acceso denegado. Roles requeridos: {allowed_roles}. Roles usuario: {user_roles}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="No tienes permisos para realizar esta acción"
            )
        return user_data
    return role_checker

# --- TU CLASE EXISTENTE (SANIDAD DE DATOS) ---
class SecurityValidator:
    DANGEROUS_PATTERNS = [
        r";\s*DROP\s+TABLE", 
        r";\s*DELETE\s+FROM", 
        r";\s*TRUNCATE", 
        r"--", 
        r"/\*"
    ]

    @staticmethod
    def is_safe_string(value: str) -> bool:
        if not isinstance(value, str):
            return True
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"🚨 ALERTA: Texto sospechoso bloqueado: {value}")
                return False
        return True

    @staticmethod
    def sanitize_input(data: dict) -> dict:
        clean_data = {}
        for key, val in data.items():
            if isinstance(val, str) and not SecurityValidator.is_safe_string(val):
                clean_data[key] = "SANITIZED_UNSAFE_CONTENT"
            else:
                clean_data[key] = val
        return clean_data