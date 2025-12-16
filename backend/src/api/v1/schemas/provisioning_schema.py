from pydantic import BaseModel, Field

class ProvisioningRequest(BaseModel):
    # --- DATOS DEL SERVICIO (Tabla InspectorService) ---
    inspector_service_id: str = Field(..., description="ID del contrato o servicio, ej: 1111")
    
    # IDs seleccionados de los catálogos
    city_id: int
    cmts_olt_id: int
    product_id: int
    technology_id: int
    service_type_id: int
    crm_id: int
    
    # Datos manuales
    address: str
    client_name: str
    down_speed: int
    up_speed: int

    # --- DATOS DEL EQUIPO (Tabla Inspector + Balena) ---
    new_device_name: str = Field(..., description="Nombre final generado (ej: andina_med_olt_..._INS123)")
    status_id: int = Field(..., description="ID del estado (ej: Ocupado)")