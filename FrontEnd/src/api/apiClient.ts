import axios from 'axios';
import keycloak from '../features/auth/keycloakService';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});

// Interceptor: Antes de cada petición, pega el token actual
apiClient.interceptors.request.use(
    (config) => {
        if (keycloak.token) {
            config.headers.Authorization = `Bearer ${keycloak.token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default apiClient;