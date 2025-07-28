# Configuración de Docker para Inspector API

## Autor: Daniel Bermúdez
## Versión: 1.0.0
## Descripción: Guía completa para configurar y ejecutar la aplicación en contenedores Docker

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Archivos de Configuración](#archivos-de-configuración)
3. [Configuración Inicial](#configuración-inicial)
4. [Modos de Ejecución](#modos-de-ejecución)
5. [Gestión de Servicios](#gestión-de-servicios)
6. [Troubleshooting](#troubleshooting)
7. [Optimizaciones](#optimizaciones)

## 🔧 Requisitos Previos

### Software Requerido
- **Docker**: Versión 20.10 o superior
- **Docker Compose**: Versión 2.0 o superior
- **OpenSSL**: Para generar certificados SSL (incluido en la mayoría de sistemas)

### Verificación de Instalación
```bash
# Verificar Docker
docker --version

# Verificar Docker Compose
docker-compose --version

# Verificar OpenSSL
openssl version
```

## 📁 Archivos de Configuración

### 1. Dockerfile
**Ubicación**: `./Dockerfile`
**Propósito**: Define la imagen base y configuración de la aplicación

**Características**:
- Imagen base: Python 3.11-slim
- Optimizaciones de rendimiento
- Instalación de dependencias del sistema
- Configuración de directorios y permisos

### 2. docker-compose.yml
**Ubicación**: `./docker-compose.yml`
**Propósito**: Configuración para producción

**Servicios incluidos**:
- **api**: Aplicación FastAPI
- **db**: Base de datos PostgreSQL
- **redis**: Caché Redis (opcional)
- **nginx**: Proxy reverso con SSL

### 3. docker-compose.dev.yml
**Ubicación**: `./docker-compose.dev.yml`
**Propósito**: Configuración para desarrollo

**Diferencias con producción**:
- Hot reload habilitado
- Volúmenes montados para desarrollo
- Configuraciones de debug
- pgAdmin incluido

### 4. nginx.conf
**Ubicación**: `./nginx.conf`
**Propósito**: Configuración del proxy reverso

**Características**:
- SSL/TLS configurado
- Rate limiting
- Headers de seguridad
- Compresión gzip
- Logs estructurados

### 5. .dockerignore
**Ubicación**: `./.dockerignore`
**Propósito**: Excluir archivos innecesarios del contexto Docker

## 🚀 Configuración Inicial

### Paso 1: Configurar el Entorno
```bash
# Ejecutar el script de configuración
./scripts/docker-setup.sh setup
```

Este comando:
- Verifica la instalación de Docker
- Genera certificados SSL auto-firmados
- Crea archivos de inicialización de BD
- Construye la imagen Docker

### Paso 2: Variables de Entorno
Crear archivo `.env` con las siguientes variables:

```env
# Configuración de Base de Datos
DATABASE_URL=postgresql://inspector_user:inspector_pass@db:5432/inspector_db

# Configuración de Seguridad
SECRET_KEY=tu_clave_secreta_aqui_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de Logs
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Configuración de CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Configuración de Caché
ENABLE_CACHE=true
CACHE_TTL=300

# Configuración de API
API_TITLE=Inspector API
API_DESCRIPTION=API para gestión de inventario de dispositivos
API_VERSION=1.0.0
```

## 🎯 Modos de Ejecución

### Modo Desarrollo
```bash
# Iniciar servicios de desarrollo
./scripts/docker-setup.sh dev
```

**Características**:
- Hot reload habilitado
- Logs detallados
- pgAdmin disponible en puerto 8080
- Base de datos en puerto 5433
- Redis en puerto 6380

**URLs de Acceso**:
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs
- pgAdmin: http://localhost:8080

### Modo Producción
```bash
# Iniciar servicios de producción
./scripts/docker-setup.sh prod
```

**Características**:
- SSL/TLS habilitado
- Nginx como proxy reverso
- Optimizaciones de rendimiento
- Logs estructurados

**URLs de Acceso**:
- API: https://localhost
- Documentación: https://localhost/docs

## 🛠️ Gestión de Servicios

### Comandos Básicos

```bash
# Detener servicios
./scripts/docker-setup.sh stop

# Ver logs de producción
./scripts/docker-setup.sh logs

# Ver logs de desarrollo
./scripts/docker-setup.sh logs-dev

# Ejecutar migraciones
./scripts/docker-setup.sh migrate

# Ejecutar tests
./scripts/docker-setup.sh test

# Limpiar recursos
./scripts/docker-setup.sh cleanup
```

### Comandos Docker Directos

```bash
# Ver contenedores activos
docker ps

# Ver logs de un contenedor específico
docker logs inspector_api_1

# Ejecutar comando en contenedor
docker exec -it inspector_api_1 bash

# Reconstruir imagen
docker-compose build --no-cache

# Escalar servicios
docker-compose up -d --scale api=3
```

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Puerto ya en uso
```bash
# Verificar puertos en uso
netstat -tulpn | grep :8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar 8000 por 8001
```

#### 2. Error de permisos
```bash
# Dar permisos al script
chmod +x scripts/docker-setup.sh

# En Windows (PowerShell)
icacls scripts/docker-setup.sh /grant Everyone:F
```

#### 3. Error de certificados SSL
```bash
# Regenerar certificados
rm -rf ssl/
./scripts/docker-setup.sh setup
```

#### 4. Base de datos no conecta
```bash
# Verificar estado de contenedores
docker-compose ps

# Ver logs de base de datos
docker-compose logs db

# Reiniciar servicios
docker-compose restart
```

#### 5. Error de memoria
```bash
# Aumentar memoria disponible para Docker
# En Docker Desktop: Settings > Resources > Memory
```

### Logs y Debugging

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de servicio específico
docker-compose logs -f api

# Ver logs con timestamps
docker-compose logs -f --timestamps

# Ver logs de últimos N minutos
docker-compose logs --since 10m
```

## ⚡ Optimizaciones

### Optimizaciones de Imagen

1. **Multi-stage builds** (futura implementación)
2. **Caché de dependencias**
3. **Imagen base optimizada**

### Optimizaciones de Rendimiento

1. **Configuración de Nginx**:
   - Compresión gzip
   - Caché de archivos estáticos
   - Rate limiting

2. **Configuración de Base de Datos**:
   - Pool de conexiones
   - Índices optimizados
   - Configuración de memoria

3. **Configuración de Aplicación**:
   - Workers múltiples
   - Caché Redis
   - Logs estructurados

### Monitoreo

```bash
# Ver uso de recursos
docker stats

# Ver espacio en disco
docker system df

# Limpiar recursos no utilizados
docker system prune -a
```

## 📊 Métricas y Monitoreo

### Health Checks
- Endpoint: `/health`
- Intervalo: 30 segundos
- Timeout: 10 segundos

### Métricas Disponibles
- Uso de CPU y memoria
- Latencia de respuesta
- Tasa de errores
- Conexiones activas

## 🔒 Seguridad

### Configuraciones de Seguridad

1. **Headers de Seguridad**:
   - X-Frame-Options
   - X-Content-Type-Options
   - X-XSS-Protection
   - Content-Security-Policy

2. **SSL/TLS**:
   - Certificados auto-firmados (desarrollo)
   - Certificados Let's Encrypt (producción)

3. **Rate Limiting**:
   - API: 10 requests/segundo
   - Login: 5 requests/minuto

4. **CORS**:
   - Orígenes permitidos configurados
   - Credenciales habilitadas

## 📝 Notas de Desarrollo

### Estructura de Directorios
```
inspector_api/
├── app/                    # Código de la aplicación
├── alembic/               # Migraciones de BD
├── logs/                  # Logs de la aplicación
├── scripts/               # Scripts de utilidad
├── ssl/                   # Certificados SSL
├── tests/                 # Tests unitarios
├── Dockerfile             # Configuración Docker
├── docker-compose.yml     # Servicios producción
├── docker-compose.dev.yml # Servicios desarrollo
├── nginx.conf            # Configuración Nginx
└── .dockerignore         # Archivos a excluir
```

### Variables de Entorno por Entorno

#### Desarrollo
- `LOG_LEVEL=DEBUG`
- `ENABLE_CACHE=false`
- `ENABLE_COMPRESSION=false`
- `ENABLE_METRICS=false`

#### Producción
- `LOG_LEVEL=INFO`
- `ENABLE_CACHE=true`
- `ENABLE_COMPRESSION=true`
- `ENABLE_METRICS=true`

## 🚀 Próximos Pasos

1. **CI/CD Pipeline**: Configurar GitHub Actions
2. **Monitoreo**: Integrar Prometheus/Grafana
3. **Logs**: Configurar ELK Stack
4. **Backup**: Automatizar backups de BD
5. **Scaling**: Configurar load balancer

---

**Nota**: Esta configuración está optimizada para desarrollo y producción. Ajusta las configuraciones según tus necesidades específicas. 