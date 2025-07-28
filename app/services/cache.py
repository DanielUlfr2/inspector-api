import time
import logging
from typing import Any, Optional, Dict, Tuple

logger = logging.getLogger(__name__)

class SimpleCache:
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Almacena un valor en el cache con TTL en segundos
        :param key: Clave del cache
        :param value: Valor a almacenar
        :param ttl: Tiempo de vida en segundos (default: 5 minutos)
        """
        expiry_time = time.time() + ttl
        self._cache[key] = (value, expiry_time)
        logger.info(f"Cache set: {key} (TTL: {ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del cache si no ha expirado
        :param key: Clave del cache
        :return: Valor cacheado o None si no existe o expiró
        """
        if key not in self._cache:
            return None
        
        value, expiry_time = self._cache[key]
        if time.time() > expiry_time:
            # El valor expiró, eliminarlo
            del self._cache[key]
            logger.info(f"Cache expired: {key}")
            return None
        
        logger.info(f"Cache hit: {key}")
        return value
    
    def delete(self, key: str) -> bool:
        """
        Elimina una clave del cache
        :param key: Clave a eliminar
        :return: True si existía y se eliminó, False si no existía
        """
        if key in self._cache:
            del self._cache[key]
            logger.info(f"Cache deleted: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """
        Limpia todo el cache
        """
        self._cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """
        Limpia entradas expiradas del cache
        :return: Número de entradas eliminadas
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry_time) in self._cache.items()
            if current_time > expiry_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)

# Instancia global del cache
cache = SimpleCache() 