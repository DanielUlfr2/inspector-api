import React, { useState } from 'react';
import { Trash2, Plus, Lock, Settings } from 'lucide-react';
import { Variable, variableService } from '../../features/devices/variableService';
import styles from './VariableManager.module.css';

interface Props {
    title: string;
    type: 'device' | 'fleet';
    targetId: string;
    variables: Variable[];
    onUpdate: () => void;
}

const VariableManager = ({ title, type, targetId, variables, onUpdate }: Props) => {
    const [loading, setLoading] = useState(false);
    const [newVar, setNewVar] = useState({ name: '', value: '' });

    const handleSave = async () => {
        if (!newVar.name || !newVar.value) return;
        setLoading(true);
        try {
            if (type === 'device') {
                await variableService.setDeviceVariable(targetId, newVar);
            } else {
                await variableService.setFleetVariable(targetId, newVar);
            }
            setNewVar({ name: '', value: '' });
            onUpdate();
        } catch (error) {
            alert("Error al guardar la variable");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (key: string) => {
        if (!confirm(`¿Eliminar ${key}?`)) return;
        setLoading(true);
        try {
            if (type === 'device') {
                await variableService.deleteDeviceVariable(targetId, key);
            } else {
                await variableService.deleteFleetVariable(targetId, key);
            }
            onUpdate();
        } catch (error) {
            alert("Error al eliminar");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.varCard}>
            <div className={styles.varHeader}>
                {type === 'device' ? <Settings size={16} /> : <Lock size={16} />}
                <h3>{title}</h3>
            </div>

            <div className={styles.varList}>
                {variables.length === 0 && <p className={styles.empty}>Sin variables configuradas</p>}
                {variables.map((v) => (
                    <div key={v.name} className={styles.varItem}>
                        <div className={styles.varInfo}>
                            <span className={styles.varKey}>{v.name}</span>
                            <span className={styles.varValue}>{v.value}</span>
                        </div>
                        <button onClick={() => handleDelete(v.name)} className={styles.delBtn} disabled={loading}>
                            <Trash2 size={14} />
                        </button>
                    </div>
                ))}
            </div>

            <div className={styles.varForm}>
                <input
                    placeholder="KEY"
                    value={newVar.name}
                    onChange={e => setNewVar({ ...newVar, name: e.target.value.toUpperCase() })}
                />
                <input
                    placeholder="VALUE"
                    value={newVar.value}
                    onChange={e => setNewVar({ ...newVar, value: e.target.value })}
                />
                <button onClick={handleSave} disabled={loading || !newVar.name} className={styles.addBtn}>
                    {loading ? '...' : <Plus size={16} />}
                </button>
            </div>
        </div>
    );
};

export default VariableManager;