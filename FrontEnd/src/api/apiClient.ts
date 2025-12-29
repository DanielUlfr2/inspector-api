import axios from 'axios';
import keycloak from '../features/auth/keycloakService';

const apiClient = axios.create({
    // Usamos la variable que apunta al Gateway (puerto 8081)
    baseURL: import.meta.env.VITE_API_BASE_URL,
});

// Interceptor Asíncrono: Asegura que el token sea válido antes de enviar
apiClient.interceptors.request.use(
    async (config) => {
        try {
            // updateToken(5) intenta refrescar el token si le quedan menos de 5 segundos de vida
            await keycloak.updateToken(5);

            if (keycloak.token) {
                config.headers.Authorization = `Bearer ${keycloak.token}`;
            }
        } catch (error) {
            console.error("No se pudo refrescar el token de Keycloak", error);
            // Si el refresco falla (ej: sesión cerrada), podrías forzar el logout
            // keycloak.logout(); 
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default apiClient;