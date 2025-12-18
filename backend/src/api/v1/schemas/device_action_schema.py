from pydantic import BaseModel, Field

class DeviceNoteRequest(BaseModel):
    note: str = Field(..., description="El contenido de la nota/comentario para el equipo.")

class DeviceMoveRequest(BaseModel):
    target_fleet: str = Field(..., description="El SLUG de la flota destino (ej: 'flota-medellin')")