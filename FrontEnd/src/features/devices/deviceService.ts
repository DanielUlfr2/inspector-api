// src/features/devices/deviceService.ts
import apiClient from '../../api/apiClient';
import { Device, DeviceResponse, DeviceHistory } from '../../types/device';
import { FormOptions, ProvisionPayload } from '../../types/provision';

const API_BASE = import.meta.env.VITE_API_BASE_URL;
const DEVICES_PATH = import.meta.env.VITE_API_DEVICES_INFO;
const ADMIN_PATH = import.meta.env.VITE_API_ADMIN_PATH;

export type DeviceAction = 'reboot' | 'restart' | 'shutdown';

export const deviceService = {
    /**
     * Obtiene la lista completa de dispositivos
     */
    async getDevices(): Promise<Device[]> {
        const url = `${API_BASE}${DEVICES_PATH}`;
        const response = await apiClient.get<DeviceResponse>(url);
        return response.data.devices.filter(
            (device: Device) => device.uuidinspector !== 'DEFAULT'
        );
    },

    /**
     * Obtiene el detalle técnico de un solo dispositivo por UUID
     */
    async getDeviceByUuid(uuid: string): Promise<Device> {
        const url = `${API_BASE}${DEVICES_PATH}/${uuid}`;
        const response = await apiClient.get<Device>(url);
        return response.data;
    },

    /**
     * Envía una acción administrativa individual (reboot, etc)
     */
    async sendAction(uuid: string, action: DeviceAction) {
        const url = `${API_BASE}${ADMIN_PATH}/${uuid}/${action}`;
        return await apiClient.post(url);
    },

    /**
     * Envía acciones en lote (paralelo)
     */
    async sendBulkAction(uuids: string[], action: DeviceAction) {
        return Promise.all(uuids.map(uuid => this.sendAction(uuid, action)));
    },

    /**
     * Envía acciones en lote usando el endpoint bulk (más eficiente para >5 dispositivos)
     */
    async sendBulkActionOptimized(uuids: string[], action: DeviceAction) {
        const url = `${API_BASE}${ADMIN_PATH}/bulk/${action}`;
        return await apiClient.post(url, { uuids });
    },

    /**
     * Obtiene logs (Legacy/Sync)
     */
    async getDeviceLogs(uuid: string): Promise<string> {
        const url = `${API_BASE}${ADMIN_PATH}/${uuid}/logs`;
        const response = await apiClient.get<string>(url);
        return response.data;
    },

    /**
     * Actualiza la nota rápida del dispositivo
     */
    async updateNote(uuid: string, note: string) {
        const url = `${API_BASE}${ADMIN_PATH}/${uuid}/note`;
        return await apiClient.put(url, { note });
    },

    /**
     * Obtiene las opciones de los catálogos para el formulario
     */
    async getFormOptions(): Promise<FormOptions> {
        const url = `${API_BASE}/v1/catalogs/form-options`;
        const response = await apiClient.get<FormOptions>(url);
        return response.data;
    },

    /**
     * NUEVO: Obtiene el historial de métricas
     */
    async getDeviceHistory(uuid: string, startDate?: Date, endDate?: Date): Promise<DeviceHistory[]> {
        // Aseguramos que la URL sea correcta usando el path de devices
        let url = `${API_BASE}${DEVICES_PATH}/${uuid}/history`;

        // Agregar parámetros de fecha si se proporcionan
        const params = new URLSearchParams();
        if (startDate) {
            params.append('start_date', startDate.toISOString());
        }
        if (endDate) {
            params.append('end_date', endDate.toISOString());
        }
        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        const response = await apiClient.get<DeviceHistory[] | any>(url);

        // KrakenD puede envolver la respuesta, manejamos ambos casos
        const data = response.data;

        // Si ya es un array, lo retornamos directamente
        if (Array.isArray(data)) {
            return data;
        }

        // Si está envuelto en un objeto, intentamos extraer el array
        // Casos comunes: { data: [...] }, { history: [...] }, { collection: [...] }
        if (data && typeof data === 'object') {
            const possibleArrays = [(data as any).data, (data as any).history, (data as any).collection, (data as any).results];
            for (const arr of possibleArrays) {
                if (Array.isArray(arr)) {
                    return arr;
                }
            }
        }

        console.error('Unexpected response format:', data);
        return [];
    },

    /**
     * NUEVO: Ejecuta la provisión completa del dispositivo
     */
    async provisionDevice(uuid: string, data: ProvisionPayload): Promise<any> {
        const url = `${API_BASE}${ADMIN_PATH}/${uuid}/provision`;
        const response = await apiClient.post(url, data);
        return response.data;
    },

    /**
     * NUEVO: Elimina un dispositivo (BD + Balena)
     */
    async deleteDevice(uuid: string): Promise<any> {
        // Endpoint configurado en KrakenD: DELETE /v1/admin/{uuid}
        // Backend Real: DELETE /api/v1/admin/{uuid}
        const url = `${API_BASE}${ADMIN_PATH}/${uuid}`;
        const response = await apiClient.delete(url);
        return response.data;
    },

    /**
     * Envía una acción individual y retorna info, incluyendo task_id
     */
    async sendSingleAction(uuid: string, action: DeviceAction) {
        const url = `${API_BASE}${ADMIN_PATH}/${uuid}/${action}`;
        const response = await apiClient.post(url);
        return response.data;
    },

    /**
     * Obtiene el estado de una tarea async
     */
    async getTaskStatus(taskId: string) {
        const url = `${API_BASE}${ADMIN_PATH}/tasks/${taskId}`;
        const response = await apiClient.get(url);
        return response.data;
    }
};