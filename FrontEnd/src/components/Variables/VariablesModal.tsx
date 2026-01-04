import { useState } from 'react';
import { Trash2, Plus, Settings, X, Pencil, Check } from 'lucide-react';
import { Variable, variableService } from '../../features/devices/variableService';
import styles from './VariablesModal.module.css';

interface Props {
    deviceUuid: string;
    deviceName: string;
    variables: Variable[];
    onClose: () => void;
    onUpdate: () => void;
}

const VariablesModal = ({ deviceUuid, deviceName, variables, onClose, onUpdate }: Props) => {
    const [loading, setLoading] = useState(false);
    const [newVar, setNewVar] = useState({ name: '', value: '' });
    const [editingKey, setEditingKey] = useState<string | null>(null);
    const [editValue, setEditValue] = useState('');
    const [viewingValue, setViewingValue] = useState<{ name: string; value: string } | null>(null);

    const handleCreate = async () => {
        if (!newVar.name || !newVar.value) return;
        setLoading(true);
        try {
            await variableService.setDeviceVariable(deviceUuid, newVar);
            setNewVar({ name: '', value: '' });
            onUpdate();
        } catch (error: any) {
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                alert("No tienes permisos para crear variables.");
            } else {
                alert("Error al guardar la variable");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleStartEdit = (variable: Variable) => {
        setEditingKey(variable.name);
        setEditValue(variable.value);
    };

    const handleSaveEdit = async (key: string) => {
        setLoading(true);
        try {
            await variableService.setDeviceVariable(deviceUuid, { name: key, value: editValue });
            setEditingKey(null);
            onUpdate();
        } catch (error: any) {
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                alert("No tienes permisos para editar variables.");
            } else {
                alert("Error al actualizar");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleCancelEdit = () => {
        setEditingKey(null);
        setEditValue('');
    };

    const handleDelete = async (key: string) => {
        if (!confirm(`¿Estás seguro de eliminar la variable "${key}"?`)) return;
        setLoading(true);
        try {
            await variableService.deleteDeviceVariable(deviceUuid, key);
            onUpdate();
        } catch (error: any) {
            if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                alert("No tienes permisos para eliminar variables.");
            } else {
                alert("Error al eliminar");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.modalOverlay}>
            <div className={styles.modalContent}>
                {/* Header */}
                <div className={styles.modalHeader}>
                    <div className={styles.headerTitle}>
                        <Settings size={24} color="#a855f7" />
                        <h2>Variables del Dispositivo</h2>
                    </div>
                    <button className={styles.closeBtn} onClick={onClose}>
                        <X size={24} />
                    </button>
                </div>

                <div className={styles.deviceInfo}>
                    <span className={styles.deviceName}>{deviceName}</span>
                    <code className={styles.deviceUuid}>{deviceUuid}</code>
                </div>

                {/* Create Variable Form */}
                <div className={styles.createSection}>
                    <h3>Crear Nueva Variable</h3>
                    <div className={styles.createForm}>
                        <input
                            placeholder="NOMBRE_VARIABLE"
                            value={newVar.name}
                            onChange={e => setNewVar({ ...newVar, name: e.target.value.toUpperCase() })}
                            className={styles.input}
                        />
                        <input
                            placeholder="Valor"
                            value={newVar.value}
                            onChange={e => setNewVar({ ...newVar, value: e.target.value })}
                            className={styles.input}
                        />
                        <button
                            onClick={handleCreate}
                            disabled={loading || !newVar.name || !newVar.value}
                            className={styles.createBtn}
                        >
                            <Plus size={16} /> Crear
                        </button>
                    </div>
                </div>

                {/* Variables Table */}
                <div className={styles.tableSection}>
                    {variables.length === 0 ? (
                        <div className={styles.emptyState}>
                            <Settings size={48} color="#6b7280" />
                            <p>Sin variables configuradas</p>
                        </div>
                    ) : (
                        <table className={styles.table}>
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Valor</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {variables.map((v) => (
                                    <tr key={v.name}>
                                        <td className={styles.keyCell}>
                                            <code>{v.name}</code>
                                        </td>
                                        <td className={styles.valueCell} onClick={() => !editingKey && setViewingValue({ name: v.name, value: v.value })}>
                                            {editingKey === v.name ? (
                                                <input
                                                    value={editValue}
                                                    onChange={e => setEditValue(e.target.value)}
                                                    className={styles.editInput}
                                                    autoFocus
                                                />
                                            ) : (
                                                <span>{v.value}</span>
                                            )}
                                        </td>
                                        <td className={styles.actionsCell}>
                                            {editingKey === v.name ? (
                                                <>
                                                    <button
                                                        onClick={() => handleSaveEdit(v.name)}
                                                        className={styles.saveBtn}
                                                        disabled={loading}
                                                        title="Guardar"
                                                    >
                                                        <Check size={16} />
                                                    </button>
                                                    <button
                                                        onClick={handleCancelEdit}
                                                        className={styles.cancelBtn}
                                                        disabled={loading}
                                                        title="Cancelar"
                                                    >
                                                        <X size={16} />
                                                    </button>
                                                </>
                                            ) : (
                                                <>
                                                    <button
                                                        onClick={() => handleStartEdit(v)}
                                                        className={styles.editBtn}
                                                        disabled={loading}
                                                        title="Editar"
                                                    >
                                                        <Pencil size={16} />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDelete(v.name)}
                                                        className={styles.deleteBtn}
                                                        disabled={loading}
                                                        title="Eliminar"
                                                    >
                                                        <Trash2 size={16} />
                                                    </button>
                                                </>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Value Detail Modal */}
                {viewingValue && (
                    <div className={styles.valueModal} onClick={() => setViewingValue(null)}>
                        <div className={styles.valueModalContent} onClick={e => e.stopPropagation()}>
                            <div className={styles.valueModalHeader}>
                                <h3>{viewingValue.name}</h3>
                                <button className={styles.valueModalClose} onClick={() => setViewingValue(null)}>
                                    <X size={18} />
                                </button>
                            </div>
                            <div className={styles.valueModalBody}>
                                {viewingValue.value}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default VariablesModal;
