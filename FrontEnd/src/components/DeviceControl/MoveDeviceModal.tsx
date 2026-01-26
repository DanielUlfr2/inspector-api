import { useState, useEffect } from 'react';
import { X, ArrowRight, Truck } from 'lucide-react';
import { fleetService } from '../../features/fleets/fleetService';
import { Fleet } from '../../types/fleet';
import styles from './MoveDeviceModal.module.css';
import SearchableSelect from '../Common/SearchableSelect';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: (targetFleetSlug: string) => Promise<void>;
    deviceName: string; // To show "Moving [device]..."
}

const MoveDeviceModal = ({ isOpen, onClose, onConfirm, deviceName }: Props) => {
    const [fleets, setFleets] = useState<Fleet[]>([]);
    const [selectedFleet, setSelectedFleet] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        if (isOpen) {
            loadFleets();
        }
    }, [isOpen]);

    const loadFleets = async () => {
        setLoading(true);
        try {
            const data = await fleetService.getAllFleets();
            setFleets(data);
        } catch (error) {
            console.error('Error fetching fleets:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleConfirm = async () => {
        if (!selectedFleet) return;
        setSubmitting(true);
        try {
            await onConfirm(selectedFleet);
            onClose();
        } catch (error) {
            console.error('Error moving device:', error);
        } finally {
            setSubmitting(false);
        }
    };

    if (!isOpen) return null;

    const fleetOptions = fleets.map(fleet => ({
        value: fleet.id,
        label: `${fleet.id} (${fleet.device_type_slug})`
    }));

    return (
        <div className={styles.overlay}>
            <div className={styles.modal}>
                <div className={styles.header}>
                    <h3>Mover Dispositivo</h3>
                    <button onClick={onClose} className={styles.closeBtn}>
                        <X size={20} />
                    </button>
                </div>

                <div className={styles.content}>
                    <div className={styles.summary}>
                        <p>Estás moviendo el dispositivo:</p>
                        <div className={styles.deviceCard}>
                            <Truck size={20} />
                            <strong>{deviceName}</strong>
                        </div>
                    </div>

                    <div className={styles.formGroup}>
                        <label>Selecciona la nueva flota:</label>
                        {loading ? (
                            <div className={styles.loading}>Cargando flotas...</div>
                        ) : (
                            <SearchableSelect
                                value={selectedFleet}
                                onChange={(val) => setSelectedFleet(String(val))}
                                options={fleetOptions}
                                placeholder="-- Seleccionar Flota --"
                            />
                        )}
                    </div>

                    <div className={styles.infoBox}>
                        ℹ️ El dispositivo mantendrá su historial, pero cambiará su configuración a la de la nueva flota.
                    </div>
                </div>

                <div className={styles.footer}>
                    <button onClick={onClose} className={styles.cancelBtn} disabled={submitting}>
                        Cancelar
                    </button>
                    <button
                        onClick={handleConfirm}
                        className={styles.confirmBtn}
                        disabled={!selectedFleet || submitting}
                    >
                        {submitting ? 'Moviendo...' : 'Mover Equipo'}
                        {!submitting && <ArrowRight size={16} />}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MoveDeviceModal;
