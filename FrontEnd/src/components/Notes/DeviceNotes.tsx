import { useState, useEffect } from 'react';
import { Pencil, Check, X, StickyNote } from 'lucide-react';
import { deviceService } from '../../features/devices/deviceService';
import styles from './DeviceNotes.module.css';

interface DeviceNotesProps {
    deviceUuid: string;
    initialNote: string | null;
}

const DeviceNotes = ({ deviceUuid, initialNote }: DeviceNotesProps) => {
    const [note, setNote] = useState(initialNote || '');
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [tempNote, setTempNote] = useState('');

    useEffect(() => {
        setNote(initialNote || '');
    }, [initialNote]);

    const [error, setError] = useState<string | null>(null);

    const handleEdit = () => {
        setTempNote(note);
        setIsEditing(true);
        setError(null);
    };

    const handleCancel = () => {
        setIsEditing(false);
        setTempNote('');
        setError(null);
    };

    const handleSave = async () => {
        setIsSaving(true);
        setError(null);
        try {
            await deviceService.updateNote(deviceUuid, tempNote);
            setNote(tempNote);
            setIsEditing(false);
        } catch (err: any) {
            console.error('Error saving note:', err);
            if (err.response && (err.response.status === 401 || err.response.status === 403)) {
                setError("No tienes permisos para editar notas.");
            } else {
                setError("Error al guardar. Inténtalo de nuevo.");
            }
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className={styles.notesContainer}>
            <div className={styles.header}>
                <span className={styles.title}>
                    <StickyNote size={16} />
                    Notas del Dispositivo
                </span>
                {!isEditing && (
                    <button
                        className={styles.editBtn}
                        onClick={handleEdit}
                        title="Editar notas"
                    >
                        <Pencil size={16} />
                    </button>
                )}
            </div>

            {isEditing ? (
                <div className={styles.editMode}>
                    <textarea
                        className={styles.textarea}
                        value={tempNote}
                        onChange={(e) => setTempNote(e.target.value)}
                        placeholder="Escribe una nota para este dispositivo..."
                        autoFocus
                    />
                    <div className={styles.actions}>
                        <button
                            className={`${styles.actionBtn} ${styles.cancelBtn}`}
                            onClick={handleCancel}
                            disabled={isSaving}
                        >
                            <X size={16} /> Cancelar
                        </button>
                        <button
                            className={`${styles.actionBtn} ${styles.saveBtn}`}
                            onClick={handleSave}
                            disabled={isSaving}
                        >
                            {isSaving ? 'Guardando...' : (
                                <>
                                    <Check size={16} /> Guardar
                                </>
                            )}
                        </button>
                    </div>
                </div>
            ) : (
                <div className={styles.noteContent}>
                    {note ? (
                        note
                    ) : (
                        <span className={styles.emptyNote}>Sin notas registradas.</span>
                    )}
                </div>
            )}
        </div>
    );
};

export default DeviceNotes;
