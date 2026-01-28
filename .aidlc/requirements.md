# InspectorGestion 5.0 - Requirements Specification

> **Metodología**: Este documento utiliza la notación **EARS** (Easy Approach to Requirements Syntax) para garantizar claridad, no ambigüedad y verificabilidad de cada requisito.

---

## 1. Alcance y Propósito

### 1.1 Objetivo del Sistema

El sistema InspectorGestion 5.0 debe proporcionar una plataforma centralizada para la gestión, monitoreo y control remoto de dispositivos IoT tipo "Inspector" desplegados en campo, integrándose con Balena Cloud como fuente de verdad del inventario.

### 1.2 Límites del Sistema

**Incluido**:

- Sincronización de inventario con Balena Cloud
- Gestión de flotas y dispositivos
- Monitoreo de métricas en tiempo real
- Ejecución de acciones remotas
- Auditoría de transacciones
- Gestión de configuración (variables)

**Excluido**:

- Desarrollo de aplicaciones para dispositivos
- Actualización de firmware
- Gestión de conectividad de red de dispositivos
- Facturación o gestión comercial

---

## 2. Requisitos Funcionales

### 2.1 Gestión de Inventario

#### RF-INV-001: Sincronización Automática de Inventario

**Mientras** el sistema está operativo,  
**cuando** llega la hora programada (5:00 AM),  
**entonces** el sistema debe iniciar automáticamente la sincronización de inventario con Balena Cloud.

**Criterios de Verificación**:

- La tarea `tasks.run_automatic_sync` debe ejecutarse diariamente a las 5:00 AM
- Debe registrarse una transacción en `HistoricScriptTransaction` con `strScriptId = 'INVENTORY_SYNC_AUTO'`

---

#### RF-INV-002: Sincronización Manual de Inventario

**Cuando** un usuario con rol Administrador solicita sincronización manual,  
**entonces** el sistema debe iniciar inmediatamente la sincronización de inventario.

**Criterios de Verificación**:

- El endpoint `/api/v1/sync/inventory` debe estar disponible
- Debe registrarse una transacción con `strScriptId = 'INVENTORY_SYNC_MANUAL'`
- Debe retornar el estado de la tarea Celery

---

#### RF-INV-003: Obtención de Flotas desde Balena

**Cuando** se ejecuta la sincronización de inventario,  
**entonces** el sistema debe obtener la lista completa de flotas desde Balena Cloud mediante el comando `balena fleets --json`.

**Criterios de Verificación**:

- Debe ejecutarse `BalenaService.get_fleets()`
- Debe retornar un array JSON con todas las flotas
- En caso de error, debe registrarse en logs con nivel ERROR

---

#### RF-INV-004: Actualización de Flotas en Base de Datos

**Cuando** se obtiene la lista de flotas desde Balena,  
**entonces** el sistema debe actualizar o insertar cada flota en la tabla `InspectorFleets`.

**Criterios de Verificación**:

- Debe ejecutarse `FleetRepository.upsert_fleet()` para cada flota
- Debe actualizarse `dtModificationDate` con timestamp actual
- Debe mantenerse la relación con `DeviceType`

---

#### RF-INV-005: Obtención de Dispositivos por Flota

**Cuando** se procesa una flota durante la sincronización,  
**entonces** el sistema debe obtener todos los dispositivos de esa flota mediante `balena devices --fleet <slug> --json`.

**Criterios de Verificación**:

- Debe ejecutarse `BalenaService.get_devices_by_fleet(fleet_slug)`
- Debe retornar array JSON con dispositivos
- Debe manejar flotas vacías sin error

---

#### RF-INV-006: Obtención de Detalles de Dispositivo

**Cuando** se procesa un dispositivo durante la sincronización,  
**entonces** el sistema debe obtener sus métricas detalladas mediante `balena device <uuid> --json`.

**Criterios de Verificación**:

- Debe ejecutarse `BalenaService.get_device_detail(uuid)`
- Debe retornar métricas: CPU, memoria, almacenamiento, temperatura
- Debe procesar hasta 5 dispositivos concurrentemente (semáforo)

---

#### RF-INV-007: Actualización de Dispositivos en Base de Datos

**Cuando** se obtienen los detalles de un dispositivo,  
**entonces** el sistema debe actualizar o insertar el dispositivo en la tabla `Inspector`.

**Criterios de Verificación**:

- Debe ejecutarse `InfoDevicesRepository.upsert_device()`
- Debe actualizar todos los campos: métricas, estado, versiones, conectividad
- Debe mantener `dtModificationDate` actualizado

---

#### RF-INV-008: Registro de Histórico de Estados

**Cuando** se actualiza un dispositivo durante la sincronización,  
**entonces** el sistema debe registrar su estado en `StatusInspectorHistory`.

**Criterios de Verificación**:

- Debe ejecutarse `HistoryRepository.insert_device_status()`
- Debe incluir: `uuidInspector`, métricas, `boolOnline`, `idHistoricScript`
- Debe registrarse con `dtValidate` = timestamp actual

---

#### RF-INV-009: Actualización de Estadísticas Globales

**Cuando** se completa la sincronización de una flota,  
**entonces** el sistema debe calcular y registrar estadísticas agregadas en `InspectorGlobalStats`.

**Criterios de Verificación**:

- Debe contar dispositivos por estado: online, offline, reducido, libre
- Debe registrarse en tabla particionada por mes
- Debe asociarse con `stridInspectorFleet`

---

### 2.2 Gestión de Flotas

#### RF-FLT-001: Creación de Flota

**Cuando** un usuario con rol Administrador solicita crear una flota,  
**entonces** el sistema debe crear la flota en Balena Cloud y registrarla en la base de datos local.

**Criterios de Verificación**:

- Debe ejecutarse `balena fleet create <name> --type <device_type>`
- Debe registrarse en `InspectorFleets` con `intIdBalenaFleet` único
- Debe iniciarse transacción de auditoría con `ScriptIds.MANUAL_FLEET_CREATE`

---

#### RF-FLT-002: Renombrado de Flota

**Cuando** un usuario con rol Administrador solicita renombrar una flota,  
**entonces** el sistema debe renombrar la flota en Balena Cloud y actualizar la base de datos local.

**Criterios de Verificación**:

- Debe ejecutarse `balena fleet rename <old> <new>`
- Debe actualizarse `strSlug` en `InspectorFleets`
- Debe registrarse transacción con `ScriptIds.MANUAL_FLEET_RENAME`

---

#### RF-FLT-003: Eliminación de Flota

**Cuando** un usuario con rol Administrador solicita eliminar una flota,  
**si** la flota no tiene dispositivos asociados,  
**entonces** el sistema debe eliminar la flota en Balena Cloud y en la base de datos local.

**Criterios de Verificación**:

- Debe validar que `intDeviceCount = 0`
- Debe ejecutarse `balena fleet rm <name> --yes`
- Debe eliminarse registro de `InspectorFleets`
- Debe registrarse transacción con `ScriptIds.MANUAL_FLEET_DELETE`

---

#### RF-FLT-004: Listado de Flotas

**Cuando** un usuario solicita el listado de flotas,  
**entonces** el sistema debe retornar todas las flotas con sus estadísticas.

**Criterios de Verificación**:

- Debe ejecutarse `FleetRepository.get_all_fleets()`
- Debe incluir: nombre, slug, tipo de dispositivo, conteo de dispositivos
- Debe ordenarse alfabéticamente por nombre

---

#### RF-FLT-005: Detalle de Flota

**Cuando** un usuario solicita el detalle de una flota específica,  
**entonces** el sistema debe retornar la información completa de la flota y sus dispositivos.

**Criterios de Verificación**:

- Debe ejecutarse `FleetRepository.get_fleet_by_id(fleet_id)`
- Debe incluir lista de dispositivos asociados
- Debe incluir variables de flota

---

### 2.3 Gestión de Dispositivos

#### RF-DEV-001: Listado de Dispositivos

**Cuando** un usuario solicita el listado de dispositivos,  
**entonces** el sistema debe retornar todos los dispositivos con su información básica.

**Criterios de Verificación**:

- Debe ejecutarse `InfoDevicesRepository.get_all_devices()`
- Debe incluir: UUID, nombre, flota, estado, conectividad, métricas
- Debe soportar paginación (opcional)

---

#### RF-DEV-002: Detalle de Dispositivo

**Cuando** un usuario solicita el detalle de un dispositivo específico,  
**entonces** el sistema debe retornar la información completa del dispositivo.

**Criterios de Verificación**:

- Debe ejecutarse `InfoDevicesRepository.get_device_by_uuid(uuid)`
- Debe incluir: métricas, variables, servicio asociado, histórico reciente
- Debe retornar 404 si el dispositivo no existe

---

#### RF-DEV-003: Filtrado de Dispositivos por Estado

**Cuando** un usuario solicita dispositivos filtrados por estado,  
**entonces** el sistema debe retornar solo los dispositivos que cumplan el criterio.

**Criterios de Verificación**:

- Debe soportar filtros: operativo, offline, reducido, libre
- Debe aplicarse la función `get_device_real_status()`
- Debe retornar array vacío si no hay coincidencias

---

#### RF-DEV-004: Búsqueda de Dispositivos

**Cuando** un usuario ingresa un término de búsqueda,  
**entonces** el sistema debe retornar dispositivos que coincidan en nombre, UUID o MAC.

**Criterios de Verificación**:

- Debe buscar en campos: `strInspectorName`, `uuidInspector`, `strMacSn`
- Debe ser case-insensitive
- Debe retornar resultados ordenados por relevancia

---

### 2.4 Acciones de Administración de Dispositivos

#### RF-ADM-001: Reinicio de Aplicación (Restart)

**Cuando** un usuario con permisos solicita reiniciar la aplicación de un dispositivo,  
**si** el dispositivo está en estado operativo,  
**entonces** el sistema debe ejecutar el comando de reinicio y monitorear su completitud.

**Criterios de Verificación**:

- Debe ejecutarse `balena device restart <uuid>`
- Debe encolarse tarea Celery `task_restart_single_device`
- Debe registrarse transacción con `ScriptIds.MANUAL_RESTART`
- Debe monitorear completitud con timeout de 5 minutos
- Debe actualizar estado de tarea en tiempo real

---

#### RF-ADM-002: Reinicio de Sistema Operativo (Reboot)

**Cuando** un usuario con permisos solicita reiniciar el sistema operativo de un dispositivo,  
**si** el dispositivo está en estado operativo,  
**entonces** el sistema debe ejecutar el comando de reboot y monitorear su completitud.

**Criterios de Verificación**:

- Debe ejecutarse `balena device reboot <uuid>`
- Debe encolarse tarea Celery `task_restart_single_device` con action='reboot'
- Debe registrarse transacción con `ScriptIds.MANUAL_REBOOT`
- Debe monitorear completitud con timeout de 5 minutos

---

#### RF-ADM-003: Apagado de Dispositivo (Shutdown)

**Cuando** un usuario con permisos solicita apagar un dispositivo,  
**si** el dispositivo está en estado operativo,  
**entonces** el sistema debe ejecutar el comando de apagado.

**Criterios de Verificación**:

- Debe ejecutarse `balena device shutdown <uuid>`
- Debe encolarse tarea Celery `task_restart_single_device` con action='shutdown'
- Debe registrarse transacción con `ScriptIds.MANUAL_SHUTDOWN`
- Debe monitorear completitud con timeout de 5 minutos

---

#### RF-ADM-004: Reinicio Masivo de Dispositivos

**Cuando** un usuario con permisos solicita reiniciar múltiples dispositivos,  
**entonces** el sistema debe filtrar dispositivos operativos y procesarlos en lotes de 10.

**Criterios de Verificación**:

- Debe ejecutarse `task_restart_bulk_devices`
- Debe filtrar solo dispositivos con estado "operativo"
- Debe procesar en chunks de 10 dispositivos
- Debe retornar resumen: total, válidos, excluidos

---

#### RF-ADM-005: Reinicio Automático Programado

**Mientras** el sistema está operativo,  
**cuando** llega la hora programada de reinicio automático,  
**entonces** el sistema debe reiniciar todos los dispositivos operativos.

**Criterios de Verificación**:

- Debe ejecutarse tarea `task_run_automatic_restart` (programada)
- Debe filtrar solo dispositivos operativos
- Debe registrarse transacción con `ScriptIds.AUTO_RESTART`
- Debe retornar resumen de ejecución

---

#### RF-ADM-006: Movimiento de Dispositivo entre Flotas

**Cuando** un usuario con permisos solicita mover un dispositivo a otra flota,  
**entonces** el sistema debe ejecutar el movimiento en Balena Cloud y actualizar la base de datos.

**Criterios de Verificación**:

- Debe ejecutarse `balena device move <uuid> --fleet <target>`
- Debe actualizarse `stridInspectorFleet` en tabla `Inspector`
- Debe registrarse transacción con `ScriptIds.MANUAL_DEVICE_MOVE`
- Debe manejar conversión entre ID local y slug Balena

---

#### RF-ADM-007: Eliminación de Dispositivo

**Cuando** un usuario con rol Administrador solicita eliminar un dispositivo,  
**entonces** el sistema debe eliminar el dispositivo de Balena Cloud y marcarlo como eliminado en la base de datos.

**Criterios de Verificación**:

- Debe ejecutarse `balena device rm <uuid> --yes`
- Debe actualizarse estado en BD (soft delete o hard delete según diseño)
- Debe registrarse transacción con `ScriptIds.MANUAL_DEVICE_DELETE`

---

#### RF-ADM-008: Actualización de Nota de Dispositivo

**Cuando** un usuario actualiza la nota de un dispositivo,  
**entonces** el sistema debe actualizar la nota en Balena Cloud y en la base de datos local.

**Criterios de Verificación**:

- Debe ejecutarse `balena device note <uuid> <note>`
- Debe actualizarse campo `strNote` en tabla `Inspector`
- Debe registrarse transacción con `ScriptIds.MANUAL_DEVICE_NOTE`

---

### 2.5 Gestión de Configuración (Variables)

#### RF-CFG-001: Sincronización de Variables de Flota

**Cuando** se ejecuta la sincronización de configuración,  
**entonces** el sistema debe obtener todas las variables de cada flota desde Balena Cloud.

**Criterios de Verificación**:

- Debe ejecutarse `BalenaService.get_fleet_vars(fleet_slug)`
- Debe actualizarse tabla `InspectorFleetsVariables`
- Debe registrarse auditoría en `InspectorAuditVariables`

---

#### RF-CFG-002: Sincronización de Variables de Dispositivo

**Cuando** se ejecuta la sincronización de configuración,  
**entonces** el sistema debe obtener todas las variables de cada dispositivo desde Balena Cloud.

**Criterios de Verificación**:

- Debe ejecutarse `BalenaService.get_device_vars(uuid)`
- Debe actualizarse tabla `InspectorDeviceVariables`
- Debe registrarse auditoría en `InspectorAuditVariables`

---

#### RF-CFG-003: Creación de Variable de Flota

**Cuando** un usuario con permisos crea una variable de flota,  
**entonces** el sistema debe crear la variable en Balena Cloud y registrarla en la base de datos.

**Criterios de Verificación**:

- Debe ejecutarse `balena env add <key> <value> --fleet <slug>`
- Debe insertarse en `InspectorFleetsVariables`
- Debe registrarse auditoría con `strAction = 'CREATE'`
- Debe validar unicidad de `(stridInspectorFleet, strFleetVarName)`

---

#### RF-CFG-004: Actualización de Variable de Flota

**Cuando** un usuario con permisos actualiza una variable de flota existente,  
**entonces** el sistema debe actualizar la variable en Balena Cloud y en la base de datos.

**Criterios de Verificación**:

- Debe ejecutarse `balena env add <key> <value> --fleet <slug>` (sobrescribe)
- Debe actualizarse `strFleetVarValue` en `InspectorFleetsVariables`
- Debe registrarse auditoría con `strAction = 'UPDATE'`, incluyendo valor antiguo y nuevo

---

#### RF-CFG-005: Eliminación de Variable de Flota

**Cuando** un usuario con permisos elimina una variable de flota,  
**entonces** el sistema debe eliminar la variable de Balena Cloud y de la base de datos.

**Criterios de Verificación**:

- Debe ejecutarse `BalenaService.remove_fleet_variable(fleet_slug, key)`
- Debe eliminarse de `InspectorFleetsVariables`
- Debe registrarse auditoría con `strAction = 'DELETE'`

---

#### RF-CFG-006: Creación de Variable de Dispositivo

**Cuando** un usuario con permisos crea una variable de dispositivo,  
**entonces** el sistema debe crear la variable en Balena Cloud y registrarla en la base de datos.

**Criterios de Verificación**:

- Debe ejecutarse `balena env add <key> <value> --device <uuid>`
- Debe insertarse en `InspectorDeviceVariables`
- Debe registrarse auditoría con `strAction = 'CREATE'`
- Debe validar unicidad de `(uuidInspector, strDeviceVarName)`

---

#### RF-CFG-007: Actualización de Variable de Dispositivo

**Cuando** un usuario con permisos actualiza una variable de dispositivo existente,  
**entonces** el sistema debe actualizar la variable en Balena Cloud y en la base de datos.

**Criterios de Verificación**:

- Debe ejecutarse `balena env add <key> <value> --device <uuid>` (sobrescribe)
- Debe actualizarse `strDeviceVarValue` en `InspectorDeviceVariables`
- Debe registrarse auditoría con `strAction = 'UPDATE'`

---

#### RF-CFG-008: Eliminación de Variable de Dispositivo

**Cuando** un usuario con permisos elimina una variable de dispositivo,  
**entonces** el sistema debe eliminar la variable de Balena Cloud y de la base de datos.

**Criterios de Verificación**:

- Debe ejecutarse `BalenaService.remove_device_variable(uuid, key)`
- Debe eliminarse de `InspectorDeviceVariables`
- Debe registrarse auditoría con `strAction = 'DELETE'`

---

### 2.6 Provisioning

#### RF-PRV-001: Asociación de Dispositivo con Servicio

**Cuando** un usuario con permisos provisiona un dispositivo,  
**entonces** el sistema debe asociar el dispositivo con un servicio, ubicación geográfica y terminal.

**Criterios de Verificación**:

- Debe validar existencia de dispositivo en Balena
- Debe crear/actualizar registro en `InspectorService`
- Debe crear/actualizar registro en `InspectorTerminalClient`
- Debe actualizar `strInspectorServiceId` en tabla `Inspector`
- Debe registrarse transacción con `ScriptIds.MANUAL_PROVISIONING`

---

#### RF-PRV-002: Validación de Datos de Provisioning

**Cuando** un usuario ingresa datos de provisioning,  
**entonces** el sistema debe validar la existencia de referencias en catálogos.

**Criterios de Verificación**:

- Debe validar existencia de `idCity` en tabla `City`
- Debe validar existencia de `idProduct` en tabla `Product`
- Debe validar existencia de `idCmtsOlt` en tabla `CmtsOlt`
- Debe validar existencia de `idTerminalReference` en tabla `TerminalReference`
- Debe retornar error 400 si alguna referencia no existe

---

### 2.7 Monitoreo y Reportes

#### RF-MON-001: Dashboard de Estadísticas Globales

**Cuando** un usuario accede al dashboard,  
**entonces** el sistema debe mostrar estadísticas agregadas de todos los dispositivos.

**Criterios de Verificación**:

- Debe consultar última partición de `InspectorGlobalStats`
- Debe mostrar: total de dispositivos, online, offline, reducidos, libres
- Debe agrupar por flota

---

#### RF-MON-002: Histórico de Estados de Dispositivo

**Cuando** un usuario solicita el histórico de un dispositivo,  
**entonces** el sistema debe retornar los registros de `StatusInspectorHistory` para ese dispositivo.

**Criterios de Verificación**:

- Debe ejecutarse `HistoryRepository.get_device_history(uuid, date_range)`
- Debe soportar filtrado por rango de fechas
- Debe ordenarse por `dtValidate` descendente
- Debe incluir métricas históricas

---

#### RF-MON-003: Histórico de Transacciones

**Cuando** un usuario solicita el histórico de transacciones,  
**entonces** el sistema debe retornar los registros de `HistoricScriptTransaction`.

**Criterios de Verificación**:

- Debe ejecutarse `HistoryRepository.get_transactions_history(filters)`
- Debe soportar filtrado por: script, usuario, estado, rango de fechas
- Debe incluir: descripción, usuario ejecutor, duración, estado

---

#### RF-MON-004: Logs de Dispositivo en Tiempo Real

**Cuando** un usuario solicita los logs de un dispositivo,  
**entonces** el sistema debe transmitir los logs en tiempo real desde Balena Cloud.

**Criterios de Verificación**:

- Debe ejecutarse `BalenaService.stream_device_logs(uuid)`
- Debe retornar stream de logs (Server-Sent Events o WebSocket)
- Debe manejar desconexión y reconexión

---

### 2.8 Seguridad y Autenticación

#### RF-SEC-001: Autenticación de Usuario

**Cuando** un usuario intenta acceder al sistema,  
**entonces** el sistema debe validar sus credenciales mediante Keycloak.

**Criterios de Verificación**:

- Debe redirigir a Keycloak para autenticación
- Debe recibir token JWT válido
- Debe almacenar token en memoria del cliente (Client-Side Storage)

---

#### RF-SEC-002: Validación de Token en Cada Petición

**Cuando** se recibe una petición HTTP en el API Gateway,  
**entonces** KrakenD debe validar el token JWT antes de enrutar la petición.

**Criterios de Verificación**:

- Debe validar firma del token con clave pública de Keycloak
- Debe validar expiración del token
- Debe retornar 401 si el token es inválido o expirado

---

#### RF-SEC-003: Control de Acceso Basado en Roles

**Cuando** un usuario intenta ejecutar una acción,  
**entonces** el sistema debe validar que el rol del usuario tiene permisos para esa acción.

**Criterios de Verificación**:

- Debe extraer rol del token JWT
- Debe validar permisos según matriz de roles
- Debe retornar 403 si el usuario no tiene permisos

---

#### RF-SEC-004: Auditoría de Acciones de Usuario

**Cuando** un usuario ejecuta una acción que modifica datos,  
**entonces** el sistema debe registrar la acción en el histórico de transacciones.

**Criterios de Verificación**:

- Debe registrarse en `HistoricScriptTransaction`
- Debe incluir: `strExecuterUser`, `strExecuterRole`, timestamp
- Debe ser inmutable (no se puede editar ni eliminar)

---

### 2.9 Gestión de VPN

#### RF-VPN-001: Creación de Cliente VPN

**Cuando** un administrador solicita crear un cliente VPN,  
**entonces** el sistema debe generar configuración WireGuard para el cliente.

**Criterios de Verificación**:

- Debe ejecutarse API de `wg-fastapi`
- Debe generar par de claves pública/privada
- Debe asignar IP del rango configurado
- Debe retornar archivo de configuración `.conf`

---

#### RF-VPN-002: Listado de Clientes VPN

**Cuando** un administrador solicita la lista de clientes VPN,  
**entonces** el sistema debe retornar todos los clientes registrados.

**Criterios de Verificación**:

- Debe consultar API de `wg-fastapi`
- Debe incluir: nombre, IP asignada, última conexión, estado

---

#### RF-VPN-003: Eliminación de Cliente VPN

**Cuando** un administrador solicita eliminar un cliente VPN,  
**entonces** el sistema debe revocar el acceso del cliente.

**Criterios de Verificación**:

- Debe ejecutarse API de `wg-fastapi`
- Debe eliminar configuración del cliente
- Debe desconectar sesión activa si existe

---

## 3. Requisitos No Funcionales

### 3.1 Rendimiento

#### RNF-PER-001: Tiempo de Respuesta de API

**Mientras** el sistema está bajo carga normal (< 100 peticiones/minuto),  
**cuando** se ejecuta una consulta de lectura,  
**entonces** el sistema debe responder en menos de 500ms en el percentil 95.

**Criterios de Verificación**:

- Medición con herramientas de monitoreo (Prometheus/Grafana)
- Pruebas de carga con Apache JMeter o Locust

---

#### RNF-PER-002: Concurrencia en Sincronización

**Cuando** se ejecuta la sincronización de inventario,  
**entonces** el sistema debe procesar hasta 5 dispositivos concurrentemente.

**Criterios de Verificación**:

- Implementación de semáforo con `MAX_CONCURRENT_TASKS = 5`
- Logs deben mostrar procesamiento paralelo

---

#### RNF-PER-003: Tiempo de Sincronización Completa

**Cuando** se ejecuta la sincronización completa de inventario,  
**si** hay menos de 1000 dispositivos,  
**entonces** el proceso debe completarse en menos de 10 minutos.

**Criterios de Verificación**:

- Medición de duración en `HistoricScriptTransaction`
- Campo `dtExecutionFinish - dtExecutionStart < 10 minutos`

---

### 3.2 Disponibilidad

#### RNF-DIS-001: Disponibilidad del Sistema

**Mientras** el sistema está en producción,  
**entonces** debe mantener una disponibilidad del 99% mensual.

**Criterios de Verificación**:

- Monitoreo con healthchecks
- Cálculo: (tiempo total - tiempo de downtime) / tiempo total >= 0.99

---

#### RNF-DIS-002: Recuperación ante Fallos

**Cuando** un servicio falla,  
**entonces** Docker debe reiniciarlo automáticamente.

**Criterios de Verificación**:

- Configuración `restart: unless-stopped` en docker-compose
- Logs de Docker deben mostrar reinicios automáticos

---

### 3.3 Escalabilidad

#### RNF-ESC-001: Capacidad de Dispositivos

**Mientras** el sistema está operativo,  
**entonces** debe soportar hasta 10,000 dispositivos registrados.

**Criterios de Verificación**:

- Pruebas de carga con dataset de 10,000 dispositivos
- Consultas deben mantener tiempos de respuesta aceptables

---

#### RNF-ESC-002: Particionamiento de Tablas

**Cuando** se insertan registros en tablas históricas,  
**entonces** el sistema debe utilizar particionamiento automático por tiempo.

**Criterios de Verificación**:

- Configuración de `pg_partman` para tablas históricas
- Verificación de particiones creadas automáticamente

---

### 3.4 Seguridad

#### RNF-SEG-001: Encriptación de Comunicaciones

**Cuando** se transmiten datos entre componentes,  
**entonces** las comunicaciones deben estar encriptadas.

**Criterios de Verificación**:

- HTTPS para comunicaciones externas
- TLS para conexiones a PostgreSQL (producción)
- WireGuard para VPN

---

#### RNF-SEG-002: Almacenamiento Seguro de Credenciales

**Cuando** el sistema requiere credenciales de servicios externos,  
**entonces** deben almacenarse en variables de entorno, no en código.

**Criterios de Verificación**:

- Revisión de código: no debe haber credenciales hardcodeadas
- Uso de archivos `.env` y Docker secrets

---

#### RNF-SEG-003: Expiración de Tokens

**Cuando** se emite un token JWT,  
**entonces** debe tener un tiempo de expiración de máximo 24 horas.

**Criterios de Verificación**:

- Configuración de Keycloak con `Access Token Lifespan = 24h`
- Validación de campo `exp` en token

---

### 3.5 Mantenibilidad

#### RNF-MAN-001: Logs Estructurados

**Cuando** el sistema registra eventos,  
**entonces** los logs deben seguir un formato estructurado (JSON).

**Criterios de Verificación**:

- Configuración de logger con formato JSON
- Logs deben incluir: timestamp, nivel, mensaje, contexto

---

#### RNF-MAN-002: Retención de Datos

**Cuando** se alcanzan los límites de retención,  
**entonces** el sistema debe eliminar automáticamente datos antiguos.

**Criterios de Verificación**:

- Configuración de `pg_partman` con políticas de retención
- Verificación de eliminación automática de particiones antiguas

---

### 3.6 Usabilidad

#### RNF-USA-001: Tiempo de Carga de Dashboard

**Cuando** un usuario accede al dashboard,  
**entonces** la página debe cargar completamente en menos de 2 segundos.

**Criterios de Verificación**:

- Medición con Chrome DevTools (Lighthouse)
- Métrica: Time to Interactive < 2s

---

#### RNF-USA-002: Feedback de Acciones Asíncronas

**Cuando** un usuario ejecuta una acción asíncrona (restart, sync),  
**entonces** el sistema debe mostrar el progreso en tiempo real.

**Criterios de Verificación**:

- Implementación de polling o WebSocket
- UI debe mostrar estados: pending, in_progress, completed, failed

---

## 4. Restricciones y Suposiciones

### 4.1 Restricciones

| ID | Restricción |
|----|-------------|
| **RES-001** | El sistema debe ejecutarse en contenedores Docker |
| **RES-002** | La base de datos debe ser PostgreSQL 15+ |
| **RES-003** | La integración con Balena Cloud debe usar Balena CLI (no SDK) |
| **RES-004** | El frontend debe ser compatible con navegadores modernos (Chrome, Firefox, Edge) |
| **RES-005** | El sistema debe operar en zona horaria configurable (variable `TZ`) |

### 4.2 Suposiciones

| ID | Suposición |
|----|------------|
| **SUP-001** | Balena Cloud está disponible 99.9% del tiempo |
| **SUP-002** | Los dispositivos tienen conectividad a internet estable |
| **SUP-003** | Keycloak está correctamente configurado con realm y clientes |
| **SUP-004** | Los usuarios tienen conocimientos básicos de gestión de dispositivos IoT |
| **SUP-005** | El servidor tiene acceso a internet para comunicarse con Balena Cloud |

---

## 5. Matriz de Trazabilidad

| Requisito | Componente | Tabla BD | Endpoint API |
|-----------|------------|----------|--------------|
| RF-INV-001 | InventorySyncService | HistoricScriptTransaction | - |
| RF-INV-002 | InventorySyncService | HistoricScriptTransaction | POST /api/v1/sync/inventory |
| RF-FLT-001 | FleetAdminService | InspectorFleets | POST /api/v1/fleets |
| RF-FLT-002 | FleetAdminService | InspectorFleets | PUT /api/v1/fleets/{id} |
| RF-DEV-001 | InfoDevicesService | Inspector | GET /api/v1/infodevices |
| RF-ADM-001 | DeviceAdminService | HistoricScriptTransaction | POST /api/v1/admin/device/{uuid}/restart |
| RF-CFG-003 | ConfigurationSyncService | InspectorFleetsVariables | POST /api/v1/configuration/fleet/{id}/vars |
| RF-PRV-001 | DeviceAdminService | InspectorService, Inspector | POST /api/v1/admin/device/{uuid}/provision |

---

## 6. Criterios de Aceptación Globales

1. **Todos los requisitos funcionales** deben tener pruebas automatizadas o manuales documentadas
2. **Todas las transacciones** deben registrarse en `HistoricScriptTransaction`
3. **Todas las acciones de usuario** deben incluir usuario y rol ejecutor
4. **Todos los errores** deben registrarse en logs con nivel ERROR
5. **Todas las APIs** deben retornar códigos HTTP estándar (200, 400, 401, 403, 404, 500)
6. **Todas las fechas** deben almacenarse en formato UTC (timestamp)
7. **Todas las operaciones con Balena** deben manejar timeouts y reintentos

---

## 7. Glosario de Términos EARS

- **Mientras**: Condición de estado del sistema
- **Cuando**: Evento que dispara el requisito
- **Si**: Condición adicional que debe cumplirse
- **Entonces**: Respuesta esperada del sistema
- **Debe**: Obligatorio (requisito mandatorio)
