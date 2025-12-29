// src/features/devices/deviceService.ts
import apiClient from '../../api/apiClient';
import { Device, DeviceResponse } from '../../types/device';

// Obtenemos las piezas del "junte"
const API_BASE = import.meta.env.VITE_API_BASE_URL;
const DEVICES_PATH = import.meta.env.VITE_API_DEVICES_INFO;
const ADMIN_PATH = import.meta.env.VITE_API_ADMIN_PATH;

// Construimos la URL completa para el listado
const FULL_DEVICES_URL = `${API_BASE}${DEVICES_PATH}`;
export type DeviceAction = 'reboot' | 'restart' | 'shutdown';

export const deviceService = {
    /**
     * Obtiene la lista completa de dispositivos
     */
    async getDevices(): Promise<Device[]> {
        const response = await apiClient.get<DeviceResponse>(FULL_DEVICES_URL);

        return response.data.devices.filter(
            (device: Device) => device.uuidinspector !== 'DEFAULT'
        );
    },

    /**
     * NUEVO: Obtiene el detalle técnico de un solo dispositivo por UUID
     */
    async getDeviceByUuid(uuid: string): Promise<Device> {
        const url = `${API_BASE}${DEVICES_PATH}/${uuid}`;
        const response = await apiClient.get<Device>(url);
        return response.data;
    },

    /**
     * Envía una acción administrativa individual
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

    async getDeviceLogs(uuid: string): Promise<string> {
        const url = `${API_BASE}${ADMIN_PATH}/${uuid}/logs`;
        const response = await apiClient.get<string>(url);
        return response.data;
    },

    async updateNote(uuid: string, note: string) {
        const url = `${API_BASE}${ADMIN_PATH}/${uuid}/note`;
        return await apiClient.post(url, { note });
    }
};