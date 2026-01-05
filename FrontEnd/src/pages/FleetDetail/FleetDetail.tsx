import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { RefreshCw, Monitor, Wifi, WifiOff, AlertCircle, AlertTriangle, ExternalLink, Search } from 'lucide-react';
import { deviceService } from '../../features/devices/deviceService';
import { fleetService } from '../../features/fleets/fleetService';
import { Device } from '../../types/device';
import { Fleet } from '../../types/fleet';
import DeviceActionBar from '../../components/DeviceControl/DeviceActionBar';
import FleetActionsMenu from '../../components/Fleets/FleetActionsMenu';
import { Link } from 'react-router-dom';
import styles from './FleetDetail.module.css';

const FleetDetail: React.FC = () => {
    const { fleetId } = useParams<{ fleetId: string }>();
    const [devices, setDevices] = useState<Device[]>([]);
    const [fleetData, setFleetData] = useState<Fleet | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedUuids, setSelectedUuids] = useState<string[]>([]);
    const [searchTerm, setSearchTerm] = useState('');

    // Filtros por columna
    const [columnFilters, setColumnFilters] = useState({
        status: '',
        name: '',
        note: ''
    });

    const fetchData = async () => {
        try {
            setLoading(true);

            // Fetch fleet data
            const fleets = await fleetService.getAllFleets();
            const currentFleet = fleets.find(f => f.id === fleetId);
            setFleetData(currentFleet || null);

            // Fetch devices
            const data = await deviceService.getDevices();
            const filtered = data.filter(d => d.stridinspectorfleet === fleetId);
            setDevices(filtered);
            setSelectedUuids([]);
        } catch (error) {
            console.error("Error al cargar datos de la flota:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [fleetId]);

    // Configuración visual de los estados
    const getStatusConfig = (statusRaw?: string) => {
        const status = statusRaw?.toLowerCase() || 'unknown';
        switch (status) {
            case 'operational':
                return { label: 'Operational', className: styles.online, icon: <Wifi size={14} /> };
            case 'disconnected':
                return { label: 'Disconnected', className: styles.offline, icon: <WifiOff size={14} /> };
            case 'reduced-functionality':
                return { label: 'Reduced', className: styles.reduced, icon: <AlertTriangle size={14} /> };
            default:
                return { label: status, className: styles.unknown, icon: <AlertCircle size={14} /> };
        }
    };

    // Calcular estadísticas de la flota
    const fleetStats = useMemo(() => {
        const stats = {
            total: devices.length,
            operativo: 0,
            reducido: 0,
            desconectado: 0,
            libre: 0
        };

        devices.forEach(device => {
            const status = device.jsonbobservaciones.overall_status_raw?.toLowerCase();
            switch (status) {
                case 'operational':
                    stats.operativo++;
                    break;
                case 'reduced-functionality':
                    stats.reducido++;
                    break;
                case 'disconnected':
                    stats.desconectado++;
                    break;
                default:
                    stats.libre++;
            }
        });

        return stats;
    }, [devices]);

    // Lógica de Filtrado
    const filteredDevices = useMemo(() => {
        return devices.filter(device => {
            const rawStatus = device.jsonbobservaciones.overall_status_raw?.toLowerCase() || '';

            const globalTerm = searchTerm.toLowerCase();
            const matchesGlobal =
                device.strinspectorname.toLowerCase().includes(globalTerm) ||
                device.strnote.toLowerCase().includes(globalTerm) ||
                device.uuidinspector.toLowerCase().includes(globalTerm);

            const matchesStatus = columnFilters.status === '' || rawStatus === columnFilters.status;
            const matchesName = device.strinspectorname.toLowerCase().includes(columnFilters.name.toLowerCase()) ||
                device.uuidinspector.toLowerCase().includes(columnFilters.name.toLowerCase());
            const matchesNote = device.strnote.toLowerCase().includes(columnFilters.note.toLowerCase());

            return matchesGlobal && matchesStatus && matchesName && matchesNote;
        });
    }, [devices, searchTerm, columnFilters]);

    // Handlers de selección
    const handleSelectAll = () => {
        if (selectedUuids.length === filteredDevices.length && filteredDevices.length > 0) {
            setSelectedUuids([]);
        } else {
            setSelectedUuids(filteredDevices.map(d => d.uuidinspector));
        }
    };

    const handleSelectRow = (uuid: string) => {
        setSelectedUuids(prev =>
            prev.includes(uuid) ? prev.filter(id => id !== uuid) : [...prev, uuid]
        );
    };

    if (loading) return <div className={styles.loading}><RefreshCw className={styles.spin} /> Cargando dispositivos...</div>;

    return (
        <div className={styles.container}>
            {/* Fleet Info Header */}
            <div className={styles.fleetHeader}>
                <div className={styles.fleetInfo}>
                    <div className={styles.fleetIcon}>🚢</div>
                    <div className={styles.fleetDetails}>
                        <h1 className={styles.fleetName}>{fleetId}</h1>
                        <span className={styles.fleetTag}>{fleetData?.slug || 'Cargando...'}</span>
                    </div>
                </div>

                <div className={styles.fleetStats}>
                    <div className={styles.deviceCount}>
                        <Monitor size={16} />
                        <span>Devices: {fleetStats.total}</span>
                    </div>

                    {/* Progress Bar */}
                    <div className={styles.progressBar}>
                        {fleetStats.operativo > 0 && (
                            <div
                                className={styles.segmentOperativo}
                                style={{ width: `${(fleetStats.operativo / fleetStats.total) * 100}%` }}
                            />
                        )}
                        {fleetStats.reducido > 0 && (
                            <div
                                className={styles.segmentReducido}
                                style={{ width: `${(fleetStats.reducido / fleetStats.total) * 100}%` }}
                            />
                        )}
                        {fleetStats.desconectado > 0 && (
                            <div
                                className={styles.segmentDesconectado}
                                style={{ width: `${(fleetStats.desconectado / fleetStats.total) * 100}%` }}
                            />
                        )}
                        {fleetStats.libre > 0 && (
                            <div
                                className={styles.segmentLibre}
                                style={{ width: `${(fleetStats.libre / fleetStats.total) * 100}%` }}
                            />
                        )}
                    </div>

                    {/* Legend */}
                    <div className={styles.legend}>
                        <div className={styles.legendItem}>
                            <span className={`${styles.dot} ${styles.dotLibre}`}></span>
                            <span>Libre: {fleetStats.libre}</span>
                        </div>
                        <div className={styles.legendItem}>
                            <span className={`${styles.dot} ${styles.dotOperativo}`}></span>
                            <span>Operativo: {fleetStats.operativo}</span>
                        </div>
                        <div className={styles.legendItem}>
                            <span className={`${styles.dot} ${styles.dotReducido}`}></span>
                            <span>Reducido: {fleetStats.reducido}</span>
                        </div>
                        <div className={styles.legendItem}>
                            <span className={`${styles.dot} ${styles.dotDesconectado}`}></span>
                            <span>Desconectado: {fleetStats.desconectado}</span>
                        </div>
                    </div>
                </div>

                <FleetActionsMenu
                    fleetId={fleetId!}
                    onUpdate={fetchData}
                />
            </div>

            {/* Table Header */}
            <header className={styles.tableHeader}>
                <div>
                    <h2>Dispositivos de la Flota</h2>
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

                    <button onClick={fetchData} className={styles.refreshBtn}>
                        <RefreshCw size={18} className={loading ? styles.spin : ''} />
                    </button>
                </div>
            </header>

            <DeviceActionBar
                selectedUuids={selectedUuids}
                onActionComplete={fetchData}
            />

            <div className={styles.tableContainer}>
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th className={styles.checkboxCell}>
                                <input
                                    type="checkbox"
                                    onChange={handleSelectAll}
                                    checked={filteredDevices.length > 0 && selectedUuids.length === filteredDevices.length}
                                />
                            </th>
                            <th>Estado</th>
                            <th>Nombre / UUID</th>
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
                                    <option value="reduced-functionality">Reduced</option>
                                </select>
                            </th>
                            <th><input placeholder="Filtrar..." value={columnFilters.name} onChange={(e) => setColumnFilters({ ...columnFilters, name: e.target.value })} className={styles.columnInput} /></th>
                            <th><input placeholder="Filtrar..." value={columnFilters.note} onChange={(e) => setColumnFilters({ ...columnFilters, note: e.target.value })} className={styles.columnInput} /></th>
                            <th colSpan={3}></th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan={7} className={styles.empty}>Sincronizando flota...</td></tr>
                        ) : filteredDevices.length === 0 ? (
                            <tr><td colSpan={7} className={styles.empty}>No hay resultados para los filtros aplicados.</td></tr>
                        ) : (
                            filteredDevices.map((device) => {
                                const statusCfg = getStatusConfig(device.jsonbobservaciones.overall_status_raw);
                                const isSelected = selectedUuids.includes(device.uuidinspector);
                                return (
                                    <tr key={device.uuidinspector} className={isSelected ? styles.rowSelected : ''}>
                                        <td className={styles.checkboxCell}>
                                            <input
                                                type="checkbox"
                                                checked={isSelected}
                                                onChange={() => handleSelectRow(device.uuidinspector)}
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

export default FleetDetail;