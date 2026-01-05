// src/components/DateRange/CustomDatePicker.tsx
import { useState, useRef, useEffect } from 'react';
import styles from './CustomDatePicker.module.css';

interface CustomDatePickerProps {
    onApply: (start: string, end: string) => void;
    onCancel: () => void;
    initialStart?: string;
    initialEnd?: string;
}

const CustomDatePicker = ({ onApply, onCancel, initialStart, initialEnd }: CustomDatePickerProps) => {
    const [startDate, setStartDate] = useState(initialStart || '');
    const [endDate, setEndDate] = useState(initialEnd || '');
    const containerRef = useRef<HTMLDivElement>(null); // Ref para detectar el clic fuera

    // Lógica para cerrar al hacer clic fuera
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                onCancel();
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [onCancel]);

    const handleQuickSet = (days: number) => {
        const end = new Date();
        const start = new Date();
        start.setDate(start.getDate() - days);

        // Función para formatear fecha local en formato datetime-local (YYYY-MM-DDTHH:mm)
        const formatLocalDateTime = (date: Date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${year}-${month}-${day}T${hours}:${minutes}`;
        };

        setStartDate(formatLocalDateTime(start));
        setEndDate(formatLocalDateTime(end));
    };

    return (
        <div className={styles.container} ref={containerRef}>
            <div className={styles.card}>
                <h4 className={styles.title}>Seleccionar Rango de Fechas</h4>

                <div className={styles.quickDateButtons}>
                    <button onClick={() => handleQuickSet(1)} className={styles.quickDateBtn}>Último día</button>
                    <button onClick={() => handleQuickSet(7)} className={styles.quickDateBtn}>Última semana</button>
                    <button onClick={() => handleQuickSet(30)} className={styles.quickDateBtn}>Último mes</button>
                </div>

                <div className={styles.dateInputs}>
                    <div className={styles.inputGroup}>
                        <label>Fecha Inicio</label>
                        <input
                            type="datetime-local"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            className={styles.dateInput}
                        />
                    </div>
                    <div className={styles.inputGroup}>
                        <label>Fecha Fin</label>
                        <input
                            type="datetime-local"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            className={styles.dateInput}
                        />
                    </div>
                </div>

                <div className={styles.actions}>
                    <button onClick={onCancel} className={styles.cancelBtn}>Cancelar</button>
                    <button
                        onClick={() => onApply(startDate, endDate)}
                        className={styles.applyBtn}
                        disabled={!startDate || !endDate}
                    >
                        Aplicar Rango
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CustomDatePicker;