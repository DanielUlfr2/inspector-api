import time
import logging
import hashlib
import json
from typing import Any, Optional, Dict, Tuple, List, Set, Callable
from functools import wraps
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AdvancedCache:
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float, Set[str]]] = {}  # key -> (value, expiry, tags)
        self._tags: Dict[str, Set[str]] = {}  # tag -> set of keys
        self._patterns: Dict[str, Set[str]] = {}  # pattern -> set of keys
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'invalidations': 0
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera una clave única basada en argumentos"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _extract_tags(self, *args, **kwargs) -> Set[str]:
        """Extrae tags automáticamente de los argumentos"""
        tags = set()
        
        # Tags basados en tipos de operación
        if 'registro' in str(args) + str(kwargs):
            tags.add('registros')
        if 'historial' in str(args) + str(kwargs):
            tags.add('historial')
        if 'total' in str(args) + str(kwargs):
            tags.add('estadisticas')
        
        # Tags basados en filtros
        for key, value in kwargs.items():
            if value is not None:
                tags.add(f"filter_{key}")
        
        return tags
    
    def set(self, key: str, value: Any, ttl: int = 300, tags: Optional[Set[str]] = None, 
            pattern: Optional[str] = None) -> None:
        """
        Almacena un valor en el cache con TTL y tags
        :param key: Clave del cache
        :param value: Valor a almacenar
        :param ttl: Tiempo de vida en segundos
        :param tags: Tags para invalidación selectiva
        :param pattern: Patrón para invalidación por patrones
        """
        expiry_time = time.time() + ttl
        tags = tags or set()
        
        # Agregar tags automáticos si no se proporcionan
        if not tags:
            tags = self._extract_tags(key)
        
        self._cache[key] = (value, expiry_time, tags)
        
        # Registrar tags
        for tag in tags:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(key)
        
        # Registrar patrón
        if pattern:
            if pattern not in self._patterns:
                self._patterns[pattern] = set()
            self._patterns[pattern].add(key)
        
        self._stats['sets'] += 1
        logger.info(f"Cache set: {key} (TTL: {ttl}s, Tags: {tags})")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del cache si no ha expirado
        :param key: Clave del cache
        :return: Valor cacheado o None si no existe o expiró
        """
        if key not in self._cache:
            self._stats['misses'] += 1
            return None
        
        value, expiry_time, tags = self._cache[key]
        if time.time() > expiry_time:
            # El valor expiró, eliminarlo
            self.delete(key)
            self._stats['misses'] += 1
            return None
        
        self._stats['hits'] += 1
        logger.info(f"Cache hit: {key}")
        return value
    
    def delete(self, key: str) -> bool:
        """
        Elimina una clave del cache
        :param key: Clave a eliminar
        :return: True si existía y se eliminó, False si no existía
        """
        if key in self._cache:
            _, _, tags = self._cache[key]
            
            # Limpiar tags
            for tag in tags:
                if tag in self._tags and key in self._tags[tag]:
                    self._tags[tag].remove(key)
                    if not self._tags[tag]:
                        del self._tags[tag]
            
            # Limpiar patrones
            for pattern, keys in self._patterns.items():
                if key in keys:
                    keys.remove(key)
                    if not keys:
                        del self._patterns[pattern]
            
            del self._cache[key]
            self._stats['deletes'] += 1
            logger.info(f"Cache deleted: {key}")
            return True
        return False
    
    def invalidate_by_tag(self, tag: str) -> int:
        """
        Invalida todas las claves con un tag específico
        :param tag: Tag a invalidar
        :return: Número de claves invalidadas
        """
        if tag not in self._tags:
            return 0
        
        keys_to_delete = list(self._tags[tag])
        for key in keys_to_delete:
            self.delete(key)
        
        self._stats['invalidations'] += len(keys_to_delete)
        logger.info(f"Invalidated {len(keys_to_delete)} keys by tag: {tag}")
        return len(keys_to_delete)
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalida todas las claves que coinciden con un patrón
        :param pattern: Patrón a invalidar
        :return: Número de claves invalidadas
        """
        keys_to_delete = []
        for key in list(self._cache.keys()):
            if pattern in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.delete(key)
        
        self._stats['invalidations'] += len(keys_to_delete)
        logger.info(f"Invalidated {len(keys_to_delete)} keys by pattern: {pattern}")
        return len(keys_to_delete)
    
    def invalidate_registros(self) -> int:
        """
        Invalida todo el cache relacionado con registros
        :return: Número de claves invalidadas
        """
        return self.invalidate_by_tag('registros')
    
    def invalidate_estadisticas(self) -> int:
        """
        Invalida todo el cache relacionado con estadísticas
        :return: Número de claves invalidadas
        """
        return self.invalidate_by_tag('estadisticas')
    
    def clear(self) -> None:
        """
        Limpia todo el cache
        """
        self._cache.clear()
        self._tags.clear()
        self._patterns.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """
        Limpia entradas expiradas del cache
        :return: Número de entradas eliminadas
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry_time, _) in self._cache.items()
            if current_time > expiry_time
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache
        :return: Diccionario con estadísticas
        """
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.2f}%",
            'cache_size': len(self._cache),
            'tags_count': len(self._tags),
            'patterns_count': len(self._patterns)
        }
    
    def cache_decorator(self, ttl: int = 300, key_prefix: str = "func", 
                       tags: Optional[Set[str]] = None):
        """
        Decorador para cachear funciones
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generar clave única
                cache_key = self._generate_key(key_prefix, *args, **kwargs)
                
                # Intentar obtener del cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Ejecutar función
                result = await func(*args, **kwargs)
                
                # Guardar en cache
                auto_tags = tags or self._extract_tags(*args, **kwargs)
                self.set(cache_key, result, ttl, auto_tags)
                
                return result
            
            return wrapper
        return decorator

# Instancia global del cache avanzado
cache = AdvancedCache()

# Configuración de TTL por tipo de operación
TTL_CONFIG = {
    'registros_lista': 60,      # 1 minuto para listas de registros
    'registro_individual': 300,  # 5 minutos para registros individuales
    'estadisticas': 180,        # 3 minutos para estadísticas
    'historial': 120,           # 2 minutos para historial
    'valores_unicos': 600,      # 10 minutos para valores únicos
    'exportacion': 30,          # 30 segundos para exportaciones
}

# Función helper para generar claves de cache
def generate_cache_key(operation: str, **params) -> str:
    """Genera una clave de cache basada en la operación y parámetros"""
    param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if v is not None)
    return f"{operation}:{hashlib.md5(param_str.encode()).hexdigest()}"

# Función helper para cachear consultas de registros
async def cached_registro_query(operation: str, ttl: int = None, **params):
    """
    Helper para cachear consultas de registros
    """
    cache_key = generate_cache_key(operation, **params)
    ttl = ttl or TTL_CONFIG.get(operation, 300)
    
    # Intentar obtener del cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    return None  # Devolver None para indicar que no está en cache

# Función helper para guardar resultados en cache
def save_to_cache(operation: str, result: Any, ttl: int = None, **params):
    """
    Helper para guardar resultados en cache
    """
    cache_key = generate_cache_key(operation, **params)
    ttl = ttl or TTL_CONFIG.get(operation, 300)
    
    # Determinar tags basados en la operación
    tags = {operation}
    if 'registro' in operation:
        tags.add('registros')
    if 'estadistica' in operation or 'total' in operation:
        tags.add('estadisticas')
    if 'historial' in operation:
        tags.add('historial')
    
    cache.set(cache_key, result, ttl, tags)
    return result 