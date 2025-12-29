export interface GlobalStat {
    timestamp: string;
    online: number;
    offline: number;
    reduced: number;
    free: number;
    total: number;
    time?: string; // Campo procesado para la gráfica (HH:mm)
}

export type TimeRange = '6h' | '12h' | '24h' | 'custom';