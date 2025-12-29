// src/components/DateRange/DateRangeSelector.tsx
import { Clock, Calendar } from 'lucide-react'; // Añadimos iconos
import { TimeRange } from '../../types/history';
import styles from './DateRangeSelector.module.css';

interface DateRangeSelectorProps {
    selectedRange: TimeRange;
    onRangeChange: (range: TimeRange) => void;
    customButtonRef?: React.RefObject<HTMLButtonElement>;
}

const DateRangeSelector = ({ selectedRange, onRangeChange, customButtonRef }: DateRangeSelectorProps) => {
    const ranges: { value: TimeRange; label: string; icon: React.ReactNode }[] = [
        { value: '6h', label: '6h', icon: <Clock size={14} /> },
        { value: '12h', label: '12h', icon: <Clock size={14} /> },
        { value: '24h', label: '24h', icon: <Clock size={14} /> },
        { value: 'custom', label: 'Personalizado', icon: <Calendar size={14} /> },
    ];

    return (
        <div className={styles.container}>
            {ranges.map((range) => (
                <button
                    key={range.value}
                    ref={range.value === 'custom' ? customButtonRef : null}
                    onClick={() => onRangeChange(range.value)}
                    className={`${styles.btn} ${selectedRange === range.value ? styles.active : ''}`}
                >
                    <span className={styles.icon}>{range.icon}</span>
                    <span className={styles.label}>{range.label}</span>
                </button>
            ))}
        </div>
    );
};

export default DateRangeSelector;