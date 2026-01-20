import { useState, useEffect, useMemo } from 'react';
import {
    Search, Monitor, Wifi, WifiOff, ExternalLink, RefreshCw, AlertCircle, AlertTriangle
} from 'lucide-react';

// Servicios y Tipos
import { deviceService } from '../../features/devices/deviceService';
import { Device } from '../../types/device';
import { getDeviceRealStatus } from '../../utils/deviceStatus';

// Componentes de Feature
import DeviceActionBar from '../../components/DeviceControl/DeviceActionBar';
import ExportCSVButton from '../../components/ExportCSV/ExportCSVButton';

// Estilos
import styles from './Devices.module.css';
import { Link } from 'react-router-dom';

const Devices = () => {
    const [devices, setDevices] = useState<Device[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedDevices, setSelectedDevices] = useState<Device[]>([]);

    // Filtros por columna
    const [columnFilters, setColumnFilters] = useState({
        status: '', // operational | disconnected | reduced-functionality
        name: '',
        fleet: '',
        note: ''
    });

    const fetchDevices = async () => {
        setLoading(true);
        try {
            const data = await deviceService.getDevices();
            setDevices(data);
            setSelectedDevices([]);
        } catch (error) {
            console.error("Error cargando dispositivos:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchDevices(); }, []);

    // Configuración visual de los estados con prioridad de "Libre"
    const getStatusConfig = (device: Device) => {
        const realStatus = getDeviceRealStatus(device);

        switch (realStatus) {
            case 'operativo':
                return { label: 'Operational', className: styles.online, icon: <Wifi size={14} />, value: 'operational' };
            case 'desconectado':
                return { label: 'Disconnected', className: styles.offline, icon: <WifiOff size={14} />, value: 'disconnected' };
            case 'reducido':
                return { label: 'Reduced', className: styles.reduced, icon: <AlertTriangle size={14} />, value: 'reduced' };
            case 'libre':
                return { label: 'Libre', className: styles.libre, icon: <AlertCircle size={14} />, value: 'libre' };
            default:
                return { label: 'Unknown', className: styles.unknown, icon: <AlertCircle size={14} />, value: 'unknown' };
        }
    };

    // Lógica de Filtrado (Global + Columnas con estados específicos)
    const filteredDevices = useMemo(() => {
        return devices.filter(device => {
            const realStatus = getDeviceRealStatus(device);
            const statusValue = realStatus === 'operativo' ? 'operational' :
                realStatus === 'desconectado' ? 'disconnected' :
                    realStatus === 'reducido' ? 'reduced' : 'libre';

            // 1. Filtro Global (Search bar)
            const globalTerm = searchTerm.toLowerCase();
            const matchesGlobal =
                device.strinspectorname.toLowerCase().includes(globalTerm) ||
                device.strnote.toLowerCase().includes(globalTerm) ||
                device.stridinspectorfleet.toLowerCase().includes(globalTerm) ||
                device.uuidinspector.toLowerCase().includes(globalTerm);

            // 2. Filtros Específicos por Columna
            const matchesStatus = columnFilters.status === '' || statusValue === columnFilters.status;
            const matchesName = device.strinspectorname.toLowerCase().includes(columnFilters.name.toLowerCase()) ||
                device.uuidinspector.toLowerCase().includes(columnFilters.name.toLowerCase());
            const matchesFleet = device.stridinspectorfleet.toLowerCase().includes(columnFilters.fleet.toLowerCase());
            const matchesNote = device.strnote.toLowerCase().includes(columnFilters.note.toLowerCase());

            return matchesGlobal && matchesStatus && matchesName && matchesFleet && matchesNote;
        });
    }, [devices, searchTerm, columnFilters]);

    // Handlers de selección
    const handleSelectAll = () => {
        if (selectedDevices.length === filteredDevices.length && filteredDevices.length > 0) {
            setSelectedDevices([]);
        } else {
            setSelectedDevices(filteredDevices);
        }
    };

    const handleSelectRow = (device: Device) => {
        setSelectedDevices(prev =>
            prev.some(d => d.uuidinspector === device.uuidinspector)
                ? prev.filter(d => d.uuidinspector !== device.uuidinspector)
                : [...prev, device]
        );
    };

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <div>
                    <h1>Gestión de Dispositivos</h1>
                    <p className={styles.subtitle}>{filteredDevices.length} equipos en la vista actual</p>
                </div>
                <div className={styles.actions}>
                    <div className={styles.searchWrapper}>
                        <Search size={18} className={styles.searchIcon} />
                        <input
                            type="text"
                            placeholder="Búsqueda global..."
                            className={styles.searchInput}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <ExportCSVButton data={filteredDevices} />

                    <button onClick={fetchDevices} className={styles.refreshBtn}>
                        <RefreshCw size={18} className={loading ? styles.spin : ''} />
                    </button>
                </div>
            </header>

            <DeviceActionBar
                selectedDevices={selectedDevices}
                onActionComplete={() => setSelectedDevices([])}
            />

            <div className={styles.tableContainer}>
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th className={styles.checkboxCell}>
                                <input
                                    type="checkbox"
                                    onChange={handleSelectAll}
                                    checked={filteredDevices.length > 0 && selectedDevices.length === filteredDevices.length}
                                />
                            </th>
                            <th>Estado</th>
                            <th>Nombre / UUID</th>
                            <th>Flota</th>
                            <th>Nota (Serial)</th>
                            <th>IP Address</th>
                            <th>Versión OS</th>
                            <th>Link</th>
                        </tr>
                        {/* Fila de Filtros */}
                        <tr className={styles.filterRow}>
                            <th></th>
                            <th>
                                <select
                                    value={columnFilters.status}
                                    onChange={(e) => setColumnFilters({ ...columnFilters, status: e.target.value })}
                                    className={styles.columnSelect}
                                >
                                    <option value="">Todos</option>
                                    <option value="operational">Operational</option>
                                    <option value="disconnected">Disconnected</option>
                                    <option value="reduced">Reduced</option>
                                    <option value="libre">Libre</option>
                                </select>
                            </th>
                            <th><input placeholder="Filtrar..." value={columnFilters.name} onChange={(e) => setColumnFilters({ ...columnFilters, name: e.target.value })} className={styles.columnInput} /></th>
                            <th><input placeholder="Filtrar..." value={columnFilters.fleet} onChange={(e) => setColumnFilters({ ...columnFilters, fleet: e.target.value })} className={styles.columnInput} /></th>
                            <th><input placeholder="Filtrar..." value={columnFilters.note} onChange={(e) => setColumnFilters({ ...columnFilters, note: e.target.value })} className={styles.columnInput} /></th>
                            <th colSpan={3}></th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan={8} className={styles.empty}>Sincronizando flota...</td></tr>
                        ) : filteredDevices.length === 0 ? (
                            <tr><td colSpan={8} className={styles.empty}>No hay resultados para los filtros aplicados.</td></tr>
                        ) : (
                            filteredDevices.map((device) => {
                                const statusCfg = getStatusConfig(device);
                                const isSelected = selectedDevices.some(d => d.uuidinspector === device.uuidinspector);
                                return (
                                    <tr key={device.uuidinspector} className={isSelected ? styles.rowSelected : ''}>
                                        <td className={styles.checkboxCell}>
                                            <input
                                                type="checkbox"
                                                checked={isSelected}
                                                onChange={() => handleSelectRow(device)}
                                            />
                                        </td>
                                        <td>
                                            <div className={`${styles.statusBadge} ${statusCfg.className}`}>
                                                {statusCfg.icon}
                                                {statusCfg.label}
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
                                            <Link
                                                to={`/devices/${device.uuidinspector}`}
                                                className={styles.actionLink}
                                                title="Ver detalles técnicos e inventario"
                                            >
                                                <ExternalLink size={16} />
                                            </Link>
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Devices;