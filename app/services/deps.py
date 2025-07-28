from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.auth import decode_access_token
from typing import Dict

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependencia para obtener el usuario actual desde el token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        payload = decode_access_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Dependencia para requerir rol admin
async def require_admin(user: Dict = Depends(get_current_user)):
    if user.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")
    return user

# Dependencia para requerir rol user o admin (solo lectura)
async def require_user_or_admin(user: Dict = Depends(get_current_user)):
    if user.get("rol") not in ["admin", "user"]:
        raise HTTPException(status_code=403, detail="No tienes permisos suficientes")
    return user 