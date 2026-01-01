import { useState, useEffect, useMemo } from 'react';
import { deviceService } from '../features/devices/deviceService';
import { FormOptions, ProvisionPayload } from '../types/provision';

export const useProvisionForm = (uuid: string) => {
    const [options, setOptions] = useState<FormOptions | null>(null);
    const [loading, setLoading] = useState(true);
    // 1. Definimos el estado de envío
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [formData, setFormData] = useState({
        country_id: 0,
        region_id: 0,
        department_id: 0,
        city_id: 0,
        cmts_olt_id: 0,
        product_id: 0,
        technology_id: 0,
        service_type_id: 0,
        crm_id: 0,
        status_id: 0,
        inspector_service_id: '',
        client_name: '',
        address: '',
        down_speed: 100,
        up_speed: 50,
        new_device_name: ''
    });

    useEffect(() => {
        deviceService.getFormOptions()
            .then(setOptions)
            .finally(() => setLoading(false));
    }, []);

    // 2. Filtros usando las llaves de tu repositorio (Postgres)
    const filtered = useMemo(() => ({
        regions: options?.regions.filter(r => r.idcountry === formData.country_id) || [],
        departments: options?.departments.filter(d => d.idregion === formData.region_id) || [],
        cities: options?.cities.filter(c => c.iddepartment === formData.department_id) || [],
        olts: options?.cmts_olts.filter(o => o.idcity === formData.city_id) || []
    }), [formData, options]);

    const handleChange = (field: string, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const submit = async () => {
        // 3. Activamos el estado de carga
        setIsSubmitting(true);
        try {
            const { country_id, region_id, department_id, ...payload } = formData;
            await deviceService.provisionDevice(uuid, payload as ProvisionPayload);
            return { success: true };
        } catch (error) {
            console.error("Error en provisión:", error);
            return { success: false };
        } finally {
            // 4. Desactivamos el estado de carga
            setIsSubmitting(false);
        }
    };

    // IMPORTANTE: Asegúrate de devolver isSubmitting aquí
    return {
        formData,
        handleChange,
        options,
        filtered,
        loading,
        isSubmitting, // <-- Esto es lo que te faltaba
        submit
    };
};