import logging
import re

# Configuración básica del Logger para toda la app
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

class SecurityValidator:
    """
    Clase para validar entradas y prevenir inyecciones obvias.
    Aunque asyncpg usa parámetros, esto añade una capa de "sanidad".
    """
    
    # Patrones peligrosos (SQL Injection básicos)
    DANGEROUS_PATTERNS = [
        r";\s*DROP\s+TABLE", 
        r";\s*DELETE\s+FROM", 
        r";\s*TRUNCATE", 
        r"--", 
        r"/\*"
    ]

    @staticmethod
    def is_safe_string(value: str) -> bool:
        if not isinstance(value, str):
            return True
            
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logging.warning(f"🚨 ALERTA DE SEGURIDAD: Texto sospechoso detectado y bloqueado: {value}")
                return False
        return True

    @staticmethod
    def sanitize_input(data: dict) -> dict:
        """Limpia un diccionario completo de datos sospechosos"""
        clean_data = {}
        for key, val in data.items():
            if isinstance(val, str) and not SecurityValidator.is_safe_string(val):
                clean_data[key] = "SANITIZED_UNSAFE_CONTENT"
            else:
                clean_data[key] = val
        return clean_data