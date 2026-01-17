import React, { useState, useEffect } from 'react';
import { X, Plus } from 'lucide-react';
import { fleetService, CreateFleetPayload, DeviceType } from '../../features/fleets/fleetService';
import CustomDropdown from './CustomDropdown';
import styles from './CreateFleetModal.module.css';

interface Props {
    onClose: () => void;
    onSuccess: () => void;
}

const CreateFleetModal: React.FC<Props> = ({ onClose, onSuccess }) => {
    const [deviceTypes, setDeviceTypes] = useState<DeviceType[]>([]);
    const [loadingDeviceTypes, setLoadingDeviceTypes] = useState(true);
    const [formData, setFormData] = useState<CreateFleetPayload>({
        name: '',
        device_type_id: 0,
        organization: null
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDeviceTypes = async () => {
            try {
                const types = await fleetService.getSupportedDevices();
                console.log('Device types received:', types);

                if (!Array.isArray(types)) {
                    console.error('Device types is not an array:', types);
                    setError('Error: respuesta inválida del servidor');
                    setDeviceTypes([]);
                    return;
                }

                setDeviceTypes(types);
                // Set default device type to the first one
                if (types.length > 0) {
                    setFormData(prev => ({ ...prev, device_type_id: types[0].iddevicetype }));
                }
            } catch (err: any) {
                console.error('Error fetching device types:', err);
                setError(err.response?.data?.detail || 'Error al cargar tipos de dispositivos');
                setDeviceTypes([]);
            } finally {
                setLoadingDeviceTypes(false);
            }
        };

        fetchDeviceTypes();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            await fleetService.createFleet(formData);
            onSuccess();
            onClose();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error al crear la flota');
            console.error('Error creating fleet:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
                <header className={styles.header}>
                    <div className={styles.title}>
                        <Plus size={24} color="#00C8FF" />
                        <h2>Crear Nueva Flota</h2>
                    </div>
                    <button className={styles.closeBtn} onClick={onClose}>
                        <X size={20} />
                    </button>
                </header>

                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.field}>
                        <label htmlFor="name">Nombre de la Flota *</label>
                        <input
                            id="name"
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            placeholder="ej: mi_flota_test"
                            required
                            className={styles.input}
                        />
                        <small className={styles.hint}>
                            Solo letras minúsculas, números y guiones bajos
                        </small>
                    </div>

                    <div className={styles.field}>
                        <label htmlFor="device_type_id">Tipo de Dispositivo *</label>
                        <CustomDropdown
                            options={deviceTypes.map(type => ({
                                value: type.iddevicetype,
                                label: type.strdevicenametype
                            }))}
                            value={formData.device_type_id}
                            onChange={(value) => setFormData({ ...formData, device_type_id: value })}
                            placeholder={loadingDeviceTypes ? "Cargando tipos..." : "Seleccionar tipo de dispositivo"}
                            disabled={loadingDeviceTypes || deviceTypes.length === 0}
                        />
                    </div>

                    <div className={styles.field}>
                        <label htmlFor="organization">Organización (Opcional)</label>
                        <input
                            id="organization"
                            type="text"
                            value={formData.organization || ''}
                            onChange={(e) => setFormData({ ...formData, organization: e.target.value || null })}
                            placeholder="ej: admin"
                            className={styles.input}
                        />
                    </div>

                    {error && (
                        <div className={styles.error}>
                            {error}
                        </div>
                    )}

                    <div className={styles.actions}>
                        <button
                            type="button"
                            onClick={onClose}
                            className={styles.cancelBtn}
                            disabled={loading}
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className={styles.submitBtn}
                            disabled={loading}
                        >
                            {loading ? 'Creando...' : 'Crear Flota'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateFleetModal;
