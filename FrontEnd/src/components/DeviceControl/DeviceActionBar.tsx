// src/components/DeviceControl/DeviceActionBar.tsx
import { useState } from 'react';
import { Power, RotateCw, RefreshCcw } from 'lucide-react';
import { useDeviceControl } from '../../features/devices/hooks/useDeviceControl';
import { DeviceAction } from '../../features/devices/deviceService';
import ActionModal from './ActionModal';
import styles from './DeviceActionBar.module.css';

interface Props {
    selectedUuids: string[];
    onActionComplete?: () => void;
}

const DeviceActionBar = ({ selectedUuids, onActionComplete }: Props) => {
    const { executeAction, status, setStatus } = useDeviceControl();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentAction, setCurrentAction] = useState<DeviceAction | 'idle'>('idle');

    const triggerAction = (action: DeviceAction) => {
        setCurrentAction(action);
        setStatus('idle');
        setIsModalOpen(true);
    };

    const handleConfirm = async () => {
        if (currentAction === 'idle') return;
        const success = await executeAction(selectedUuids, currentAction);

        // Si fue exitoso, esperamos un momento para que el usuario vea el "200 OK"
        if (success && onActionComplete) {
            setTimeout(() => {
                setIsModalOpen(false);
                onActionComplete();
            }, 1500);
        }
    };

    if (selectedUuids.length === 0) return null;

    return (
        <>
            <div className={styles.bar}>
                <span className={styles.label}>{selectedUuids.length} equipos seleccionados</span>
                <div className={styles.group}>
                    <button onClick={() => triggerAction('restart')}>
                        <RefreshCcw size={16} /> Restart
                    </button>
                    <button onClick={() => triggerAction('reboot')}>
                        <RotateCw size={16} /> Reboot
                    </button>
                    <button
                        onClick={() => triggerAction('shutdown')}
                        className={styles.danger}
                        disabled={selectedUuids.length > 1}
                    >
                        <Power size={16} /> Shutdown
                    </button>
                </div>
            </div>

            <ActionModal
                isOpen={isModalOpen}
                action={currentAction}
                count={selectedUuids.length}
                status={status}
                onConfirm={handleConfirm}
                onClose={() => setIsModalOpen(false)}
            />
        </>
    );
};

export default DeviceActionBar;