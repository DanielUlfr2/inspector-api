# InspectorGestion 5.0 - Diagramas de Flujo Técnicos

> **Propósito**: Diagramas de flujo detallados de las interacciones técnicas del backend con PostgreSQL, Redis, Celery, WireGuard y otros servicios.

---

## 1. Flujo de Autenticación Segura (HttpOnly Cookies + JWKS)

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant K as KrakenD Gateway
    participant KC as Keycloak
    participant B as Backend FastAPI
    participant PG as PostgreSQL
    
    %% INICIO DE SESIÓN
    U->>F: Ingresa credenciales
    F->>K: POST /auth/login (Credenciales)
    K->>KC: Intercambio OpenID Connect
    KC->>PG: Valida credenciales
    PG-->>KC: OK
    KC-->>K: Retorna Tokens (Access + Refresh)
    
    Note over K: TRANSFORMACIÓN DE SEGURIDAD:<br/>Krakend oculta los tokens reales
    
    K-->>F: 200 OK + Set-Cookie: SESSION_ID=...<br/>HttpOnly; Secure; SameSite=Strict
    
    Note over F: El Frontend NO recibe el JWT.<br/>Solo tiene una cookie opaca inaccesible para JS.<br/>¡Inmune a XSS!
    
    %% PETICIÓN CON COOKIE
    U->>F: Accede al Dashboard
    F->>K: GET /api/v1/infodevices<br/>Cookie: SESSION_ID=...
    
    Note over K: KrakenD valida firma localmente (JWKS)
    K->>K: 1. Extrae JWT de la Cookie/Session
    K->>K: 2. Verifica firma con clave pública en CACHÉ
    K->>K: 3. ¿Expirado? (Sin llamar a Keycloak)
    
    K->>B: Enruta petición + Header Authorization: Bearer {JWT}
    
    B->>B: Backend recibe JWT estándar
    B->>PG: SELECT * FROM Inspector
    PG-->>B: Datos
    B-->>F: 200 OK (Datos JSON)
```

---

## 2. Flujo de Validación KrakenD (Zero-Latency)

```mermaid
flowchart TD
    Start([Petición entrante]) --> HasCookie{¿Tiene Cookie<br/>HttpOnly?}
    
    HasCookie -->|No| Unauth[Retornar 401]
    HasCookie -->|Sí| Extract[KrakenD extrae el token JWT]
    
    Extract --> CheckCache{¿Claves JWKS<br/>en Caché?}
    
    CheckCache -->|No| DownloadJWKS[Descargar llaves públicas<br/>desde Keycloak (1 vez/hora)]
    DownloadJWKS --> SaveCache[Guardar en Memoria KrakenD]
    
    CheckCache -->|Sí| ValidateLocal[Validación Criptográfica Local<br/>(CPU bound, no Network IO)]
    SaveCache --> ValidateLocal
    
    ValidateLocal --> IsValid{¿Firma Válida?}
    
    IsValid -->|No| Reject[Rechazar Petición - 401]
    
    IsValid -->|Sí| InjectHeader[Inyectar Header Authorization<br/>para el Backend]
    InjectHeader --> PassToBackend[Pasar al Microservicio]
    
    style Start fill:#e1f5e1
    style PassToBackend fill:#d4edda
    style ValidateLocal fill:#fff3cd
    style DownloadJWKS fill:#ffe6cc
    style SaveCache fill:#d1ecf1
```

---

## 3. Flujo de Tareas Celery (Backend → Redis → Celery Worker)

```mermaid
sequenceDiagram
    participant API as Backend API
    participant Redis as Redis Broker
    participant Worker as Celery Worker
    participant Balena as BalenaService
    participant PG as PostgreSQL
    
    Note over API: Usuario solicita sincronización
    API->>API: Valida permisos
    API->>Redis: task.delay()<br/>Encola mensaje
    
    Note over Redis: Mensaje en cola:<br/>{task: "sync_all",<br/>args: [],<br/>task_id: "abc123"}
    
    Redis-->>API: task_id: "abc123"
    API-->>API: Retorna 202 Accepted
    
    Note over Worker: Worker escucha cola
    Worker->>Redis: Obtener siguiente tarea
    Redis-->>Worker: Tarea "sync_all"
    
    Worker->>Redis: Actualizar estado: STARTED
    Worker->>PG: TransactionManager.start_transaction()
    PG-->>Worker: historic_id: 456
    
    Worker->>Balena: BalenaService.get_fleets()
    Note over Balena: Ejecuta subprocess:<br/>balena fleets --json
    Balena-->>Worker: [fleets data]
    
    loop Para cada flota
        Worker->>Balena: get_devices_by_fleet(slug)
        Balena-->>Worker: [devices]
        
        loop Para cada dispositivo (max 5 concurrentes)
            Worker->>Balena: get_device_detail(uuid)
            Balena-->>Worker: {metrics}
            Worker->>PG: InfoDevicesRepository.upsert_device()
            PG-->>Worker: OK
        end
    end
    
    Worker->>PG: TransactionManager.finish_transaction(COMPLETO)
    Worker->>Redis: Actualizar estado: SUCCESS
    
    Note over API: Frontend hace polling
    API->>Redis: AsyncResult("abc123").state
    Redis-->>API: "SUCCESS"
    API-->>API: Retorna resultado al frontend
```

---

## 4. Flujo de Conexión a WireGuard VPN

```mermaid
flowchart TD
    Start([Administrador solicita crear cliente VPN]) --> API[POST /api/v1/vpn/clients]
    API --> Auth{¿Usuario es<br/>Administrador?}
    Auth -->|No| Forbidden[403 Forbidden]
    Auth -->|Sí| Validate[Validar datos:<br/>- nombre cliente<br/>- email]
    
    Validate --> CallVPN[Llamar a wg-fastapi]
    CallVPN --> WGCheck{¿wg-fastapi<br/>disponible?}
    
    WGCheck -->|No| ServiceUnavailable[503 Service Unavailable]
    WGCheck -->|Sí| GenerateKeys[Generar par de claves<br/>pública/privada]
    
    GenerateKeys --> AssignIP[Asignar IP del rango<br/>WG_DEFAULT_ADDRESS]
    AssignIP --> CreateConf[Crear archivo .conf<br/>con configuración]
    
    CreateConf --> SaveWG[Guardar en /etc/wireguard/<br/>del contenedor wg-easy]
    SaveWG --> Restart[Reiniciar servicio WireGuard]
    
    Restart --> SaveDB{¿Guardar en BD?}
    SaveDB -->|Sí| InsertPG[INSERT INTO wireguard_clients<br/>en wireguard_db]
    SaveDB -->|No| SkipDB[Solo en archivos]
    
    InsertPG --> ReturnConf[Retornar archivo .conf al usuario]
    SkipDB --> ReturnConf
    
    ReturnConf --> Success[201 Created]
    
    Success --> End([Usuario descarga .conf])
    Forbidden --> End
    ServiceUnavailable --> End
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style Auth fill:#fff3cd
    style WGCheck fill:#fff3cd
    style SaveDB fill:#fff3cd
    style Forbidden fill:#f8d7da
    style ServiceUnavailable fill:#f8d7da
    style Success fill:#d4edda
```

---

## 5. Flujo de Escritura en PostgreSQL con Auditoría

```mermaid
flowchart TD
    Start([Backend recibe petición de modificación]) --> Extract[Extraer usuario y rol del JWT]
    Extract --> StartTx[TransactionManager.start_transaction]
    
    StartTx --> InsertHist[INSERT INTO HistoricScriptTransaction<br/>- strScriptId<br/>- strExecuterUser<br/>- strExecuterRole<br/>- dtExecutionStart]
    
    InsertHist --> GetID[Obtener idHistoricScript]
    GetID --> BeginDB[BEGIN TRANSACTION en PostgreSQL]
    
    BeginDB --> Operation{Tipo de<br/>operación}
    
    Operation -->|Crear Variable| InsertVar[INSERT INTO InspectorDeviceVariables]
    Operation -->|Actualizar Dispositivo| UpdateDev[UPDATE Inspector SET ...]
    Operation -->|Provisionar| MultiInsert[INSERT en múltiples tablas:<br/>- InspectorService<br/>- InspectorTerminalClient<br/>- Inspector]
    
    InsertVar --> AuditVar[INSERT INTO InspectorAuditVariables<br/>- strAction: CREATE<br/>- strValueNew<br/>- idHistoricScript]
    UpdateDev --> AuditDev[INSERT INTO StatusInspectorHistory<br/>- métricas actuales<br/>- idHistoricScript]
    MultiInsert --> AuditMulti[INSERT en auditoría correspondiente]
    
    AuditVar --> CheckError{¿Algún<br/>error?}
    AuditDev --> CheckError
    AuditMulti --> CheckError
    
    CheckError -->|Sí| Rollback[ROLLBACK TRANSACTION]
    CheckError -->|No| Commit[COMMIT TRANSACTION]
    
    Rollback --> FinishFail[TransactionManager.finish_transaction<br/>status: FALLIDO]
    Commit --> FinishSuccess[TransactionManager.finish_transaction<br/>status: COMPLETO]
    
    FinishFail --> UpdateHistFail[UPDATE HistoricScriptTransaction<br/>SET idTransactionStatus = FALLIDO<br/>dtExecutionFinish = NOW]
    FinishSuccess --> UpdateHistSuccess[UPDATE HistoricScriptTransaction<br/>SET idTransactionStatus = COMPLETO<br/>dtExecutionFinish = NOW]
    
    UpdateHistFail --> ReturnError[Retornar 500 Internal Server Error]
    UpdateHistSuccess --> ReturnOK[Retornar 200 OK / 201 Created]
    
    ReturnError --> End([Respuesta HTTP])
    ReturnOK --> End
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style CheckError fill:#fff3cd
    style Rollback fill:#f8d7da
    style Commit fill:#d4edda
    style ReturnError fill:#f8d7da
    style ReturnOK fill:#d4edda
```

---

## 6. Flujo de Lectura de Caché Redis

```mermaid
flowchart TD
    Start([Backend recibe GET request]) --> CacheKey[Generar cache key<br/>ej: devices:all:page:1]
    CacheKey --> CheckRedis{¿Existe en<br/>Redis?}
    
    CheckRedis -->|Sí| GetRedis[redis.get cache_key]
    CheckRedis -->|No| QueryPG[Query a PostgreSQL]
    
    GetRedis --> Deserialize[Deserializar JSON]
    Deserialize --> ValidateTTL{¿TTL<br/>válido?}
    
    ValidateTTL -->|Sí| ReturnCache[Retornar datos del caché]
    ValidateTTL -->|No| DeleteKey[redis.delete cache_key]
    
    DeleteKey --> QueryPG
    QueryPG --> FetchPG[PostgreSQL.fetch query]
    FetchPG --> Serialize[Serializar a JSON]
    Serialize --> SetRedis[redis.set cache_key, data<br/>EX: 300 segundos]
    SetRedis --> ReturnDB[Retornar datos de BD]
    
    ReturnCache --> End([Respuesta HTTP 200])
    ReturnDB --> End
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style CheckRedis fill:#fff3cd
    style ValidateTTL fill:#fff3cd
    style ReturnCache fill:#d4edda
    style SetRedis fill:#d1ecf1
```

---

## 7. Flujo Completo: Reinicio de Dispositivo con Todos los Servicios

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant K as KrakenD
    participant KC as Keycloak
    participant B as Backend
    participant R as Redis
    participant W as Celery Worker
    participant PG as PostgreSQL
    participant Bal as Balena Cloud
    
    U->>F: Click "Reiniciar dispositivo"
    F->>K: POST /api/v1/admin/device/{uuid}/restart<br/>Authorization: Bearer {token}
    
    K->>KC: Validar JWT token
    KC-->>K: Token válido, roles: [Administrador]
    
    K->>B: Enrutar request
    B->>B: Extraer usuario del token
    B->>PG: SELECT * FROM Inspector WHERE uuid = ?
    PG-->>B: Dispositivo encontrado
    
    B->>R: task_restart_single_device.delay(uuid)
    Note over R: Mensaje encolado en Redis
    R-->>B: task_id: "xyz789"
    B-->>F: 202 Accepted {task_id: "xyz789"}
    
    F->>F: Iniciar polling cada 2s
    
    Note over W: Worker obtiene tarea de cola
    W->>R: Obtener tarea
    R-->>W: {task: restart, uuid: ...}
    
    W->>R: Actualizar estado: STARTED
    W->>PG: TransactionManager.start_transaction(MANUAL_RESTART)
    PG-->>W: historic_id: 123
    
    W->>Bal: balena device restart {uuid}
    Note over Bal: Comando enviado al dispositivo<br/>Espera confirmación (timeout 5 min)
    Bal-->>W: Comando completado
    
    W->>PG: TransactionManager.finish_transaction(COMPLETO)
    W->>R: Actualizar estado: SUCCESS
    
    loop Polling cada 2s
        F->>K: GET /api/v1/admin/task/xyz789
        K->>B: Enrutar
        B->>R: AsyncResult("xyz789").state
        R-->>B: "SUCCESS"
        B-->>F: {state: "SUCCESS", result: {...}}
    end
    
    F-->>U: "Dispositivo reiniciado exitosamente ✅"
```

---

## 8. Flujo de Sincronización Automática (Celery Beat)

```mermaid
flowchart TD
    Start([Celery Beat Scheduler]) --> CheckTime{¿Es 5:00 AM?}
    CheckTime -->|No| Sleep[Esperar 1 minuto]
    Sleep --> CheckTime
    
    CheckTime -->|Sí| Trigger[Disparar task_run_automatic_sync]
    Trigger --> Enqueue[Redis: Encolar tarea]
    
    Enqueue --> WorkerPick[Celery Worker obtiene tarea]
    WorkerPick --> StartAudit[PostgreSQL: start_transaction<br/>INVENTORY_SYNC_AUTO]
    
    StartAudit --> GetFleets[BalenaService.get_fleets]
    GetFleets --> SubprocessFleets[subprocess: balena fleets --json]
    
    SubprocessFleets --> ParseFleets[Parsear JSON de flotas]
    ParseFleets --> LoopFleets{Para cada<br/>flota}
    
    LoopFleets -->|Siguiente| UpsertFleet[PostgreSQL: upsert_fleet]
    UpsertFleet --> GetDevices[BalenaService.get_devices_by_fleet]
    GetDevices --> SubprocessDevices[subprocess: balena devices --fleet]
    
    SubprocessDevices --> Semaphore[Crear semáforo: max 5 concurrentes]
    Semaphore --> LoopDevices{Para cada<br/>dispositivo}
    
    LoopDevices -->|Siguiente| AcquireSem[Adquirir semáforo]
    AcquireSem --> GetDetail[BalenaService.get_device_detail]
    GetDetail --> SubprocessDetail[subprocess: balena device {uuid} --json]
    
    SubprocessDetail --> UpsertDevice[PostgreSQL: upsert_device]
    UpsertDevice --> InsertHistory[PostgreSQL: insert_device_status]
    InsertHistory --> ReleaseSem[Liberar semáforo]
    
    ReleaseSem --> LoopDevices
    LoopDevices -->|Fin| UpdateStats[PostgreSQL: update_fleet_stats]
    UpdateStats --> LoopFleets
    
    LoopFleets -->|Fin| FinishAudit[PostgreSQL: finish_transaction<br/>COMPLETO]
    FinishAudit --> UpdateRedis[Redis: Actualizar estado SUCCESS]
    UpdateRedis --> End([Tarea completada])
    
    style Start fill:#e1f5e1
    style End fill:#d4edda
    style CheckTime fill:#fff3cd
    style LoopFleets fill:#d1ecf1
    style LoopDevices fill:#d1ecf1
    style Semaphore fill:#ffeaa7
```

---

## 9. Flujo de Particionamiento Automático (pg_partman)

```mermaid
flowchart TD
    Start([pg_cron ejecuta cada hora]) --> CheckPartman[Ejecutar: SELECT partman.run_maintenance]
    
    CheckPartman --> CheckTables{Para cada tabla<br/>particionada}
    
    CheckTables -->|HistoricScriptTransaction| CheckHistoric[Verificar particiones]
    CheckTables -->|StatusInspectorHistory| CheckStatus[Verificar particiones]
    CheckTables -->|InspectorAuditVariables| CheckAudit[Verificar particiones]
    CheckTables -->|InspectorGlobalStats| CheckStats[Verificar particiones]
    
    CheckHistoric --> NeedCreate1{¿Necesita<br/>nuevas particiones?}
    CheckStatus --> NeedCreate2{¿Necesita<br/>nuevas particiones?}
    CheckAudit --> NeedCreate3{¿Necesita<br/>nuevas particiones?}
    CheckStats --> NeedCreate4{¿Necesita<br/>nuevas particiones?}
    
    NeedCreate1 -->|Sí| CreateDaily1[Crear partición diaria<br/>ej: _p2026_01_27]
    NeedCreate2 -->|Sí| CreateDaily2[Crear partición diaria]
    NeedCreate3 -->|Sí| CreateMonthly1[Crear partición mensual<br/>ej: _p2026_02]
    NeedCreate4 -->|Sí| CreateMonthly2[Crear partición mensual]
    
    NeedCreate1 -->|No| CheckRetention1[Verificar retención]
    NeedCreate2 -->|No| CheckRetention2[Verificar retención]
    NeedCreate3 -->|No| CheckRetention3[Verificar retención]
    NeedCreate4 -->|No| CheckRetention4[Verificar retención]
    
    CreateDaily1 --> CheckRetention1
    CreateDaily2 --> CheckRetention2
    CreateMonthly1 --> CheckRetention3
    CreateMonthly2 --> CheckRetention4
    
    CheckRetention1 --> OldData1{¿Particiones<br/>> 1 mes?}
    CheckRetention2 --> OldData2{¿Particiones<br/>> 1 mes?}
    CheckRetention3 --> OldData3{¿Particiones<br/>> 6 meses?}
    CheckRetention4 --> OldData4{¿Particiones<br/>> 1 año?}
    
    OldData1 -->|Sí| DropPartition1[DROP TABLE _p2025_12_26]
    OldData2 -->|Sí| DropPartition2[DROP TABLE _p2025_12_26]
    OldData3 -->|Sí| DropPartition3[DROP TABLE _p2025_07]
    OldData4 -->|Sí| DropPartition4[DROP TABLE _p2025_01]
    
    OldData1 -->|No| Done1[OK]
    OldData2 -->|No| Done2[OK]
    OldData3 -->|No| Done3[OK]
    OldData4 -->|No| Done4[OK]
    
    DropPartition1 --> Done1
    DropPartition2 --> Done2
    DropPartition3 --> Done3
    DropPartition4 --> Done4
    
    Done1 --> End([Mantenimiento completado])
    Done2 --> End
    Done3 --> End
    Done4 --> End
    
    style Start fill:#e1f5e1
    style End fill:#d4edda
    style NeedCreate1 fill:#fff3cd
    style NeedCreate2 fill:#fff3cd
    style NeedCreate3 fill:#fff3cd
    style NeedCreate4 fill:#fff3cd
    style OldData1 fill:#fff3cd
    style OldData2 fill:#fff3cd
    style OldData3 fill:#fff3cd
    style OldData4 fill:#fff3cd
    style DropPartition1 fill:#f8d7da
    style DropPartition2 fill:#f8d7da
    style DropPartition3 fill:#f8d7da
    style DropPartition4 fill:#f8d7da
```

---

## 10. Flujo de Gestión de Variables con Balena Cloud

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant B as Backend
    participant CS as ConfigurationSyncService
    participant BS as BalenaService
    participant BC as Balena Cloud
    participant PG as PostgreSQL
    participant R as Redis
    
    U->>F: Crear variable: MY_VAR = "value123"
    F->>B: POST /api/v1/configuration/device/{uuid}/vars<br/>{key: "MY_VAR", value: "value123"}
    
    B->>B: Validar permisos (rol Operador o Admin)
    B->>CS: create_device_variable(uuid, key, value, user, role)
    
    CS->>PG: TransactionManager.start_transaction(MANUAL_VAR_CREATE)
    PG-->>CS: historic_id: 789
    
    CS->>BS: set_device_variable(uuid, "MY_VAR", "value123")
    BS->>BS: Construir comando CLI
    Note over BS: balena env add MY_VAR value123<br/>--device {uuid}
    
    BS->>BC: Ejecutar subprocess
    BC->>BC: Validar API token
    BC->>BC: Crear/actualizar variable en dispositivo
    BC-->>BS: Comando exitoso
    BS-->>CS: Success
    
    CS->>PG: INSERT INTO InspectorDeviceVariables<br/>(uuid, varName, varValue)
    PG-->>CS: OK
    
    CS->>PG: INSERT INTO InspectorAuditVariables<br/>(scope: DEVICE, action: CREATE,<br/>valueNew: "value123", historic_id: 789)
    PG-->>CS: OK
    
    CS->>PG: TransactionManager.finish_transaction(COMPLETO)
    PG-->>CS: OK
    
    CS->>R: Invalidar caché de variables del dispositivo
    R-->>CS: OK
    
    CS-->>B: {success: true}
    B-->>F: 201 Created
    F-->>U: "Variable creada exitosamente ✅"
    
    Note over BC,U: Balena Cloud propaga la variable<br/>al dispositivo automáticamente
```

---

## Notas de Implementación

### Colores en los Diagramas

- 🟢 **Verde claro** (#e1f5e1): Inicio/Fin exitoso
- 🟡 **Amarillo** (#fff3cd): Decisiones/Validaciones
- 🔵 **Azul claro** (#d1ecf1): Operaciones con caché/Redis
- 🟢 **Verde oscuro** (#d4edda): Operaciones exitosas
- 🔴 **Rojo claro** (#f8d7da): Errores/Rollback
- 🟠 **Naranja** (#ffeaa7): Concurrencia/Semáforos

### Herramientas para Visualizar

1. **Mermaid Live Editor**: <https://mermaid.live/>
2. **VS Code Extension**: Markdown Preview Mermaid Support
3. **draw.io**: Importar desde código Mermaid (limitado)
4. **GitHub/GitLab**: Renderiza Mermaid automáticamente en README

### Exportar a draw.io

Para convertir estos diagramas a draw.io:

1. Copiar el código Mermaid
2. Ir a <https://mermaid.live/>
3. Pegar el código
4. Exportar como PNG/SVG
5. Importar imagen en draw.io y rediseñar si es necesario

---

## Trazabilidad

| Diagrama | Componentes | Archivos de Código |
|----------|-------------|-------------------|
| 1. Login | Keycloak, KrakenD, Backend | `src/core/security.py` |
| 2. Backend → PostgreSQL | FastAPI, PostgreSQL | `databases/postgres_connector.py` |
| 3. Celery Tasks | Redis, Celery, Backend | `src/worker/tasks.py`, `src/core/celery_app.py` |
| 4. WireGuard VPN | wg-fastapi, wg-easy | `vpn/main.py` |
| 5. Auditoría PostgreSQL | TransactionManager, PostgreSQL | `src/utils/transaction_manager.py` |
| 6. Caché Redis | Redis, Backend | (a implementar) |
| 7. Reinicio Completo | Todos los servicios | `src/services/device_admin_service.py` |
| 8. Sincronización Auto | Celery Beat, Balena | `src/services/inventory_sync.py` |
| 9. Particionamiento | pg_partman, pg_cron | `database/init.sql` |
| 10. Variables | Balena Cloud, PostgreSQL | `src/services/configuration_sync.py` |
