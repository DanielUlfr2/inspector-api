import React from 'react';
import { Save, User, MapPin, Cpu, Info } from 'lucide-react';
import { useProvisionForm } from '../../hooks/useProvisionForm';
import styles from './Provision.module.css';
import SearchableSelect from '../Common/SearchableSelect';

interface Props {
    device: any;
    onSuccess: () => void;
}

const ProvisionModal: React.FC<Props> = ({ device, onSuccess }) => {
    const { formData, handleChange, options, filtered, loading, isSubmitting, submit } =
        useProvisionForm(device.uuidinspector, device);

    if (loading) return <div className={styles.loader}>Cargando parámetros de red...</div>;

    const handleFormSubmit = async () => {
        const res = await submit();
        if (res.success) {
            alert("Dispositivo provisionado e inventariado correctamente.");
            onSuccess();
        } else {
            alert("Error al procesar la provisión.");
        }
    };

    // Helper para mapear opciones
    const toOptions = (list: any[], valueKey: string, labelKey: string) => {
        if (!list) return [];
        return list.map(item => ({
            value: item[valueKey],
            label: item[labelKey]
        }));
    };

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <Info size={20} color="#00377B" />
                <h2>Panel de Provisión e Inventario</h2>
            </header>

            <div className={styles.formGrid}>
                {/* GRUPO 1: DATOS CLIENTE */}
                <section className={styles.section}>
                    <h3><User size={16} /> Datos del Servicio</h3>
                    <input
                        placeholder="ID de Servicio (ej: CNT-123)"
                        value={formData.inspector_service_id}
                        onChange={e => handleChange('inspector_service_id', e.target.value)}
                    />
                    <input
                        placeholder="Nombre completo del cliente"
                        value={formData.client_name}
                        onChange={e => handleChange('client_name', e.target.value)}
                    />
                    <input
                        placeholder="Dirección de instalación"
                        value={formData.address}
                        onChange={e => handleChange('address', e.target.value)}
                    />

                    {/* Selectores de Clasificación */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                        <SearchableSelect
                            placeholder="Producto"
                            value={formData.product_id}
                            onChange={(val) => handleChange('product_id', val)}
                            options={toOptions(options?.products || [], 'idproduct', 'strproductname')}
                        />

                        <SearchableSelect
                            placeholder="Tecnología"
                            value={formData.technology_id}
                            onChange={(val) => handleChange('technology_id', val)}
                            options={toOptions(options?.technologies || [], 'idtechnology', 'strtechnologyname')}
                        />

                        <SearchableSelect
                            placeholder="Tipo Svc"
                            value={formData.service_type_id}
                            onChange={(val) => handleChange('service_type_id', val)}
                            options={toOptions(options?.service_types || [], 'idservicetype', 'strservicetypename')}
                        />

                        <SearchableSelect
                            placeholder="CRM"
                            value={formData.crm_id}
                            onChange={(val) => handleChange('crm_id', val)}
                            options={toOptions(options?.crms || [], 'idcrm', 'strcrmname')}
                        />
                    </div>
                </section>

                {/* GRUPO 2: UBICACIÓN TÉCNICA (Mapeo corregido a BD) */}
                <section className={styles.section}>
                    <h3><MapPin size={16} /> Ubicación y OLT</h3>

                    <SearchableSelect
                        placeholder="Seleccione País"
                        value={formData.country_id}
                        onChange={(val) => handleChange('country_id', val)}
                        options={toOptions(options?.countries || [], 'idcountry', 'strcountryname')}
                    />

                    <SearchableSelect
                        placeholder="Seleccione Región"
                        value={formData.region_id}
                        onChange={(val) => handleChange('region_id', val)}
                        options={toOptions(filtered.regions || [], 'idregion', 'strregionname')}
                        disabled={!formData.country_id}
                    />

                    <SearchableSelect
                        placeholder="Seleccione Departamento"
                        value={formData.department_id}
                        onChange={(val) => handleChange('department_id', val)}
                        options={toOptions(filtered.departments || [], 'iddepartment', 'strdepartmentname')}
                        disabled={!formData.region_id}
                    />

                    <SearchableSelect
                        placeholder="Seleccione Ciudad"
                        value={formData.city_id}
                        onChange={(val) => handleChange('city_id', val)}
                        options={toOptions(filtered.cities || [], 'idcity', 'strcityname')}
                        disabled={!formData.department_id}
                    />

                    <SearchableSelect
                        placeholder="Seleccione OLT / CMTS"
                        value={formData.cmts_olt_id}
                        onChange={(val) => handleChange('cmts_olt_id', val)}
                        options={toOptions(filtered.olts || [], 'idcmtsolt', 'strcmtsoltname')}
                        disabled={!formData.city_id}
                    />
                </section>

                {/* GRUPO 3: CONFIGURACIÓN FINAL */}
                <section className={styles.section}>
                    <h3><Cpu size={16} /> Parámetros del Dispositivo</h3>
                    <input
                        className={styles.highlightInput}
                        placeholder="NUEVO NOMBRE (Hostname)"
                        value={formData.new_device_name}
                        onChange={e => handleChange('new_device_name', e.target.value)}
                    />
                    <div className={styles.speedRow}>
                        <label>Down: <input type="number" value={formData.down_speed} onChange={e => handleChange('down_speed', +e.target.value)} /> Mbps</label>
                        <label>Up: <input type="number" value={formData.up_speed} onChange={e => handleChange('up_speed', +e.target.value)} /> Mbps</label>
                    </div>

                    <SearchableSelect
                        placeholder="-- Cambiar Estado --"
                        value={formData.status_id}
                        onChange={(val) => handleChange('status_id', val)}
                        options={toOptions(options?.statuses || [], 'idinventoryinspectorstatus', 'strinventorystatus')}
                        className={styles.statusSelect}
                    />
                </section>
            </div>

            <button
                className={styles.submitBtn}
                onClick={handleFormSubmit}
                disabled={isSubmitting || !formData.new_device_name || formData.status_id === 0}
            >
                <Save size={18} /> {isSubmitting ? 'Procesando...' : 'Confirmar e Inventariar'}
            </button>
        </div>
    );
};

export default ProvisionModal;