// src/features/devices/deviceService.ts
import apiClient from '../../api/apiClient';
import { Device, DeviceResponse } from '../../types/device';
// IMPORTANTE: Importamos los nuevos tipos
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
        return await apiClient.post(url, { note });
    },

    /**
     * NUEVO: Obtiene las opciones de los catálogos para el formulario
     */
    async getFormOptions(): Promise<FormOptions> {
        // Asumiendo que la ruta en KrakenD para catálogos es /api/v1/catalogs/form-options
        const url = `${API_BASE}/v1/catalogs/form-options`;
        const response = await apiClient.get<FormOptions>(url);
        return response.data;
    },

    /**
     * NUEVO: Ejecuta la provisión completa del dispositivo
     */
    async provisionDevice(uuid: string, data: ProvisionPayload) {
        const url = `${API_BASE}${ADMIN_PATH}/${uuid}/provision`;
        const response = await apiClient.post(url, data);
        return response.data;
    }
};