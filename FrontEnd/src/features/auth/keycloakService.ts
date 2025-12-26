import Keycloak from 'keycloak-js';

const keycloakConfig = {
    url: import.meta.env.VITE_KEYCLOAK_URL,
    realm: import.meta.env.VITE_KEYCLOAK_REALM,
    clientId: import.meta.env.VITE_KEYCLOAK_CLIENT,
};

const keycloak = new Keycloak(keycloakConfig);

/**
 * Inicializa Keycloak y solo arranca la App si el login es exitoso.
 */
export const initKeycloak = (onAuthenticated: () => void, onError?: (err: any) => void) => {
    keycloak
        .init({
            onLoad: 'login-required', // Redirige al login de Keycloak si no hay sesión
            checkLoginIframe: false,
        })
        .then((authenticated) => {
            if (authenticated) {
                onAuthenticated();
            } else {
                window.location.reload();
            }
        })
        .catch((err) => {
            console.error("Fallo al conectar con Keycloak:", err);
            if (onError) onError(err);
        });
};

export default keycloak;
