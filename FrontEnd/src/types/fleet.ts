export interface FleetStats {
    desconectado: number;
    libre: number;
    operativo: number;
    reducido: number;
    total: number;
}

export interface Fleet {
    id: string;
    slug: string;
    device_type_id: number;
    device_type_slug: string;
    organization: string | null;
    created_at: string;
    updated_at: string;
    stats: FleetStats;
}

export interface FleetsResponse {
    fleets: Fleet[];
}