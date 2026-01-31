# Infraestructura y Ecosistema de InspectorGestion 5.0

Este documento detalla la arquitectura, roles de servicios y flujos de comunicación del sistema InspectorGestion 5.0, basado en los diagramas de infraestructura y flujo proporcionados.

## 1. Visión General del Ecosistema

El sistema se divide en dos grandes segmentos de red:
1.  **Red Externa (Internet / Blanco)**: Donde residen los dispositivos remotos (Inspectores), el servidor OpenBalena y el Servidor de Aplicación expuesto.
2.  **Red Interna (Amarillo - Corporativa)**: Donde residen los servicios core de la aplicación, bases de datos y gestión.

---

## 2. Roles y Funciones de los Servicios

### A. Capa de Cliente y Frontend
*   **Web Browser (Usuario)**: El punto de entrada para los operadores y administradores.
*   **Frontend (React + Vite + TypeScript)**:
    *   **Rol**: Interfaz de usuario (SPA - Single Page Application).
    *   **Función**: Proporciona la experiencia visual (Dashboards, gestión de flotas, acciones). Consume la API a través del Gateway.
    *   **Tecnología**: React para componentes, Vite para empaquetado ultra-rápido, TypeScript para seguridad de tipos.

### B. Capa de Entrada y Seguridad (Gateway)
*   **KrakenD (API Gateway)**:
    *   **Rol**: Portero y orquestador de tráfico.
    *   **Función**: Recibe todas las peticiones del frontend (Puerto 8081). Valida la autenticación (comunicándose con Keycloak) antes de dejar pasar la petición al Backend. Es stateless (sin estado), lo que lo hace muy rápido.
*   **Keycloak (Identity Provider)**:
    *   **Rol**: Servidor de identidad y acceso.
    *   **Función**: Gestiona usuarios, roles, login y emisión de tokens (JWT). Garantiza que solo usuarios autenticados reciban credenciales válidas.
    *   **Seguridad**: Se ejecuta sobre HTTPS (Puerto 8443) usando certificados firmados por una Root CA interna, permitiendo validación estricta desde el Gateway.

### C. Capa de Backend y Lógica
*   **FastAPI (Backend)**:
    *   **Rol**: Cerebro de la aplicación.
    *   **Función**: Ejecuta la lógica de negocio, coordina acciones sobre los dispositivos, lee/escribe en base de datos y encola tareas pesadas. Se conecta con el Servidor OpenBalena para gestionar los dispositivos.
*   **Celery + Redis**:
    *   **Rol**: Procesamiento asíncrono y Cola de Mensajes.
    *   **Función**: Redis actúa como "broker" (buzón de mensajes). Celery (workers) recoge tareas pesadas (como "Reiniciar 500 dispositivos" o "Sincronizar inventario") y las ejecuta en segundo plano para no bloquear al usuario.

### D. Capa de Datos
*   **PostgreSQL**:
    *   **Rol**: Base de datos relacional principal.
    *   **Función**: Almacena toda la información estructurada: inventario, históricos, usuarios, configuración, auditoría. (Puerto 5432).

### E. Ecosistema de Dispositivos (Externo)
*   **OpenBalena Server**:
    *   **Rol**: Gestor de flota IoT.
    *   **Función**: Plataforma que mantiene el túnel (VPN/WireGuard) con los dispositivos remotos y gestiona su software (actualizaciones, reinicios).
*   **Inspector Devices (Raspberry Pi)**:
    *   **Rol**: Agentes en campo.
    *   **Función**: Ejecutan scripts de Python, recogen métricas, tienen base de datos local (SQLite) y se conectan vía VPN (WireGuard) al servidor OpenBalena.

---

## 3. Matriz de Comunicación y Puertos

| Origen | Destino | Protocolo | Puerto | Sentido | Descripción |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Browser** | **Frontend** | HTTPS | 443 | Bidireccional | Carga de la aplicación web. |
| **Frontend** | **KrakenD** | HTTP/JSON | 8081 | Bidireccional | Peticiones API del usuario. |
| **KrakenD** | **Keycloak** | HTTP | 8080 | Bidireccional | Validación de tokens y autenticación. |
| **KrakenD** | **FastAPI** | HTTP | Interno | Bidireccional | Enrutamiento de peticiones validadas. |
| **FastAPI** | **PostgreSQL**| TCP | 5432 | Bidireccional | Consultas y persistencia de datos. |
| **FastAPI** | **Redis** | TCP | 6379 | Bidireccional | Encolado de tareas y caché. |
| **Celery** | **Redis** | TCP | 6379 | Bidireccional | Consumo de tareas y reporte de estado. |
| **FastAPI** | **OpenBalena**| HTTPS | 443 | Saliente | Comandos de gestión (Restart, Reboot, Fleet Info). La comunicación es iniciada por FastAPI hacia OpenBalena. |
| **Devices** | **OpenBalena**| UDP/VPN | Variado | Bidireccional | Túnel WireGuard persistente para control y gestión. |

---

## 4. Flujo de Datos Detallado (Basado en el Diagrama de Secuencia)

1.  **Autenticación (Login)**:
    *   El usuario hace Login en el Frontend.
    *   Se redirige a **Keycloak** (puerto 8080) para ingresar credenciales.
    *   Keycloak valida contra **PostgreSQL** y devuelve un **Token JWT** (Access + Refresh).
    *   El Frontend guarda el token en memoria (o cookie) para usarlo en futuras peticiones.

2.  **Petición de Datos (Ej: Ver Dispositivos)**:
    *   El Frontend pide datos a `GET /api/v1/infodevices` apuntando a **KrakenD** (puerto 8081).
    *   **KrakenD** intercepta la petición y valida el Token JWT (firma criptográfica).
    *   Si es válido, inyecta headers de identidad (`X-User-Id`) y pasa la petición a **FastAPI**.
    *   **FastAPI** recibe la petición segura, consulta **PostgreSQL** (puerto 5432) y devuelve los datos JSON.

3.  **Gestión de Dispositivos (Ej: Reinicio)**:
    *   **FastAPI** recibe la orden de reinicio.
    *   Envía una petición HTTPS (Puerto 443) al **Server OpenBalena**.
    *   **Importante**: Esta conexión es **SALIENTE** desde nuestra red interna hacia OpenBalena. No se necesitan puertos de entrada abiertos en el firewall corporativo, solo salida HTTPS (443).

---

## 5. Justificación Tecnológica: Vite y TypeScript

### ¿Por qué Vite en lugar de Webpack/CRA?
Vite ("rápido" en francés) es la herramienta de construcción moderna estándar.
1.  **Velocidad de Desarrollo**: Inicia el servidor de desarrollo casi instantáneamente, a diferencia de Webpack que debe empaquetar todo primero.
2.  **HMR (Hot Module Replacement)**: Los cambios en el código se reflejan en el navegador en milisegundos, sin recargar toda la página.
3.  **Optimización**: Genera bundles de producción altamente optimizados y ligeros.

### ¿Por qué TypeScript en lugar de JavaScript?
TypeScript es un superconjunto de JavaScript que añade tipos estáticos.
1.  **Seguridad y Menos Errores**: Detecta errores "tontos" (como intentar sumar un texto y un número, o acceder a una propiedad que no existe) **mientras escribes el código**, no cuando el usuario está usando la app y esta se rompe ("undefined is not a function").
2.  **Autocompletado y Documentación**: Al saber qué forma tienen los datos (ej: un `Device` siempre tiene `uuid` y `name`), el editor de código te sugiere las propiedades. El código se documenta solo.
3.  **Mantener Proyectos Grandes**: En proyectos complejos como este, con muchos modelos de datos (Dispositivos, Flotas, Usuarios), TypeScript es vital para que el equipo pueda refactorizar y trabajar sin miedo a romper partes ocultas del sistema.
