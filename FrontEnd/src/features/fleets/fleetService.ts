import apiClient from '../../api/apiClient';
import { Fleet } from '../../types/fleet';

export interface CreateFleetPayload {
    name: string;
    device_type_id: number;
    organization?: string | null;
}

export interface RenameFleetPayload {
    new_name: string;
}

export interface DeviceType {
    iddevicetype: number;
    strdevicenametype: string;
    strdeviceslug: string;
}

export const fleetService = {
    /**
     * Obtiene la lista de tipos de dispositivos soportados
     * Endpoint: GET /v1/fleets/supported-devices
     */
    async getSupportedDevices(): Promise<DeviceType[]> {
        const response = await apiClient.get<DeviceType[] | { device_types: DeviceType[] }>('/v1/fleets/supported-devices');
        // Handle both direct array and wrapped response
        if (Array.isArray(response.data)) {
            return response.data;
        }
        return (response.data as any).device_types || (response.data as any).supported_devices || [];
    },
    /**
     * Obtiene la lista completa de flotas con sus estadísticas
     * Endpoint: GET /v1/fleets
     */
    async getAllFleets(): Promise<Fleet[]> {
        const response = await apiClient.get<{ fleets: Fleet[] }>('/v1/fleets');
        // KrakenD envuelve la respuesta en { fleets: [...] } debido al mapping
        return response.data.fleets || [];
    },

    /**
     * Crea una nueva flota
     * Endpoint: POST /v1/fleets
     */
    async createFleet(payload: CreateFleetPayload): Promise<Fleet> {
        const response = await apiClient.post<Fleet>('/v1/fleets', payload);
        return response.data;
    },

    /**
     * Renombra una flota existente
     * Endpoint: PUT /v1/fleets/{slug}/rename
     */
    async renameFleet(slug: string, payload: RenameFleetPayload): Promise<Fleet> {
        const encodedSlug = encodeURIComponent(slug);
        const response = await apiClient.put<Fleet>(`/v1/fleets/${encodedSlug}/rename`, payload);
        return response.data;
    },

    /**
     * Elimina una flota (solo si está vacía)
     * Endpoint: DELETE /v1/fleets/{slug}
     */
    async deleteFleet(slug: string): Promise<void> {
        const encodedSlug = encodeURIComponent(slug);
        await apiClient.delete(`/v1/fleets/${encodedSlug}`);
    }
};