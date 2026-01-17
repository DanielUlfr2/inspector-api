import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search } from 'lucide-react';
import styles from './CustomDropdown.module.css';

export interface DropdownOption {
    value: number;
    label: string;
}

interface Props {
    options: DropdownOption[];
    value: number;
    onChange: (value: number) => void;
    placeholder?: string;
    disabled?: boolean;
}

const CustomDropdown: React.FC<Props> = ({
    options,
    value,
    onChange,
    placeholder = 'Seleccionar...',
    disabled = false
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const dropdownRef = useRef<HTMLDivElement>(null);
    const searchInputRef = useRef<HTMLInputElement>(null);

    const selectedOption = options.find(opt => opt.value === value);

    const filteredOptions = options.filter(option =>
        option.label.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
                setSearchTerm('');
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen]);

    // Focus search input when dropdown opens
    useEffect(() => {
        if (isOpen && searchInputRef.current) {
            searchInputRef.current.focus();
        }
    }, [isOpen]);

    const handleToggle = () => {
        if (!disabled) {
            setIsOpen(!isOpen);
            if (isOpen) {
                setSearchTerm('');
            }
        }
    };

    const handleSelect = (optionValue: number) => {
        onChange(optionValue);
        setIsOpen(false);
        setSearchTerm('');
    };

    return (
        <div className={styles.container} ref={dropdownRef}>
            <button
                type="button"
                className={`${styles.trigger} ${isOpen ? styles.triggerOpen : ''} ${disabled ? styles.triggerDisabled : ''}`}
                onClick={handleToggle}
                disabled={disabled}
            >
                <span className={styles.triggerText}>
                    {selectedOption ? selectedOption.label : placeholder}
                </span>
                <ChevronDown
                    size={20}
                    className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ''}`}
                />
            </button>

            {isOpen && (
                <div className={styles.dropdown}>
                    <div className={styles.searchContainer}>
                        <Search size={16} className={styles.searchIcon} />
                        <input
                            ref={searchInputRef}
                            type="text"
                            className={styles.searchInput}
                            placeholder="Buscar dispositivo..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            onClick={(e) => e.stopPropagation()}
                        />
                    </div>

                    <div className={styles.optionsList}>
                        {filteredOptions.length === 0 ? (
                            <div className={styles.noResults}>
                                No se encontraron resultados
                            </div>
                        ) : (
                            filteredOptions.map((option) => (
                                <button
                                    key={option.value}
                                    type="button"
                                    className={`${styles.option} ${option.value === value ? styles.optionSelected : ''}`}
                                    onClick={() => handleSelect(option.value)}
                                >
                                    {option.label}
                                </button>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default CustomDropdown;
