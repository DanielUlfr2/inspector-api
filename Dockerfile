# Dockerfile para Inspector API
# Autor: Daniel Bermúdez
# Versión: 1.0.0
# Descripción: Configuración de Docker para la aplicación FastAPI

# Usar Python 3.11 como imagen base
FROM python:3.14-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ ./app/
COPY alembic.ini .
COPY alembic/ ./alembic/

# Crear directorio para logs
RUN mkdir -p /app/logs

# Exponer el puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 