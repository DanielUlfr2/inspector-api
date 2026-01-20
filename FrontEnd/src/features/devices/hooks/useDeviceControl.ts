// src/features/devices/hooks/useDeviceControl.ts
import { useState } from 'react';
import { deviceService, DeviceAction } from '../deviceService';
import { Device } from '../../../types/device';
import { getDeviceRealStatus } from '../../../utils/deviceStatus';

export const useDeviceControl = () => {
    // Manejamos estados granulares para el modal
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error' | 'partial'>('idle');
    const [excludedCount, setExcludedCount] = useState(0);
    const [excludedReasons, setExcludedReasons] = useState<string[]>([]);

    const executeAction = async (devices: Device[], action: DeviceAction) => {
        if (devices.length === 0) return false;

        setStatus('loading');

        // 🔍 FILTRAR DISPOSITIVOS VÁLIDOS (solo operativos)
        const validDevices = devices.filter(device => {
            const realStatus = getDeviceRealStatus(device);
            return realStatus === 'operativo';
        });

        const excluded = devices.length - validDevices.length;
        setExcludedCount(excluded);

        // Generar lista de razones de exclusión
        if (excluded > 0) {
            const reasons = devices
                .filter(d => getDeviceRealStatus(d) !== 'operativo')
                .map(d => `${d.strinspectorname} (${getDeviceRealStatus(d)})`);
            setExcludedReasons(reasons);
        } else {
            setExcludedReasons([]);
        }

        // Si no hay dispositivos válidos, error
        if (validDevices.length === 0) {
            setStatus('error');
            return false;
        }

        try {
            const uuids = validDevices.map(d => d.uuidinspector);

            // Usar endpoint bulk si hay más de 5 dispositivos
            if (uuids.length > 5) {
                await deviceService.sendBulkActionOptimized(uuids, action);
            } else {
                await deviceService.sendBulkAction(uuids, action);
            }

            // Partial si hubo exclusiones, success si todos fueron procesados
            setStatus(excluded > 0 ? 'partial' : 'success');
            return true;
        } catch (error) {
            console.error("Error en la acción:", error);
            setStatus('error');
            return false;
        }
    };

    return { executeAction, status, setStatus, excludedCount, excludedReasons };
};