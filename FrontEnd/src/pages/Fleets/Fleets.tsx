import React, { useState } from 'react';
import { LayoutGrid, List, RefreshCw, Plus } from 'lucide-react';
import { useFleets } from '../../hooks/useFleets';
import { useNavigate } from 'react-router-dom';
import CreateFleetModal from '../../components/Fleets/CreateFleetModal';
import FlotasIcon from '../../assets/icons/Flotas.png';
import styles from './Fleets.module.css';

const Fleets: React.FC = () => {
    const { fleets, loading, error, refresh } = useFleets();
    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const navigate = useNavigate();

    if (loading) return <div style={{ padding: '2rem' }}>Cargando flotas...</div>;
    if (error) return <div style={{ padding: '2rem', color: 'red' }}>Error: {error}</div>;

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <div className={styles.titleSection}>
                    <h1>Flotas</h1>
                    <span className={styles.badge}>{fleets.length}</span>
                </div>
                <div className={styles.actions}>
                    <button className={styles.createBtn} onClick={() => setShowCreateModal(true)}>
                        <Plus size={18} />
                        <span>Nueva Flota</span>
                    </button>
                    <button className={styles.refreshBtn} onClick={refresh}>
                        <RefreshCw size={18} />
                    </button>
                    <div className={styles.viewToggle}>
                        <button
                            className={viewMode === 'grid' ? styles.active : ''}
                            onClick={() => setViewMode('grid')}
                        >
                            <LayoutGrid size={18} />
                        </button>
                        <button
                            className={viewMode === 'list' ? styles.active : ''}
                            onClick={() => setViewMode('list')}
                        >
                            <List size={18} />
                        </button>
                    </div>
                </div>
            </header>

            <div className={viewMode === 'grid' ? styles.grid : styles.list}>
                {fleets.length === 0 ? (
                    <div className={styles.emptyState}>No hay flotas disponibles</div>
                ) : (
                    fleets.map(fleet => (
                        <div
                            key={fleet.id}
                            className={styles.fleetCard}
                            onClick={() => navigate(`/fleets/${fleet.id}`)}
                        >
                            {/* Header con icono y nombre */}
                            <div className={styles.cardHeader}>
                                <div className={styles.fleetIcon}>
                                    <img src={FlotasIcon} alt="Fleet Icon" style={{ width: '100%', height: '100%', objectFit: 'contain', transform: 'scaleX(-1)' }} />
                                </div>
                                <div className={styles.fleetInfo}>
                                    <h3 className={styles.fleetName}>{fleet.id}</h3>
                                    <span className={styles.fleetType}>{fleet.device_type_slug || 'Tipo uno'}</span>
                                </div>
                            </div>

                            {/* Contador de dispositivos */}
                            <div className={styles.deviceCount}>
                                <span className={styles.count}>{fleet.stats.total}</span>
                                <span className={styles.label}>DEVICES</span>
                            </div>

                            {/* Barra de progreso */}
                            <div className={styles.progressBar}>
                                {fleet.stats.operativo > 0 && (
                                    <div
                                        className={styles.segmentOperativo}
                                        style={{ width: `${(fleet.stats.operativo / fleet.stats.total) * 100}%` }}
                                    />
                                )}
                                {fleet.stats.reducido > 0 && (
                                    <div
                                        className={styles.segmentReducido}
                                        style={{ width: `${(fleet.stats.reducido / fleet.stats.total) * 100}%` }}
                                    />
                                )}
                                {fleet.stats.desconectado > 0 && (
                                    <div
                                        className={styles.segmentDesconectado}
                                        style={{ width: `${(fleet.stats.desconectado / fleet.stats.total) * 100}%` }}
                                    />
                                )}
                                {fleet.stats.libre > 0 && (
                                    <div
                                        className={styles.segmentLibre}
                                        style={{ width: `${(fleet.stats.libre / fleet.stats.total) * 100}%` }}
                                    />
                                )}
                            </div>

                            {/* Leyenda de estados */}
                            <div className={styles.statusLegend}>
                                <div className={styles.legendItem}>
                                    <span className={`${styles.dot} ${styles.dotOperativo}`}></span>
                                    <span>{fleet.stats.operativo} operational</span>
                                </div>
                                <div className={styles.legendItem}>
                                    <span className={`${styles.dot} ${styles.dotDesconectado}`}></span>
                                    <span>{fleet.stats.desconectado} disconnected</span>
                                </div>
                                <div className={styles.legendItem}>
                                    <span className={`${styles.dot} ${styles.dotReducido}`}></span>
                                    <span>{fleet.stats.reducido} reduced</span>
                                </div>
                                <div className={styles.legendItem}>
                                    <span className={`${styles.dot} ${styles.dotLibre}`}></span>
                                    <span>{fleet.stats.libre} free</span>
                                </div>
                            </div>

                            {/* Fecha de actualización */}
                            <div className={styles.cardFooter}>
                                <span className={styles.updateLabel}>UPDATED</span>
                                <span className={styles.updateDate}>{formatDate(fleet.updated_at)}</span>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {showCreateModal && (
                <CreateFleetModal
                    onClose={() => setShowCreateModal(false)}
                    onSuccess={refresh}
                />
            )}
        </div>
    );
};

export default Fleets;