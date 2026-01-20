from pydantic import BaseModel, Field

class DeviceNoteRequest(BaseModel):
    note: str = Field(..., description="El contenido de la nota/comentario para el equipo.")

class DeviceMoveRequest(BaseModel):
    target_fleet: str = Field(..., description="El SLUG de la flota destino (ej: 'flota-medellin')")

class BulkActionRequest(BaseModel):
    """Schema for bulk device actions"""
    uuids: list[str] = Field(..., min_length=1, description="List of device UUIDs")