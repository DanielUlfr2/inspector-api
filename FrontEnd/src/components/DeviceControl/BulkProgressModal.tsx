import { useEffect, useState, useRef } from 'react';
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react';
import styles from './BulkProgressModal.module.css';
import { Device } from '../../types/device';
import { deviceService } from '../../features/devices/deviceService';

interface BulkProgressModalProps {
    isOpen: boolean;
    action: 'restart' | 'reboot' | 'shutdown';
    devices: Device[];
    onClose: () => void;
}

interface DeviceStatus {
    uuid: string;
    name: string;
    status: 'pending' | 'processing' | 'success' | 'error';
    message?: string;
    step?: string;
}

const MAX_CONCURRENT = 5;

const BulkProgressModal = ({ isOpen, action, devices, onClose }: BulkProgressModalProps) => {
    const [statuses, setStatuses] = useState<DeviceStatus[]>([]);
    const [overallStatus, setOverallStatus] = useState<'idle' | 'processing' | 'completed'>('idle');
    const processingRef = useRef(false);

    const prevDevicesRef = useRef<string>('');

    useEffect(() => {
        if (isOpen && devices.length > 0) {
            // Check if devices actually changed by comparing UUID strings
            const currentDevicesStr = devices.map(d => d.uuidinspector).sort().join(',');

            if (currentDevicesStr !== prevDevicesRef.current) {
                const initialStatuses: DeviceStatus[] = devices.map(d => ({
                    uuid: d.uuidinspector,
                    name: d.strinspectorname || d.uuidinspector,
                    status: 'pending'
                }));
                setStatuses(initialStatuses);
                setOverallStatus('idle');
                processingRef.current = false;
                prevDevicesRef.current = currentDevicesStr;
            }
        } else if (!isOpen) {
            // Reset reference when modal closes so it re-initializes correctly next time
            prevDevicesRef.current = '';
        }
    }, [isOpen, devices]);

    const startProcessing = async () => {
        if (processingRef.current) return;
        processingRef.current = true;
        setOverallStatus('processing');

        const queue = [...devices];
        let activeCount = 0;
        let currentIndex = 0;

        const processDevice = async (device: Device) => {
            setStatuses(prev => prev.map(s =>
                s.uuid === device.uuidinspector ? { ...s, status: 'processing', message: 'Iniciando...' } : s
            ));

            try {
                const response = await deviceService.sendSingleAction(device.uuidinspector, action);

                if (response.task_id) {
                    // Esperar 1s para que el worker tome la tarea de la cola
                    await new Promise(r => setTimeout(r, 1000));

                    let taskStatus = 'PENDING';
                    let attempts = 0;

                    // Polling mejorado que lee metadata
                    // 480 intentos * 250ms = 120 segundos (2 minutos) de timeout
                    while (['PENDING', 'STARTED'].includes(taskStatus) && attempts < 480) {
                        await new Promise(r => setTimeout(r, 250));
                        const statusResponse = await deviceService.getTaskStatus(response.task_id);
                        taskStatus = statusResponse.status;

                        // Si hay metadata de progreso, actualizamos la UI
                        if (statusResponse.meta) {
                            setStatuses(prev => prev.map(s =>
                                s.uuid === device.uuidinspector ? {
                                    ...s,
                                    message: statusResponse.meta.message,
                                    step: statusResponse.meta.step
                                } : s
                            ));
                        }

                        if (['SUCCESS', 'FAILURE', 'REVOKED'].includes(taskStatus)) {
                            // Si terminó exitosamente, usamos el mensaje final
                            if (taskStatus === 'SUCCESS' && statusResponse.result) {
                                setStatuses(prev => prev.map(s =>
                                    s.uuid === device.uuidinspector ? {
                                        ...s,
                                        status: 'success',
                                        message: statusResponse.result.message || 'Completado'
                                    } : s
                                ));
                            }
                            // Si falló, usamos el error
                            if (taskStatus === 'FAILURE') {
                                throw new Error(statusResponse.error || 'Error en la tarea');
                            }
                            break;
                        }
                        attempts++;
                    }

                    if (taskStatus !== 'SUCCESS') {
                        throw new Error(`Timeout o error desconocido (Status: ${taskStatus})`);
                    }
                } else {
                    setStatuses(prev => prev.map(s =>
                        s.uuid === device.uuidinspector ? { ...s, status: 'success', message: 'Completado' } : s
                    ));
                }

            } catch (error: any) {
                console.error(`Error processing ${device.uuidinspector}`, error);
                setStatuses(prev => prev.map(s =>
                    s.uuid === device.uuidinspector ? {
                        ...s,
                        status: 'error',
                        message: error.message || 'Error desconocido'
                    } : s
                ));
            } finally {
                activeCount--;
                // Cuando termina una, inicia la siguiente
                if (currentIndex < queue.length) {
                    const nextDevice = queue[currentIndex];
                    currentIndex++;
                    activeCount++;
                    processDevice(nextDevice);
                }
            }
        };

        // Iniciar las primeras MAX_CONCURRENT tareas
        const initialBatch = Math.min(MAX_CONCURRENT, queue.length);
        for (let i = 0; i < initialBatch; i++) {
            activeCount++;
            currentIndex++;
            processDevice(queue[i]);
        }

        // Esperar a que todas terminen
        while (activeCount > 0 || currentIndex < queue.length) {
            await new Promise(r => setTimeout(r, 500));
        }

        setOverallStatus('completed');
        processingRef.current = false;
    };

    if (!isOpen) return null;

    const completedCount = statuses.filter(s => s.status === 'success').length;
    const errorCount = statuses.filter(s => s.status === 'error').length;

    return (
        <div className={styles.overlay}>
            <div className={styles.modal}>
                <h3>Procesando {action} ({completedCount + errorCount}/{devices.length})</h3>

                <div className={styles.list}>
                    {statuses.map(s => (
                        <div key={s.uuid} className={styles.item}>
                            <div className={styles.itemContent}>
                                <span className={styles.name}>{s.name}</span>
                                {s.message && (
                                    <span className={`${styles.message} ${s.status === 'error' ? styles.errorText : ''}`}>
                                        {s.message}
                                    </span>
                                )}
                            </div>
                            <div className={styles.status}>
                                {s.status === 'pending' && <Clock className={styles.pending} size={20} />}
                                {s.status === 'processing' && <Loader2 className={styles.spin} size={20} />}
                                {s.status === 'success' && <CheckCircle2 className={styles.success} size={20} />}
                                {s.status === 'error' && <XCircle className={styles.error} size={20} />}
                            </div>
                        </div>
                    ))}
                </div>

                <div className={styles.actions}>
                    {overallStatus === 'idle' && (
                        <>
                            <button onClick={onClose} className={styles.cancelBtn}>Cancelar</button>
                            <button onClick={startProcessing} className={styles.confirmBtn}>
                                Iniciar Acción
                            </button>
                        </>
                    )}
                    {overallStatus === 'processing' && (
                        <button disabled className={styles.processingBtn}>Procesando...</button>
                    )}
                    {overallStatus === 'completed' && (
                        <button onClick={onClose} className={styles.closeBtn}>Cerrar</button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default BulkProgressModal;
