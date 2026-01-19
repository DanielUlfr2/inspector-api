import React, { useState } from 'react';
import { AlertTriangle, Trash2 } from 'lucide-react';
import styles from './DeleteConfirmationModal.module.css';

interface DeleteConfirmationModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title: string;
    message: React.ReactNode;
    loading?: boolean;
    error?: string | null;
}

const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({
    isOpen,
    onClose,
    onConfirm,
    title,
    message,
    loading = false,
    error = null
}) => {
    const [confirmText, setConfirmText] = useState('');
    const EXPECTED_TEXT = "Delete";

    if (!isOpen) return null;

    const isConfirmed = confirmText === EXPECTED_TEXT;

    return (
        <div className={styles.overlay} onClick={onClose}>
            <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
                <div className={styles.header}>
                    <h3><AlertTriangle size={24} /> {title}</h3>
                </div>

                <div className={styles.body}>
                    <div className={styles.message}>
                        {message}
                    </div>

                    <label className={styles.inputLabel}>
                        Escribe <strong>{EXPECTED_TEXT}</strong> para confirmar:
                    </label>
                    <input
                        type="text"
                        value={confirmText}
                        onChange={(e) => setConfirmText(e.target.value)}
                        className={styles.input}
                        placeholder={EXPECTED_TEXT}
                        autoFocus
                    />
                </div>

                {error && <div className={styles.error}>{error}</div>}

                <div className={styles.actions}>
                    <button
                        onClick={onClose}
                        className={styles.cancelBtn}
                        disabled={loading}
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={onConfirm}
                        className={styles.deleteBtn}
                        disabled={!isConfirmed || loading}
                    >
                        {loading ? 'Eliminando...' : <> <Trash2 size={16} /> Eliminar</>}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DeleteConfirmationModal;
