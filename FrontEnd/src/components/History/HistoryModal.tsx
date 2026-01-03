import React, { useEffect, useState } from 'react';
import { X, Activity, Cpu, HardDrive, Thermometer, BarChart2 } from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { deviceService } from '../../features/devices/deviceService';
import { DeviceHistory } from '../../types/device';
import styles from './History.module.css';

interface Props {
    uuid: string;
    onClose: () => void;
    initialMetric?: 'cpu' | 'ram' | 'disk' | 'temp' | 'all' | null;
}

const HistoryModal: React.FC<Props> = ({ uuid, onClose, initialMetric }) => {
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState<number>(24); // Horas por defecto

    useEffect(() => {
        loadHistory();
    }, [uuid, timeRange]); // Recargar cuando cambie el rango

    const loadHistory = async () => {
        try {
            setLoading(true);

            // Calcular fechas basadas en el rango seleccionado
            const endDate = new Date();
            const startDate = new Date();
            startDate.setHours(startDate.getHours() - timeRange);

            const data = await deviceService.getDeviceHistory(uuid, startDate, endDate);

            console.log("Raw API response:", data);
            console.log("Is array?", Array.isArray(data));

            // Verificar si data es un array
            if (!Array.isArray(data)) {
                console.error("Expected array but got:", typeof data, data);
                setHistory([]);
                return;
            }

            // Formatear fechas para el gráfico (backend ya devuelve timestamps redondeados)
            const formatted = data.map((d, index) => {
                const timestamp = new Date(d.timestamp);

                // Formato de hora
                const timeFormat = timestamp.toLocaleTimeString('es-ES', {
                    hour: '2-digit',
                    minute: '2-digit'
                });

                // Incluir fecha si es necesario (primer punto o cambio de día)
                const showDate = index === 0 ||
                    (index > 0 && timestamp.toDateString() !== new Date(data[index - 1].timestamp).toDateString());

                return {
                    ...d,
                    time: showDate
                        ? `${timestamp.toLocaleDateString('es-ES', { month: 'short', day: 'numeric' })} ${timeFormat}`
                        : timeFormat,
                    fullDate: timestamp.toLocaleString('es-ES')
                };
            });
            setHistory(formatted);
        } catch (error) {
            console.error("Error loading history:", error);
            setHistory([]);
        } finally {
            setLoading(false);
        }
    };

    const CustomTooltip = ({ active, payload, unit }: any) => {
        if (active && payload && payload.length) {
            return (
                <div style={{ background: '#1f2937', border: '1px solid #374151', padding: '10px', borderRadius: '8px' }}>
                    <p style={{ margin: 0, color: '#9ca3af', fontSize: '12px' }}>{payload[0].payload.fullDate}</p>
                    <p style={{ margin: '5px 0 0', color: '#fff', fontWeight: 'bold' }}>
                        {payload[0].name}: {payload[0].value} {unit}
                    </p>
                </div>
            );
        }
        return null;
    };

    const renderChart = (metric: string, color: string, name: string, unit: string, icon: any) => (
        <div className={styles.chartCard}>
            <div className={styles.chartHeader}>
                <h3>{icon} {name}</h3>
            </div>
            <div className={styles.chartContainer}>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={history}>
                        <defs>
                            <linearGradient id={`color${metric}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={color} stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                        <XAxis
                            dataKey="time"
                            stroke="#9ca3af"
                            fontSize={11}
                            tickLine={false}
                            axisLine={false}
                            interval={0}
                            tick={(props) => {
                                const { x, y, payload, index } = props;

                                // Solo mostrar si es la primera aparición de este valor
                                const firstIndex = history.findIndex(h => h.time === payload.value);
                                if (firstIndex !== index) {
                                    return null; // No mostrar duplicados
                                }

                                return (
                                    <g transform={`translate(${x},${y})`}>
                                        <text
                                            x={0}
                                            y={0}
                                            dy={16}
                                            textAnchor="middle"
                                            fill="#9ca3af"
                                            fontSize={11}
                                        >
                                            {payload.value}
                                        </text>
                                    </g>
                                );
                            }}
                        />
                        <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                        <Tooltip content={<CustomTooltip unit={unit} />} />
                        <Area
                            type="monotone"
                            dataKey={metric}
                            stroke={color}
                            fillOpacity={1}
                            fill={`url(#color${metric})`}
                            name={name}
                            strokeWidth={2}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );

    // Filtrar qué gráficas mostrar según initialMetric
    const showCpu = !initialMetric || initialMetric === 'all' || initialMetric === 'cpu';
    const showRam = !initialMetric || initialMetric === 'all' || initialMetric === 'ram';
    const showDisk = !initialMetric || initialMetric === 'all' || initialMetric === 'disk';
    const showTemp = !initialMetric || initialMetric === 'all' || initialMetric === 'temp';

    return (
        <div className={styles.modalOverlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
            <div className={styles.modalContent}>
                <header className={styles.modalHeader}>
                    <div className={styles.headerTitle}>
                        <BarChart2 size={24} color="#a855f7" />
                        <h2>Histórico de Rendimiento</h2>
                    </div>

                    {/* Selector de Rango de Tiempo */}
                    <div className={styles.timeRangeSelector}>
                        {[6, 12, 24, 48, 168].map(hours => (
                            <button
                                key={hours}
                                className={`${styles.timeRangeBtn} ${timeRange === hours ? styles.active : ''}`}
                                onClick={() => setTimeRange(hours)}
                            >
                                {hours < 24 ? `${hours}h` : hours === 24 ? '24h' : `${hours / 24}d`}
                            </button>
                        ))}
                    </div>

                    <button className={styles.closeBtn} onClick={onClose}>
                        <X size={24} />
                    </button>
                </header>

                <div className={styles.modalBody}>
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '50px', color: '#9ca3af' }}>Cargando datos históricos...</div>
                    ) : (
                        <div className={`${styles.chartGrid} ${(showCpu && !showRam && !showDisk && !showTemp) ||
                            (!showCpu && showRam && !showDisk && !showTemp) ||
                            (!showCpu && !showRam && showDisk && !showTemp) ||
                            (!showCpu && !showRam && !showDisk && showTemp)
                            ? styles.singleChart : ''
                            }`}>
                            {showCpu && renderChart('cpu_usage', '#a855f7', 'Uso de CPU', '%', <Activity size={16} />)}
                            {showTemp && renderChart('cpu_temp', '#f59e0b', 'Temperatura', '°C', <Thermometer size={16} />)}
                            {showRam && renderChart('memory_usage', '#3b82f6', 'Memoria RAM', 'MB', <Cpu size={16} />)}
                            {showDisk && renderChart('storage_usage', '#10b981', 'Almacenamiento', 'MB', <HardDrive size={16} />)}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default HistoryModal;
