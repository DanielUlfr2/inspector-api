import React, { useState } from 'react';
import { MoreVertical, Edit2, Trash2 } from 'lucide-react';
import { fleetService } from '../../features/fleets/fleetService';
import { useNavigate } from 'react-router-dom';
import styles from './FleetActionsMenu.module.css';

interface Props {
    fleetId: string;
}

const FleetActionsMenu: React.FC<Props> = ({ fleetId }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [showRenameModal, setShowRenameModal] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [newName, setNewName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleRename = async () => {
        if (!newName.trim()) return;

        setLoading(true);
        setError(null);

        try {
            await fleetService.renameFleet(fleetId, { new_name: newName });
            setShowRenameModal(false);
            setNewName('');

            // Navigate to the new fleet name to keep URL in sync
            navigate(`/fleets/${newName}`);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error al renombrar la flota');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        setLoading(true);
        setError(null);

        try {
            await fleetService.deleteFleet(fleetId);
            navigate('/fleets');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error al eliminar la flota');
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <button className={styles.menuBtn} onClick={() => setIsOpen(!isOpen)}>
                <MoreVertical size={20} />
            </button>

            {isOpen && (
                <>
                    <div className={styles.overlay} onClick={() => setIsOpen(false)} />
                    <div className={styles.menu}>
                        <button
                            className={styles.menuItem}
                            onClick={() => {
                                setShowRenameModal(true);
                                setIsOpen(false);
                            }}
                        >
                            <Edit2 size={16} />
                            <span>Renombrar Flota</span>
                        </button>
                        <button
                            className={`${styles.menuItem} ${styles.danger}`}
                            onClick={() => {
                                setShowDeleteConfirm(true);
                                setIsOpen(false);
                            }}
                        >
                            <Trash2 size={16} />
                            <span>Eliminar Flota</span>
                        </button>
                    </div>
                </>
            )}

            {/* Rename Modal */}
            {showRenameModal && (
                <div className={styles.modalOverlay} onClick={() => setShowRenameModal(false)}>
                    <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
                        <h3>Renombrar Flota</h3>
                        <p>Ingresa el nuevo nombre para la flota <strong>{fleetId}</strong></p>

                        <input
                            type="text"
                            value={newName}
                            onChange={(e) => setNewName(e.target.value)}
                            placeholder="nuevo_nombre_flota"
                            className={styles.input}
                            autoFocus
                        />

                        {error && <div className={styles.error}>{error}</div>}

                        <div className={styles.actions}>
                            <button
                                onClick={() => setShowRenameModal(false)}
                                className={styles.cancelBtn}
                                disabled={loading}
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleRename}
                                className={styles.submitBtn}
                                disabled={loading || !newName.trim()}
                            >
                                {loading ? 'Renombrando...' : 'Renombrar'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Confirmation */}
            {showDeleteConfirm && (
                <div className={styles.modalOverlay} onClick={() => setShowDeleteConfirm(false)}>
                    <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
                        <h3>Eliminar Flota</h3>
                        <p>¿Estás seguro de que deseas eliminar la flota <strong>{fleetId}</strong>?</p>
                        <p className={styles.warning}>Esta acción no se puede deshacer. La flota debe estar vacía para ser eliminada.</p>

                        {error && <div className={styles.error}>{error}</div>}

                        <div className={styles.actions}>
                            <button
                                onClick={() => setShowDeleteConfirm(false)}
                                className={styles.cancelBtn}
                                disabled={loading}
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleDelete}
                                className={styles.deleteBtn}
                                disabled={loading}
                            >
                                {loading ? 'Eliminando...' : 'Eliminar'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FleetActionsMenu;
