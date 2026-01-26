import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

const AuthCallback = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const processedCode = useRef<string | null>(null);

    useEffect(() => {
        const processCallback = async () => {
            // Extraer query params
            const searchParams = new URLSearchParams(location.search);
            let code = searchParams.get('code');
            let error = searchParams.get('error');

            // Si no está en query, buscar en hash
            if (!code && location.hash) {
                const hashParams = new URLSearchParams(location.hash.substring(1));
                code = hashParams.get('code');
                error = hashParams.get('error');
            }

            // Evitar procesar el mismo código dos veces (React StrictMode)
            if (code && processedCode.current === code) {
                console.log("Código ya procesado, ignorando duplicado.");
                return;
            }

            if (code) {
                processedCode.current = code;
            }

            if (error) {


                console.error("Error devuelto por Keycloak:", error);
                // Redirigir a login o mostrar error
                return;
            }

            if (!code) {
                console.error("No se encontró 'code' en la URL. URL completa:", window.location.href);
                console.log("Search Params:", searchParams.toString());
                return;
            }


            try {
                // Intercambiar código por cookies de sesión
                await axios.post(
                    `${import.meta.env.VITE_API_BASE_URL}/auth/callback`,
                    {
                        code,
                        redirect_uri: `${window.location.origin}/auth/callback`
                    },
                    { withCredentials: true } // Importante para recibir cookies
                );

                console.log("Autenticación exitosa, redirigiendo...");
                // Limpiar URL y redirigir
                navigate('/', { replace: true });

            } catch (err) {
                console.error("Error al procesar callback:", err);
                // Mostrar feedback al usuario o redirigir a login
            }
        };

        processCallback();
    }, [location, navigate]);

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            background: '#121212',
            color: '#fff'
        }}>
            <div>
                <h2>Autenticando...</h2>
                <p>Por favor espere mientras establecemos su sesión segura.</p>
                <div className="spinner" style={{
                    marginTop: '20px',
                    width: '40px',
                    height: '40px',
                    border: '4px solid rgba(255,255,255,0.3)',
                    borderRadius: '50%',
                    borderTop: '4px solid #fff',
                    animation: 'spin 1s linear infinite'
                }}></div>
                <style>{`
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `}</style>
            </div>
        </div>
    );
};

export default AuthCallback;
