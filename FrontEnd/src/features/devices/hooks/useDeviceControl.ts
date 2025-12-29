// src/features/devices/hooks/useDeviceControl.ts
import { useState } from 'react';
import { deviceService, DeviceAction } from '../deviceService';

export const useDeviceControl = () => {
    // Manejamos estados granulares para el modal
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

    const executeAction = async (uuids: string[], action: DeviceAction) => {
        if (uuids.length === 0) return false;

        setStatus('loading');
        try {
            // Ejecutamos y verificamos que el servidor responda 200 OK
            const results = await deviceService.sendBulkAction(uuids, action);

            // Validamos si todas las respuestas fueron exitosas (status 200)
            const allSuccessful = results.every(res => res.status === 200);

            if (allSuccessful) {
                setStatus('success');
                return true;
            }
            throw new Error("Respuesta del servidor no válida");
        } catch (error) {
            console.error("Error en la acción:", error);
            setStatus('error');
            return false;
        }
    };

    return { executeAction, status, setStatus };
};