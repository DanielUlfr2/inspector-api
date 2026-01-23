import React, { useEffect, useState } from 'react';
import { X } from 'lucide-react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend
} from 'recharts';
import styles from './FleetStatsModal.module.css';
import apiClient from '../../api/apiClient';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    fleetId: string;
}

interface StatPoint {
    timestamp: string;
    online: number;
    offline: number;
    reduced: number;
    free: number;
    total: number;
}

export const FleetStatsModal: React.FC<Props> = ({ isOpen, onClose, fleetId }) => {
    const [data, setData] = useState<StatPoint[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen && fleetId) {
            fetchStats();
        }
    }, [isOpen, fleetId]);

    const fetchStats = async () => {
        setLoading(true);
        try {
            // Calculate date range (last 7 days by default)
            const end = new Date();
            const start = new Date();
            start.setDate(start.getDate() - 7);

            const response = await apiClient.get('/history/global-stats', {
                params: {
                    start_date: start.toISOString(),
                    end_date: end.toISOString(),
                    fleet_id: fleetId
                }
            });
            setData(response.data);
        } catch (error) {
            console.error("Error loading stats:", error);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className={styles.overlay}>
            <div className={styles.modal}>
                <div className={styles.header}>
                    <h2>Estadísticas: {fleetId}</h2>
                    <button onClick={(e) => { e.stopPropagation(); onClose(); }} className={styles.closeBtn}>
                        <X size={24} />
                    </button>
                </div>

                <div className={styles.content}>
                    {loading ? (
                        <div className={styles.loading}>Cargando datos...</div>
                    ) : data.length === 0 ? (
                        <div className={styles.noData}>No hay datos históricos disponibles</div>
                    ) : (
                        <div style={{ width: '100%', height: 400 }}>
                            <ResponsiveContainer>
                                <AreaChart data={data}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis
                                        dataKey="timestamp"
                                        tickFormatter={(str) => new Date(str).toLocaleDateString()}
                                    />
                                    <YAxis />
                                    <Tooltip
                                        labelFormatter={(str) => new Date(str).toLocaleString()}
                                    />
                                    <Legend />
                                    <Area type="monotone" dataKey="online" stackId="1" stroke="#82ca9d" fill="#82ca9d" name="Online" />
                                    <Area type="monotone" dataKey="reduced" stackId="1" stroke="#ffc658" fill="#ffc658" name="Reduced" />
                                    <Area type="monotone" dataKey="offline" stackId="1" stroke="#ff8042" fill="#ff8042" name="Offline" />
                                    <Area type="monotone" dataKey="free" stackId="1" stroke="#8884d8" fill="#8884d8" name="Free" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
