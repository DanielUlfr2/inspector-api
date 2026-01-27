import React, { useState, useEffect, useRef } from 'react';
import { initKeycloak } from './keycloakService';

interface AuthInitializerProps {
    children: React.ReactNode;
}

const AuthInitializer: React.FC<AuthInitializerProps> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
    const didInit = useRef(false);

    useEffect(() => {
        // Evitar doble inicialización en React.StrictMode
        if (didInit.current) return;
        didInit.current = true;

        initKeycloak((authenticated) => {
            setIsAuthenticated(authenticated);
        });
    }, []);

    if (isAuthenticated === null) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#121212', color: '#fff' }}>
                <div style={{ textAlign: 'center' }}>
                    <div className="spinner" style={{
                        margin: '0 auto 20px',
                        width: '40px',
                        height: '40px',
                        border: '4px solid rgba(255,255,255,0.3)',
                        borderRadius: '50%',
                        borderTop: '4px solid #fff',
                        animation: 'spin 1s linear infinite'
                    }}></div>
                    <p>Conectando con Keycloak...</p>
                    <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <div>No autenticado. Redirigiendo...</div>;
    }

    return <>{children}</>;
};

export default AuthInitializer;
