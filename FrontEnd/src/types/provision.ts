// types/provision.ts
export interface CatalogItem { id: number; name: string;[key: string]: any; }

export interface FormOptions {
    countries: Array<{ idcountry: number; strcountryname: string }>;
    regions: Array<{ idregion: number; strregionname: string; idcountry: number }>;
    departments: Array<{ iddepartment: number; strdepartmentname: string; idregion: number }>;
    cities: Array<{ idcity: number; strcityname: string; iddepartment: number }>;
    cmts_olts: Array<{ idcmtsolt: number; strcmtsoltname: string; idcity: number }>;
    products: Array<{ idproduct: number; strproductname: string }>;
    technologies: Array<{ idtechnology: number; strtechnologyname: string }>;
    service_types: Array<{ idservicetype: number; strservicetypename: string }>;
    crms: Array<{ idcrm: number; strcrmname: string }>;
    statuses: Array<{ idinventoryinspectorstatus: number; strinventorystatus: string }>;
}

export interface ProvisionPayload {
    inspector_service_id: string;
    city_id: number;
    cmts_olt_id: number;
    product_id: number;
    technology_id: number;
    service_type_id: number;
    crm_id: number;
    address: string;
    client_name: string;
    down_speed: number;
    up_speed: number;
    new_device_name: string;
    status_id: number;
}