// src/pages/Devices/Devices.tsx
import { useState, useEffect, useMemo } from 'react';
import { Search, Monitor, Wifi, WifiOff, ExternalLink, RefreshCw } from 'lucide-react';
import { deviceService } from '../../features/devices/deviceService';
import { Device } from '../../types/device';
import styles from './Devices.module.css';

const Devices = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    const fetchDevices = async () => {
        setLoading(true);
        try {
            const data = await deviceService.getDevices();
            setDevices(data);
        } catch (error) {
            console.error("Error cargando dispositivos:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchDevices(); }, []);

    // Lógica de filtrado reactivo
    const filteredDevices = useMemo(() => {
        const term = searchTerm.toLowerCase();
        return devices.filter(d =>
            d.strinspectorname.toLowerCase().includes(term) ||
            d.strnote.toLowerCase().includes(term) ||
            d.stridinspectorfleet.toLowerCase().includes(term) ||
            d.uuidinspector.toLowerCase().includes(term)
        );
    }, [devices, searchTerm]);

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <div>
                    <h1>Gestión de Dispositivos</h1>
                    <p className={styles.subtitle}>{filteredDevices.length} equipos encontrados</p>
                </div>
                <div className={styles.actions}>
                    <div className={styles.searchWrapper}>
                        <Search size={18} className={styles.searchIcon} />
                        <input
                            type="text"
                            placeholder="Buscar por nombre, flota, nota o UUID..."
                            className={styles.searchInput}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button onClick={fetchDevices} className={styles.refreshBtn}>
                        <RefreshCw size={18} className={loading ? styles.spin : ''} />
                    </button>
                </div>
            </header>

            <div className={styles.tableContainer}>
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th>Estado</th>
                            <th>Nombre del Inspector</th>
                            <th>Flota</th>
                            <th>Nota (Serial)</th>
                            <th>IP Address</th>
                            <th>Versión OS</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan={7} className={styles.empty}>Cargando flota...</td></tr>
                        ) : filteredDevices.map((device) => (
                            <tr key={device.uuidinspector}>
                                <td>
                                    <div className={`${styles.statusBadge} ${device.boolonline ? styles.online : styles.offline}`}>
                                        {device.boolonline ? <Wifi size={14} /> : <WifiOff size={14} />}
                                        {device.boolonline ? 'Online' : 'Offline'}
                                    </div>
                                </td>
                                <td>
                                    <div className={styles.nameCell}>
                                        <Monitor size={16} />
                                        <span>{device.strinspectorname}</span>
                                    </div>
                                    <small className={styles.uuid}>{device.uuidinspector}</small>
                                </td>
                                <td><span className={styles.fleetBadge}>{device.stridinspectorfleet}</span></td>
                                <td><code>{device.strnote}</code></td>
                                <td>{device.stripaddress.split(' ')[0]}</td>
                                <td>{device.strosversion}</td>
                                <td>
                                    {device.jsonbobservaciones.dashboard_url && (
                                        <a
                                            href={device.jsonbobservaciones.dashboard_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className={styles.actionLink}
                                        >
                                            <ExternalLink size={16} />
                                        </a>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Devices;