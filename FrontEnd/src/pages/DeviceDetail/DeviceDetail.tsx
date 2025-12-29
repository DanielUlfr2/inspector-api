import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ChevronLeft, Cpu, HardDrive, Thermometer, Activity,
    Globe, Clock, Clipboard, Check, Pencil,
    AlertCircle, Save, X, Terminal
} from 'lucide-react';

import { deviceService } from '../../features/devices/deviceService';
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

    // Referencia para el scroll automático de logs
    const logEndRef = useRef<HTMLDivElement>(null);

    // 1. Función para manejar el STREAM de logs (Evita el timeout de 20s)
    // src/pages/DeviceDetail/DeviceDetail.tsx

    const startLogsStream = useCallback(async (targetUuid: string) => {
        setLogs("Conectando al stream de administración...");
        try {
            // Obtenemos el token del almacenamiento local (ajusta la llave según tu app)
            const token = localStorage.getItem('access_token');

            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/v1/admin/${targetUuid}/logs`, {
                method: 'GET',
                headers: {
                    // AGREGAR ESTA LÍNEA:
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'text/plain' // O el tipo de contenido que devuelva tu API
                }
            });

            // Si el stream devuelve 401 antes de empezar, lanzamos error
            if (response.status === 401) {
                setLogs("Error 401: Sesión expirada o sin permisos para ver logs.");
                return;
            }

            if (!response.body) throw new Error("Stream no soportado");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedLogs = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                accumulatedLogs += chunk;
                setLogs(accumulatedLogs);
            }
        } catch (err) {
            console.error("Stream Error:", err);
            setLogs("Error: No se pudo establecer conexión con el flujo de logs.");
        }
    }, []);

    // 2. Carga de datos iniciales del dispositivo
    const loadData = useCallback(async () => {
        if (!uuid) return;
        setLoading(true);
        try {
            const deviceData = await deviceService.getDeviceByUuid(uuid);
            setDevice(deviceData);
            setTempNote(deviceData.strnote || '');

            // Iniciamos el stream de logs una vez cargado el dispositivo
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
            {/* LÍNEA 1: Navegación */}
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
                {/* Panel Izquierdo */}
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

                {/* Panel Derecho */}
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