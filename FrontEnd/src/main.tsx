import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import AuthInitializer from './features/auth/AuthInitializer';
import './assets/styles/index.css';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

root.render(
    <AuthInitializer>
        <React.StrictMode>
            <App />
        </React.StrictMode>
    </AuthInitializer>
);
