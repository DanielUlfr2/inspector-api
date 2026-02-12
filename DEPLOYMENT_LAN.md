# Guía de Despliegue - Inspector en Red LAN

## 📋 Resumen de Cambios

Este documento describe los cambios realizados para permitir el acceso al servicio Inspector desde la red LAN (192.168.10.20).

## 🔧 Cambios Realizados

### 1. Resolución de Conflictos de Puertos

**Análisis de puertos ocupados por servicios pipe:**
```
pipe-frontend:   5173
pipe-backend:    8000 (interno)
pipe-postgres:   5440
pipe-redis:      6379  ⚠️ CONFLICTO
pipe-qdrant:     6444
```

**Configuración de puertos Inspector:**
```
✅ PostgreSQL:  5432:5432   (OK - pipe usa 5440)
✅ Redis:       6380:6379   (OK - evita conflicto con pipe-redis:6379)
✅ Frontend:    3001:80     (OK - pipe usa 5173)
✅ Keycloak:    8080:8080   (OK - pipe backend usa 8000 interno)
✅ KrakenD:     8081:8080   (OK)
✅ Backend:     5000:5000   (OK)
✅ WireGuard:   51820, 51821 (OK)
```

> **Nota**: El único conflicto era Redis. El docker-compose.yml ya estaba correctamente configurado con `6380:6379`.

### 2. Configuración de Red LAN

#### Archivos Modificados:

**`gateway/krakend.json`**
- ✅ Agregado `http://192.168.10.20:3001` a `allow_origins`
- ✅ Agregado `http://192.168.10.20:8081` a `allow_origins`

**`backend/.env`**
- ✅ Cambiado `COOKIE_DOMAIN=localhost` → `COOKIE_DOMAIN=192.168.10.20`

**`frontend/.env`**
- ✅ Ya estaba configurado con las URLs de 192.168.10.20

## 🚀 Proceso de Despliegue

### Paso 1: Detener servicios actuales (si están corriendo)

```bash
cd /home/admin/inspector/InspectorGestion5.0
docker-compose down
```

### Paso 2: Levantar servicios con nueva configuración

```bash
docker-compose up -d
```

### Paso 3: Verificar que todos los servicios están corriendo

```bash
docker-compose ps
```

Deberías ver todos los servicios con estado `Up`:
- open_balena_apis
- frontend_inspector
- redis_inspector
- postgres_inspector
- keycloak_inspector
- krakend_inspector
- wg-easy_inspector
- wg-fastapi_inspector
- celery_worker_inspector
- celery_beat_inspector

### Paso 4: Actualizar configuración de Keycloak

**Opción A: Usando el script automático (Recomendado)**

```bash
chmod +x update_keycloak_config.sh
./update_keycloak_config.sh
```

**Opción B: Manualmente desde la interfaz web**

1. Acceder a Keycloak: `http://192.168.10.20:8080`
2. Login con credenciales de admin (ver `.env`)
3. Ir a: `Realm: inspector_realm` → `Clients` → `inspector_client`
4. En la pestaña **Settings**, actualizar:

   **Valid Redirect URIs:**
   ```
   http://192.168.10.20:3001/*
   http://localhost:3001/*
   http://192.168.10.20:8081/*
   ```

   **Web Origins:**
   ```
   http://192.168.10.20:3001
   http://localhost:3001
   http://192.168.10.20:8081
   +
   ```

5. Click en **Save**

### Paso 5: Verificar acceso

Desde cualquier equipo en la red LAN (192.168.10.x):

1. Abrir navegador
2. Ir a: `http://192.168.10.20:3001`
3. Debería cargar el frontend de Inspector
4. Probar login con credenciales válidas

## 🧪 Pruebas de Verificación

### Test 1: Conectividad de servicios

```bash
# Verificar frontend
curl http://192.168.10.20:3001

# Verificar API Gateway
curl http://192.168.10.20:8081/health

# Verificar Keycloak
curl http://192.168.10.20:8080/realms/inspector_realm
```

### Test 2: Verificar logs

```bash
# Ver logs del gateway
docker logs krakend_inspector --tail 50

# Ver logs del backend
docker logs open_balena_apis --tail 50

# Ver logs de Keycloak
docker logs keycloak_inspector --tail 50
```

### Test 3: Verificar Redis

```bash
# Conectar a Redis desde el host
redis-cli -h 192.168.10.20 -p 6380 -a LgsBqGhsQI1FURGg ping
# Debería responder: PONG
```

## 🔍 Troubleshooting

### Problema: No puedo acceder desde otro equipo en la red

**Solución:**
1. Verificar que el firewall del servidor permite tráfico en los puertos:
   ```bash
   sudo firewall-cmd --list-ports
   # Agregar puertos si es necesario:
   sudo firewall-cmd --permanent --add-port=3001/tcp
   sudo firewall-cmd --permanent --add-port=8080/tcp
   sudo firewall-cmd --permanent --add-port=8081/tcp
   sudo firewall-cmd --reload
   ```

### Problema: Error de CORS en el navegador

**Solución:**
1. Verificar que `krakend.json` tiene las URLs correctas en `allow_origins`
2. Reiniciar el gateway:
   ```bash
   docker restart krakend_inspector
   ```

### Problema: Las cookies no se establecen

**Solución:**
1. Verificar que `COOKIE_DOMAIN` en `backend/.env` es `192.168.10.20`
2. Reiniciar el backend:
   ```bash
   docker restart open_balena_apis
   ```

### Problema: Keycloak no redirige correctamente

**Solución:**
1. Verificar que los Redirect URIs en Keycloak incluyen la IP de la red LAN
2. Ejecutar nuevamente el script `update_keycloak_config.sh`

## 📊 Puertos Expuestos

| Servicio | Puerto Externo | Puerto Interno | Descripción |
|----------|---------------|----------------|-------------|
| Frontend | 3001 | 80 | Interfaz web de Inspector |
| Backend API | 5000 | 5000 | API REST de Inspector |
| Keycloak | 8080, 8443 | 8080, 8443 | Autenticación y autorización |
| KrakenD | 8081 | 8080 | API Gateway |
| PostgreSQL | 5432 | 5432 | Base de datos principal |
| Redis | 6380 | 6379 | Caché y cola de mensajes |
| WireGuard | 51820, 51821 | 51820, 51821 | VPN |

## 🔐 Seguridad

> **Importante**: Esta configuración es para uso en red LAN privada. Para producción en internet:
> - Implementar HTTPS con certificados válidos
> - Configurar firewall restrictivo
> - Usar contraseñas más robustas
> - Implementar rate limiting
> - Considerar usar un reverse proxy con Nginx

## 📝 Notas Adicionales

- Los servicios se comunican internamente a través de la red Docker `InspecNet` (172.16.0.0/27)
- El acceso externo es a través de la IP del host (192.168.10.20)
- Las credenciales están en los archivos `.env` (mantener seguros)
