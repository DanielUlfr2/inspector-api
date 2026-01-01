import React from 'react';
import { Save, User, MapPin, Cpu, Info } from 'lucide-react';
import { useProvisionForm } from '../../hooks/useProvisionForm';
import styles from './Provision.module.css';

interface Props {
    device: any;
    onSuccess: () => void;
}

const ProvisionModal: React.FC<Props> = ({ device, onSuccess }) => {
    const { formData, handleChange, options, filtered, loading, isSubmitting, submit } =
        useProvisionForm(device.uuidinspector);

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

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <Info size={20} color="#a855f7" />
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
                        <select value={formData.product_id} onChange={e => handleChange('product_id', +e.target.value)}>
                            <option value={0}>Producto</option>
                            {options?.products.map(p => (
                                <option key={p.idproduct} value={p.idproduct}>{p.strproductname}</option>
                            ))}
                        </select>

                        <select value={formData.technology_id} onChange={e => handleChange('technology_id', +e.target.value)}>
                            <option value={0}>Tecnología</option>
                            {options?.technologies.map(t => (
                                <option key={t.idtechnology} value={t.idtechnology}>{t.strtechnologyname}</option>
                            ))}
                        </select>

                        <select value={formData.service_type_id} onChange={e => handleChange('service_type_id', +e.target.value)}>
                            <option value={0}>Tipo Svc</option>
                            {options?.service_types.map(s => (
                                <option key={s.idservicetype} value={s.idservicetype}>{s.strservicetypename}</option>
                            ))}
                        </select>

                        <select value={formData.crm_id} onChange={e => handleChange('crm_id', +e.target.value)}>
                            <option value={0}>CRM</option>
                            {options?.crms.map(c => (
                                <option key={c.idcrm} value={c.idcrm}>{c.strcrmname}</option>
                            ))}
                        </select>
                    </div>
                </section>

                {/* GRUPO 2: UBICACIÓN TÉCNICA (Mapeo corregido a BD) */}
                <section className={styles.section}>
                    <h3><MapPin size={16} /> Ubicación y OLT</h3>

                    {/* Países */}
                    <select value={formData.country_id} onChange={e => handleChange('country_id', +e.target.value)}>
                        <option value={0}>Seleccione País</option>
                        {options?.countries.map(c => (
                            <option key={c.idcountry} value={c.idcountry}>{c.strcountryname}</option>
                        ))}
                    </select>

                    {/* Regiones */}
                    <select disabled={!formData.country_id} value={formData.region_id} onChange={e => handleChange('region_id', +e.target.value)}>
                        <option value={0}>Seleccione Región</option>
                        {filtered.regions.map(r => (
                            <option key={r.idregion} value={r.idregion}>{r.strregionname}</option>
                        ))}
                    </select>

                    {/* Departamentos */}
                    <select disabled={!formData.region_id} value={formData.department_id} onChange={e => handleChange('department_id', +e.target.value)}>
                        <option value={0}>Seleccione Departamento</option>
                        {filtered.departments.map(d => (
                            <option key={d.iddepartment} value={d.iddepartment}>{d.strdepartmentname}</option>
                        ))}
                    </select>

                    {/* Ciudades */}
                    <select disabled={!formData.department_id} value={formData.city_id} onChange={e => handleChange('city_id', +e.target.value)}>
                        <option value={0}>Seleccione Ciudad</option>
                        {filtered.cities.map(c => (
                            <option key={c.idcity} value={c.idcity}>{c.strcityname}</option>
                        ))}
                    </select>

                    {/* OLT / CMTS */}
                    <select disabled={!formData.city_id} value={formData.cmts_olt_id} onChange={e => handleChange('cmts_olt_id', +e.target.value)}>
                        <option value={0}>Seleccione OLT / CMTS</option>
                        {filtered.olts.map(o => (
                            <option key={o.idcmtsolt} value={o.idcmtsolt}>{o.strcmtsoltname}</option>
                        ))}
                    </select>
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

                    {/* Estados de Inventario */}
                    <select className={styles.statusSelect} value={formData.status_id} onChange={e => handleChange('status_id', +e.target.value)}>
                        <option value={0}>-- Cambiar Estado --</option>
                        {options?.statuses.map(s => (
                            <option key={s.idinventoryinspectorstatus} value={s.idinventoryinspectorstatus}>
                                {s.strinventorystatus}
                            </option>
                        ))}
                    </select>
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