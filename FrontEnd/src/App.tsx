import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout/MainLayout';
import Settings from './pages/Settings/Settings';
import DashboardPage from './pages/Dashboard/Dashboard';
import DevicesPage from './pages/Devices/Devices';
import DeviceDetail from './pages/DeviceDetail/DeviceDetail';
import Fleets from './pages/Fleets/Fleets';
import FleetDetail from './pages/FleetDetail/FleetDetail';
import NotFound from './pages/NotFound/NotFound';


// Importación de Páginas (Features)
// Nota: Por ahora crearemos componentes simples para que no te dé error
// DashboardPage se importa desde ./pages/Dashboard/Dashboard


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
                    <Route path="settings" element={<Settings />} />
                    <Route path="/devices/:uuid" element={<DeviceDetail />} />
                    <Route path="fleets" element={<Fleets />} />
                    <Route path="fleets/:fleetId" element={<FleetDetail />} />

                </Route>

                {/* Ruta 404 fuera del Layout principal (sin sidebar) */}
                <Route path="*" element={<NotFound />} />
            </Routes>
        </Router>
    );

}

export default App;