from pydantic import BaseModel, Field
from typing import Optional

class FleetCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre de la nueva flota (Ej: proyecto_medellin)")
    device_type_id: int = Field(..., description="ID del tipo de dispositivo (Viene del catálogo)")
    organization: Optional[str] = Field(None, description="Slug de la organización (Opcional)")

class FleetRenameRequest(BaseModel):
    new_name: str = Field(..., min_length=3, description="El nuevo nombre para la flota")