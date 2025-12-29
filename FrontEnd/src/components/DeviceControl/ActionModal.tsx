// src/components/DeviceControl/ActionModal.tsx
import { AlertTriangle, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import styles from './ActionModal.module.css';

interface ActionModalProps {
    isOpen: boolean;
    action: string;
    count: number;
    status: 'idle' | 'loading' | 'success' | 'error';
    onConfirm: () => void;
    onClose: () => void;
}

const ActionModal = ({ isOpen, action, count, status, onConfirm, onClose }: ActionModalProps) => {
    if (!isOpen) return null;

    return (
        <div className={styles.overlay}>
            <div className={styles.modal}>
                {status === 'idle' && (
                    <div className={styles.content}>
                        <AlertTriangle className={styles.warningIcon} size={48} />
                        <h3>¿Confirmar {action}?</h3>
                        <p>Se ejecutará en <strong>{count}</strong> dispositivo(s).</p>
                        <div className={styles.actions}>
                            <button onClick={onClose} className={styles.cancelBtn}>Cancelar</button>
                            <button onClick={onConfirm} className={styles.confirmBtn}>Sí, ejecutar</button>
                        </div>
                    </div>
                )}

                {status === 'loading' && (
                    <div className={styles.content}>
                        <Loader2 className={styles.spin} size={48} />
                        <h3>Procesando...</h3>
                        <p>Enviando comando al API Gateway.</p>
                    </div>
                )}

                {status === 'success' && (
                    <div className={styles.content}>
                        <CheckCircle2 className={styles.successIcon} size={48} />
                        <h3>200 OK - Éxito</h3>
                        <p>La acción se ha procesado correctamente.</p>
                        <button onClick={onClose} className={styles.closeBtn}>Cerrar</button>
                    </div>
                )}

                {status === 'error' && (
                    <div className={styles.content}>
                        <XCircle className={styles.errorIcon} size={48} />
                        <h3>Error</h3>
                        <p>No se pudo completar la acción en el servidor.</p>
                        <button onClick={onClose} className={styles.closeBtn}>Cerrar</button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActionModal;