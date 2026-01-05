import React, { useEffect, useState, useRef } from 'react';
import { X, Activity, Cpu, HardDrive, Thermometer, BarChart2 } from 'lucide-react';
import {
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { deviceService } from '../../features/devices/deviceService';
import { DeviceHistory } from '../../types/device';
import { TimeRange } from '../../types/history';
import DateRangeSelector from '../DateRange/DateRangeSelector';
import CustomDatePicker from '../DateRange/CustomDatePicker';
import styles from './History.module.css';

interface Props {
    uuid: string;
    onClose: () => void;
    initialMetric?: 'cpu' | 'ram' | 'disk' | 'temp' | 'all' | null;
}

const HistoryModal: React.FC<Props> = ({ uuid, onClose, initialMetric }) => {
    const [history, setHistory] = useState<DeviceHistory[]>([]);
    const [loading, setLoading] = useState(true);

    // Estados para el rango de fechas
    const [selectedRange, setSelectedRange] = useState<TimeRange>('24h');
    const [customRange, setCustomRange] = useState<{ start: Date; end: Date } | null>(null);
    const [isCustomPickerOpen, setIsCustomPickerOpen] = useState(false);

    const customButtonRef = useRef<HTMLButtonElement>(null);

    useEffect(() => {
        loadHistory();
    }, [uuid, selectedRange, customRange]);

    const loadHistory = async () => {
        try {
            setLoading(true);
            let startDate = new Date();
            let endDate = new Date();

            if (selectedRange === 'custom' && customRange) {
                startDate = customRange.start;
                endDate = customRange.end;
            } else {
                // Cálculo basado en horas predefinidas
                const hoursMap: Record<string, number> = { '6h': 6, '12h': 12, '24h': 24 };
                const hours = hoursMap[selectedRange] || 24;
                startDate.setHours(startDate.getHours() - hours);
            }

            const data = await deviceService.getDeviceHistory(uuid, startDate, endDate);

            if (!Array.isArray(data)) {
                console.error("Expected array but got:", typeof data, data);
                setHistory([]);
                return;
            }

            // Formatear fechas para el gráfico
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

    const handleRangeChange = (range: TimeRange) => {
        if (range === 'custom') {
            setIsCustomPickerOpen(true);
        } else {
            setSelectedRange(range);
            setCustomRange(null);
        }
    };

    const handleCustomApply = (startStr: string, endStr: string) => {
        setCustomRange({
            start: new Date(startStr),
            end: new Date(endStr)
        });
        setSelectedRange('custom');
        setIsCustomPickerOpen(false);
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

    const renderChart = (metric: keyof DeviceHistory, color: string, name: string, unit: string, icon: any) => (
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
                            interval="preserveStartEnd"
                            minTickGap={50}
                            tick={{ fill: '#9ca3af', fontSize: 11 }}
                        />
                        <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                        <Tooltip content={<CustomTooltip unit={unit} />} />
                        <Area
                            type="monotone"
                            dataKey={metric as string}
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
        <div className={styles.modalOverlay}>
            <div className={styles.modalContent}>
                <header className={styles.modalHeader}>
                    <div className={styles.headerTitle}>
                        <BarChart2 size={24} color="#a855f7" />
                        <h2>Histórico de Rendimiento</h2>
                    </div>

                    <div style={{ position: 'relative' }}>
                        <DateRangeSelector
                            selectedRange={selectedRange}
                            onRangeChange={handleRangeChange}
                            customButtonRef={customButtonRef}
                        />

                        {isCustomPickerOpen && (
                            <div style={{ position: 'absolute', top: '100%', right: 0, zIndex: 50, marginTop: '10px' }}>
                                <CustomDatePicker
                                    onApply={handleCustomApply}
                                    onCancel={() => setIsCustomPickerOpen(false)}
                                />
                            </div>
                        )}
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
