import { useState } from 'react';
import { Power, RotateCw, RefreshCcw, Truck } from 'lucide-react';
import { DeviceAction, deviceService } from '../../features/devices/deviceService';
import { Device } from '../../types/device';
import BulkProgressModal from './BulkProgressModal';
import MoveDeviceModal from './MoveDeviceModal';
import styles from './DeviceActionBar.module.css';

interface Props {
    selectedDevices: Device[];
    onActionComplete?: () => void;
}

const DeviceActionBar = ({ selectedDevices, onActionComplete }: Props) => {
    const [isActionModalOpen, setIsActionModalOpen] = useState(false);
    const [isMoveModalOpen, setIsMoveModalOpen] = useState(false);
    const [currentAction, setCurrentAction] = useState<DeviceAction | 'idle'>('idle');

    const triggerAction = (action: DeviceAction) => {
        setCurrentAction(action);
        setIsActionModalOpen(true);
    };

    const handleMoveConfirm = async (targetFleetSlug: string) => {
        if (selectedDevices.length === 1) {
            await deviceService.moveDevice(selectedDevices[0].uuidinspector, targetFleetSlug);
            if (onActionComplete) onActionComplete();
        } else {
            alert('Por seguridad, mueva los dispositivos uno por uno.');
        }
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

                    {/* Move Button - Only supported for single device selection currently */}
                    <button
                        onClick={() => setIsMoveModalOpen(true)}
                        disabled={selectedDevices.length !== 1}
                        title={selectedDevices.length !== 1 ? "Seleccione un solo dispositivo para mover" : "Mover a otra flota"}
                    >
                        <Truck size={16} /> Mover
                    </button>

                    <button
                        onClick={() => triggerAction('shutdown')}
                        className={styles.danger}
                        disabled={selectedDevices.length > 1}
                        title={selectedDevices.length > 1 ? "Solo se puede apagar un equipo a la vez" : "Apagar equipo"}
                    >
                        <Power size={16} /> Shutdown
                    </button>
                </div>
            </div>

            {currentAction !== 'idle' && (
                <BulkProgressModal
                    isOpen={isActionModalOpen}
                    action={currentAction}
                    devices={selectedDevices}
                    onClose={() => {
                        setIsActionModalOpen(false);
                        setCurrentAction('idle');
                        if (onActionComplete) onActionComplete();
                    }}
                />
            )}

            {selectedDevices.length === 1 && (
                <MoveDeviceModal
                    isOpen={isMoveModalOpen}
                    onClose={() => setIsMoveModalOpen(false)}
                    onConfirm={handleMoveConfirm}
                    deviceName={selectedDevices[0].strinspectorname || selectedDevices[0].uuidinspector.substring(0, 7)}
                />
            )}
        </>
    );
};

export default DeviceActionBar;