export interface Registro {
  id: number;
  numero_inspector: number;
  nombre: string;
  observaciones: string;
  status: string;
  region: string;
  flota: string;
  encargado: string;
  celular: string;
  correo: string;
  direccion: string;
  uso: string;
  departamento: string;
  ciudad: string;
  tecnologia: string;
  cmts_olt: string;
  id_servicio: string;
  mac_sn: string;
  uuid?: string;
}

export interface RegistroCreate {
  numero_inspector: number;
  nombre: string;
  observaciones: string;
  status: string;
  region: string;
  flota: string;
  encargado: string;
  celular: string;
  correo: string;
  direccion: string;
  uso: string;
  departamento: string;
  ciudad: string;
  tecnologia: string;
  cmts_olt: string;
  id_servicio: string;
  mac_sn: string;
  uuid?: string;
}

export interface RegistroUpdate extends Partial<RegistroCreate> {}

export interface HistorialItem {
  fecha: string;
  descripcion: string;
  autor: string;
  campo?: string;
  valor_anterior?: string;
  valor_nuevo?: string;
  usuario?: string;
} 