import React from 'react';
import { FleetStats } from '../../types/fleet';
import styles from './StatusProgressBar.module.css'; // Asegúrate de crear este CSS

interface Props { stats: FleetStats; }

export const StatusProgressBar: React.FC<Props> = ({ stats }) => {
    const getW = (n: number) => (n / stats.total) * 100 + '%';
    return (
        <div style={{ display: 'flex', height: '8px', borderRadius: '4px', overflow: 'hidden', background: '#eee' }}>
            <div style={{ width: getW(stats.operativo), background: '#2ecc71' }} />
            <div style={{ width: getW(stats.reducido), background: '#f1c40f' }} />
            <div style={{ width: getW(stats.desconectado), background: '#e74c3c' }} />
            <div style={{ width: getW(stats.libre), background: '#3498db' }} />
        </div>
    );
};