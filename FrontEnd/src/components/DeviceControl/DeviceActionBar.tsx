// src/components/DeviceControl/DeviceActionBar.tsx
import { useState } from 'react';
import { Power, RotateCw, RefreshCcw } from 'lucide-react';
import { DeviceAction } from '../../features/devices/deviceService';
import { Device } from '../../types/device';
import BulkProgressModal from './BulkProgressModal';
import styles from './DeviceActionBar.module.css';

interface Props {
    selectedDevices: Device[];
    onActionComplete?: () => void;
}

const DeviceActionBar = ({ selectedDevices, onActionComplete }: Props) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentAction, setCurrentAction] = useState<DeviceAction | 'idle'>('idle');

    const triggerAction = (action: DeviceAction) => {
        setCurrentAction(action);
        setIsModalOpen(true);
    };

    if (selectedDevices.length === 0) return null;

    return (
        <>
            <div className={styles.bar}>
                <span className={styles.label}>
                    {selectedDevices.length} equipos seleccionados
                </span>
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
                    >
                        <Power size={16} /> Shutdown
                    </button>
                </div>
            </div>

            {currentAction !== 'idle' && (
                <BulkProgressModal
                    isOpen={isModalOpen}
                    action={currentAction}
                    devices={selectedDevices}
                    onClose={() => {
                        setIsModalOpen(false);
                        setCurrentAction('idle');
                        if (onActionComplete) onActionComplete();
                    }}
                />
            )}
        </>
    );
};

export default DeviceActionBar;