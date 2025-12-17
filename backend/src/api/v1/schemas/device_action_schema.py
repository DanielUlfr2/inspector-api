from pydantic import BaseModel, Field

class DeviceNoteRequest(BaseModel):
    note: str = Field(..., description="El contenido de la nota/comentario para el equipo.")