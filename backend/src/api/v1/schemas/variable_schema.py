from pydantic import BaseModel, Field

class VariableRequest(BaseModel):
    name: str = Field(..., description="Nombre de la variable (ej: WIFI_SSID)", min_length=1)
    value: str = Field(..., description="Valor de la variable (ej: MiCasa123)")