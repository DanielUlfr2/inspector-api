from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FleetCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre de la nueva flota (Ej: proyecto_medellin)")
    device_type_id: int = Field(..., description="ID del tipo de dispositivo (Viene del catálogo)")
    organization: Optional[str] = Field(None, description="Slug de la organización (Opcional)")

class FleetRenameRequest(BaseModel):
    new_name: str = Field(..., min_length=3, description="El nuevo nombre para la flota")

class FleetStats(BaseModel):
    total: int = 0
    operativo: int = 0
    reducido: int = 0
    desconectado: int = 0
    libre: int = 0

class FleetSummary(BaseModel):
    id: str
    slug: str
    organization: Optional[str] = None
    device_type_id: int
    device_type_slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stats: FleetStats