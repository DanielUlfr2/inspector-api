from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# --- ESQUEMA RESUMIDO (LISTADO) ---
class DeviceInfoSchema(BaseModel):
    uuid: str = Field(..., alias="uuidinspector") 
    name: str = Field(..., alias="strinspectorname")
    status_id: int = Field(..., alias="idinventoryinspectorstatus")
    is_online: bool = Field(..., alias="boolonline")
    fleet_id: str = Field(..., alias="stridinspectorfleet")
    ip_address: Optional[str] = Field(None, alias="stripaddress")
    last_seen: Optional[datetime] = Field(None, alias="dtlastconnectivityevent")
    os_version: Optional[str] = Field(None, alias="strosversion")
    observaciones: Optional[Dict[str, Any]] = Field({}, alias="jsonbobservaciones")
    note: Optional[str] = Field(None, alias="strnote")
    device_status_id: Optional[int] = Field(2, alias="iddevicestatus")

    class Config:
        from_attributes = True
        populate_by_name = True 

# --- [NUEVO] ESQUEMA DETALLADO (FICHA TÉCNICA) ---
class DeviceDetailSchema(BaseModel):
    # IDs y Nombres
    uuid: str = Field(..., alias="uuidinspector")
    name: str = Field(..., alias="strinspectorname")
    
    # Relaciones (Estos vienen de los alias AS en el SQL)
    status_name: Optional[str] = Field("Desconocido", alias="status_name") 
    service_name: Optional[str] = Field("Sin Asignar", alias="service_name") # Será el Nombre del Cliente
    fleet_id: str = Field(..., alias="stridinspectorfleet")

    # Estado Técnico
    is_online: bool = Field(..., alias="boolonline")
    api_heartbeat: bool = Field(..., alias="boolapihearbeatstate")
    last_connectivity: Optional[datetime] = Field(None, alias="dtlastconnectivityevent")
    ip_address: Optional[str] = Field(None, alias="stripaddress")
    vpn_connected: bool = Field(False, alias="boolconnectedtovpn")
    last_vpn_event: Optional[datetime] = Field(None, alias="dtlastvpnevent")

    # Hardware / Software
    supervisor_version: Optional[str] = Field(None, alias="strsupervisorversion")
    os_version: Optional[str] = Field(None, alias="strosversion")
    memory_usage: int = Field(0, alias="intmemoryusagemb")
    memory_total: int = Field(0, alias="intmemorytotalmb")
    storage_usage: int = Field(0, alias="intstorageusagemb")
    storage_total: int = Field(0, alias="intstoragetotalmb")
    cpu_temp: int = Field(0, alias="intcputempc")
    cpu_usage: int = Field(0, alias="intcpuusagepercent")

    # Meta
    note: Optional[str] = Field(None, alias="strnote")
    observaciones: Optional[Dict[str, Any]] = Field({}, alias="jsonbobservaciones")
    last_metric_update: Optional[datetime] = Field(None, alias="dtlastmetricupdate")
    created_at: Optional[datetime] = Field(None, alias="dtdatecreate")

    class Config:
        from_attributes = True
        populate_by_name = True