# Inspector API

Sistema de gestión de inspecciones con API REST y frontend React.

## 🚀 Características

- **Backend**: FastAPI con SQLAlchemy
- **Frontend**: React + TypeScript
- **Base de datos**: PostgreSQL/SQLite
- **Autenticación**: JWT
- **CI/CD**: GitHub Actions
- **Containerización**: Docker

## 📋 Estado del CI/CD

- ✅ Análisis de código (Flake8, Black, Isort)
- ✅ Tests automatizados
- ✅ Build de Docker optimizado
- ✅ Análisis de seguridad
- ✅ Despliegue automático
- ✅ Releases automáticos

## 📊 Métricas de CI/CD

![CI/CD Pipeline](https://github.com/DanielUlfr2/inspector-api/workflows/CI/CD%20Pipeline/badge.svg)
![Security Analysis](https://github.com/DanielUlfr2/inspector-api/workflows/Security%20Analysis/badge.svg)
![Dependabot](https://img.shields.io/badge/dependabot-enabled-brightgreen)

## 🔧 Instalación

```bash
# Clonar repositorio
git clone https://github.com/DanielUlfr2/inspector-api.git
cd inspector-api

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

## 🐳 Docker

```bash
# Construir imagen
docker build -t inspector-api .

# Ejecutar contenedor
docker run -p 8000:8000 inspector-api
```

## 📚 Documentación

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔒 Seguridad

- ✅ Análisis de vulnerabilidades automático
- ✅ Detección de secretos en código
- ✅ Análisis de dependencias
- ✅ Escaneo de Docker

## 📝 Licencia

MIT License