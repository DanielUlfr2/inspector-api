// src/pages/Dashboard/Dashboard.tsx
import { useState, useEffect, useCallback } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Activity, MonitorOff, AlertTriangle, CheckCircle, RefreshCcw, Calendar } from 'lucide-react';

import { historyService } from '../../features/history/historyService';
import { GlobalStat, TimeRange } from '../../types/history';
import DateRangeSelector from '../../components/DateRange/DateRangeSelector';
import CustomDatePicker from '../../components/DateRange/CustomDatePicker';

import styles from './Dashboard.module.css';

const Dashboard = () => {
    const [stats, setStats] = useState<GlobalStat[]>([]);
    // 1. Separamos los loadings
    const [isInitialLoading, setIsInitialLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const [selectedRange, setSelectedRange] = useState<TimeRange>('24h');
    const [showDatePicker, setShowDatePicker] = useState(false);
    const [customDates, setCustomDates] = useState({ start: '', end: '' });

    // NUEVO: Estado para filtrar qué líneas se ven
    const [activeFilter, setActiveFilter] = useState<string | null>(null);

    const toggleFilter = (filter: string) => {
        setActiveFilter(activeFilter === filter ? null : filter);
    };

    const loadData = useCallback(async (range?: TimeRange, custom?: { start: string, end: string }) => {
        // Si no es la primera vez, usamos el loading de "refresco"
        if (!isInitialLoading) setIsRefreshing(true);

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

            const data = await historyService.getGlobalStats(startStr, endStr);
            setStats(data);
        } catch (err) {
            console.error("Error en Dashboard:", err);
        } finally {
            setIsInitialLoading(false);
            setIsRefreshing(false);
        }
    }, [selectedRange, customDates, isInitialLoading]);

    useEffect(() => { loadData(); }, []); // Carga inicial

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

    const hasData = stats && stats.length > 0;
    const latest = hasData
        ? stats[stats.length - 1]
        : { free: 0, online: 0, reduced: 0, offline: 0, total: 0 };

    const kpiCards = [
        { id: 'free', label: 'Libres', val: latest.free, color: '#a855f7', icon: <CheckCircle size={24} /> },
        { id: 'online', label: 'Operativos', val: latest.online, color: '#10b981', icon: <Activity size={24} /> },
        { id: 'reduced', label: 'Reducidos', val: latest.reduced, color: '#f59e0b', icon: <AlertTriangle size={24} /> },
        { id: 'offline', label: 'Disconnected', val: latest.offline, color: '#ef4444', icon: <MonitorOff size={24} /> },
    ];

    // Spinner de pantalla completa SOLO la primera vez
    if (isInitialLoading) {
        return (
            <div className={styles.loaderContainer}>
                <div className={styles.spinner}>
                    <RefreshCcw className={styles.spin} size={48} />
                </div>
                <p className={styles.loadingText}>Sincronizando flota...</p>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <div className={styles.headerLeft}>
                    <h1>Dashboard de Inspección</h1>
                    <div className={styles.subtitle}>
                        <span className={styles.totalVehicles}>Total: {latest.total} vehículos</span>
                    </div>
                </div>
                <button
                    onClick={() => loadData()}
                    className={`${styles.refreshButton} ${isRefreshing ? styles.refreshing : ''}`}
                    disabled={isRefreshing}
                >
                    <RefreshCcw size={18} className={isRefreshing ? styles.spin : ''} />
                    <span>{isRefreshing ? 'Actualizando...' : 'Refrescar Datos'}</span>
                </button>
            </header>

            <div className={styles.kpiGrid}>
                {kpiCards.map((kpi) => (
                    <div
                        key={kpi.id}
                        className={`${styles.card} ${activeFilter === kpi.id ? styles.cardActive : ''} ${activeFilter && activeFilter !== kpi.id ? styles.cardInactive : ''}`}
                        style={{ '--accent': kpi.color } as any}
                        onClick={() => toggleFilter(kpi.id)}
                    >
                        <div className={styles.cardHeader}>
                            <div className={styles.iconWrapper}>{kpi.icon}</div>
                            <span className={styles.cardLabel}>{kpi.label}</span>
                        </div>
                        <div className={styles.cardBody}>
                            <span className={styles.cardValue}>{kpi.val}</span>
                        </div>
                        {activeFilter === kpi.id && <div className={styles.filterIndicator}>Solo visualizando</div>}
                        <div className={styles.cardGlow}></div>
                    </div>
                ))}
            </div>

            <section className={styles.chartSection}>
                {/* 2. Overlay de carga para la gráfica (Sectional Loading) */}
                {isRefreshing && (
                    <div className={styles.chartOverlay}>
                        <div className={styles.spinnerSmall}>
                            <RefreshCcw className={styles.spin} size={24} />
                        </div>
                    </div>
                )}

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

                {!stats.length && !isInitialLoading && !isRefreshing ? (
                    <div className={styles.noData}>
                        <Calendar size={48} />
                        <p>No hay datos históricos para este periodo.</p>
                    </div>
                ) : (
                    <div className={styles.chartContainer}>
                        <ResponsiveContainer width="99%" height="100%">
                            {/* Margen ajustado para evitar overflow */}
                            <LineChart data={stats} margin={{ top: 10, right: 10, left: -15, bottom: 5 }}>
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
                                    contentStyle={{
                                        borderRadius: '16px',
                                        border: '1px solid #e5e7eb',
                                        background: '#ffffff',
                                        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                                        padding: '16px',
                                        fontWeight: 500
                                    }}
                                    labelStyle={{ color: '#111827', fontWeight: 600, marginBottom: '8px' }}
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
                                    fill="url(#colorFree)"
                                    hide={activeFilter !== null && activeFilter !== 'free'}
                                />
                                <Line
                                    name="Operativo"
                                    type="monotone"
                                    dataKey="online"
                                    stroke="#10b981"
                                    strokeWidth={4}
                                    dot={false}
                                    activeDot={{ r: 7, strokeWidth: 2, stroke: '#fff' }}
                                    fill="url(#colorOnline)"
                                    hide={activeFilter !== null && activeFilter !== 'online'}
                                />
                                <Line
                                    name="Reducido"
                                    type="monotone"
                                    dataKey="reduced"
                                    stroke="#f59e0b"
                                    strokeWidth={4}
                                    dot={false}
                                    activeDot={{ r: 7, strokeWidth: 2, stroke: '#fff' }}
                                    hide={activeFilter !== null && activeFilter !== 'reduced'}
                                />
                                <Line
                                    name="Disconnected"
                                    type="monotone"
                                    dataKey="offline"
                                    stroke="#ef4444"
                                    strokeWidth={4}
                                    dot={false}
                                    activeDot={{ r: 7, strokeWidth: 2, stroke: '#fff' }}
                                    hide={activeFilter !== null && activeFilter !== 'offline'}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </section>
        </div>
    );
};

export default Dashboard;
