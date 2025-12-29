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
    service_name: string;

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
}

// Respuesta del endpoint de lista (/v1/infodevices)
export interface DeviceResponse {
    devices: Device[];
}