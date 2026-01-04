import apiClient from '../../api/apiClient';

const API_BASE = import.meta.env.VITE_API_BASE_URL;
const CONFIG_PATH = '/v1/configuration';

export interface Variable {
    name: string;
    value: string;
}

export const variableService = {
    async setFleetVariable(fleetSlug: string, variable: Variable) {
        // Encodificación del slug para manejar el '/'
        const url = `${API_BASE}${CONFIG_PATH}/fleet/${encodeURIComponent(fleetSlug)}/variable`;
        return await apiClient.post(url, variable);
    },

    async deleteFleetVariable(fleetSlug: string, key: string) {
        const url = `${API_BASE}${CONFIG_PATH}/fleet/${encodeURIComponent(fleetSlug)}/variable/${key}`;
        return await apiClient.delete(url);
    },

    async setDeviceVariable(uuid: string, variable: Variable) {
        const url = `${API_BASE}${CONFIG_PATH}/device/${uuid}/variable`;
        return await apiClient.post(url, variable);
    },

    async deleteDeviceVariable(uuid: string, key: string) {
        const url = `${API_BASE}${CONFIG_PATH}/device/${uuid}/variable/${key}`;
        return await apiClient.delete(url);
    },

    async getDeviceVariables(uuid: string) {
        const url = `${API_BASE}${CONFIG_PATH}/device/${uuid}/variables`;
        return await apiClient.get(url);
    }
};