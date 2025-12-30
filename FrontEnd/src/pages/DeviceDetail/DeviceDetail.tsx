import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ChevronLeft, Cpu, HardDrive, Thermometer, Activity,
    Globe, Clock, Clipboard, Check, Pencil,
    AlertCircle, Save, X, Terminal
} from 'lucide-react';

import { deviceService } from '../../features/devices/deviceService';
import keycloak from '../../features/auth/keycloakService';
import { Device } from '../../types/device';
import DeviceActionBar from '../../components/DeviceControl/DeviceActionBar';
import styles from './DeviceDetail.module.css';

const DeviceDetail = () => {
    const { uuid } = useParams<{ uuid: string }>();
    const navigate = useNavigate();

    const [device, setDevice] = useState<Device | null>(null);
    const [logs, setLogs] = useState<string>('Iniciando flujo de registros...');
    const [loading, setLoading] = useState(true);
    const [copiedKey, setCopiedKey] = useState<string | null>(null);
    const [isEditingNote, setIsEditingNote] = useState(false);
    const [tempNote, setTempNote] = useState('');

    const logEndRef = useRef<HTMLDivElement>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    // Auto-scroll automático cuando llegan logs
    useEffect(() => {
        if (logEndRef.current) {
            logEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs]);

    const startLogsStream = useCallback(async (targetUuid: string) => {
        // Cerramos conexión previa si existe
        if (abortControllerRef.current) abortControllerRef.current.abort();
        abortControllerRef.current = new AbortController();

        try {
            // Aseguramos que el token esté fresco antes de iniciar el stream
            await keycloak.updateToken(30);

            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/v1/admin/${targetUuid}/logs`, {
                headers: {
                    'Authorization': `Bearer ${keycloak.token}`,
                    'Accept': 'text/plain'
                },
                signal: abortControllerRef.current.signal
            });

            if (response.status === 401) {
                setLogs("Error 401: El servidor administrativo rechazó el acceso. Verifica los permisos en KrakenD.");
                return;
            }

            if (!response.body) return;

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            setLogs(""); // Limpiar consola al conectar

            while (true) {
                const { done, value } = await reader.read();

                // SOLUCIÓN AL TEXTO CORTADO:
                // Si done es true, decodificamos el último fragmento sin {stream: true} para vaciar el buffer
                if (done) {
                    const lastChunk = decoder.decode();
                    if (lastChunk) setLogs(prev => (prev + lastChunk).slice(-50000));
                    break;
                }

                // Mientras hay datos, decodificamos con {stream: true} para mantener el estado de caracteres incompletos
                const chunk = decoder.decode(value, { stream: true });
                setLogs(prev => (prev + chunk).slice(-50000));
            }

        } catch (err: any) {
            if (err.name === 'AbortError') {
                console.log("Stream detenido por navegación.");
            } else {
                console.error("Error de Stream:", err);
                setLogs(prev => prev + "\n[Error de conexión con el flujo de logs]");
            }
        }
    }, []);

    const loadData = useCallback(async () => {
        if (!uuid) return;
        setLoading(true);
        try {
            const deviceData = await deviceService.getDeviceByUuid(uuid);
            setDevice(deviceData);
            setTempNote(deviceData.strnote || '');
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

    const handleSaveNote = async () => {
        if (!uuid) return;
        try {
            await deviceService.updateNote(uuid, tempNote);
            setIsEditingNote(false);
            const updated = await deviceService.getDeviceByUuid(uuid);
            setDevice(updated);
        } catch (error) {
            alert("Error al actualizar la nota.");
        }
    };

    if (loading) return <div className={styles.loadingState}>Sincronizando con Inspector...</div>;
    if (!device) return <div className={styles.errorState}>Dispositivo no encontrado.</div>;

    return (
        <div className={styles.container}>
            {/* LÍNEA 1: Navegación Superior */}
            <nav className={styles.topNav}>
                <button onClick={() => navigate('/dispositivos')} className={styles.backBtn}>
                    <ChevronLeft size={20} /> Volver a lista de equipos
                </button>
            </nav>

            {/* LÍNEA 2: Título y UUID */}
            <header className={styles.header}>
                <div className={styles.headerInfo}>
                    <h1>{device.strinspectorname}</h1>
                    <div className={styles.uuidWrapper}>
                        <code className={styles.uuidCode}>{device.uuidinspector}</code>
                        <button onClick={() => handleCopy(device.uuidinspector, 'uuid-header')} className={styles.copyBtnInline}>
                            {copiedKey === 'uuid-header' ? <Check size={14} color="#10b981" /> : <Clipboard size={14} />}
                        </button>
                    </div>
                </div>
            </header>

            <div className={styles.actionWrapper}>
                <DeviceActionBar
                    selectedUuids={[device.uuidinspector]}
                    onActionComplete={loadData}
                />
            </div>

            <div className={styles.layout}>
                {/* Panel Izquierdo: Red e Inventario */}
                <div className={styles.leftPanel}>
                    <section className={styles.card}>
                        <div className={styles.cardHeader}>
                            <Globe size={18} /> <h2>Información Técnica</h2>
                        </div>
                        <div className={styles.infoGrid}>
                            <InfoField label="IP ADDRESS" value={device.stripaddress} copyable onCopy={() => handleCopy(device.stripaddress, 'ip')} isCopied={copiedKey === 'ip'} />
                            <InfoField label="MAC ADDRESS" value={device.jsonbobservaciones.mac_address || 'N/A'} copyable onCopy={() => handleCopy(device.jsonbobservaciones.mac_address || '', 'mac')} isCopied={copiedKey === 'mac'} />
                            <InfoField label="VPN" value={device.boolconnectedtovpn ? 'Conectado' : 'Desconectado'} isStatus online={device.boolconnectedtovpn} />
                            <InfoField label="LAST SYNC" value={new Date(device.dtlastmetricupdate).toLocaleString()} icon={<Clock size={14} />} />
                            <InfoField label="OS VERSION" value={device.strosversion} />
                            <InfoField label="SUPERVISOR" value={device.strsupervisorversion} />
                        </div>
                    </section>

                    <section className={styles.card}>
                        <div className={styles.cardHeader}>
                            <AlertCircle size={18} /> <h2>Notas e Inventario</h2>
                            <button className={styles.editBtn} onClick={() => setIsEditingNote(!isEditingNote)}>
                                {isEditingNote ? <X size={16} /> : <Pencil size={16} />}
                            </button>
                        </div>
                        <div className={styles.noteBody}>
                            {isEditingNote ? (
                                <div className={styles.editor}>
                                    <textarea value={tempNote} onChange={(e) => setTempNote(e.target.value)} />
                                    <button onClick={handleSaveNote} className={styles.saveNoteBtn}>
                                        <Save size={16} /> Guardar Cambios
                                    </button>
                                </div>
                            ) : (
                                <p className={styles.noteText}>{device.strnote || "Sin notas registradas."}</p>
                            )}
                        </div>
                    </section>
                </div>

                {/* Panel Derecho: Telemetría y Logs */}
                <div className={styles.rightPanel}>
                    <section className={styles.statsGrid}>
                        <MetricCard title="CPU" value={`${device.intcpuusagepercent}%`} icon={<Activity size={18} />} percent={device.intcpuusagepercent} />
                        <MetricCard title="Temperatura" value={`${device.intcputempc}°C`} icon={<Thermometer size={18} />} percent={device.intcputempc} color="#f59e0b" />
                        <MetricCard title="RAM" value={`${device.intmemoryusagemb} MB`} icon={<Cpu size={18} />} percent={(device.intmemoryusagemb / device.intmemorytotalmb) * 100} />
                        <MetricCard title="Almacenamiento" value={`${Math.round(device.intstorageusagemb / 1024)} GB`} icon={<HardDrive size={18} />} percent={(device.intstorageusagemb / device.intstoragetotalmb) * 100} />
                    </section>

                    <section className={styles.consoleCard}>
                        <div className={styles.cardHeader}>
                            <Terminal size={18} /> <h2>Consola de Logs (Stream)</h2>
                        </div>
                        <div className={styles.console}>
                            <pre><code>{logs}</code></pre>
                            <div ref={logEndRef} />
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
};

// --- Sub-componentes ---

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