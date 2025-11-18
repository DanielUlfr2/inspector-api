import { Registro } from '../types/Registro';

const isDemoMode =
  import.meta.env.VITE_DEMO_MODE === 'true' ||
  import.meta.env.MODE === 'demo';

// Datos de demostración para registros
export const DEMO_REGISTROS: Registro[] = [
  {
    id: 1,
    numero_inspector: 1001,
    uuid: 'uuid-demo-001',
    nombre: 'ins1001 Equipo Principal',
    observaciones: 'Equipo en buen estado, requiere mantenimiento preventivo',
    status: 'activo',
    region: 'Norte',
    flota: 'Flota A',
    encargado: 'Juan Pérez',
    celular: '3001234567',
    correo: 'juan.perez@example.com',
    direccion: 'Calle 123 #45-67',
    uso: 'Residencial',
    departamento: 'Antioquia',
    ciudad: 'Medellín',
    tecnologia: 'FTTH',
    cmts_olt: 'OLT-001',
    id_servicio: 'SERV-001',
    mac_sn: 'AA:BB:CC:DD:EE:01'
  },
  {
    id: 2,
    numero_inspector: 1002,
    uuid: 'uuid-demo-002',
    nombre: 'ins1002 Estación Central',
    observaciones: 'Instalación nueva, funcionando correctamente',
    status: 'activo',
    region: 'Sur',
    flota: 'Flota B',
    encargado: 'María García',
    celular: '3009876543',
    correo: 'maria.garcia@example.com',
    direccion: 'Carrera 78 #90-12',
    uso: 'Comercial',
    departamento: 'Valle del Cauca',
    ciudad: 'Cali',
    tecnologia: 'HFC',
    cmts_olt: 'CMTS-002',
    id_servicio: 'SERV-002',
    mac_sn: 'FF:EE:DD:CC:BB:02'
  },
  {
    id: 3,
    numero_inspector: 1003,
    uuid: 'uuid-demo-003',
    nombre: 'ins1003 Punto de Acceso',
    observaciones: 'Requiere revisión técnica urgente',
    status: 'inactivo',
    region: 'Centro',
    flota: 'Flota C',
    encargado: 'Carlos Rodríguez',
    celular: '3015551234',
    correo: 'carlos.rodriguez@example.com',
    direccion: 'Avenida Principal #234',
    uso: 'Residencial',
    departamento: 'Cundinamarca',
    ciudad: 'Bogotá',
    tecnologia: 'FTTH',
    cmts_olt: 'OLT-003',
    id_servicio: 'SERV-003',
    mac_sn: '11:22:33:44:55:03'
  },
  {
    id: 4,
    numero_inspector: 1004,
    uuid: 'uuid-demo-004',
    nombre: 'ins1004 Terminal Remoto',
    observaciones: 'Equipo en mantenimiento programado',
    status: 'activo',
    region: 'Norte',
    flota: 'Flota A',
    encargado: 'Ana López',
    celular: '3026667890',
    correo: 'ana.lopez@example.com',
    direccion: 'Transversal 56 #78-90',
    uso: 'Comercial',
    departamento: 'Antioquia',
    ciudad: 'Medellín',
    tecnologia: 'HFC',
    cmts_olt: 'CMTS-004',
    id_servicio: 'SERV-004',
    mac_sn: 'AA:11:BB:22:CC:04'
  },
  {
    id: 5,
    numero_inspector: 1005,
    uuid: 'uuid-demo-005',
    nombre: 'ins1005 Nodo Distrital',
    observaciones: 'Operación normal, sin incidencias',
    status: 'activo',
    region: 'Sur',
    flota: 'Flota B',
    encargado: 'Luis Martínez',
    celular: '3037778901',
    correo: 'luis.martinez@example.com',
    direccion: 'Diagonal 89 #12-34',
    uso: 'Residencial',
    departamento: 'Valle del Cauca',
    ciudad: 'Cali',
    tecnologia: 'FTTH',
    cmts_olt: 'OLT-005',
    id_servicio: 'SERV-005',
    mac_sn: 'DD:33:EE:44:FF:05'
  },
  {
    id: 6,
    numero_inspector: 1006,
    uuid: 'uuid-demo-006',
    nombre: 'ins1006 Hub Regional',
    observaciones: 'Actualización de firmware pendiente',
    status: 'activo',
    region: 'Centro',
    flota: 'Flota C',
    encargado: 'Sofia Hernández',
    celular: '3048889012',
    correo: 'sofia.hernandez@example.com',
    direccion: 'Circunvalar 123 #45-67',
    uso: 'Comercial',
    departamento: 'Cundinamarca',
    ciudad: 'Bogotá',
    tecnologia: 'HFC',
    cmts_olt: 'CMTS-006',
    id_servicio: 'SERV-006',
    mac_sn: '11:AA:22:BB:33:06'
  },
  {
    id: 7,
    numero_inspector: 1007,
    uuid: 'uuid-demo-007',
    nombre: 'ins1007 Estación Satelital',
    observaciones: 'Nueva instalación, en fase de pruebas',
    status: 'activo',
    region: 'Norte',
    flota: 'Flota A',
    encargado: 'Diego Ramírez',
    celular: '3059990123',
    correo: 'diego.ramirez@example.com',
    direccion: 'Calle 234 #56-78',
    uso: 'Residencial',
    departamento: 'Antioquia',
    ciudad: 'Medellín',
    tecnologia: 'FTTH',
    cmts_olt: 'OLT-007',
    id_servicio: 'SERV-007',
    mac_sn: '44:CC:55:DD:66:07'
  },
  {
    id: 8,
    numero_inspector: 1008,
    uuid: 'uuid-demo-008',
    nombre: 'ins1008 Punto de Conexión',
    observaciones: 'Funcionamiento óptimo',
    status: 'activo',
    region: 'Sur',
    flota: 'Flota B',
    encargado: 'Laura Torres',
    celular: '3061112345',
    correo: 'laura.torres@example.com',
    direccion: 'Avenida 345 #67-89',
    uso: 'Comercial',
    departamento: 'Valle del Cauca',
    ciudad: 'Cali',
    tecnologia: 'HFC',
    cmts_olt: 'CMTS-008',
    id_servicio: 'SERV-008',
    mac_sn: '77:EE:88:FF:99:08'
  },
  {
    id: 9,
    numero_inspector: 1009,
    uuid: 'uuid-demo-009',
    nombre: 'ins1009 Terminal Local',
    observaciones: 'Requiere cambio de cableado',
    status: 'inactivo',
    region: 'Centro',
    flota: 'Flota C',
    encargado: 'Roberto Sánchez',
    celular: '3072223456',
    correo: 'roberto.sanchez@example.com',
    direccion: 'Carrera 456 #78-90',
    uso: 'Residencial',
    departamento: 'Cundinamarca',
    ciudad: 'Bogotá',
    tecnologia: 'FTTH',
    cmts_olt: 'OLT-009',
    id_servicio: 'SERV-009',
    mac_sn: 'AA:11:BB:22:CC:09'
  },
  {
    id: 10,
    numero_inspector: 1010,
    uuid: 'uuid-demo-010',
    nombre: 'ins1010 Nodo Urbano',
    observaciones: 'Equipo en excelente estado',
    status: 'activo',
    region: 'Norte',
    flota: 'Flota A',
    encargado: 'Patricia Morales',
    celular: '3083334567',
    correo: 'patricia.morales@example.com',
    direccion: 'Transversal 567 #89-01',
    uso: 'Comercial',
    departamento: 'Antioquia',
    ciudad: 'Medellín',
    tecnologia: 'HFC',
    cmts_olt: 'CMTS-010',
    id_servicio: 'SERV-010',
    mac_sn: 'DD:33:EE:44:FF:10'
  }
];

// Datos de demostración para usuarios
export const DEMO_USUARIOS = [
  {
    id: 1,
    username: 'demo',
    email: 'demo@example.com',
    nombre: 'Demo',
    apellido: 'Admin',
    rol: 'admin',
    foto_perfil: null,
    fecha_creacion: new Date().toISOString(),
    activo: true
  },
  {
    id: 2,
    username: 'usuario1',
    email: 'usuario1@example.com',
    nombre: 'Usuario',
    apellido: 'Uno',
    rol: 'user',
    foto_perfil: null,
    fecha_creacion: new Date().toISOString(),
    activo: true
  },
  {
    id: 3,
    username: 'usuario2',
    email: 'usuario2@example.com',
    nombre: 'Usuario',
    apellido: 'Dos',
    rol: 'user',
    foto_perfil: null,
    fecha_creacion: new Date().toISOString(),
    activo: true
  }
];

// Historial de cambios de demostración
export const DEMO_HISTORIAL = [
  {
    fecha: new Date().toISOString(),
    descripcion: 'Registro creado',
    autor: 'Demo Admin',
    campo: null,
    valor_anterior: null,
    valor_nuevo: null,
    usuario: 'Demo Admin'
  },
  {
    fecha: new Date(Date.now() - 86400000).toISOString(),
    descripcion: 'Campo status modificado',
    autor: 'Demo Admin',
    campo: 'status',
    valor_anterior: 'inactivo',
    valor_nuevo: 'activo',
    usuario: 'Demo Admin'
  }
];

// Valores únicos para filtros
export const DEMO_UNIQUE_VALUES: { [key: string]: string[] } = {
  status: ['activo', 'inactivo'],
  region: ['Norte', 'Sur', 'Centro'],
  flota: ['Flota A', 'Flota B', 'Flota C'],
  uso: ['Residencial', 'Comercial'],
  departamento: ['Antioquia', 'Valle del Cauca', 'Cundinamarca'],
  ciudad: ['Medellín', 'Cali', 'Bogotá'],
  tecnologia: ['FTTH', 'HFC'],
  encargado: ['Juan Pérez', 'María García', 'Carlos Rodríguez', 'Ana López', 'Luis Martínez', 'Sofia Hernández', 'Diego Ramírez', 'Laura Torres', 'Roberto Sánchez', 'Patricia Morales']
};

export function getDemoData() {
  return {
    registros: DEMO_REGISTROS,
    usuarios: DEMO_USUARIOS,
    historial: DEMO_HISTORIAL,
    uniqueValues: DEMO_UNIQUE_VALUES
  };
}

export default getDemoData;

