// src/types/device.ts
export interface Device {
    boolonline: boolean;
    dtlastconnectivityevent: string;
    idinventoryinspectorstatus: number;
    jsonbobservaciones: {
        cpu_id?: string;
        dashboard_url?: string;
        mac_address?: string;
        overall_status_raw?: string;
        public_address?: string | null;
    };
    stridinspectorfleet: string;
    strinspectorname: string;
    stripaddress: string;
    strnote: string;
    strosversion: string;
    uuidinspector: string;
}

export interface DeviceResponse {
    devices: Device[];
}