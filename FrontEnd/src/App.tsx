import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout/MainLayout';
import Settings from './pages/Settings/Settings';
import DashboardPage from './pages/Dashboard/Dashboard';

// Importación de Páginas (Features)
// Nota: Por ahora crearemos componentes simples para que no te dé error
// DashboardPage se importa desde ./pages/Dashboard/Dashboard

const DevicesPage = () => (
    <div style={{
        background: 'rgba(255,255,255,0.8)',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 24px rgba(0,0,0,0.06)'
    }}>
        <h1 style={{ margin: '0 0 8px 0', fontSize: '2rem', fontWeight: '700', color: '#0f172a' }}>
            Dispositivos
        </h1>
        <p style={{ margin: 0, color: '#64748b' }}>Listado de dispositivos conectados</p>
    </div>
);

const HistoryPage = () => (
    <div style={{
        background: 'rgba(255,255,255,0.8)',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 24px rgba(0,0,0,0.06)'
    }}>
        <h1 style={{ margin: '0 0 8px 0', fontSize: '2rem', fontWeight: '700', color: '#0f172a' }}>
            Historial
        </h1>
        <p style={{ margin: 0, color: '#64748b' }}>Estadísticas y registros históricos</p>
    </div>
);

function App() {
    return (
        <Router>
            <Routes>
                {/* Envolvemos las rutas protegidas en un Layout común */}
                <Route path="/" element={<MainLayout />}>
                    {/* Al entrar a "/", redirigimos automáticamente al Dashboard */}
                    <Route index element={<Navigate to="/dashboard" replace />} />

                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="devices" element={<DevicesPage />} />
                    <Route path="history" element={<HistoryPage />} />
                    <Route path="settings" element={<Settings />} />

                    {/* Ruta para manejar errores 404 */}
                    <Route path="*" element={<div>404 - Página no encontrada</div>} />
                </Route>
            </Routes>
        </Router>
    );
}

export default App;