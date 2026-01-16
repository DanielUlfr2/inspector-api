import { Device } from '../types/device';

/**
 * Determina el estado real de un dispositivo aplicando la lógica de prioridad:
 * 1. Si la nota contiene "Libre" → Libre (prioridad absoluta)
 * 2. Si no, usa iddevicestatus
 */
export const getDeviceRealStatus = (device: Device): 'libre' | 'operativo' | 'desconectado' | 'reducido' => {
    // PRIORIDAD 1: Nota con "Libre"
    if (device.strnote && device.strnote.toLowerCase().includes('libre')) {
        return 'libre';
    }

    // PRIORIDAD 2: iddevicestatus
    const statusId = device.iddevicestatus;

    if (statusId === 4) {
        return 'libre';
    } else if ([3, 8].includes(statusId)) {
        return 'desconectado';
    } else if ([2, 9].includes(statusId)) {
        return 'reducido';
    } else if ([1, 5, 6, 7].includes(statusId)) {
        return 'operativo';
    }

    // Fallback
    return 'desconectado';
};

/**
 * Obtiene la configuración visual para el estado de un dispositivo
 */
export const getStatusDisplay = (status: ReturnType<typeof getDeviceRealStatus>) => {
    switch (status) {
        case 'operativo':
            return { label: 'Operational', value: 'operational', color: 'green' };
        case 'desconectado':
            return { label: 'Disconnected', value: 'disconnected', color: 'red' };
        case 'reducido':
            return { label: 'Reduced', value: 'reduced', color: 'orange' };
        case 'libre':
            return { label: 'Libre', value: 'libre', color: 'purple' };
        default:
            return { label: 'Unknown', value: 'unknown', color: 'gray' };
    }
};
