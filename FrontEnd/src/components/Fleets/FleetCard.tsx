// src/components/Fleets/FleetCard.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Activity } from 'lucide-react';
import FlotasIcon from '../../assets/icons/Flotas.png';
import { Fleet } from '../../types/fleet';
import { StatusProgressBar } from './StatusProgressBar';
import styles from './FleetCard.module.css';
import { FleetStatsModal } from './FleetStatsModal';

interface Props {
    fleet: Fleet;
}

export const FleetCard: React.FC<Props> = ({ fleet }) => {
    const navigate = useNavigate();
    const [showStats, setShowStats] = useState(false);

    const handleStatsClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        setShowStats(true);
    };

    return (
        <>
            <div className={styles.card} onClick={() => navigate(`/flotas/${fleet.id}`)}>
                <div className={styles.header}>
                    <div className={styles.iconContainer}>
                        <img src={FlotasIcon} alt="Fleet Icon" style={{ width: '100%', height: '100%', objectFit: 'contain', transform: 'scaleX(-1)' }} />
                    </div>
                    <div className={styles.titleInfo}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '10px' }}>
                            <h3>{fleet.id}</h3>
                            <button
                                onClick={handleStatsClick}
                                className={styles.statsButton}
                                title="Ver Estadísticas"
                                style={{
                                    background: 'transparent',
                                    border: '1px solid #444',
                                    borderRadius: '4px',
                                    padding: '4px',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: '#aaa',
                                    transition: 'all 0.2s'
                                }}
                            >
                                <Activity size={16} />
                            </button>
                        </div>
                        <span>{fleet.device_type_slug}</span>
                    </div>
                </div>

                <div className={styles.statsSummary}>
                    <div className={styles.mainStat}>
                        <span className={styles.count}>{fleet.stats.total}</span>
                        <span className={styles.label}>DEVICES</span>
                    </div>
                    <StatusProgressBar stats={fleet.stats} />
                </div>

                <div className={styles.footer}>
                    <div className={styles.updatedAt}>
                        <Clock size={12} />
                        <span>{new Date(fleet.updated_at).toLocaleString()}</span>
                    </div>
                </div>
            </div>

            <FleetStatsModal
                isOpen={showStats}
                onClose={() => setShowStats(false)}
                fleetId={fleet.id}
            />
        </>
    );
};