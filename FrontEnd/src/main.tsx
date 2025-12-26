import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { initKeycloak } from './features/auth/keycloakService';
import './assets/styles/index.css'; // Crea este archivo vacío por ahora si no existe

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

// 🛡️ Solo renderizamos la App si el usuario está autenticado
initKeycloak(() => {
    root.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    );
});