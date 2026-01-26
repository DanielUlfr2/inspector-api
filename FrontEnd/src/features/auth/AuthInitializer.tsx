import React, { useState, useEffect } from 'react';
import { checkSession, login } from './keycloakService';

interface AuthInitializerProps {
    children: React.ReactNode;
}

const AuthInitializer: React.FC<AuthInitializerProps> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

    useEffect(() => {
        const initAuth = async () => {
            // Permitir ruta de callback sin verificación previa
            if (window.location.pathname.startsWith('/auth/callback')) {
                setIsAuthenticated(true);
                return;
            }

            const hasSession = await checkSession();

            if (hasSession) {
                setIsAuthenticated(true);
            } else {
                login();
            }
        };

        initAuth();
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
                    <p>Verificando sesión...</p>
                    <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
                </div>
            </div>
        );
    }

    return <>{children}</>;
};

export default AuthInitializer;
