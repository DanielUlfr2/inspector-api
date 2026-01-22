import { useState, useEffect, useRef } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import styles from './SearchableSelect.module.css';

interface Option {
    value: string | number;
    label: string;
}

interface SearchableSelectProps {
    value: string | number;
    onChange: (value: any) => void;
    options: Option[];
    placeholder?: string;
    disabled?: boolean;
    className?: string;
}

const SearchableSelect = ({
    value,
    onChange,
    options = [],
    placeholder = 'Seleccionar...',
    disabled = false,
    className = ''
}: SearchableSelectProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const containerRef = useRef<HTMLDivElement>(null);
    const searchInputRef = useRef<HTMLInputElement>(null);

    const filteredOptions = options.filter(opt =>
        opt.label.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const selectedOption = options.find(opt => opt.value === value);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        if (isOpen && searchInputRef.current) {
            searchInputRef.current.focus();
        } else {
            setSearchTerm(''); // Reset search on close
        }
    }, [isOpen]);

    const handleSelect = (val: string | number) => {
        onChange(val);
        setIsOpen(false);
    };

    return (
        <div className={`${styles.container} ${className}`} ref={containerRef}>
            <div
                className={`${styles.trigger} ${isOpen ? styles.open : ''} ${disabled ? styles.disabled : ''}`}
                onClick={() => !disabled && setIsOpen(!isOpen)}
            >
                <span className={selectedOption ? '' : styles.placeholder}>
                    {selectedOption ? selectedOption.label : placeholder}
                </span>
                {isOpen ? <ChevronUp size={16} color="#00C8FF" /> : <ChevronDown size={16} color="#64748b" />}
            </div>

            {isOpen && !disabled && (
                <div className={styles.dropdown}>
                    <div className={styles.searchBox}>
                        <input
                            ref={searchInputRef}
                            type="text"
                            className={styles.searchInput}
                            placeholder="Buscar..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            onClick={(e) => e.stopPropagation()}
                        />
                    </div>
                    <div className={styles.optionsList}>
                        {filteredOptions.length > 0 ? (
                            filteredOptions.map((opt) => (
                                <div
                                    key={opt.value}
                                    className={`${styles.option} ${opt.value === value ? styles.selected : ''}`}
                                    onClick={() => handleSelect(opt.value)}
                                >
                                    {opt.label}
                                </div>
                            ))
                        ) : (
                            <div className={styles.noResults}>No hay resultados</div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SearchableSelect;
