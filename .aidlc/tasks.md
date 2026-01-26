# InspectorGestion 5.0 - Implementation Tasks

> **Propósito**: Este documento descompone la implementación del sistema en tareas secuenciales, verificables y trazables a requisitos y diseño.

---

## Estructura de Tareas

Cada tarea incluye:

- **ID**: Identificador único
- **Descripción**: Qué se debe hacer
- **Dependencias**: Tareas que deben completarse primero
- **Requisitos**: Trazabilidad a requirements.md
- **Verificación**: Cómo validar que está completa

---

## Fase 1: Infraestructura y Base de Datos

### T-001: Configuración de Docker Compose

- **Descripción**: Crear archivo `docker-compose.yml` con todos los servicios
- **Dependencias**: Ninguna
- **Requisitos**: RNF-DIS-002
- **Verificación**:
  - [ ] `docker-compose up -d` ejecuta sin errores
  - [ ] Todos los contenedores están en estado `running`
  - [ ] Healthcheck de PostgreSQL pasa

### T-002: Creación de Esquema de Base de Datos

- **Descripción**: Ejecutar `database/init.sql` para crear tablas y esquemas
- **Dependencias**: T-001
- **Requisitos**: Diseño sección 2.1
- **Verificación**:
  - [ ] Esquema `inspector` existe en PostgreSQL
  - [ ] 20+ tablas creadas correctamente
  - [ ] Constraints y foreign keys aplicados
  - [ ] Extensiones `pg_partman`, `pg_cron`, `postgis` instaladas

### T-003: Configuración de Particionamiento

- **Descripción**: Configurar `pg_partman` para tablas históricas
- **Dependencias**: T-002
- **Requisitos**: RNF-ESC-002
- **Verificación**:
  - [ ] Particiones creadas para `HistoricScriptTransaction`
  - [ ] Particiones creadas para `StatusInspectorHistory`
  - [ ] Particiones creadas para `InspectorAuditVariables`
  - [ ] Particiones creadas para `InspectorGlobalStats`
  - [ ] Políticas de retención configuradas

### T-004: Población de Catálogos Iniciales

- **Descripción**: Insertar datos iniciales en tablas de catálogos
- **Dependencias**: T-002
- **Requisitos**: Diseño sección 2.1.2
- **Verificación**:
  - [ ] `TransactionStatus` tiene registros (COMPLETO, FALLIDO, EN_PROCESO)
  - [ ] `DeviceStatus` tiene registros (operativo, offline, reducido, libre)
  - [ ] `InventoryInspectorStatus` tiene registros
  - [ ] `DeviceType` tiene al menos 1 tipo de dispositivo

### T-005: Configuración de Redis

- **Descripción**: Configurar Redis como broker de Celery y caché
- **Dependencias**: T-001
- **Requisitos**: Diseño sección 6.1
- **Verificación**:
  - [ ] Redis acepta conexiones en puerto 6379
  - [ ] Autenticación con password funciona
  - [ ] Comando `redis-cli ping` retorna PONG

---

## Fase 2: Backend - Core

### T-006: Estructura de Proyecto Backend

- **Descripción**: Crear estructura de carpetas y archivos base
- **Dependencias**: T-001
- **Requisitos**: Diseño sección 1.1
- **Verificación**:
  - [ ] Carpetas `src/api`, `src/services`, `src/repositories`, `src/utils` creadas
  - [ ] `main.py` con FastAPI app básica
  - [ ] `requirements.txt` con dependencias

### T-007: Configuración y Variables de Entorno

- **Descripción**: Implementar `src/core/config.py` con Pydantic Settings
- **Dependencias**: T-006
- **Requisitos**: RNF-SEG-002
- **Verificación**:
  - [ ] Variables de entorno cargadas desde `.env`
  - [ ] `settings.BALENA_API_TOKEN` accesible
  - [ ] `settings.DATABASE_URL` correcta

### T-008: Conector de PostgreSQL

- **Descripción**: Implementar `databases/postgres_connector.py` con pool de conexiones
- **Dependencias**: T-002, T-007
- **Requisitos**: Diseño sección 11.1
- **Verificación**:
  - [ ] Pool de conexiones se inicializa en startup
  - [ ] Queries ejecutan correctamente
  - [ ] Pool se cierra en shutdown

### T-009: Logger Centralizado

- **Descripción**: Configurar logger estructurado en `src/core/logger.py`
- **Dependencias**: T-006
- **Requisitos**: RNF-MAN-001
- **Verificación**:
  - [ ] Logs se escriben en `./backend_logs/`
  - [ ] Formato JSON implementado
  - [ ] Niveles DEBUG, INFO, WARNING, ERROR funcionan

---

## Fase 3: Integración con Balena Cloud

### T-010: Balena Service - Autenticación

- **Descripción**: Implementar `BalenaService.login()` en `src/services/balena_service.py`
- **Dependencias**: T-007
- **Requisitos**: RF-INV-003, Diseño sección 4.1
- **Verificación**:
  - [ ] `balena login --token` ejecuta sin error
  - [ ] Token almacenado en sesión CLI
  - [ ] Timeout de 30 segundos configurado

### T-011: Balena Service - Consulta de Flotas

- **Descripción**: Implementar `BalenaService.get_fleets()`
- **Dependencias**: T-010
- **Requisitos**: RF-INV-003
- **Verificación**:
  - [ ] Retorna array JSON de flotas
  - [ ] Parseo de JSON exitoso
  - [ ] Manejo de errores implementado

### T-012: Balena Service - Consulta de Dispositivos

- **Descripción**: Implementar `BalenaService.get_devices_by_fleet()` y `get_device_detail()`
- **Dependencias**: T-010
- **Requisitos**: RF-INV-005, RF-INV-006
- **Verificación**:
  - [ ] `get_devices_by_fleet(slug)` retorna dispositivos
  - [ ] `get_device_detail(uuid)` retorna métricas
  - [ ] Timeout de 30 segundos por dispositivo

### T-013: Balena Service - Acciones de Dispositivos

- **Descripción**: Implementar `restart_device()`, `reboot_device()`, `shutdown_device()`
- **Dependencias**: T-010
- **Requisitos**: RF-ADM-001, RF-ADM-002, RF-ADM-003
- **Verificación**:
  - [ ] Comandos ejecutan sin error
  - [ ] Monitoreo de completitud implementado
  - [ ] Timeout de 5 minutos configurado

### T-014: Balena Service - Gestión de Variables

- **Descripción**: Implementar `get_fleet_vars()`, `set_fleet_variable()`, `remove_fleet_variable()`
- **Dependencias**: T-010
- **Requisitos**: RF-CFG-001, RF-CFG-003, RF-CFG-005
- **Verificación**:
  - [ ] Variables se obtienen correctamente
  - [ ] Creación/actualización funciona
  - [ ] Eliminación funciona

---

## Fase 4: Repositories

### T-015: Base Repository

- **Descripción**: Implementar `src/repositories/base.py` con métodos comunes
- **Dependencias**: T-008
- **Requisitos**: Diseño sección 11.1
- **Verificación**:
  - [ ] `execute_query()` funciona
  - [ ] Manejo de errores de BD implementado
  - [ ] Connection pooling utilizado

### T-016: Fleet Repository

- **Descripción**: Implementar `src/repositories/fleet_repo.py`
- **Dependencias**: T-015
- **Requisitos**: RF-FLT-004, RF-FLT-005
- **Verificación**:
  - [ ] `get_all_fleets()` retorna flotas
  - [ ] `get_fleet_by_id()` retorna flota específica
  - [ ] `upsert_fleet()` inserta/actualiza correctamente

### T-017: Info Devices Repository

- **Descripción**: Implementar `src/repositories/info_devices_repo.py`
- **Dependencias**: T-015
- **Requisitos**: RF-DEV-001, RF-DEV-002
- **Verificación**:
  - [ ] `get_all_devices()` retorna dispositivos
  - [ ] `get_device_by_uuid()` retorna dispositivo específico
  - [ ] `upsert_device()` funciona correctamente

### T-018: History Repository

- **Descripción**: Implementar `src/repositories/history_repo.py`
- **Dependencias**: T-015
- **Requisitos**: RF-MON-002, RF-MON-003
- **Verificación**:
  - [ ] `insert_device_status()` inserta en tabla particionada
  - [ ] `get_device_history()` retorna histórico
  - [ ] `get_transactions_history()` retorna transacciones

### T-019: Variables Repositories

- **Descripción**: Implementar `device_vars_repo.py` y `fleet_vars_repo.py`
- **Dependencias**: T-015
- **Requisitos**: RF-CFG-003, RF-CFG-006
- **Verificación**:
  - [ ] CRUD de variables de flota funciona
  - [ ] CRUD de variables de dispositivo funciona
  - [ ] Constraint de unicidad respetado

---

## Fase 5: Transaction Manager

### T-020: Script IDs Enum

- **Descripción**: Definir enum `ScriptIds` en `src/utils/transaction_manager.py`
- **Dependencias**: T-006
- **Requisitos**: Diseño sección 5.1.1
- **Verificación**:
  - [ ] Todos los script IDs definidos
  - [ ] Registros en tabla `ScriptTransaction`

### T-021: Transaction Manager - Start

- **Descripción**: Implementar `TransactionManager.start_transaction()`
- **Dependencias**: T-020, T-018
- **Requisitos**: RF-SEC-004, Diseño sección 5.1.2
- **Verificación**:
  - [ ] Inserta registro en `HistoricScriptTransaction`
  - [ ] Retorna `idHistoricScript`
  - [ ] Incluye usuario y rol

### T-022: Transaction Manager - Finish

- **Descripción**: Implementar `TransactionManager.finish_transaction()`
- **Dependencias**: T-021
- **Requisitos**: RF-SEC-004
- **Verificación**:
  - [ ] Actualiza registro con estado final
  - [ ] Calcula duración correctamente
  - [ ] Registra descripción de finalización

---

## Fase 6: Services

### T-023: Inventory Sync Service

- **Descripción**: Implementar `src/services/inventory_sync.py`
- **Dependencias**: T-012, T-016, T-017, T-021
- **Requisitos**: RF-INV-001, RF-INV-002
- **Verificación**:
  - [ ] `sync_all()` sincroniza flotas y dispositivos
  - [ ] Concurrencia de 5 dispositivos implementada
  - [ ] Transacciones registradas correctamente

### T-024: Configuration Sync Service

- **Descripción**: Implementar `src/services/configuration_sync.py`
- **Dependencias**: T-014, T-019, T-021
- **Requisitos**: RF-CFG-001, RF-CFG-002
- **Verificación**:
  - [ ] `sync_all_variables()` sincroniza variables
  - [ ] Auditoría de cambios implementada
  - [ ] Transacciones registradas

### T-025: Device Admin Service

- **Descripción**: Implementar `src/services/device_admin_service.py`
- **Dependencias**: T-013, T-017, T-021
- **Requisitos**: RF-ADM-001, RF-ADM-002, RF-ADM-003
- **Verificación**:
  - [ ] `execute_power_action()` ejecuta acciones
  - [ ] `monitor_power_action()` monitorea completitud
  - [ ] Transacciones registradas con usuario

### T-026: Fleet Admin Service

- **Descripción**: Implementar `src/services/fleet_admin_service.py`
- **Dependencias**: T-011, T-016, T-021
- **Requisitos**: RF-FLT-001, RF-FLT-002, RF-FLT-003
- **Verificación**:
  - [ ] Creación de flotas funciona
  - [ ] Renombrado funciona
  - [ ] Eliminación valida dispositivos asociados

---

## Fase 7: API Endpoints

### T-027: Health Endpoint

- **Descripción**: Implementar `src/api/v1/endpoints/health.py`
- **Dependencias**: T-006
- **Requisitos**: RNF-DIS-001
- **Verificación**:
  - [ ] `GET /api/v1/health` retorna 200
  - [ ] Incluye estado de BD y Redis
  - [ ] Tiempo de respuesta < 100ms

### T-028: Sync Endpoints

- **Descripción**: Implementar `src/api/v1/endpoints/sync.py`
- **Dependencias**: T-023, T-024
- **Requisitos**: RF-INV-002
- **Verificación**:
  - [ ] `POST /api/v1/sync/inventory` dispara sincronización
  - [ ] `POST /api/v1/sync/configuration` dispara sync de variables
  - [ ] Retorna task_id de Celery

### T-029: Info Devices Endpoints

- **Descripción**: Implementar `src/api/v1/endpoints/info_devices.py`
- **Dependencias**: T-017
- **Requisitos**: RF-DEV-001, RF-DEV-002
- **Verificación**:
  - [ ] `GET /api/v1/infodevices` retorna lista
  - [ ] `GET /api/v1/infodevices/{uuid}` retorna detalle
  - [ ] Filtros funcionan correctamente

### T-030: Device Admin Endpoints

- **Descripción**: Implementar `src/api/v1/endpoints/device_admin.py`
- **Dependencias**: T-025
- **Requisitos**: RF-ADM-001, RF-ADM-002, RF-ADM-003
- **Verificación**:
  - [ ] `POST /api/v1/admin/device/{uuid}/restart` funciona
  - [ ] `POST /api/v1/admin/device/{uuid}/reboot` funciona
  - [ ] `POST /api/v1/admin/device/{uuid}/shutdown` funciona
  - [ ] Validación de permisos implementada

### T-031: Fleets Endpoints

- **Descripción**: Implementar `src/api/v1/endpoints/fleets.py`
- **Dependencias**: T-026
- **Requisitos**: RF-FLT-001, RF-FLT-002, RF-FLT-003
- **Verificación**:
  - [ ] CRUD completo de flotas funciona
  - [ ] Validaciones implementadas
  - [ ] Códigos HTTP correctos

### T-032: Configuration Endpoints

- **Descripción**: Implementar `src/api/v1/endpoints/configuration.py`
- **Dependencias**: T-024
- **Requisitos**: RF-CFG-003, RF-CFG-006
- **Verificación**:
  - [ ] CRUD de variables de flota funciona
  - [ ] CRUD de variables de dispositivo funciona
  - [ ] Auditoría registrada

### T-033: History Endpoints

- **Descripción**: Implementar `src/api/v1/endpoints/history.py`
- **Dependencias**: T-018
- **Requisitos**: RF-MON-002, RF-MON-003
- **Verificación**:
  - [ ] `GET /api/v1/history/devices/{uuid}` retorna histórico
  - [ ] `GET /api/v1/history/transactions` retorna transacciones
  - [ ] Filtros por fecha funcionan

---

## Fase 8: Celery Workers

### T-034: Configuración de Celery

- **Descripción**: Implementar `src/core/celery_app.py`
- **Dependencias**: T-005, T-007
- **Requisitos**: Diseño sección 6.1
- **Verificación**:
  - [ ] Celery se conecta a Redis
  - [ ] Worker arranca sin errores
  - [ ] Beat scheduler funciona

### T-035: Tareas de Sincronización

- **Descripción**: Implementar tareas en `src/worker/tasks.py`
- **Dependencias**: T-034, T-023, T-024
- **Requisitos**: RF-INV-001
- **Verificación**:
  - [ ] `task_run_automatic_sync` ejecuta a las 5:00 AM
  - [ ] `task_run_configuration_sync` ejecuta correctamente
  - [ ] Logs registrados

### T-036: Tareas de Administración de Dispositivos

- **Descripción**: Implementar `task_restart_single_device`, `task_restart_bulk_devices`
- **Dependencias**: T-034, T-025
- **Requisitos**: RF-ADM-001, RF-ADM-004
- **Verificación**:
  - [ ] Tarea individual funciona
  - [ ] Tarea masiva procesa en chunks de 10
  - [ ] Estados de Celery actualizados en tiempo real

### T-037: Tarea de Reinicio Automático

- **Descripción**: Implementar `task_run_automatic_restart`
- **Dependencias**: T-036
- **Requisitos**: RF-ADM-005
- **Verificación**:
  - [ ] Filtra solo dispositivos operativos
  - [ ] Registra transacción
  - [ ] Retorna resumen de ejecución

---

## Fase 9: Seguridad

### T-038: Configuración de Keycloak

- **Descripción**: Configurar realm, clientes y roles en Keycloak
- **Dependencias**: T-001
- **Requisitos**: RF-SEC-001, Diseño sección 7.1
- **Verificación**:
  - [ ] Realm `inspector` creado
  - [ ] Cliente `inspector-app` configurado
  - [ ] Roles Administrador, Operador, Auditor creados

### T-039: Configuración de KrakenD

- **Descripción**: Crear `gateway/krakend.json` con validación JWT
- **Dependencias**: T-038
- **Requisitos**: RF-SEC-002
- **Verificación**:
  - [ ] KrakenD valida tokens JWT usando **cache local de JWKS** (no introspección por request)
  - [ ] Implementa patrón Phantom Token: Convierte Cookie `SESSION_ID` entrante a Header `Authorization: Bearer ...` hacia el backend
  - [ ] Bloquea peticiones sin cookie válida
  - [ ] Enrutamiento a backend funciona

### T-040: Middleware de Seguridad en Backend

- **Descripción**: Implementar `src/core/security.py` con validación de roles
- **Dependencias**: T-039
- **Requisitos**: RF-SEC-003
- **Verificación**:
  - [ ] `get_current_user()` extrae usuario del token (recibido desde KrakenD)
  - [ ] `require_role()` valida permisos
  - [ ] Retorna 403 si no tiene permisos

---

## Fase 10: Frontend

### T-041: Estructura de Proyecto Frontend

- **Descripción**: Crear proyecto React con Vite
- **Dependencias**: Ninguna
- **Requisitos**: Diseño sección 1.2
- **Verificación**:
  - [ ] `npm create vite@latest` ejecutado
  - [ ] TypeScript configurado
  - [ ] `npm run dev` arranca sin errores

### T-042: Configuración de Routing

- **Descripción**: Implementar React Router en `src/App.tsx`
- **Dependencias**: T-041
- **Requisitos**: Overview sección 4
- **Verificación**:
  - [ ] Rutas `/dashboard`, `/devices`, `/fleets`, `/settings` funcionan
  - [ ] Navegación entre páginas funciona
  - [ ] 404 page implementada

### T-043: Layout Principal y Gestión de Sesión

- **Descripción**: Crear `src/layouts/MainLayout.tsx` y gestión de estado de auth
- **Dependencias**: T-042
- **Requisitos**: RNF-USA-001, RF-SEC-001
- **Verificación**:
  - [ ] Auth state se maneja en memoria (Context/Zustand), **NO en localStorage**
  - [ ] Sidebar con navegación
  - [ ] Header con usuario y logout
  - [ ] Logout limpia la cookie (petición a backend)

### T-044: Dashboard Page

- **Descripción**: Implementar `src/pages/Dashboard/Dashboard.tsx`
- **Dependencias**: T-043
- **Requisitos**: RF-MON-001
- **Verificación**:
  - [ ] Muestra estadísticas globales
  - [ ] Gráficos de dispositivos por estado
  - [ ] Actualización automática cada 30s

### T-045: Devices Page

- **Descripción**: Implementar `src/pages/Devices/Devices.tsx`
- **Dependencias**: T-043
- **Requisitos**: RF-DEV-001, RF-DEV-003
- **Verificación**:
  - [ ] Lista de dispositivos con paginación
  - [ ] Filtros por estado funcionan
  - [ ] Búsqueda implementada

### T-046: Device Detail Page

- **Descripción**: Implementar `src/pages/DeviceDetail/DeviceDetail.tsx`
- **Dependencias**: T-045
- **Requisitos**: RF-DEV-002
- **Verificación**:
  - [ ] Muestra métricas en tiempo real
  - [ ] Botones de acción (restart, reboot, shutdown)
  - [ ] Histórico de estados

### T-047: Fleets Page

- **Descripción**: Implementar `src/pages/Fleets/Fleets.tsx`
- **Dependencias**: T-043
- **Requisitos**: RF-FLT-004
- **Verificación**:
  - [ ] Lista de flotas
  - [ ] Botón crear flota
  - [ ] Navegación a detalle de flota

### T-048: Fleet Detail Page

- **Descripción**: Implementar `src/pages/FleetDetail/FleetDetail.tsx`
- **Dependencias**: T-047
- **Requisitos**: RF-FLT-005
- **Verificación**:
  - [ ] Muestra dispositivos de la flota
  - [ ] Variables de flota
  - [ ] Acciones de flota (rename, delete)

### T-049: Device Action Components

- **Descripción**: Implementar componentes de acciones con polling de estado
- **Dependencias**: T-046
- **Requisitos**: RF-ADM-001, RNF-USA-002
- **Verificación**:
  - [ ] Botones ejecutan acciones
  - [ ] Polling de estado Celery cada 2s
  - [ ] UI muestra progreso en tiempo real
  - [ ] Notificaciones de éxito/error

### T-050: Variables Management Components

- **Descripción**: Implementar CRUD de variables en frontend
- **Dependencias**: T-046, T-048
- **Requisitos**: RF-CFG-003, RF-CFG-006
- **Verificación**:
  - [ ] Modal de creación de variable
  - [ ] Edición inline de variables
  - [ ] Confirmación de eliminación

---

## Fase 11: VPN

### T-051: Configuración de WireGuard

- **Descripción**: Configurar `wg-easy` en Docker Compose
- **Dependencias**: T-001
- **Requisitos**: RF-VPN-001
- **Verificación**:
  - [ ] WireGuard arranca correctamente
  - [ ] Puerto UDP 51820 expuesto
  - [ ] UI de wg-easy accesible en puerto 51821

### T-052: WireGuard FastAPI Wrapper

- **Descripción**: Implementar API en `vpn/main.py`
- **Dependencias**: T-051
- **Requisitos**: RF-VPN-001, RF-VPN-002, RF-VPN-003
- **Verificación**:
  - [ ] Endpoints de CRUD de clientes funcionan
  - [ ] Generación de configuración `.conf` funciona
  - [ ] Integración con contenedor wg-easy

---

## Fase 12: Testing y Validación

### T-053: Tests Unitarios de Repositories

- **Descripción**: Crear tests para repositories
- **Dependencias**: T-015, T-016, T-017, T-018, T-019
- **Requisitos**: Diseño sección 12.1
- **Verificación**:
  - [ ] Coverage > 80% en repositories
  - [ ] Mocks de BD implementados
  - [ ] `pytest` ejecuta sin errores

### T-054: Tests Unitarios de Services

- **Descripción**: Crear tests para services
- **Dependencias**: T-023, T-024, T-025, T-026
- **Requisitos**: Diseño sección 12.1
- **Verificación**:
  - [ ] Coverage > 80% en services
  - [ ] Mocks de Balena CLI implementados
  - [ ] Tests de casos de error

### T-055: Tests de Integración de API

- **Descripción**: Crear tests end-to-end de endpoints
- **Dependencias**: T-027 a T-033
- **Requisitos**: Diseño sección 12.2
- **Verificación**:
  - [ ] Tests con TestClient de FastAPI
  - [ ] Validación de códigos HTTP
  - [ ] Validación de schemas de respuesta

### T-056: Tests de Celery Tasks

- **Descripción**: Crear tests para tareas Celery
- **Dependencias**: T-035, T-036, T-037
- **Requisitos**: Diseño sección 12.2
- **Verificación**:
  - [ ] Tests con Celery test runner
  - [ ] Validación de estados de tareas
  - [ ] Tests de reintentos

### T-057: Pruebas Manuales End-to-End

- **Descripción**: Ejecutar flujos completos manualmente
- **Dependencias**: T-050
- **Requisitos**: Todos los RF
- **Verificación**:
  - [ ] Flujo de sincronización completo
  - [ ] Flujo de reinicio de dispositivo
  - [ ] Flujo de creación de flota
  - [ ] Flujo de gestión de variables
  - [ ] Flujo de provisioning

---

## Fase 13: Documentación y Despliegue

### T-058: Documentación de API (OpenAPI)

- **Descripción**: Generar documentación Swagger/ReDoc
- **Dependencias**: T-027 a T-033
- **Requisitos**: N/A
- **Verificación**:
  - [ ] `/docs` muestra Swagger UI
  - [ ] `/redoc` muestra ReDoc
  - [ ] Todos los endpoints documentados

### T-059: README y Guías de Instalación

- **Descripción**: Crear README.md con instrucciones
- **Dependencias**: T-057
- **Requisitos**: N/A
- **Verificación**:
  - [ ] Instrucciones de instalación claras
  - [ ] Variables de entorno documentadas
  - [ ] Comandos de inicio documentados

### T-060: Scripts de Deployment

- **Descripción**: Crear scripts de despliegue en producción
- **Dependencias**: T-057
- **Requisitos**: Diseño sección 8
- **Verificación**:
  - [ ] Script de backup de BD
  - [ ] Script de restauración
  - [ ] Script de actualización sin downtime

---

## Matriz de Trazabilidad

| Fase | Tareas | Requisitos Principales | Componentes |
|------|--------|------------------------|-------------|
| 1 | T-001 a T-005 | RNF-DIS-002, RNF-ESC-002 | Docker, PostgreSQL, Redis |
| 2 | T-006 a T-009 | RNF-SEG-002, RNF-MAN-001 | Backend Core |
| 3 | T-010 a T-014 | RF-INV-003 a RF-INV-006, RF-CFG-001 | Balena Integration |
| 4 | T-015 a T-019 | RF-DEV-001, RF-FLT-004, RF-MON-002 | Repositories |
| 5 | T-020 a T-022 | RF-SEC-004 | Transaction Manager |
| 6 | T-023 a T-026 | RF-INV-001, RF-CFG-001, RF-ADM-001, RF-FLT-001 | Services |
| 7 | T-027 a T-033 | Todos los RF | API Endpoints |
| 8 | T-034 a T-037 | RF-INV-001, RF-ADM-001, RF-ADM-005 | Celery Workers |
| 9 | T-038 a T-040 | RF-SEC-001, RF-SEC-002, RF-SEC-003 | Security |
| 10 | T-041 a T-050 | RF-DEV-001, RF-FLT-004, RNF-USA-001 | Frontend |
| 11 | T-051 a T-052 | RF-VPN-001, RF-VPN-002, RF-VPN-003 | VPN |
| 12 | T-053 a T-057 | Todos | Testing |
| 13 | T-058 a T-060 | N/A | Documentation |

---

## Puntos de Verificación (Checkpoints)

### Checkpoint 1: Infraestructura Lista

- **Tareas**: T-001 a T-005
- **Criterio**: Todos los contenedores arrancando, BD con esquema completo

### Checkpoint 2: Backend Core Funcional

- **Tareas**: T-006 a T-022
- **Criterio**: API básica responde, transacciones se registran

### Checkpoint 3: Integración con Balena Completa

- **Tareas**: T-010 a T-014, T-023 a T-026
- **Criterio**: Sincronización manual funciona end-to-end

### Checkpoint 4: API Completa

- **Tareas**: T-027 a T-033
- **Criterio**: Todos los endpoints responden correctamente

### Checkpoint 5: Procesamiento Asíncrono Funcional

- **Tareas**: T-034 a T-037
- **Criterio**: Tareas Celery ejecutan correctamente, sincronización automática funciona

### Checkpoint 6: Seguridad Implementada

- **Tareas**: T-038 a T-040
- **Criterio**: Autenticación y autorización funcionan

### Checkpoint 7: Frontend Funcional

- **Tareas**: T-041 a T-050
- **Criterio**: Todas las páginas funcionan, acciones de dispositivos ejecutan

### Checkpoint 8: Sistema Completo

- **Tareas**: T-051 a T-057
- **Criterio**: Todos los flujos end-to-end funcionan

---

## Estimación de Esfuerzo

| Fase | Tareas | Días Estimados | Complejidad |
|------|--------|----------------|-------------|
| 1 | 5 | 2 | Baja |
| 2 | 4 | 2 | Media |
| 3 | 5 | 5 | Alta |
| 4 | 5 | 3 | Media |
| 5 | 3 | 2 | Media |
| 6 | 4 | 5 | Alta |
| 7 | 7 | 5 | Media |
| 8 | 4 | 3 | Media |
| 9 | 3 | 2 | Media |
| 10 | 10 | 8 | Alta |
| 11 | 2 | 2 | Media |
| 12 | 5 | 5 | Alta |
| 13 | 3 | 2 | Baja |
| **TOTAL** | **60** | **46 días** | - |

> **Nota**: Estimación asume 1 desarrollador full-time. Con equipo de 2-3 personas, se puede reducir a 20-25 días.

---

## Dependencias Críticas

1. **Balena Cloud API**: Disponibilidad y estabilidad
2. **Keycloak**: Configuración correcta de realm y clientes
3. **PostgreSQL**: Extensiones `pg_partman`, `pg_cron`, `postgis` disponibles
4. **Docker**: Versión compatible con docker-compose v3.8+

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Balena CLI cambia sintaxis | Media | Alto | Versionar Balena CLI en Dockerfile |
| Timeouts en sincronización | Alta | Medio | Implementar reintentos y chunking |
| Particiones no se crean automáticamente | Baja | Alto | Validar pg_partman en T-003 |
| Keycloak no integra con KrakenD | Baja | Alto | Probar integración en T-039 |
| Frontend no actualiza en tiempo real | Media | Medio | Implementar polling robusto en T-049 |

---

## Notas de Implementación

- Cada tarea debe tener un commit Git independiente
- Usar branches por fase (`fase-1-infraestructura`, `fase-2-backend-core`, etc.)
- Pull requests requieren revisión antes de merge
- Tests deben pasar antes de marcar tarea como completa
- Documentar decisiones técnicas en comentarios de código
