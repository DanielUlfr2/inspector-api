import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ChevronLeft, Cpu, HardDrive, Thermometer, Activity,
    Globe, Clipboard, Check, Terminal, Settings,
    Pencil, Info as InfoIcon, ChevronDown, ChevronUp, X, BarChart2
} from 'lucide-react';

import { deviceService } from '../../features/devices/deviceService';
import keycloak from '../../features/auth/keycloakService';
import { Device } from '../../types/device';
import DeviceActionBar from '../../components/DeviceControl/DeviceActionBar';
import styles from './DeviceDetail.module.css';
import ProvisionModal from '../../components/Provision/ProvisionModal';
import HistoryModal from '../../components/History/HistoryModal';
import DeviceNotes from '../../components/Notes/DeviceNotes';
import VariablesModal from '../../components/Variables/VariablesModal';
import { Variable } from '../../types/device';
import { variableService } from '../../features/devices/variableService';

const DeviceDetail = () => {
    const { uuid } = useParams<{ uuid: string }>();
    const navigate = useNavigate();

    // Estados de datos
    const [device, setDevice] = useState<Device | null>(null);
    const [logs, setLogs] = useState<string>('Iniciando flujo de registros...');
    const [loading, setLoading] = useState(true);
    const [copiedKey, setCopiedKey] = useState<string | null>(null);

    // Estados de UI (Nuevos)
    const [isInventoryOpen, setIsInventoryOpen] = useState(false);
    const [showMoreInfo, setShowMoreInfo] = useState(false);
    const [historyMetric, setHistoryMetric] = useState<'cpu' | 'ram' | 'disk' | 'temp' | 'all' | null>(null);
    const [isVariablesOpen, setIsVariablesOpen] = useState(false);

    // Estados de Variables
    const [deviceVariables, setDeviceVariables] = useState<Variable[]>([]);

    const consoleRef = useRef<HTMLDivElement>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    // Auto-scroll de logs
    useEffect(() => {
        if (consoleRef.current) {
            consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
        }
    }, [logs]);

    const startLogsStream = useCallback(async (targetUuid: string) => {
        if (abortControllerRef.current) abortControllerRef.current.abort();
        abortControllerRef.current = new AbortController();

        try {
            await keycloak.updateToken(30);
            const logsUrl = import.meta.env.VITE_LOGS_DIRECT_URL;

            const response = await fetch(`${logsUrl}/v1/admin/${targetUuid}/logs`, {
                headers: {
                    'Authorization': `Bearer ${keycloak.token}`,
                    'Accept': 'text/event-stream'
                },
                signal: abortControllerRef.current.signal
            });

            if (response.status === 401 || response.status === 403) {
                setLogs(`Error ${response.status}: Acceso denegado.`);
                return;
            }

            if (!response.body) return;
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            setLogs("");

            let partialChunk = "";
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = (partialChunk + chunk).split('\n\n');
                partialChunk = lines.pop() || "";

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const message = line.replace('data: ', '').trim();
                        if (message) {
                            setLogs(prev => (prev + message + '\n').slice(-50000));
                        }
                    }
                }
            }
        } catch (err: any) {
            if (err.name !== 'AbortError') {
                setLogs(prev => prev + "\n[Error de conexión con el backend]");
            }
        }
    }, []);

    const loadData = useCallback(async () => {
        if (!uuid) return;
        setLoading(true);
        try {
            const deviceData = await deviceService.getDeviceByUuid(uuid);
            setDevice(deviceData);

            // Cargar variables desde endpoint dedicado
            try {
                const varsResponse = await variableService.getDeviceVariables(uuid);
                setDeviceVariables(varsResponse.data?.variables || []);
            } catch (error) {
                console.error('Error loading variables:', error);
                setDeviceVariables([]);
            }

            startLogsStream(uuid);
        } catch (error) {
            console.error("Error crítico:", error);
            setDevice(null);
        } finally {
            setLoading(false);
        }
    }, [uuid, startLogsStream]);

    useEffect(() => { loadData(); }, [loadData]);

    const handleCopy = (text: string, key: string) => {
        navigator.clipboard.writeText(text);
        setCopiedKey(key);
        setTimeout(() => setCopiedKey(null), 2000);
    };

    if (loading) return <div className={styles.loadingState}>Sincronizando con Inspector...</div>;
    if (!device) return <div className={styles.errorState}>Dispositivo no encontrado.</div>;

    return (
        <div className={styles.container}>
            {/* 1. NAVEGACIÓN */}
            <nav className={styles.topNav}>
                <button onClick={() => navigate('/devices')} className={styles.backBtn}>
                    <ChevronLeft size={20} /> Volver a lista de equipos
                </button>
            </nav>

            {/* 2. HEADER DINÁMICO */}
            <header className={styles.header}>
                <div className={styles.headerMain}>
                    <div className={styles.titleGroup}>
                        <h1>{device.strinspectorname}</h1>
                        <button className={styles.pencilBtn} onClick={() => setIsInventoryOpen(true)} title="Editar Inventario">
                            <Pencil size={18} />
                        </button>
                    </div>

                    <div className={styles.actionsGroup}>
                        <button className={styles.infoToggleBtn} onClick={() => setShowMoreInfo(!showMoreInfo)}>
                            <InfoIcon size={16} />
                            {showMoreInfo ? 'Ocultar detalles' : 'Obtener más información'}
                            {showMoreInfo ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        </button>

                        <button className={styles.infoToggleBtn} onClick={() => setIsVariablesOpen(true)}>
                            <Settings size={16} />
                            Variables
                        </button>
                    </div>
                </div>

                <div className={styles.uuidRow}>
                    <code className={styles.uuidCode}>{device.uuidinspector}</code>
                    <button onClick={() => handleCopy(device.uuidinspector, 'uuid-header')} className={styles.copyBtnInline}>
                        {copiedKey === 'uuid-header' ? <Check size={14} color="#10b981" /> : <Clipboard size={14} />}
                    </button>
                </div>

                {/* PANEL EXPANDIBLE: MÁS INFORMACIÓN */}
                {showMoreInfo && (
                    <div className={styles.moreInfoPanel}>
                        <div className={styles.infoGrid}>
                            <InfoField label="SERVICE ID" value={device.inspector_service_id || 'N/A'} />
                            <InfoField label="CLIENTE" value={device.client_name || 'Sin registro'} />
                            <InfoField label="DIRECCIÓN" value={device.address || 'Sin registro'} />
                            <InfoField label="VELOCIDAD" value={`${device.down_speed || 0} / ${device.up_speed || 0} Mbps`} />
                            <InfoField label="ESTADO" value={device.status_name || 'Desconocido'} />
                            <InfoField label="FLEET" value={device.stridinspectorfleet} />
                        </div>
                    </div>
                )}
            </header>

            {/* 3. ACCIONES RÁPIDAS */}
            <div className={styles.actionWrapper}>
                <DeviceActionBar
                    selectedUuids={[device.uuidinspector]}
                    onActionComplete={loadData}
                />
            </div>

            {/* 4. LAYOUT PRINCIPAL */}
            <div className={styles.layout}>
                {/* Panel Izquierdo: Red */}
                <div className={styles.leftPanel}>
                    <section className={styles.card}>
                        <div className={styles.cardHeader}>
                            <Globe size={18} /> <h2>Información Técnica</h2>
                        </div>
                        <div className={styles.techInfoGrid}>
                            {/* Fila 1: Estado y Fleet */}
                            <div className={styles.techField}>
                                <span className={styles.techLabel}>ESTADO INVENTARIO</span>
                                <div className={styles.techValue}>
                                    <span className={styles.statusBadge} data-status={device.status_name}>
                                        {device.status_name || 'Desconocido'}
                                    </span>
                                </div>
                            </div>

                            <div className={styles.techField}>
                                <span className={styles.techLabel}>FLEET</span>
                                <span className={styles.techValue}>{device.stridinspectorfleet}</span>
                            </div>

                            {/* Fila 2: Conectividad */}
                            <div className={styles.techField}>
                                <span className={styles.techLabel}>CONECTIVIDAD</span>
                                <div className={styles.techValue}>
                                    <div className={styles.statusIndicator}>
                                        <div className={device.boolonline ? styles.statusDotGreen : styles.statusDotRed}></div>
                                        <span>{device.boolonline ? 'En línea' : 'Desconectado'}</span>
                                    </div>
                                </div>
                            </div>

                            <div className={styles.techField}>
                                <span className={styles.techLabel}>ÚLTIMA CONEXIÓN</span>
                                <span className={styles.techValue}>
                                    {new Date(device.dtlastconnectivityevent).toLocaleString('es-ES', {
                                        day: '2-digit',
                                        month: 'short',
                                        year: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })}
                                </span>
                            </div>

                            {/* Fila 3: Direcciones */}
                            <div className={styles.techField} style={{ gridColumn: '1 / -1' }}>
                                <span className={styles.techLabel}>DIRECCIÓN IP</span>
                                <div className={styles.techValue}>
                                    <code className={styles.codeValue}>{device.stripaddress}</code>
                                    <button onClick={() => handleCopy(device.stripaddress, 'ip')} className={styles.copyIconButton}>
                                        {copiedKey === 'ip' ? <Check size={14} color="#10b981" /> : <Clipboard size={14} />}
                                    </button>
                                </div>
                            </div>

                            <div className={styles.techField} style={{ gridColumn: '1 / -1' }}>
                                <span className={styles.techLabel}>MAC ADDRESS</span>
                                <div className={styles.techValue}>
                                    <code className={styles.codeValue}>{device.jsonbobservaciones.mac_address || 'N/A'}</code>
                                    <button onClick={() => handleCopy(device.jsonbobservaciones.mac_address || '', 'mac')} className={styles.copyIconButton}>
                                        {copiedKey === 'mac' ? <Check size={14} color="#10b981" /> : <Clipboard size={14} />}
                                    </button>
                                </div>
                            </div>

                            {/* Fila 4: Versiones */}
                            <div className={styles.techField}>
                                <span className={styles.techLabel}>SUPERVISOR</span>
                                <span className={styles.techValue}>{device.strsupervisorversion}</span>
                            </div>

                            <div className={styles.techField}>
                                <span className={styles.techLabel}>SISTEMA OPERATIVO</span>
                                <span className={styles.techValue}>{device.strosversion}</span>
                            </div>

                            {/* Fila 5: Notas (Componente Interactivo) */}
                            <DeviceNotes
                                deviceUuid={device.uuidinspector}
                                initialNote={device.strnote}
                            />
                        </div>
                    </section>
                </div>

                {/* Panel Derecho: Telemetría y Logs */}
                <div className={styles.rightPanel}>
                    <section className={styles.card}>
                        <div className={styles.cardHeader}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <Activity size={18} /> <h2>Métricas en Tiempo Real</h2>
                                </div>
                                <button className={styles.iconBtn} onClick={() => setHistoryMetric('all')} title="Ver Histórico Completo">
                                    <BarChart2 size={18} />
                                </button>
                            </div>
                        </div>
                        <div className={styles.metricsGrid}>
                            <div onClick={() => setHistoryMetric('cpu')} style={{ cursor: 'pointer' }}>
                                <MetricCard title="CPU" value={`${device.intcpuusagepercent}%`} icon={<Activity size={18} />} percent={device.intcpuusagepercent} />
                            </div>
                            <div onClick={() => setHistoryMetric('temp')} style={{ cursor: 'pointer' }}>
                                <MetricCard title="Temperatura" value={`${device.intcputempc}°C`} icon={<Thermometer size={18} />} percent={device.intcputempc} color="#f59e0b" />
                            </div>
                            <div onClick={() => setHistoryMetric('ram')} style={{ cursor: 'pointer' }}>
                                <MetricCard title="RAM" value={`${device.intmemoryusagemb} MB`} icon={<Cpu size={18} />} percent={(device.intmemoryusagemb / device.intmemorytotalmb) * 100} />
                            </div>
                            <div onClick={() => setHistoryMetric('disk')} style={{ cursor: 'pointer' }}>
                                <MetricCard title="Disco" value={`${Math.round(device.intstorageusagemb / 1024)} GB`} icon={<HardDrive size={18} />} percent={(device.intstorageusagemb / device.intstoragetotalmb) * 100} />
                            </div>
                        </div>
                    </section>

                    <section className={styles.consoleCard}>
                        <div className={styles.cardHeader}>
                            <Terminal size={18} /> <h2>Consola de Logs (Stream)</h2>
                        </div>
                        <div className={styles.console} ref={consoleRef}>
                            <pre><code>{logs}</code></pre>
                        </div>
                    </section>
                </div>
            </div>

            {/* 5. MODAL FLOTANTE DE INVENTARIO */}
            {isInventoryOpen && (
                <div className={styles.modalOverlay}>
                    <div className={styles.modalContent}>
                        <div className={styles.modalHeader}>
                            <h3>Gestión de Inventario y Aprovisionamiento</h3>
                            <button className={styles.closeModalBtn} onClick={() => setIsInventoryOpen(false)}>
                                <X size={20} />
                            </button>
                        </div>
                        <div className={styles.modalBody}>
                            <ProvisionModal
                                device={device}
                                onSuccess={() => {
                                    loadData();
                                    setIsInventoryOpen(false);
                                }}
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* 6. MODAL DE HISTÓRICO */}
            {historyMetric && (
                <HistoryModal
                    uuid={device.uuidinspector}
                    onClose={() => setHistoryMetric(null)}
                    initialMetric={historyMetric}
                />
            )}

            {/* 7. MODAL DE VARIABLES */}
            {isVariablesOpen && (
                <VariablesModal
                    deviceUuid={device.uuidinspector}
                    deviceName={device.strinspectorname}
                    variables={deviceVariables}
                    onClose={() => setIsVariablesOpen(false)}
                    onUpdate={loadData}
                />
            )}
        </div>
    );
};

// --- SUB-COMPONENTES ---

const InfoField = ({ label, value, copyable, onCopy, isCopied, icon, isStatus, online }: any) => (
    <div className={styles.infoField}>
        <span className={styles.fieldLabel}>{label} {icon}</span>
        <div className={styles.fieldValue}>
            {isStatus && <span className={online ? styles.statusDotGreen : styles.statusDotRed} />}
            {value}
            {copyable && (
                <button onClick={onCopy} className={styles.copyIconButton}>
                    {isCopied ? <Check size={14} color="#10b981" /> : <Clipboard size={14} />}
                </button>
            )}
        </div>
    </div>
);

const MetricCard = ({ title, value, icon, percent, color }: any) => (
    <div className={styles.metricCard}>
        <div className={styles.metricTop}>
            {icon}
            <div className={styles.metricText}>
                <span className={styles.metricTitle}>{title}</span>
                <span className={styles.metricVal}>{value}</span>
            </div>
        </div>
        <div className={styles.progressTrack}>
            <div className={styles.progressFill} style={{ width: `${percent}%`, backgroundColor: color || '#a855f7' }} />
        </div>
    </div>
);

export default DeviceDetail;