# InspectorGestion 5.0 - Diagrams Specification

> **Propósito**: Este documento especifica los diagramas visuales necesarios para complementar la documentación AIDLC. Todos los diagramas están diseñados para ser creados en **draw.io** (diagrams.net).

---

## 1. Diagrama de Contexto del Sistema

### 1.1 Propósito
Mostrar la relación del sistema InspectorGestion con actores externos y sistemas externos.

### 1.2 Elementos

**Actores Externos**:
- Administrador del Sistema
- Operador de Campo
- Auditor

**Sistemas Externos**:
- Balena Cloud (API)
- Keycloak (Identity Provider)
- Sistemas CRM (Bases de datos externas)

**Sistema Central**:
- InspectorGestion 5.0

### 1.3 Relaciones

| Desde | Hacia | Descripción |
|-------|-------|-------------|
| Administrador | InspectorGestion | Gestiona flotas, dispositivos, usuarios |
| Operador | InspectorGestion | Monitorea y ejecuta acciones básicas |
| Auditor | InspectorGestion | Consulta históricos y reportes |
| InspectorGestion | Balena Cloud | Sincroniza inventario, ejecuta comandos |
| InspectorGestion | Keycloak | Valida autenticación |
| InspectorGestion | Sistemas CRM | Consulta información de servicios |

### 1.4 Instrucciones para draw.io

1. Usar forma **Rectángulo redondeado** para el sistema central (color azul)
2. Usar forma **Actor** (stickman) para usuarios humanos
3. Usar forma **Cilindro** para sistemas externos
4. Usar flechas **bidireccionales** para comunicación
5. Etiquetar cada flecha con el tipo de interacción

**Trazabilidad**: Overview sección 2, 3

---

## 2. Diagrama de Arquitectura de Componentes

### 2.1 Propósito
Mostrar la arquitectura de microservicios y la comunicación entre contenedores Docker.

### 2.2 Componentes (Contenedores Docker)

| Componente | Color | Forma |
|------------|-------|-------|
| Frontend (React) | Verde | Rectángulo |
| KrakenD Gateway | Naranja | Rectángulo |
| Backend (FastAPI) | Azul | Rectángulo |
| PostgreSQL | Gris | Cilindro |
| Redis | Rojo | Cilindro |
| Keycloak | Morado | Rectángulo |
| WireGuard VPN | Amarillo | Rectángulo |
| Celery Worker | Azul claro | Rectángulo |
| Celery Beat | Azul claro | Rectángulo |
| Balena Cloud | Gris claro (externo) | Nube |

### 2.3 Conexiones

| Desde | Hacia | Protocolo | Puerto |
|-------|-------|-----------|--------|
| Cliente Browser | Frontend | HTTP | 3001 |
| Frontend | KrakenD | HTTP/REST | 8081 |
| KrakenD | Keycloak | HTTP (JWT validation) | 8080 |
| KrakenD | Backend | HTTP/REST | 5000 |
| Backend | PostgreSQL | TCP/SQL | 5432 |
| Backend | Redis | TCP | 6379 |
| Celery Worker | Redis | TCP (broker) | 6379 |
| Celery Worker | PostgreSQL | TCP/SQL | 5432 |
| Celery Beat | Redis | TCP (broker) | 6379 |
| Backend | Balena Cloud | HTTPS (CLI) | 443 |
| Dispositivos | WireGuard VPN | UDP | 51820 |

### 2.4 Instrucciones para draw.io

1. Agrupar componentes por capa (Frontend, Gateway, Backend, Data, Workers)
2. Usar **Contenedores** (Container shape) de draw.io
3. Mostrar red Docker `InspecNet` como un rectángulo grande de fondo
4. Etiquetar IPs internas (172.16.0.x)
5. Usar flechas con etiquetas de protocolo y puerto
6. Balena Cloud fuera de la red Docker

**Trazabilidad**: Design sección 1.2, Overview sección 5.1

---

## 3. Diagrama de Flujo: Sincronización de Inventario

### 3.1 Propósito
Mostrar el flujo completo de sincronización automática de inventario desde Balena Cloud.

### 3.2 Pasos del Flujo

```
[Inicio] → Celery Beat dispara tarea (5:00 AM)
    ↓
[Decisión] ¿Es hora programada?
    Sí → Continuar
    No → Fin
    ↓
[Proceso] Iniciar transacción de auditoría
    ↓
[Proceso] BalenaService.get_fleets()
    ↓
[Subproceso] Ejecutar: balena fleets --json
    ↓
[Decisión] ¿Comando exitoso?
    No → [Proceso] Registrar error → Fin
    Sí → Continuar
    ↓
[Proceso] Parsear JSON de flotas
    ↓
[Loop] Para cada flota:
    ├─ [Proceso] FleetRepository.upsert_fleet()
    ├─ [Proceso] BalenaService.get_devices_by_fleet(slug)
    ├─ [Subproceso] Ejecutar: balena devices --fleet <slug> --json
    ├─ [Loop] Para cada dispositivo (max 5 concurrentes):
    │   ├─ [Proceso] BalenaService.get_device_detail(uuid)
    │   ├─ [Subproceso] Ejecutar: balena device <uuid> --json
    │   ├─ [Proceso] InfoDevicesRepository.upsert_device()
    │   └─ [Proceso] HistoryRepository.insert_device_status()
    └─ [Proceso] FleetRepository.update_fleet_stats()
    ↓
[Proceso] Finalizar transacción (COMPLETO)
    ↓
[Fin]
```

### 3.3 Elementos del Diagrama

- **Óvalo**: Inicio/Fin
- **Rectángulo**: Proceso
- **Rombo**: Decisión
- **Rectángulo con bordes dobles**: Subproceso (llamada externa)
- **Hexágono**: Loop

### 3.4 Instrucciones para draw.io

1. Usar **Flowchart shapes** de draw.io
2. Colores:
   - Verde: Procesos exitosos
   - Rojo: Errores
   - Azul: Decisiones
   - Amarillo: Subprocesos externos
3. Flechas con etiquetas "Sí"/"No" en decisiones
4. Agrupar loop con rectángulo punteado

**Trazabilidad**: Requirements RF-INV-001 a RF-INV-009, Design sección 10.1

---

## 4. Diagrama de Flujo: Reinicio de Dispositivo

### 4.1 Propósito
Mostrar el flujo de ejecución de una acción de reinicio de dispositivo con monitoreo asíncrono.

### 4.2 Pasos del Flujo

```
[Inicio] Usuario hace clic en "Reiniciar"
    ↓
[Proceso] Frontend envía POST /api/v1/admin/device/{uuid}/restart
    ↓
[Decisión] KrakenD: ¿Token JWT válido?
    No → [Fin] Retornar 401 Unauthorized
    Sí → Continuar
    ↓
[Decisión] Backend: ¿Usuario tiene permisos?
    No → [Fin] Retornar 403 Forbidden
    Sí → Continuar
    ↓
[Decisión] ¿Dispositivo existe?
    No → [Fin] Retornar 404 Not Found
    Sí → Continuar
    ↓
[Proceso] Encolar tarea Celery: task_restart_single_device
    ↓
[Proceso] Retornar task_id al frontend (202 Accepted)
    ↓
[Paralelo] Dos flujos:
    
    Flujo A (Frontend):
    ├─ [Proceso] Mostrar "Reinicio en progreso..."
    ├─ [Loop] Polling cada 2 segundos:
    │   ├─ [Proceso] GET /api/v1/admin/task/{task_id}
    │   ├─ [Decisión] ¿Estado = SUCCESS o FAILURE?
    │   │   No → Continuar polling
    │   │   Sí → Salir del loop
    │   └─ [Proceso] Actualizar UI con resultado
    └─ [Fin]
    
    Flujo B (Celery Worker):
    ├─ [Proceso] Iniciar transacción de auditoría
    ├─ [Proceso] Actualizar estado Celery: STARTED
    ├─ [Subproceso] BalenaService.restart_device(uuid)
    ├─ [Subproceso] Ejecutar: balena device restart <uuid>
    ├─ [Proceso] Monitorear completitud (timeout 5 min)
    ├─ [Decisión] ¿Comando completado?
    │   No → [Proceso] Registrar FALLIDO → Actualizar Celery: FAILURE
    │   Sí → [Proceso] Registrar COMPLETO → Actualizar Celery: SUCCESS
    └─ [Fin]
```

### 4.3 Instrucciones para draw.io

1. Usar **Swimlanes** para separar actores (Frontend, Gateway, Backend, Celery Worker)
2. Mostrar flujos paralelos con líneas punteadas
3. Usar colores diferentes por swimlane
4. Incluir tiempos estimados en procesos largos (ej: "Monitoreo: hasta 5 min")

**Trazabilidad**: Requirements RF-ADM-001, Design sección 10.2

---

## 5. Diagrama de Modelo de Datos (ER Diagram)

### 5.1 Propósito
Mostrar las relaciones entre las tablas principales de la base de datos.

### 5.2 Tablas Principales

**Grupo 1: Jerarquía Geográfica**
- Country (1) → (N) Region
- Region (1) → (N) Department
- Department (1) → (N) City

**Grupo 2: Dispositivos y Flotas**
- DeviceType (1) → (N) InspectorFleets
- InspectorFleets (1) → (N) Inspector
- InspectorService (1) → (1) Inspector

**Grupo 3: Históricos (Particionadas)**
- Inspector (1) → (N) StatusInspectorHistory
- InspectorFleets (1) → (N) InspectorGlobalStats
- ScriptTransaction (1) → (N) HistoricScriptTransaction

**Grupo 4: Variables**
- InspectorFleets (1) → (N) InspectorFleetsVariables
- Inspector (1) → (N) InspectorDeviceVariables

### 5.3 Cardinalidades

| Relación | Cardinalidad | Descripción |
|----------|--------------|-------------|
| Country → Region | 1:N | Un país tiene muchas regiones |
| InspectorFleets → Inspector | 1:N | Una flota tiene muchos dispositivos |
| Inspector → StatusInspectorHistory | 1:N | Un dispositivo tiene muchos registros históricos |
| InspectorService → Inspector | 1:1 | Un servicio está asociado a un dispositivo |

### 5.4 Instrucciones para draw.io

1. Usar **Entity Relationship** shapes
2. Formato de tabla:
   - Nombre de tabla en header (negrita)
   - PK con icono de llave
   - FK con icono de flecha
   - Tipos de datos en gris
3. Líneas de relación:
   - Crow's foot notation para cardinalidad
   - Línea sólida para relaciones obligatorias
   - Línea punteada para opcionales
4. Agrupar tablas por dominio con rectángulos de fondo

**Trazabilidad**: Design sección 2.1, database/init.sql

---

## 6. Diagrama de Secuencia: Gestión de Variables

### 6.1 Propósito
Mostrar la interacción entre componentes al crear/modificar una variable de dispositivo.

### 6.2 Actores y Componentes

- Usuario
- Frontend
- KrakenD
- Backend (Configuration Endpoint)
- ConfigurationSyncService
- BalenaService
- Balena Cloud
- DeviceVarsRepository
- PostgreSQL
- HistoryRepository (Auditoría)

### 6.3 Secuencia de Mensajes

```
Usuario → Frontend: Ingresa nueva variable (key, value)
Frontend → KrakenD: POST /api/v1/configuration/device/{uuid}/vars
KrakenD → Keycloak: Validar JWT
Keycloak → KrakenD: Token válido
KrakenD → Backend: Enrutar petición
Backend → ConfigurationSyncService: create_device_variable(uuid, key, value, user, role)
ConfigurationSyncService → TransactionManager: start_transaction(MANUAL_VAR_CREATE)
TransactionManager → PostgreSQL: INSERT INTO HistoricScriptTransaction
ConfigurationSyncService → BalenaService: set_device_variable(uuid, key, value)
BalenaService → Balena Cloud: balena env add <key> <value> --device <uuid>
Balena Cloud → BalenaService: Comando exitoso
BalenaService → ConfigurationSyncService: Success
ConfigurationSyncService → DeviceVarsRepository: insert_device_variable(uuid, key, value)
DeviceVarsRepository → PostgreSQL: INSERT INTO InspectorDeviceVariables
ConfigurationSyncService → HistoryRepository: insert_variable_audit(...)
HistoryRepository → PostgreSQL: INSERT INTO InspectorAuditVariables
ConfigurationSyncService → TransactionManager: finish_transaction(COMPLETO)
TransactionManager → PostgreSQL: UPDATE HistoricScriptTransaction
ConfigurationSyncService → Backend: {success: true}
Backend → Frontend: 201 Created
Frontend → Usuario: "Variable creada exitosamente ✅"
```

### 6.4 Instrucciones para draw.io

1. Usar **UML Sequence Diagram** template
2. Actores a la izquierda, sistemas a la derecha
3. Líneas de vida (lifelines) verticales
4. Flechas sólidas para llamadas síncronas
5. Flechas punteadas para respuestas
6. Rectángulos de activación en lifelines
7. Notas para explicar pasos críticos

**Trazabilidad**: Requirements RF-CFG-006, Design sección 10

---

## 7. Diagrama de Despliegue (Deployment Diagram)

### 7.1 Propósito
Mostrar la infraestructura física/virtual y cómo se despliegan los componentes.

### 7.2 Nodos

**Servidor Principal** (Docker Host):
- Sistema Operativo: Linux
- Docker Engine
- Red: InspecNet (172.16.0.0/27)

**Contenedores**:
- frontend_inspector (opcional, puede ser externo)
- krakend_inspector
- open_balena_apis
- postgres_inspector
- redis_inspector
- keycloak_inspector
- wg-easy_inspector
- wg-fastapi_inspector
- celery_worker_inspector
- celery_beat_inspector

**Volúmenes Persistentes**:
- pgdata (PostgreSQL data)
- redis_data (Redis data)
- wireguard_data (VPN configs)
- backend_logs (Application logs)

**Sistemas Externos**:
- Balena Cloud (SaaS)
- Dispositivos Inspector (IoT devices en campo)

### 7.3 Conexiones de Red

| Desde | Hacia | Tipo | Puerto |
|-------|-------|------|--------|
| Internet | KrakenD | HTTP | 8081 |
| Internet | WireGuard | UDP | 51820 |
| Todos los contenedores | PostgreSQL | TCP | 5432 (interno) |
| Todos los contenedores | Redis | TCP | 6379 (interno) |
| Backend/Celery | Balena Cloud | HTTPS | 443 |

### 7.4 Instrucciones para draw.io

1. Usar **UML Deployment Diagram** shapes
2. Servidor como **Node** (cubo 3D)
3. Contenedores como **Component** dentro del Node
4. Volúmenes como **Artifact** (documento)
5. Conexiones con **Association** (líneas con estereotipos)
6. Mostrar puertos expuestos vs internos
7. Balena Cloud como nube externa

**Trazabilidad**: Design sección 8, docker-compose.yml

---

## 8. Diagrama de Estados: Dispositivo Inspector

### 8.1 Propósito
Mostrar los posibles estados de un dispositivo y las transiciones entre ellos.

### 8.2 Estados

| Estado | Descripción | Color |
|--------|-------------|-------|
| **Libre** | Dispositivo sin servicio asociado | Gris |
| **Operativo** | Online con servicio asociado | Verde |
| **Offline** | Sin conectividad | Rojo |
| **Reducido** | Online pero con métricas degradadas | Amarillo |
| **Eliminado** | Dispositivo removido del sistema | Negro |

### 8.3 Transiciones

```
[Libre] 
    → (Provisioning) → [Operativo]
    → (Eliminación) → [Eliminado]

[Operativo]
    → (Pérdida de conectividad) → [Offline]
    → (Degradación de métricas) → [Reducido]
    → (Desprovisionamiento) → [Libre]
    → (Eliminación) → [Eliminado]

[Offline]
    → (Reconexión) → [Operativo]
    → (Timeout > 7 días) → [Eliminado]

[Reducido]
    → (Recuperación de métricas) → [Operativo]
    → (Pérdida de conectividad) → [Offline]

[Eliminado]
    → (Estado final, no hay transiciones)
```

### 8.4 Eventos que Disparan Transiciones

- **Provisioning**: Usuario ejecuta provisioning desde UI
- **Pérdida de conectividad**: `boolOnline = false` en sincronización
- **Degradación de métricas**: CPU > 90%, Memoria > 90%, Temp > 80°C
- **Reconexión**: `boolOnline = true` en sincronización
- **Recuperación**: Métricas vuelven a rangos normales
- **Eliminación**: Usuario ejecuta eliminación desde UI

### 8.5 Instrucciones para draw.io

1. Usar **UML State Machine Diagram**
2. Estados como **Rounded rectangles**
3. Estado inicial: círculo negro sólido
4. Estado final: círculo negro con borde
5. Transiciones: flechas con etiquetas de evento
6. Colores según tabla de estados
7. Agregar condiciones de guarda en corchetes [condición]

**Trazabilidad**: Requirements RF-DEV-003, utils/deviceStatus.py

---

## 9. Diagrama de Casos de Uso

### 9.1 Propósito
Mostrar las funcionalidades principales del sistema desde la perspectiva de los actores.

### 9.2 Actores

- Administrador del Sistema
- Operador de Campo
- Auditor
- Sistema Celery (actor secundario)

### 9.3 Casos de Uso

**Gestión de Dispositivos**:
- Ver lista de dispositivos
- Ver detalle de dispositivo
- Reiniciar dispositivo
- Apagar dispositivo
- Mover dispositivo a otra flota
- Eliminar dispositivo
- Provisionar dispositivo
- Actualizar nota de dispositivo

**Gestión de Flotas**:
- Ver lista de flotas
- Crear flota
- Renombrar flota
- Eliminar flota

**Gestión de Variables**:
- Ver variables de dispositivo
- Crear/modificar variable de dispositivo
- Eliminar variable de dispositivo
- Ver variables de flota
- Crear/modificar variable de flota
- Eliminar variable de flota

**Sincronización**:
- Sincronizar inventario manualmente
- Sincronizar inventario automáticamente (Celery)
- Sincronizar configuración

**Monitoreo**:
- Ver dashboard de estadísticas
- Ver histórico de dispositivo
- Ver histórico de transacciones

**VPN**:
- Crear cliente VPN
- Listar clientes VPN
- Eliminar cliente VPN

### 9.4 Relaciones

| Actor | Puede Ejecutar |
|-------|----------------|
| Administrador | Todos los casos de uso |
| Operador | Ver, Reiniciar, Provisionar, Ver variables, Crear/modificar variables |
| Auditor | Ver (solo lectura) |
| Sistema Celery | Sincronización automática, Reinicio automático |

### 9.5 Extensiones e Inclusiones

- **Include**: "Validar autenticación" incluido en todos los casos de uso
- **Include**: "Registrar transacción" incluido en todos los casos de modificación
- **Extend**: "Enviar notificación" extiende casos de éxito/error

### 9.6 Instrucciones para draw.io

1. Usar **UML Use Case Diagram**
2. Actores como **stickman** a los lados
3. Casos de uso como **óvalos**
4. Sistema como **rectángulo** que contiene los casos de uso
5. Relaciones:
   - Línea sólida: Actor → Caso de uso
   - Flecha punteada con <<include>>: Inclusión
   - Flecha punteada con <<extend>>: Extensión
6. Agrupar casos de uso por módulo con colores

**Trazabilidad**: Requirements sección 2 (todos los RF), Overview sección 2

---

## 10. Diagrama de Actividad: Provisioning de Dispositivo

### 10.1 Propósito
Mostrar el flujo detallado del proceso de provisioning de un dispositivo.

### 10.2 Actividades

```
[Inicio]
    ↓
[Actividad] Usuario ingresa datos de provisioning
    ├─ UUID del dispositivo
    ├─ ID de servicio
    ├─ Ciudad
    ├─ Producto
    ├─ Tecnología
    ├─ CMTS/OLT
    ├─ Terminal (MAC/SN)
    └─ Datos de cliente
    ↓
[Decisión] ¿Dispositivo existe en Balena?
    No → [Actividad] Mostrar error "Dispositivo no encontrado" → [Fin]
    Sí → Continuar
    ↓
[Actividad Paralela] Validar referencias en catálogos:
    ├─ [Fork] Validar Ciudad
    ├─ [Fork] Validar Producto
    ├─ [Fork] Validar CMTS/OLT
    └─ [Fork] Validar Terminal Reference
    ↓
[Join] Todas las validaciones
    ↓
[Decisión] ¿Todas las referencias válidas?
    No → [Actividad] Mostrar errores de validación → [Fin]
    Sí → Continuar
    ↓
[Actividad] Iniciar transacción de auditoría
    ↓
[Decisión] ¿Servicio ya existe?
    No → [Actividad] Crear registro en InspectorService
    Sí → [Actividad] Actualizar registro en InspectorService
    ↓
[Decisión] ¿Terminal ya existe?
    No → [Actividad] Crear registro en InspectorTerminalClient
    Sí → [Actividad] Actualizar registro en InspectorTerminalClient
    ↓
[Actividad] Actualizar Inspector.strInspectorServiceId
    ↓
[Actividad] Finalizar transacción (COMPLETO)
    ↓
[Actividad] Mostrar mensaje "Provisioning exitoso ✅"
    ↓
[Fin]
```

### 10.3 Instrucciones para draw.io

1. Usar **UML Activity Diagram**
2. Actividades como **rectángulos redondeados**
3. Decisiones como **rombos**
4. Fork/Join como **barras horizontales negras**
5. Inicio/Fin como **círculos**
6. Swimlanes para separar responsabilidades (UI, Backend, BD)
7. Colores para diferenciar tipos de actividad

**Trazabilidad**: Requirements RF-PRV-001, RF-PRV-002

---

## 11. Diagrama de Paquetes (Package Diagram)

### 11.1 Propósito
Mostrar la organización de módulos del backend y sus dependencias.

### 11.2 Paquetes

```
src/
├── api/
│   └── v1/
│       ├── endpoints/
│       └── schemas/
├── services/
├── repositories/
├── models/
├── utils/
├── core/
└── worker/
```

### 11.3 Dependencias

| Paquete | Depende de |
|---------|------------|
| api.v1.endpoints | services, schemas |
| api.v1.schemas | models |
| services | repositories, utils, models |
| repositories | core (config, db), models |
| worker | services, utils |
| utils | core, models |

### 11.4 Instrucciones para draw.io

1. Usar **UML Package Diagram**
2. Paquetes como **carpetas** (folder shape)
3. Dependencias como **flechas punteadas** con <<import>>
4. Anidar subpaquetes
5. Colores por capa:
   - API: Verde
   - Services: Azul
   - Repositories: Gris
   - Utils: Amarillo
   - Core: Rojo

**Trazabilidad**: Design sección 1.2, estructura de carpetas backend

---

## 12. Diagrama de Comunicación: Celery Task Execution

### 12.1 Propósito
Mostrar la comunicación entre componentes durante la ejecución de una tarea Celery.

### 12.2 Objetos

1. Frontend
2. Backend API
3. Celery (Redis Broker)
4. Celery Worker
5. BalenaService
6. PostgreSQL

### 12.3 Mensajes

```
1: Frontend → Backend API: POST /api/v1/sync/inventory
2: Backend API → Celery: task.delay()
3: Celery → Redis: Encolar mensaje
4: Backend API → Frontend: {task_id: "abc123"}
5: Celery Worker → Redis: Obtener mensaje de cola
6: Celery Worker → BalenaService: sync_all()
7: BalenaService → Balena Cloud: balena fleets --json
8: Balena Cloud → BalenaService: [fleets data]
9: BalenaService → PostgreSQL: INSERT/UPDATE
10: Celery Worker → Redis: Actualizar estado SUCCESS
11: Frontend → Backend API: GET /task/abc123 (polling)
12: Backend API → Redis: AsyncResult(abc123).state
13: Redis → Backend API: "SUCCESS"
14: Backend API → Frontend: {state: "SUCCESS"}
```

### 12.4 Instrucciones para draw.io

1. Usar **UML Communication Diagram**
2. Objetos como **rectángulos**
3. Líneas de comunicación entre objetos
4. Numerar mensajes en orden secuencial
5. Flechas para indicar dirección
6. Agrupar mensajes relacionados con colores

**Trazabilidad**: Design sección 6, worker/tasks.py

---

## 13. Resumen de Diagramas

| # | Nombre | Tipo | Trazabilidad | Prioridad |
|---|--------|------|--------------|-----------|
| 1 | Contexto del Sistema | Context Diagram | Overview §2,3 | Alta |
| 2 | Arquitectura de Componentes | Component Diagram | Design §1.2 | Alta |
| 3 | Flujo de Sincronización | Flowchart | RF-INV-001 | Alta |
| 4 | Flujo de Reinicio | Flowchart + Swimlanes | RF-ADM-001 | Alta |
| 5 | Modelo de Datos | ER Diagram | Design §2.1 | Alta |
| 6 | Gestión de Variables | Sequence Diagram | RF-CFG-006 | Media |
| 7 | Despliegue | Deployment Diagram | Design §8 | Media |
| 8 | Estados de Dispositivo | State Machine | RF-DEV-003 | Media |
| 9 | Casos de Uso | Use Case Diagram | Requirements §2 | Alta |
| 10 | Provisioning | Activity Diagram | RF-PRV-001 | Media |
| 11 | Paquetes Backend | Package Diagram | Design §1.2 | Baja |
| 12 | Comunicación Celery | Communication Diagram | Design §6 | Baja |

---

## 14. Convenciones Generales para draw.io

### 14.1 Colores Estándar

| Elemento | Color Hex | Uso |
|----------|-----------|-----|
| Proceso exitoso | #D5E8D4 | Fondo verde claro |
| Proceso con error | #F8CECC | Fondo rojo claro |
| Decisión | #DAE8FC | Fondo azul claro |
| Subproceso externo | #FFF2CC | Fondo amarillo claro |
| Actor humano | #E1D5E7 | Fondo morado claro |
| Sistema externo | #F5F5F5 | Fondo gris claro |

### 14.2 Fuentes

- **Títulos**: Arial, 14pt, Bold
- **Texto normal**: Arial, 11pt
- **Etiquetas**: Arial, 9pt, Italic

### 14.3 Tamaño de Página

- Formato: A4 Landscape (horizontal)
- Márgenes: 1cm
- Escala: Ajustar para que quepa en una página

### 14.4 Exportación

- Formato: PNG (alta resolución, 300 DPI)
- Formato alternativo: SVG (para documentos editables)
- Incluir en carpeta: `.aidlc/diagrams/`

---

## 15. Checklist de Validación

Cada diagrama debe cumplir:

- [ ] Título claro y descriptivo
- [ ] Leyenda de símbolos (si aplica)
- [ ] Colores consistentes con convenciones
- [ ] Texto legible (mínimo 9pt)
- [ ] Trazabilidad a requisitos/diseño documentada
- [ ] Exportado en PNG y SVG
- [ ] Revisado por al menos 1 persona
- [ ] Versionado en Git

---

## 16. Orden de Creación Recomendado

1. **Diagrama de Contexto** (entender el sistema completo)
2. **Casos de Uso** (entender funcionalidades)
3. **Arquitectura de Componentes** (entender estructura técnica)
4. **Modelo de Datos** (entender persistencia)
5. **Flujos principales** (Sincronización, Reinicio)
6. **Diagramas de detalle** (Secuencia, Actividad, Estados)
7. **Diagramas técnicos** (Despliegue, Paquetes, Comunicación)

---

## 17. Herramientas Alternativas

Si draw.io no está disponible, se pueden usar:

- **PlantUML**: Para diagramas de secuencia y casos de uso (texto → imagen)
- **Mermaid**: Para diagramas simples embebidos en Markdown
- **Lucidchart**: Alternativa online a draw.io
- **Microsoft Visio**: Para entornos corporativos

---

## 18. Mantenimiento de Diagramas

Los diagramas deben actualizarse cuando:

- Se agregan nuevos endpoints o servicios
- Se modifican flujos principales
- Se agregan/eliminan tablas de BD
- Se cambia la arquitectura de despliegue
- Se identifican errores o inconsistencias

**Responsable**: Arquitecto de Software o Tech Lead

**Frecuencia de revisión**: Trimestral o al finalizar cada sprint mayor
