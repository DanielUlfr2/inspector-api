import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    ChevronLeft, Cpu, HardDrive, Thermometer, Activity,
    Globe, Clock, Clipboard, Check, Terminal
} from 'lucide-react';

import { deviceService } from '../../features/devices/deviceService';
import keycloak from '../../features/auth/keycloakService';
import { Device } from '../../types/device';
import DeviceActionBar from '../../components/DeviceControl/DeviceActionBar';
import styles from './DeviceDetail.module.css';
import ProvisionModal from '../../components/Provision/ProvisionModal';

const DeviceDetail = () => {
    const { uuid } = useParams<{ uuid: string }>();
    const navigate = useNavigate();

    const [device, setDevice] = useState<Device | null>(null);
    const [logs, setLogs] = useState<string>('Iniciando flujo de registros...');
    const [loading, setLoading] = useState(true);
    const [copiedKey, setCopiedKey] = useState<string | null>(null);


    const consoleRef = useRef<HTMLDivElement>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    // Auto-scroll automático cuando llegan logs (Fixed: solo scrollear el contenedor)
    useEffect(() => {
        if (consoleRef.current) {
            consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
        }
    }, [logs]);

    const startLogsStream = useCallback(async (targetUuid: string) => {
        // Cerramos conexión previa si existe
        if (abortControllerRef.current) abortControllerRef.current.abort();
        abortControllerRef.current = new AbortController();

        try {
            await keycloak.updateToken(30);

            // --- CAMBIO: Usamos VITE_LOGS_DIRECT_URL (Bypass) ---
            const logsUrl = import.meta.env.VITE_LOGS_DIRECT_URL;

            const response = await fetch(`${logsUrl}/v1/admin/${targetUuid}/logs`, {
                headers: {
                    'Authorization': `Bearer ${keycloak.token}`,
                    'Accept': 'text/event-stream' // <-- Cambiado a event-stream
                },
                signal: abortControllerRef.current.signal
            });

            if (response.status === 401 || response.status === 403) {
                setLogs(`Error ${response.status}: Acceso denegado. Revisa tus permisos de Inspector.`);
                return;
            }

            if (!response.body) return;

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            setLogs("");

            let partialChunk = ""; // Para manejar líneas cortadas entre chunks

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = (partialChunk + chunk).split('\n\n');

                // Guardamos la última línea por si quedó incompleta
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
            if (err.name === 'AbortError') {
                console.log("Stream detenido.");
            } else {
                console.error("Error de Bypass Stream:", err);
                setLogs(prev => prev + "\n[Error de conexión directa con el backend]");
            }
        }
    }, []);

    const loadData = useCallback(async () => {
        if (!uuid) return;
        setLoading(true);
        try {
            const deviceData = await deviceService.getDeviceByUuid(uuid);
            setDevice(deviceData);

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
            {/* LÍNEA 1: Navegación Superior */}
            <nav className={styles.topNav}>
                <button onClick={() => navigate('/devices')} className={styles.backBtn}>
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

                    {/* 2. NUEVO COMPONENTE DE PROVISIÓN E INVENTARIO */}
                    {/* Reemplazamos la sección de notas antigua por esta */}
                    <ProvisionModal
                        device={device}
                        onSuccess={loadData}
                    />
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
                        <div className={styles.console} ref={consoleRef}>
                            <pre><code>{logs}</code></pre>
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