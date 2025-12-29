// src/features/devices/deviceService.ts
import apiClient from '../../api/apiClient';
import { Device, DeviceResponse } from '../../types/device';

export const deviceService = {
    async getDevices(): Promise<Device[]> {
        const response = await apiClient.get<DeviceResponse>('/v1/infodevices');
        // Filtramos los equipos que son "DEFAULT"
        return response.data.devices.filter(
            (device: Device) => device.uuidinspector !== 'DEFAULT'
        );
    }
};