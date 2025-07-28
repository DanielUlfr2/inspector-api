"""
📋 Esquemas de Registro - Inspector API

Este módulo define los esquemas Pydantic para validación y serialización
de datos relacionados con los registros de inspección.

Esquemas incluidos:
- RegistroBase: Esquema base con validaciones comunes
- RegistroCreate: Para creación de nuevos registros
- RegistroUpdate: Para actualización de registros existentes
- RegistroOut: Para respuestas de la API
- RegistroListResponse: Para listas paginadas
- TotalRegistrosResponse: Para conteos de registros

Autor: Daniel Bermúdez
Versión: 1.0.0
"""

from pydantic import BaseModel, EmailStr, constr, field_validator
from typing import Optional, List
import logging

# Configuración básica del logger
logger = logging.getLogger(__name__)


class RegistroBase(BaseModel):
    """
    Esquema base para registros de inspección.
    
    Define los campos comunes y validaciones para todos los registros
    del sistema de gestión de inventario.
    
    Atributos:
        numero_inspector: Número único del inspector (debe ser > 0)
        uuid: Identificador único universal (opcional)
        nombre: Nombre del dispositivo (mínimo 3 caracteres)
        status: Estado del dispositivo (mínimo 3 caracteres)
        observaciones: Observaciones sobre el dispositivo
        flota: Flota asignada (mínimo 3 caracteres)
        uso: Tipo de uso (mínimo 3 caracteres)
        encargado: Persona responsable (mínimo 3 caracteres)
        celular: Número de contacto (exactamente 10 dígitos)
        correo: Correo electrónico válido
        region: Región geográfica (mínimo 3 caracteres)
        departamento: Departamento (mínimo 3 caracteres)
        ciudad: Ciudad (mínimo 3 caracteres)
        direccion: Dirección física (mínimo 3 caracteres)
        id_servicio: Identificador del servicio (mínimo 3 caracteres)
        tecnologia: Tecnología utilizada (mínimo 3 caracteres)
        cmts_olt: Equipo CMTS/OLT (mínimo 3 caracteres)
        mac_sn: Dirección MAC o número de serie (mínimo 3 caracteres)
    """
    numero_inspector: int
    uuid: Optional[str] = None
    nombre: constr(min_length=3)
    status: constr(min_length=3)
    observaciones: constr(min_length=3)
    flota: constr(min_length=3)
    uso: constr(min_length=3)
    encargado: constr(min_length=3)
    celular: str  # Ahora acepta cualquier string
    correo: EmailStr
    region: constr(min_length=3)
    departamento: constr(min_length=3)
    ciudad: constr(min_length=3)
    direccion: constr(min_length=3)
    id_servicio: constr(min_length=3)
    tecnologia: constr(min_length=3)
    cmts_olt: constr(min_length=3)
    mac_sn: constr(min_length=3)

    @field_validator('numero_inspector')
    def validar_inspector_positivo(cls, v):
        """
        Valida que el número de inspector sea positivo.
        
        Args:
            v: Valor del número de inspector
            
        Returns:
            int: Número de inspector validado
            
        Raises:
            ValueError: Si el número no es positivo
        """
        try:
            if v <= 0:
                logger.error("El número de inspector debe ser mayor que 0.")
                raise ValueError("El número de inspector debe ser mayor que 0.")
            logger.info(f"Validación exitosa para numero_inspector: {v}")
            return v
        except Exception as e:
            logger.error(f"Error en validación de numero_inspector: {e}")
            raise

    @field_validator('celular')
    def validar_celular_10_digitos(cls, v):
        """
        Valida que el número de celular tenga exactamente 10 dígitos.
        
        Args:
            v: Número de celular a validar
            
        Returns:
            str: Número de celular validado
            
        Raises:
            ValueError: Si el número no tiene 10 dígitos
        """
        if v is not None and len(v) != 10:
            logger.warning(f"El número de celular '{v}' no tiene 10 dígitos.")
            raise ValueError("El número de celular debe tener exactamente 10 dígitos.")
        return v


class RegistroCreate(RegistroBase):
    """
    Esquema para creación de nuevos registros.
    
    Hereda todas las validaciones de RegistroBase y se usa
    específicamente para operaciones de creación.
    """
    pass


class RegistroUpdate(RegistroBase):
    """
    Esquema para actualización de registros existentes.
    
    Hereda todas las validaciones de RegistroBase y se usa
    específicamente para operaciones de actualización.
    """
    pass


class RegistroOut(RegistroBase):
    """
    Esquema para respuestas de la API con registros.
    
    Incluye el ID del registro y está configurado para trabajar
    con objetos SQLAlchemy mediante from_attributes=True.
    
    Atributos adicionales:
        id: Identificador único del registro en la base de datos
    """
    id: int

    model_config = {
        "from_attributes": True  # Reemplazo de orm_mode=True en Pydantic v2
    }


class RegistroListResponse(BaseModel):
    """
    Esquema para respuestas de listas paginadas de registros.
    
    Usado cuando se devuelven múltiples registros con información
    de paginación.
    
    Atributos:
        total_records: Número total de registros disponibles
        registros: Lista de registros para la página actual
    """
    total_records: int
    registros: List[RegistroOut]


class TotalRegistrosResponse(BaseModel):
    """
    Esquema para respuestas de conteo de registros.
    
    Usado cuando solo se necesita el número total de registros
    que cumplen ciertos criterios.
    
    Atributos:
        total: Número total de registros
    """
    total: int