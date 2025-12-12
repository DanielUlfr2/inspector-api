from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class DeviceInfoSchema(BaseModel):
    uuid: str = Field(..., alias="uuidInspector") # Alias para mapear DB -> JSON bonito
    name: str = Field(..., alias="strInspectorName")
    status_id: int = Field(..., alias="idInventoryInspectorStatus")
    is_online: bool = Field(..., alias="boolOnline")
    fleet_id: str = Field(..., alias="stridInspectorFleet")
    ip_address: Optional[str] = Field(None, alias="strIpAddress")
    last_seen: Optional[datetime] = Field(None, alias="dtLastConnectivityEvent")
    os_version: Optional[str] = Field(None, alias="strOsVersion")
    observaciones: Optional[Dict[str, Any]] = Field({}, alias="jsonbObservaciones")

    class Config:
        from_attributes = True
        populate_by_name = True # Permite usar los nombres bonitos (uuid) o los de DB