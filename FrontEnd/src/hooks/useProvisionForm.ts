import { useState, useEffect, useMemo } from 'react';
import { deviceService } from '../features/devices/deviceService';
import { FormOptions, ProvisionPayload } from '../types/provision';
import { Device } from '../types/device';

export const useProvisionForm = (uuid: string, initialDevice?: Device | null) => {
    const [options, setOptions] = useState<FormOptions | null>(null);
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [formData, setFormData] = useState({
        country_id: 0, // El país no suele venir en el service, se elige manualmente o se infiere
        region_id: 0,
        department_id: 0,
        city_id: initialDevice?.city_id || 0,
        cmts_olt_id: initialDevice?.cmts_olt_id || 0,
        product_id: initialDevice?.product_id || 0,
        technology_id: initialDevice?.technology_id || 0,
        service_type_id: initialDevice?.service_type_id || 0,
        crm_id: initialDevice?.crm_id || 0,
        status_id: initialDevice?.idinventoryinspectorstatus || 0,
        inspector_service_id: initialDevice?.inspector_service_id || '',
        client_name: initialDevice?.client_name || '',
        address: initialDevice?.address || '',
        down_speed: initialDevice?.down_speed || 100,
        up_speed: initialDevice?.up_speed || 50,
        new_device_name: initialDevice?.strinspectorname || ''
    });

    // Sincronizar cuando el dispositivo cargue (importante para el modo edición)
    useEffect(() => {
        if (initialDevice) {
            setFormData(prev => ({
                ...prev,
                city_id: initialDevice.city_id || 0,
                cmts_olt_id: initialDevice.cmts_olt_id || 0,
                product_id: initialDevice.product_id || 0,
                technology_id: initialDevice.technology_id || 0,
                service_type_id: initialDevice.service_type_id || 0,
                crm_id: initialDevice.crm_id || 0,
                status_id: initialDevice.idinventoryinspectorstatus || 0,
                inspector_service_id: initialDevice.inspector_service_id || '',
                client_name: initialDevice.client_name || '',
                address: initialDevice.address || '',
                down_speed: initialDevice.down_speed || 100,
                up_speed: initialDevice.up_speed || 50,
                new_device_name: initialDevice.strinspectorname || ''
            }));
        }
    }, [initialDevice]);

    useEffect(() => {
        deviceService.getFormOptions()
            .then(setOptions)
            .finally(() => setLoading(false));
    }, []);

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
        setIsSubmitting(true);
        try {
            const { country_id, region_id, department_id, ...payload } = formData;
            await deviceService.provisionDevice(uuid, payload as ProvisionPayload);
            return { success: true };
        } catch (error) {
            return { success: false };
        } finally {
            setIsSubmitting(false);
        }
    };

    return { formData, handleChange, options, filtered, loading, isSubmitting, submit };
};