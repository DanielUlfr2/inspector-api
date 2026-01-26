# InspectorGestion 5.0 - System Overview

## 1. Propósito del Sistema

**InspectorGestion 5.0** es una plataforma de gestión y monitoreo centralizado de dispositivos IoT (Internet of Things) desplegados en campo, específicamente dispositivos tipo "Inspector" basados en la plataforma **Balena Cloud**. El sistema permite la administración remota, sincronización de inventario, monitoreo de métricas en tiempo real, y ejecución de acciones de control sobre flotas de dispositivos distribuidos geográficamente.

### Objetivos Principales

- **Gestión Centralizada**: Administrar múltiples flotas de dispositivos IoT desde una interfaz única
- **Sincronización Automática**: Mantener sincronizado el inventario local con Balena Cloud
- **Monitoreo en Tiempo Real**: Visualizar estado, métricas y conectividad de dispositivos
- **Control Remoto**: Ejecutar acciones de administración (reinicio, apagado, configuración) de forma remota
- **Auditoría Completa**: Registrar todas las transacciones y cambios en el sistema
- **Seguridad**: Gestión de acceso mediante VPN y autenticación centralizada

---

## 2. Actores Principales

### 2.1 Usuarios Humanos

| Actor | Descripción | Responsabilidades |
|-------|-------------|-------------------|
| **Administrador del Sistema** | Usuario con privilegios completos | Gestión de flotas, dispositivos, usuarios, configuración global |
| **Operador de Campo** | Usuario técnico con acceso limitado | Monitoreo de dispositivos, ejecución de acciones básicas |
| **Auditor** | Usuario de solo lectura | Revisión de históricos, reportes, auditorías |

### 2.2 Sistemas Externos

| Sistema | Tipo | Función |
|---------|------|---------|
| **Balena Cloud** | Plataforma IoT | Fuente de verdad para inventario de dispositivos y flotas |
| **Keycloak** | Identity Provider | Autenticación y autorización de usuarios |
| **WireGuard VPN** | Red Privada Virtual | Acceso seguro a dispositivos en campo |
| **Sistemas CRM Externos** | Bases de datos externas | Información de servicios y clientes |

### 2.3 Agentes del Sistema

| Agente | Tipo | Función |
|--------|------|---------|
| **Celery Worker** | Proceso asíncrono | Ejecución de tareas de sincronización y administración |
| **Celery Beat** | Scheduler | Programación de tareas automáticas (sincronización diaria, reinicios programados) |
| **KrakenD Gateway** | API Gateway | Enrutamiento, autenticación y rate limiting de peticiones |

---

## 3. Alcance del Sistema

### 3.1 Funcionalidades Incluidas

#### Gestión de Flotas
- Creación, renombrado y eliminación de flotas
- Visualización de dispositivos por flota
- Gestión de variables de configuración a nivel flota
- Estadísticas agregadas por flota

#### Gestión de Dispositivos
- Visualización de inventario completo
- Monitoreo de métricas (CPU, memoria, almacenamiento, temperatura)
- Control de estado (online/offline/reducido/libre)
- Acciones de administración:
  - Reinicio de aplicación (restart)
  - Reinicio de sistema operativo (reboot)
  - Apagado (shutdown)
  - Movimiento entre flotas
  - Eliminación de dispositivos
  - Gestión de notas y observaciones

#### Sincronización de Inventario
- Sincronización automática programada (diaria)
- Sincronización manual bajo demanda
- Sincronización selectiva por flota
- Concurrencia controlada para optimizar rendimiento

#### Gestión de Configuración
- Variables de entorno a nivel dispositivo
- Variables de entorno a nivel flota
- Sincronización bidireccional con Balena Cloud
- Auditoría de cambios de configuración

#### Monitoreo y Reportes
- Dashboard con estadísticas globales
- Histórico de estados de dispositivos
- Histórico de transacciones del sistema
- Logs de ejecución de scripts

#### Provisioning
- Asociación de dispositivos con servicios
- Vinculación con información de CRM
- Geolocalización (país, región, departamento, ciudad)

### 3.2 Funcionalidades Excluidas

- Gestión de contenido de aplicaciones en dispositivos (responsabilidad de Balena)
- Actualización de firmware (manejado por Balena Cloud)
- Gestión de redes celulares/WiFi de dispositivos
- Facturación o gestión comercial de servicios

### 3.3 Límites del Sistema

| Límite | Descripción |
|--------|-------------|
| **Geográfico** | Dispositivos pueden estar en cualquier ubicación con conectividad a internet |
| **Escalabilidad** | Diseñado para manejar hasta 10,000 dispositivos concurrentes |
| **Tecnológico** | Solo dispositivos compatibles con Balena Cloud (ARM/x86) |
| **Temporal** | Retención de históricos: 1 mes (transacciones), 6 meses (auditoría), 1 año (estadísticas) |

---

## 4. Flujos Principales

### 4.1 Flujo de Sincronización de Inventario

```
[Celery Beat] → Dispara tarea programada (5:00 AM)
    ↓
[Celery Worker] → Inicia transacción de auditoría
    ↓
[InventorySyncService] → Consulta Balena Cloud API
    ↓
[Balena Cloud] → Retorna lista de flotas y dispositivos
    ↓
[InventorySyncService] → Consulta detalles de cada dispositivo (concurrente)
    ↓
[InfoDevicesRepository] → Actualiza/inserta dispositivos en BD local
    ↓
[FleetRepository] → Actualiza estadísticas de flotas
    ↓
[HistoryRepository] → Registra histórico de estados
    ↓
[TransactionManager] → Cierra transacción con estado COMPLETO/FALLIDO
```

### 4.2 Flujo de Acción de Dispositivo (Restart/Reboot/Shutdown)

```
[Usuario] → Solicita acción desde Frontend
    ↓
[KrakenD Gateway] → Valida token JWT con Keycloak
    ↓
[Device Admin Endpoint] → Valida permisos y estado del dispositivo
    ↓
[Celery Worker] → Encola tarea asíncrona
    ↓
[DeviceAdminService] → Inicia transacción de auditoría
    ↓
[BalenaService] → Ejecuta comando Balena CLI
    ↓
[Balena Cloud] → Envía comando al dispositivo
    ↓
[Dispositivo Inspector] → Ejecuta acción y reporta estado
    ↓
[BalenaService] → Monitorea completitud (timeout 5 min)
    ↓
[TransactionManager] → Registra resultado en histórico
    ↓
[Frontend] → Actualiza UI con estado de tarea (polling)
```

### 4.3 Flujo de Gestión de Variables

```
[Usuario] → Crea/modifica variable desde Frontend
    ↓
[Configuration Endpoint] → Valida formato y permisos
    ↓
[ConfigurationSyncService] → Inicia transacción
    ↓
[BalenaService] → Actualiza variable en Balena Cloud
    ↓
[Device/Fleet Vars Repository] → Actualiza BD local
    ↓
[InspectorAuditVariables] → Registra cambio en tabla de auditoría
    ↓
[TransactionManager] → Cierra transacción
    ↓
[Balena Cloud] → Propaga cambio a dispositivos (automático)
```

### 4.4 Flujo de Provisioning

```
[Usuario] → Ingresa datos de provisioning (UUID, Servicio, Ciudad, etc.)
    ↓
[Admin Endpoint] → Valida existencia de dispositivo en Balena
    ↓
[ProvisioningRepository] → Busca/crea registros en catálogos
    ↓
[InspectorService] → Crea/actualiza registro de servicio
    ↓
[InspectorTerminalClient] → Asocia MAC/SN con servicio
    ↓
[Inspector] → Actualiza dispositivo con servicio asociado
    ↓
[TransactionManager] → Registra operación
```

---

## 5. Arquitectura de Alto Nivel

### 5.1 Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  (React + TypeScript + Vite)                                │
│  - Dashboard, Devices, Fleets, Settings                     │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/REST
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                    KRAKEND GATEWAY                           │
│  - Routing, JWT Validation, Rate Limiting                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ API Endpoints                                        │   │
│  │ - Health, Sync, Configuration, Devices, Fleets       │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Services                                             │   │
│  │ - BalenaService, InventorySync, DeviceAdmin          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Repositories                                         │   │
│  │ - Fleet, InfoDevices, History, Catalogs             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
┌───────────────┐   ┌──────────────────┐
│  POSTGRESQL   │   │  REDIS           │
│  - Inspector  │   │  - Celery Broker │
│  - Keycloak   │   │  - Cache         │
│  - WireGuard  │   └──────────────────┘
└───────────────┘
        ↑
        │
┌───────────────────────────────────────────────────────────┐
│              CELERY WORKERS                                │
│  - Inventory Sync Tasks                                   │
│  - Configuration Sync Tasks                               │
│  - Device Admin Tasks (Restart/Reboot/Shutdown)           │
│  - Scheduled Tasks (Celery Beat)                          │
└───────────────┬───────────────────────────────────────────┘
                │
                ↓
        ┌───────────────┐
        │ BALENA CLOUD  │
        │ (External API)│
        └───────────────┘
```

### 5.2 Tecnologías Utilizadas

| Capa | Tecnología | Versión/Detalles |
|------|------------|------------------|
| **Frontend** | React | TypeScript, Vite |
| **Backend** | FastAPI | Python 3.11+ |
| **Base de Datos** | PostgreSQL | 15+ con PostGIS, pg_partman, pg_cron |
| **Cache/Broker** | Redis | Latest |
| **Task Queue** | Celery | Con Redis como broker |
| **API Gateway** | KrakenD | Latest |
| **Autenticación** | Keycloak | 24.0 |
| **VPN** | WireGuard | wg-easy + FastAPI wrapper |
| **Orquestación** | Docker Compose | Multi-container |
| **IoT Platform** | Balena Cloud | External SaaS |

---

## 6. Modelo de Datos Simplificado

### 6.1 Entidades Principales

```
Country → Region → Department → City
                                  ↓
                            InspectorService
                                  ↓
                              Inspector ←→ InspectorFleets
                                  ↓
                      InspectorDeviceVariables
                                  ↓
                   StatusInspectorHistory (Particionada)
```

### 6.2 Catálogos de Soporte

- `TerminalBrand`, `TerminalType`, `TerminalReference`
- `Technology`, `ServiceType`, `ServiceStatus`
- `Product`, `Crm`, `CmtsOlt`
- `DeviceType`, `DeviceStatus`
- `InventoryInspectorStatus`

### 6.3 Auditoría y Transacciones

- `ScriptTransaction`: Definición de scripts del sistema
- `HistoricScriptTransaction`: Histórico de ejecuciones (particionada por día)
- `InspectorAuditVariables`: Auditoría de cambios de variables (particionada por mes)
- `InspectorGlobalStats`: Estadísticas agregadas por flota (particionada por mes)

---

## 7. Seguridad

### 7.1 Autenticación y Autorización

- **Keycloak**: Gestión de identidades y tokens JWT
- **KrakenD**: Validación de tokens en cada petición
- **Roles**: Administrador, Operador, Auditor (definidos en Keycloak)

### 7.2 Comunicación Segura

- **HTTPS**: Todas las comunicaciones externas
- **WireGuard VPN**: Acceso seguro a dispositivos en campo
- **API Keys**: Autenticación con Balena Cloud (almacenadas en variables de entorno)

### 7.3 Auditoría

- Todas las transacciones registran usuario y rol ejecutor
- Histórico inmutable de cambios de configuración
- Logs centralizados en `/app/logs`

---

## 8. Escalabilidad y Rendimiento

### 8.1 Estrategias de Optimización

- **Particionamiento de Tablas**: Históricos particionados por tiempo
- **Concurrencia Controlada**: Semáforos en sincronización (máx 5 dispositivos simultáneos)
- **Caché**: Redis para datos frecuentemente consultados
- **Procesamiento Asíncrono**: Celery para operaciones pesadas
- **Chunking**: Procesamiento en lotes de 10 dispositivos

### 8.2 Retención de Datos

| Tabla | Retención | Estrategia |
|-------|-----------|------------|
| `HistoricScriptTransaction` | 1 mes | Auto-eliminación por pg_partman |
| `InspectorAuditVariables` | 6 meses | Auto-eliminación por pg_partman |
| `InspectorGlobalStats` | 1 año | Auto-eliminación por pg_partman |
| `StatusInspectorHistory` | 1 mes | Auto-eliminación por pg_partman |

---

## 9. Despliegue

### 9.1 Arquitectura de Contenedores

| Servicio | Contenedor | IP Interna | Puerto Expuesto |
|----------|------------|------------|-----------------|
| Backend API | `open_balena_apis` | 172.16.0.2 | 5000 |
| Gateway | `krakend_inspector` | 172.16.0.11 | 8081 |
| Database | `postgres_inspector` | 172.16.0.8 | 5432 |
| Cache | `redis_inspector` | 172.16.0.6 | 6380 |
| Auth | `keycloak_inspector` | 172.16.0.10 | 8080 |
| VPN | `wg-easy_inspector` | 172.16.0.12 | 51820/51821 |
| VPN API | `wg-fastapi_inspector` | 172.16.0.13 | 5000 |
| Worker | `celery_worker_inspector` | 172.16.0.14 | - |
| Scheduler | `celery_beat_inspector` | 172.16.0.15 | - |

### 9.2 Red Interna

- **Subnet**: 172.16.0.0/27
- **Red Docker**: `InspecNet`

---

## 10. Dependencias Externas

### 10.1 Balena Cloud

- **Tipo**: SaaS Platform
- **Función**: Gestión de dispositivos IoT
- **Interfaz**: Balena CLI (subprocess)
- **Autenticación**: API Token (variable de entorno)

### 10.2 Sistemas CRM

- **Tipo**: Bases de datos externas (no incluidas en este proyecto)
- **Función**: Información de servicios y clientes
- **Interfaz**: Relación a través de `InspectorService.strInspectorServiceId`

---

## 11. Glosario

| Término | Definición |
|---------|------------|
| **Inspector** | Dispositivo IoT desplegado en campo, gestionado por Balena Cloud |
| **Flota** | Agrupación lógica de dispositivos con la misma aplicación/configuración |
| **Balena Cloud** | Plataforma SaaS para gestión de dispositivos IoT |
| **Provisioning** | Proceso de asociar un dispositivo con un servicio y ubicación |
| **Sync** | Sincronización de inventario entre Balena Cloud y BD local |
| **CMTS/OLT** | Cable Modem Termination System / Optical Line Terminal |
| **UUID** | Identificador único universal del dispositivo en Balena |
| **Slug** | Identificador de flota en formato `organización/nombre` |
| **Transaction** | Ejecución auditada de un script del sistema |

---

## 12. Contacto y Mantenimiento

- **Repositorio**: InspectorGestion5.0
- **Documentación Técnica**: `.aidlc/` directory
- **Logs**: `./backend_logs/`
- **Base de Datos**: PostgreSQL schema `inspector`
