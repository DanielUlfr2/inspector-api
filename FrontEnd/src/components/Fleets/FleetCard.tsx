// src/components/Fleets/FleetCard.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock } from 'lucide-react';
import FlotasIcon from '../../assets/icons/Flotas.png';
import { Fleet } from '../../types/fleet';
import { StatusProgressBar } from './StatusProgressBar';
import styles from './FleetCard.module.css';

interface Props {
    fleet: Fleet;
}

export const FleetCard: React.FC<Props> = ({ fleet }) => {
    const navigate = useNavigate();

    return (
        <div className={styles.card} onClick={() => navigate(`/flotas/${fleet.id}`)}>
            <div className={styles.header}>
                <div className={styles.iconContainer}>
                    <img src={FlotasIcon} alt="Fleet Icon" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                </div>
                <div className={styles.titleInfo}>
                    <h3>{fleet.id}</h3>
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
    );
};