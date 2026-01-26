// Versión modificada para Cookie-based Auth
import Keycloak from 'keycloak-js';
import axios from 'axios';

const keycloakConfig = {
    url: import.meta.env.VITE_KEYCLOAK_URL,
    realm: import.meta.env.VITE_KEYCLOAK_REALM,
    clientId: import.meta.env.VITE_KEYCLOAK_CLIENT,
};

const keycloak = new Keycloak(keycloakConfig);

/**
 * Verifica si existe una sesión válida en el backend (vía cookie)
 */
export const checkSession = async (): Promise<boolean> => {
    try {
        const response = await axios.get(
            `${import.meta.env.VITE_API_BASE_URL}/auth/session`,
            { withCredentials: true }
        );
        return response.data.authenticated === true;
    } catch (error) {
        console.error("Error verificando sesión:", error);
        return false;
    }
};

/**
 * Inicia el proceso de login redirigiendo a Keycloak
 */
/**
 * Inicia el proceso de login redirigiendo a Keycloak manualmente
 * Evitamos usar keycloak.init() para tener control total de la URL y parámetros
 */
export const login = () => {
    const redirectUri = encodeURIComponent(`${window.location.origin}/auth/callback`);
    const clientId = import.meta.env.VITE_KEYCLOAK_CLIENT;
    const realm = import.meta.env.VITE_KEYCLOAK_REALM;
    const keycloakUrl = import.meta.env.VITE_KEYCLOAK_URL;

    // Construimos la URL estándar de OAuth2/OpenID Connect
    const authUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=openid profile email`;

    window.location.href = authUrl;
};


/**
 * Cierra sesión: primero en backend (limpia cookies), luego en Keycloak
 */
export const logout = async () => {
    try {
        // 1. Limpiar cookies en backend
        await axios.post(
            `${import.meta.env.VITE_API_BASE_URL}/auth/logout`,
            {},
            { withCredentials: true }
        );
    } catch (error) {
        console.error("Error en logout de backend:", error);
    } finally {
        // 2. Redirigir a Keycloak para logout completo
        // Se reinicia Keycloak solo para usar su método logout
        if (!keycloak.authenticated) {
            const redirectUri = window.location.origin;
            window.location.href = `${keycloakConfig.url}/realms/${keycloakConfig.realm}/protocol/openid-connect/logout?client_id=${keycloakConfig.clientId}&post_logout_redirect_uri=${encodeURIComponent(redirectUri)}`;
        } else {
            keycloak.logout({ redirectUri: window.location.origin });
        }
    }
};


export default keycloak;
