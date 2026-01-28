import Keycloak from 'keycloak-js';

const keycloakConfig = {
    url: import.meta.env.VITE_KEYCLOAK_URL,
    realm: import.meta.env.VITE_KEYCLOAK_REALM,
    clientId: import.meta.env.VITE_KEYCLOAK_CLIENT,
};

const keycloak = new Keycloak(keycloakConfig);

/**
 * Establece el token en una cookie accesible (NO HttpOnly) para que el backend pueda leerla.
 * @param token Token JWT
 */
const setSessionCookie = (token: string | undefined) => {
    if (token) {
        // Establecemos la cookie 'SESSION_ID' con el token.
        // path=/ asegura que esté disponible para todo el dominio.
        // samesite=Lax permite navegación segura.
        // NO usamos HttpOnly porque js debe escribirla.
        document.cookie = `SESSION_ID=${token}; path=/; samesite=Lax; secure`;
    }
};

/**
 * Inicializa Keycloak y configura los listeners de eventos.
 */
export const initKeycloak = (onAuthenticatedCallback: (authenticated: boolean) => void) => {
    keycloak.init({
        onLoad: 'login-required',
        pkceMethod: 'S256',
        checkLoginIframe: false,
    })
        .then((authenticated) => {
            if (authenticated) {
                setSessionCookie(keycloak.token);

                // Configurar actualización automática del token
                setInterval(() => {
                    keycloak.updateToken(70).then((refreshed) => {
                        if (refreshed) {
                            console.log('Token refreshed, updating cookie');
                            setSessionCookie(keycloak.token);
                        }
                    }).catch(() => {
                        console.error('Failed to refresh token');
                        keycloak.logout();
                    });
                }, 60000); // Chequear cada minuto
            }
            onAuthenticatedCallback(authenticated);
        })
        .catch((error) => {
            console.error("Keycloak init failed", error);
            onAuthenticatedCallback(false);
        });
};

export const logout = () => {
    // Limpiamos la cookie al salir
    document.cookie = "SESSION_ID=; path=/; max-age=0; samesite=Lax";
    keycloak.logout({ redirectUri: window.location.origin });
};

/**
 * Helper para obtener información del usuario desde el token parseado
 */
export const getUserProfile = () => {
    if (keycloak.tokenParsed) {
        return {
            username: keycloak.tokenParsed.preferred_username,
            email: keycloak.tokenParsed.email,
            name: keycloak.tokenParsed.name,
            roles: keycloak.tokenParsed.realm_access?.roles || [],
            avatar: keycloak.tokenParsed.avatar, // Puede ser string o array según mapper
        };
    }
    return null;
};

export const getToken = () => keycloak.token;

export default keycloak;
