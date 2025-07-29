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

- ✅ Análisis de código (Flake8, Black, Isort, Mypy)
- ✅ Tests automatizados con cobertura
- ✅ Build de Docker optimizado
- ✅ Análisis de seguridad (Trivy, Bandit)
- ✅ Despliegue automático
- ✅ Releases automáticos

## 🔧 Instalación

```bash
# Clonar repositorio
git clone https://github.com/DanielUlfr2/inventario-web-inspector.git
cd inventario-web-inspector

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

## 📊 Métricas

![CI/CD](https://github.com/DanielUlfr2/inventario-web-inspector/workflows/CI/CD/badge.svg)
![Security](https://github.com/DanielUlfr2/inventario-web-inspector/workflows/Security/badge.svg)

## 📝 Licencia

MIT License