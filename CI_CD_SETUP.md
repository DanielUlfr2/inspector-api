# Configuración de CI/CD con GitHub Actions

## Autor: Daniel Bermúdez
## Versión: 1.0.0
## Descripción: Guía completa para configurar y usar el pipeline de CI/CD

## 📋 Tabla de Contenidos

1. [Resumen de Implementación](#resumen-de-implementación)
2. [Workflows Configurados](#workflows-configurados)
3. [Configuración de Secrets](#configuración-de-secrets)
4. [Uso del Pipeline](#uso-del-pipeline)
5. [Monitoreo y Notificaciones](#monitoreo-y-notificaciones)
6. [Troubleshooting](#troubleshooting)
7. [Próximos Pasos](#próximos-pasos)

## 🎯 Resumen de Implementación

Se ha implementado un **pipeline completo de CI/CD** con GitHub Actions que incluye:

### ✅ Funcionalidades Implementadas
- **Análisis de código**: flake8, black, isort, mypy, bandit
- **Tests automatizados**: unitarios, integración, cobertura
- **Build de Docker**: imágenes optimizadas con cache
- **Análisis de seguridad**: Trivy, safety, bandit, secret scanning
- **Despliegue automático**: staging y producción
- **Releases automáticos**: con tags y changelog
- **Dependabot**: actualizaciones automáticas de dependencias
- **Plantillas**: issues, pull requests, releases

## 🔄 Workflows Configurados

### 1. **ci-cd.yml** - Pipeline Principal
**Ubicación**: `.github/workflows/ci-cd.yml`

**Jobs incluidos**:
- **code-analysis**: Análisis de estilo y calidad de código
- **test**: Tests unitarios e integración con PostgreSQL
- **docker-build**: Build y test de imagen Docker
- **security-scan**: Análisis de seguridad de imagen
- **deploy-staging**: Despliegue automático a staging
- **deploy-production**: Despliegue automático a producción
- **notify**: Notificaciones de resultados

**Triggers**:
- Push a `main` y `develop`
- Pull requests a `main` y `develop`
- Manual dispatch con selección de entorno

### 2. **security.yml** - Análisis de Seguridad
**Ubicación**: `.github/workflows/security.yml`

**Jobs incluidos**:
- **dependency-check**: Análisis de vulnerabilidades en dependencias
- **secret-scanning**: Detección de secretos en código
- **docker-security**: Análisis de seguridad de Docker
- **infrastructure-security**: Validación de configuración
- **security-report**: Generación de reportes consolidados

**Triggers**:
- Diario a las 2:00 AM UTC
- Push y pull requests
- Manual dispatch

### 3. **release.yml** - Releases Automáticos
**Ubicación**: `.github/workflows/release.yml`

**Jobs incluidos**:
- **create-release**: Crear release en GitHub
- **docker-release**: Build de imagen para release
- **deploy-release**: Despliegue automático de release

**Triggers**:
- Push de tags `v*`
- Manual dispatch con versión

### 4. **dependabot.yml** - Actualizaciones Automáticas
**Ubicación**: `.github/dependabot.yml`

**Configuraciones**:
- **Python**: Semanal (lunes 9:00 AM)
- **Docker**: Semanal (martes 9:00 AM)
- **GitHub Actions**: Semanal (miércoles 9:00 AM)
- **npm**: Semanal (jueves 9:00 AM) - futuro

## 🔐 Configuración de Secrets

### Secrets Requeridos

```bash
# Base de datos
STAGING_DATABASE_URL=postgresql://user:pass@host:port/db
PRODUCTION_DATABASE_URL=postgresql://user:pass@host:port/db

# Seguridad
STAGING_SECRET_KEY=tu_clave_secreta_staging
PRODUCTION_SECRET_KEY=tu_clave_secreta_produccion

# Notificaciones (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz

# Infraestructura (específico de tu setup)
KUBECONFIG_BASE64=base64_encoded_kubeconfig
DOCKER_REGISTRY_TOKEN=tu_token_del_registro
```

### Cómo Configurar Secrets

1. **Ir a tu repositorio en GitHub**
2. **Settings → Secrets and variables → Actions**
3. **New repository secret**
4. **Agregar cada secret con su valor**

### Secrets por Entorno

#### Staging
- `STAGING_DATABASE_URL`
- `STAGING_SECRET_KEY`

#### Production
- `PRODUCTION_DATABASE_URL`
- `PRODUCTION_SECRET_KEY`

## 🚀 Uso del Pipeline

### Flujo Automático

```bash
# 1. Hacer cambios en develop
git checkout develop
git add .
git commit -m "feat: nueva característica"
git push origin develop

# 2. Crear pull request a main
# 3. El pipeline se ejecuta automáticamente
# 4. Si pasa, se despliega a staging
# 5. Merge a main despliega a producción
```

### Despliegue Manual

```bash
# Desde GitHub Actions UI
# 1. Ir a Actions → ci-cd.yml
# 2. Run workflow
# 3. Seleccionar entorno (staging/production)
# 4. Ejecutar
```

### Crear Release

```bash
# Opción 1: Tag automático
git tag v1.0.0
git push origin v1.0.0

# Opción 2: Manual desde GitHub
# Actions → release.yml → Run workflow
```

## 📊 Monitoreo y Notificaciones

### Métricas Disponibles

1. **Cobertura de Tests**: Subida automática a Codecov
2. **Análisis de Seguridad**: Reportes en GitHub Security
3. **Build Status**: Badges en README
4. **Deployment Status**: Notificaciones en Slack

### Badges para README

```markdown
![CI/CD](https://github.com/{username}/{repo}/workflows/CI%2FCD%20Pipeline/badge.svg)
![Security](https://github.com/{username}/{repo}/workflows/Security%20Analysis/badge.svg)
![Release](https://github.com/{username}/{repo}/workflows/Release/badge.svg)
```

### Notificaciones Configuradas

- **Slack**: Canales #deployments, #security, #releases
- **GitHub**: Issues y pull requests automáticos
- **Email**: Notificaciones de GitHub (configurar en settings)

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Tests Fallando
```bash
# Verificar logs
# Actions → ci-cd.yml → test job → logs

# Problemas comunes:
# - Base de datos no disponible
# - Variables de entorno faltantes
# - Dependencias desactualizadas
```

#### 2. Build de Docker Fallando
```bash
# Verificar Dockerfile
# Verificar .dockerignore
# Verificar permisos de registry
```

#### 3. Despliegue Fallando
```bash
# Verificar secrets configurados
# Verificar conectividad de red
# Verificar permisos de infraestructura
```

#### 4. Análisis de Seguridad Fallando
```bash
# Verificar dependencias vulnerables
# Verificar secretos en código
# Verificar configuración de Docker
```

### Comandos de Debug

```bash
# Ejecutar tests localmente
pytest tests/ -v

# Verificar Docker build
docker build -t inspector-api .

# Verificar análisis de seguridad
safety check
bandit -r app/
```

## 📈 Métricas de Implementación

| Aspecto | Estado | Detalles |
|---------|--------|----------|
| Análisis de Código | ✅ Completado | flake8, black, isort, mypy |
| Tests Automatizados | ✅ Completado | pytest, cobertura, PostgreSQL |
| Build Docker | ✅ Completado | Multi-stage, cache, registry |
| Análisis Seguridad | ✅ Completado | Trivy, safety, bandit |
| Despliegue Automático | ✅ Completado | Staging y producción |
| Releases | ✅ Completado | Tags automáticos |
| Dependabot | ✅ Completado | Actualizaciones semanales |
| Plantillas | ✅ Completado | Issues, PRs, releases |

## 🎯 Cumplimiento de Estándares

### ✅ Arquitectura Guidelines
- **CI/CD Pipeline**: Implementado completamente
- **Tests automatizados**: Unitarios e integración
- **Análisis de seguridad**: Múltiples herramientas
- **Despliegue automático**: Staging y producción
- **Documentación**: Guía completa creada

### ✅ Mejores Prácticas
- **Separación de entornos**: Staging y producción
- **Análisis de código**: Múltiples herramientas
- **Seguridad**: Escaneo automático
- **Notificaciones**: Slack y GitHub
- **Rollback**: Preparado para implementación

## 🚀 Próximos Pasos

### Inmediatos
1. **Configurar secrets** en GitHub
2. **Probar pipeline** con un commit
3. **Configurar notificaciones** (opcional)
4. **Personalizar despliegue** según tu infraestructura

### Futuros
1. **Kubernetes**: Configurar despliegue a K8s
2. **Monitoring**: Integrar Prometheus/Grafana
3. **Logs**: Configurar ELK Stack
4. **Backup**: Automatizar backups
5. **Scaling**: Configurar auto-scaling

## 📝 Comandos Útiles

### Verificar Estado
```bash
# Ver workflows activos
gh run list

# Ver logs de un workflow
gh run view <run-id>

# Ver logs de un job específico
gh run view <run-id> --log
```

### Debug Local
```bash
# Ejecutar análisis de código
flake8 app/ tests/
black --check app/ tests/
isort --check-only app/ tests/
mypy app/

# Ejecutar tests
pytest tests/ -v --cov=app

# Build Docker
docker build -t inspector-api .
```

### Gestión de Releases
```bash
# Crear tag
git tag v1.0.0
git push origin v1.0.0

# Ver releases
gh release list

# Crear release manual
gh release create v1.0.0 --title "Release 1.0.0" --notes "Nuevas características"
```

---

**Estado**: ✅ **COMPLETADO** - El pipeline de CI/CD está configurado y listo para uso. 