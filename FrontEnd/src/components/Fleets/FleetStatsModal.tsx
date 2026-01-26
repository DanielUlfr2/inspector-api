import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend
} from 'recharts';
import styles from './FleetStatsModal.module.css';
import { historyService } from '../../features/history/historyService';
import { GlobalStat, TimeRange } from '../../types/history';
import DateRangeSelector from '../../components/DateRange/DateRangeSelector';
import CustomDatePicker from '../../components/DateRange/CustomDatePicker';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    fleetId: string;
}

const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
        const dataPoint = payload[0].payload;
        const rawTimestamp = dataPoint.timestamp.endsWith('Z') ? dataPoint.timestamp.slice(0, -1) : dataPoint.timestamp;
        const dateObj = new Date(rawTimestamp);

        return (
            <div className={styles.customTooltip}>
                <p className={styles.tooltipLabel}>
                    {dateObj.toLocaleTimeString('es-CO', {
                        timeZone: 'America/Bogota',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    })}
                    <span style={{ fontSize: '0.8em', fontWeight: 'normal', marginLeft: '0.5rem', opacity: 0.7 }}>
                        ({dateObj.toLocaleDateString('es-CO', { timeZone: 'America/Bogota' })})
                    </span>
                </p>
                {payload.map((entry: any) => (
                    <div key={entry.name} className={styles.tooltipItem} style={{ color: entry.color }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
                            <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: entry.color }}></div>
                            {entry.name}:
                        </span>
                        <span style={{ fontWeight: 600 }}>{entry.value}</span>
                    </div>
                ))}
            </div>
        );
    }
    return null;
};

export const FleetStatsModal: React.FC<Props> = ({ isOpen, onClose, fleetId }) => {
    const [data, setData] = useState<GlobalStat[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedRange, setSelectedRange] = useState<TimeRange>('24h');
    const [showDatePicker, setShowDatePicker] = useState(false);
    const [customDates, setCustomDates] = useState({ start: '', end: '' });

    useEffect(() => {
        if (isOpen && fleetId) {
            loadData();
        }
    }, [isOpen, fleetId]);

    const loadData = async (range?: TimeRange, custom?: { start: string, end: string }) => {
        setLoading(true);
        try {
            let startStr: string | undefined;
            let endStr: string | undefined;
            const activeRange = range || selectedRange;

            if (activeRange === 'custom') {
                const targetDates = custom || customDates;
                if (targetDates.start && targetDates.end) {
                    startStr = historyService.formatDateToLocalISO(new Date(targetDates.start));
                    endStr = historyService.formatDateToLocalISO(new Date(targetDates.end));
                }
            } else {
                const hoursMap: Record<string, number> = { '6h': 6, '12h': 12, '24h': 24 };
                const rangeData = historyService.getRangeByHours(hoursMap[activeRange] || 24);
                startStr = rangeData.start;
                endStr = rangeData.end;
            }

            const stats = await historyService.getGlobalStats(startStr, endStr, fleetId);
            setData(stats);
        } catch (error) {
            console.error("Error loading stats:", error);
            setData([]);
        } finally {
            setLoading(false);
        }
    };

    const handleRangeChange = (range: TimeRange) => {
        setSelectedRange(range);
        if (range !== 'custom') {
            setShowDatePicker(false);
            loadData(range);
        } else {
            setShowDatePicker(true);
        }
    };

    const handleCustomApply = (start: string, end: string) => {
        setCustomDates({ start, end });
        loadData('custom', { start, end });
        setShowDatePicker(false);
    };

    if (!isOpen) return null;

    return (
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
                <div className={styles.header}>
                    <div>
                        <h2>Estadísticas Históricas</h2>
                        <p className={styles.fleetName}>{fleetId}</p>
                    </div>
                    <button onClick={onClose} className={styles.closeBtn}>
                        <X size={24} />
                    </button>
                </div>

                <div className={styles.chartHeader}>
                    <div className={styles.chartTitle}>
                        <h3>Tendencia de Estado</h3>
                        <span className={styles.chartSubtitle}>
                            {selectedRange === 'custom' ? 'Rango personalizado' : `Últimas ${selectedRange}`}
                        </span>
                    </div>

                    <div className={styles.selectorWrapper}>
                        <DateRangeSelector
                            selectedRange={selectedRange}
                            onRangeChange={handleRangeChange}
                        />
                        {showDatePicker && (
                            <CustomDatePicker
                                initialStart={customDates.start}
                                initialEnd={customDates.end}
                                onApply={handleCustomApply}
                                onCancel={() => setShowDatePicker(false)}
                            />
                        )}
                    </div>
                </div>

                <div className={styles.content}>
                    {loading ? (
                        <div className={styles.loading}>Cargando datos...</div>
                    ) : data.length === 0 ? (
                        <div className={styles.noData}>No hay datos históricos disponibles</div>
                    ) : (
                        <div className={styles.chartContainer}>
                            <ResponsiveContainer width="99%" height="100%">
                                <LineChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" opacity={0.5} />
                                    <XAxis
                                        dataKey="time"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                        dy={10}
                                    />
                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#6b7280', fontSize: 12 }}
                                        dx={-10}
                                    />
                                    <Tooltip
                                        content={<CustomTooltip />}
                                        cursor={{ stroke: '#6b7280', strokeWidth: 1, strokeDasharray: '4 4' }}
                                    />
                                    <Legend verticalAlign="top" height={40} iconType="circle" />
                                    <Line
                                        name="Libre"
                                        type="monotone"
                                        dataKey="free"
                                        stroke="#a855f7"
                                        strokeWidth={4}
                                        dot={false}
                                        activeDot={{ r: 7, strokeWidth: 2, stroke: '#fff' }}
                                    />
                                    <Line
                                        name="Operativo"
                                        type="monotone"
                                        dataKey="online"
                                        stroke="#10b981"
                                        strokeWidth={4}
                                        dot={false}
                                        activeDot={{ r: 7, strokeWidth: 2, stroke: '#fff' }}
                                    />
                                    <Line
                                        name="Reducido"
                                        type="monotone"
                                        dataKey="reduced"
                                        stroke="#f59e0b"
                                        strokeWidth={4}
                                        dot={false}
                                        activeDot={{ r: 7, strokeWidth: 2, stroke: '#fff' }}
                                    />
                                    <Line
                                        name="Disconnected"
                                        type="monotone"
                                        dataKey="offline"
                                        stroke="#ef4444"
                                        strokeWidth={4}
                                        dot={false}
                                        activeDot={{ r: 7, strokeWidth: 2, stroke: '#fff' }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
