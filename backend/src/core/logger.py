import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuraciones básicas
APP_ENV = os.getenv("APP_ENV", "development").lower()
LOG_BASE_DIR = "logs"

def setup_logger(name: str = "inspector_app"):
    """
    Configura un logger que escribe en consola y en archivo
    organizado por Año/Mes/Dia.
    """
    
    # 1. Definir Nivel de Log según el entorno
    if APP_ENV == "production":
        log_level = logging.INFO
    elif APP_ENV == "staging":
        log_level = logging.DEBUG
    else:
        log_level = logging.DEBUG # Default development

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Evitar duplicar handlers si ya existen (hot-reload issue)
    if logger.handlers:
        return logger

    # 2. Formato del Log
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 3. Handler de Consola (Stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 4. Handler de Archivo (Solo si queremos persistencia)
    try:
        # Estructura: logs/2025/12/13/
        now = datetime.now()
        dir_path = os.path.join(
            LOG_BASE_DIR, 
            str(now.year), 
            f"{now.month:02d}", 
            f"{now.day:02d}"
        )
        
        # Crear directorios si no existen
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        file_path = os.path.join(dir_path, "system.log")
        
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    except Exception as e:
        print(f"⚠️ No se pudo crear el archivo de log: {e}")

    return logger

# Instancia global para importar fácilmente
logger = setup_logger()