import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { RefreshCw, Monitor, Wifi, WifiOff, AlertCircle, AlertTriangle, ExternalLink, Search, ArrowLeft, TrendingUp } from 'lucide-react';
import { deviceService } from '../../features/devices/deviceService';
import { fleetService } from '../../features/fleets/fleetService';
import { variableService, Variable } from '../../features/devices/variableService';
import { Device } from '../../types/device';
import { Fleet } from '../../types/fleet';
import { getDeviceRealStatus } from '../../utils/deviceStatus';
import DeviceActionBar from '../../components/DeviceControl/DeviceActionBar';
import FleetActionsMenu from '../../components/Fleets/FleetActionsMenu';
import VariablesModal from '../../components/Variables/VariablesModal';
import { FleetStatsModal } from '../../components/Fleets/FleetStatsModal';
import { Link, useNavigate } from 'react-router-dom';
import FlotasIcon from '../../assets/icons/Flotas.png';
import styles from './FleetDetail.module.css';

const FleetDetail: React.FC = () => {
    const { fleetId } = useParams<{ fleetId: string }>();
    const navigate = useNavigate();
    const [devices, setDevices] = useState<Device[]>([]);
    const [fleetData, setFleetData] = useState<Fleet | null>(null);
    const [loading, setLoading] = useState(true);
    const [selectedDevices, setSelectedDevices] = useState<Device[]>([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [showVariablesModal, setShowVariablesModal] = useState(false);
    const [fleetVariables, setFleetVariables] = useState<Variable[]>([]);
    const [showStatsModal, setShowStatsModal] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);

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

            // Si la flota no existe, redirigir a 404
            if (!currentFleet) {
                navigate('/404', { replace: true });
                return;
            }

            setFleetData(currentFleet);

            // Fetch devices
            const data = await deviceService.getDevices();
            const filtered = data.filter(d => d.stridinspectorfleet === fleetId);
            setDevices(filtered);
            setSelectedDevices([]);
        } catch (error) {
            console.error("Error al cargar datos de la flota:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchFleetVariables = async () => {
        if (!fleetId) return;
        try {
            const response = await variableService.getFleetVariables(fleetId);
            setFleetVariables(response.data?.variables || []);
        } catch (error) {
            console.error("Error al cargar variables de la flota:", error);
            setFleetVariables([]);
        }
    };

    const handleOpenVariables = async () => {
        await fetchFleetVariables();
        setShowVariablesModal(true);
    };

    const handleCloseVariables = () => {
        setShowVariablesModal(false);
    };

    const handleUpdateVariables = async () => {
        await fetchFleetVariables();
    };

    const handleSync = async () => {
        // Prevent multiple clicks
        if (syncing) return;

        // Rate limiting: prevent sync if last sync was < 30 seconds ago
        if (lastSyncTime && (Date.now() - lastSyncTime.getTime()) < 30000) {
            alert('⏳ Espera 30 segundos entre sincronizaciones');
            return;
        }

        setSyncing(true);
        try {
            const result = await deviceService.syncFleet(fleetId!);
            setLastSyncTime(new Date());

            // Auto-refresh after sync
            await fetchData();

            alert(`✅ ${result.message}\n\n📊 Dispositivos sincronizados: ${result.devices_synced}`);
        } catch (error: any) {
            console.error('Error syncing fleet:', error);
            const errorMsg = error.response?.data?.detail || error.message || 'Error desconocido';
            alert(`❌ Error al sincronizar flota:\n\n${errorMsg}`);
        } finally {
            setSyncing(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [fleetId]);

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
            // PRIORIDAD 1: Si la nota contiene "Libre", es Libre
            if (device.strnote && device.strnote.toLowerCase().includes('libre')) {
                stats.libre++;
                return;
            }

            // PRIORIDAD 2: Usar iddevicestatus
            const statusId = device.iddevicestatus;

            // Mapeo según la lógica del backend (inventory_sync.py)
            // Categorías: 1-Operativo, 2-Reducido, 3-Desconectado, 4-Libre
            if (statusId === 4) {
                // Free
                stats.libre++;
            } else if (statusId === 3 || statusId === 8) {
                // Disconnected (3) o Inactive (8)
                stats.desconectado++;
            } else if (statusId === 2 || statusId === 9) {
                // Reduced (2) o Frozen (9)
                stats.reducido++;
            } else if (statusId === 1 || statusId === 5 || statusId === 6 || statusId === 7) {
                // Operational (1), Configuring (5), Updating (6), Post-Provisioning (7)
                stats.operativo++;
            } else {
                // Fallback para valores desconocidos
                stats.desconectado++;
            }
        });

        return stats;
    }, [devices]);

    // Lógica de Filtrado
    const filteredDevices = useMemo(() => {
        return devices.filter(device => {
            const realStatus = getDeviceRealStatus(device);
            const statusValue = realStatus === 'operativo' ? 'operational' :
                realStatus === 'desconectado' ? 'disconnected' :
                    realStatus === 'reducido' ? 'reduced' : 'libre';

            const globalTerm = searchTerm.toLowerCase();
            const matchesGlobal =
                device.strinspectorname.toLowerCase().includes(globalTerm) ||
                device.strnote.toLowerCase().includes(globalTerm) ||
                device.uuidinspector.toLowerCase().includes(globalTerm);

            const matchesStatus = columnFilters.status === '' || statusValue === columnFilters.status;
            const matchesName = device.strinspectorname.toLowerCase().includes(columnFilters.name.toLowerCase()) ||
                device.uuidinspector.toLowerCase().includes(columnFilters.name.toLowerCase());
            const matchesNote = device.strnote.toLowerCase().includes(columnFilters.note.toLowerCase());

            return matchesGlobal && matchesStatus && matchesName && matchesNote;
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

    if (loading) return <div className={styles.loading}><RefreshCw className={styles.spin} /> Cargando dispositivos...</div>;

    return (
        <div className={styles.container}>
            {/* 1. NAVEGACIÓN */}
            <nav className={styles.topNav}>
                <button onClick={() => navigate('/fleets')} className={styles.backBtn}>
                    <ArrowLeft size={20} /> Volver a lista de flotas
                </button>
            </nav>

            {/* Fleet Info Header */}
            <div className={styles.fleetHeader}>
                <div className={styles.fleetInfo}>
                    <div className={styles.fleetIcon}>
                        <img src={FlotasIcon} alt="Fleet Icon" style={{ width: '60%', height: '60%', objectFit: 'contain', transform: 'scaleX(-1)' }} />
                    </div>
                    <div className={styles.fleetDetails}>
                        <h1 className={styles.fleetName}>{fleetData?.id || fleetId}</h1>
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

                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <button
                        onClick={handleSync}
                        className={styles.syncBtn}
                        disabled={syncing}
                        title={syncing ? "Sincronizando..." : "Sincronizar con Balena Cloud"}
                    >
                        <RefreshCw size={18} className={syncing ? styles.spin : ''} />
                        <span>{syncing ? 'Sincronizando...' : 'Sincronizar'}</span>
                    </button>

                    <button
                        onClick={() => setShowStatsModal(true)}
                        className={styles.statsBtn}
                        title="Ver histórico de estadísticas"
                    >
                        <TrendingUp size={18} />
                        <span>Histórico</span>
                    </button>

                    <FleetActionsMenu
                        fleetId={fleetId!}
                        onVariablesClick={handleOpenVariables}
                    />
                </div>
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
                selectedDevices={selectedDevices}
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
                                    checked={filteredDevices.length > 0 && selectedDevices.length === filteredDevices.length}
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
                                    <option value="reduced">Reduced</option>
                                    <option value="libre">Libre</option>
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

            {/* Variables Modal */}
            {showVariablesModal && fleetData && (
                <VariablesModal
                    deviceUuid={fleetId!}
                    deviceName={fleetData.id}
                    variables={fleetVariables}
                    onClose={handleCloseVariables}
                    onUpdate={handleUpdateVariables}
                    entityType="fleet"
                />
            )}

            {/* Fleet Stats Modal */}
            <FleetStatsModal
                isOpen={showStatsModal}
                onClose={() => setShowStatsModal(false)}
                fleetId={fleetId!}
            />
        </div>
    );
};

export default FleetDetail;