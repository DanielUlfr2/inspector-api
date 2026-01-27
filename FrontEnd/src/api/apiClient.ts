import axios from 'axios';
import { logout } from '../features/auth/keycloakService';

// Configuración para usar cookies
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    withCredentials: true, // Importante: permite enviar cookies (session_id)
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor para manejar 401s (Token expirado que no pudo refrescarse automáticamente)
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            console.warn("Sesión no válida o expirada (401).");
            // Opcional: Podríamos intentar keycloak.updateToken() aquí si quisiéramos ser robustos,
            // pero el intervalo en keycloakService ya debería encargarse.
            // logout(); // Descomentar si queremos forzar logout inmediato
        }
        return Promise.reject(error);
    }
);

export default apiClient;
