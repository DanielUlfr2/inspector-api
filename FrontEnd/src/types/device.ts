// Estructura de las observaciones técnicas (JSONB en base de datos)
export interface DeviceObservations {
    cpu_id?: string;
    dashboard_url?: string;
    mac_address?: string;
    overall_status_raw?: string;
    public_address?: string | null;
}

// Interfaz principal del Dispositivo (Inspector)
export interface Device {
    // Identificadores y nombres
    uuidinspector: string;
    strinspectorname: string;
    stridinspectorfleet: string;
    strnote: string;

    // Estados y conexiones
    boolonline: boolean;
    boolapihearbeatstate: boolean;
    boolconnectedtovpn: boolean;
    status_name: string;

    // Red y Software
    stripaddress: string;
    strosversion: string;
    strsupervisorversion: string;

    // Métricas de Hardware (Telemetría)
    intcputempc: number;
    intcpuusagepercent: number;
    intmemorytotalmb: number;
    intmemoryusagemb: number;
    intstoragetotalmb: number;
    intstorageusagemb: number;

    // Fechas y Eventos (ISO Strings)
    dtdatecreate: string;
    dtlastconnectivityevent: string;
    dtlastmetricupdate: string;
    dtlastvpnevent: string;

    // Datos dinámicos y estados de inventario
    jsonbobservaciones: DeviceObservations;
    idinventoryinspectorstatus: number;
    iddevicestatus: number;

    inspector_service_id?: string;
    client_name?: string;
    address?: string;
    city_id?: number;
    cmts_olt_id?: number;
    product_id?: number;
    technology_id?: number;
    service_type_id?: number;
    crm_id?: number;
    down_speed?: number;
    up_speed?: number;
    country_id?: number;
    region_id?: number;
    department_id?: number;

    // Names (Joined)
    city_name?: string;
    cmts_olt_name?: string;
    technology_name?: string;
    service_type_name?: string;

    // Variables de configuración
    device_variables?: Variable[];
    fleet_variables?: Variable[];
}

// Variable Interface
export interface Variable {
    name: string;
    value: string;
}

// Respuesta del endpoint de lista (/v1/infodevices)
export interface DeviceResponse {
    devices: Device[];
}

// History Data Interface
export interface DeviceHistory {
    id: number;
    uuid: string;
    timestamp: string;
    cpu_usage: number;
    cpu_temp: number;
    memory_usage: number;
    memory_total: number;
    storage_usage: number;
    storage_total: number;
    is_online: boolean;
}