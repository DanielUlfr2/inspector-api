"""
⚙️ Configuración Centralizada - Inspector API

Este módulo contiene toda la configuración del sistema, cargando valores
desde variables de entorno con valores por defecto seguros.

Características:
- Carga automática de variables de entorno desde .env
- Valores por defecto seguros para desarrollo
- Configuración modular por categorías
- Soporte para diferentes entornos (dev/prod/test)

Autor: Daniel Bermúdez
Versión: 1.0.0
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ===== CONFIGURACIÓN DE BASE DE DATOS =====
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./inspector.db")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test_inspector.db")

# ===== CONFIGURACIÓN DE AUTENTICACIÓN JWT =====
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ===== CONFIGURACIÓN DE CORS =====
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8000,http://127.0.0.1:8000")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",")]

# ===== CONFIGURACIÓN DE LOGGING =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "app.log")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s %(levelname)s %(name)s: %(message)s")

# ===== CONFIGURACIÓN DE CACHE =====
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

# ===== CONFIGURACIÓN DE SERVIDOR =====
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
RELOAD = os.getenv("RELOAD", "false").lower() == "true"

# ===== CONFIGURACIÓN DE ARCHIVOS =====
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB por defecto
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "app/static/uploads")
ALLOWED_EXTENSIONS_STR = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,pdf,xlsx,xls,csv")
ALLOWED_EXTENSIONS = [ext.strip() for ext in ALLOWED_EXTENSIONS_STR.split(",")]

# ===== CONFIGURACIÓN DE SEGURIDAD =====
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "1800"))

# ===== CONFIGURACIÓN DE EMAIL (OPCIONAL) =====
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

# ===== CONFIGURACIÓN DE REDIS (OPCIONAL) =====
REDIS_URL = os.getenv("REDIS_URL")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"

# ===== CONFIGURACIÓN DE MONITORING =====
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
ENABLE_HEALTH_CHECK = os.getenv("ENABLE_HEALTH_CHECK", "true").lower() == "true"
ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "true").lower() == "true"

# ===== CONFIGURACIÓN DE DESARROLLO =====
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
TESTING = os.getenv("TESTING", "false").lower() == "true"

# ===== CONFIGURACIÓN DE FRONTEND =====
VITE_API_URL = os.getenv("VITE_API_URL", "http://localhost:8000")
VITE_APP_TITLE = os.getenv("VITE_APP_TITLE", "Inspector")
VITE_APP_VERSION = os.getenv("VITE_APP_VERSION", "1.0.0")
