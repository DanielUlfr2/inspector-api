from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    rol: str = 'user'
    foto_perfil: Optional[str] = None

class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str
    rol: str = "user"
    foto_perfil: Optional[str] = None

class UsuarioOut(BaseModel):
    id: int
    username: str
    email: str
    rol: str
    foto_perfil: Optional[str] = None
    fecha_creacion: str
    activo: bool

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None 

class HistorialUsuarioOut(BaseModel):
    id: int
    usuario_id: int
    fecha: str
    admin_que_realizo_cambio: str
    accion: str
    campo: Optional[str] = None
    valor_anterior: Optional[str] = None
    valor_nuevo: Optional[str] = None
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Convertir datetime a string si es necesario
        if hasattr(obj, 'fecha') and obj.fecha:
            if isinstance(obj.fecha, datetime):
                obj.fecha = obj.fecha.isoformat()
        return super().from_orm(obj) 