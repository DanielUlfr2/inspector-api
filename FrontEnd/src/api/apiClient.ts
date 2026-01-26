import axios from 'axios';
import { login } from '../features/auth/keycloakService';

// Configuración para usar cookies (HttpOnly)
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    withCredentials: true, // Importante: permite enviar y recibir cookies
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor de respuesta para manejar errores de sesión (401)
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // Si recibimos un 401 (No autorizado) y no hemos re-intentado
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Intentamos refrescar el token (el backend usa la cookie REFRESH_TOKEN)
                // Usamos una instancia separada para evitar bucles infinitos
                await axios.post(
                    `${import.meta.env.VITE_API_BASE_URL}/auth/refresh`,
                    {},
                    { withCredentials: true }
                );

                // Si el refresh es exitoso, reintentamos la petición original
                // Las cookies se envían automáticamente
                return apiClient(originalRequest);
            } catch (refreshError) {
                console.error("Sesión expirada. Redirigiendo a login...", refreshError);
                // Si falla el refresh, forzamos logout en Keycloak
                login();
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default apiClient;