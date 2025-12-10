import asyncpg
import logging
from src.core.config import settings

# Configuración de logs para ver qué pasa en la consola
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("postgres_connector")

class PostgresConnector:
    _pool = None

    @classmethod
    async def init_pool(cls):
        """
        Inicializa el pool de conexiones al arrancar la aplicación.
        Lee las credenciales desde src.core.config.settings
        """
        if cls._pool is None:
            try:
                logger.info(f"🔌 Conectando a Postgres en {settings.POSTGRES_SERVER}...")
                cls._pool = await asyncpg.create_pool(
                    user=settings.POSTGRES_USER,
                    password=settings.POSTGRES_PASSWORD,
                    database=settings.POSTGRES_DB,
                    host=settings.POSTGRES_SERVER,
                    port=settings.POSTGRES_PORT,
                    min_size=2,   # Mínimo de conexiones abiertas
                    max_size=20,  # Máximo de conexiones (ajustar según carga)
                )
                logger.info("✅ Pool de conexiones PostgreSQL creado exitosamente.")
            except Exception as e:
                logger.error(f"❌ Error CRÍTICO al conectar a la Base de Datos: {e}")
                # Re-lanzamos el error para que la app falle si no hay DB
                raise e

    @classmethod
    async def get_connection(cls):
        """Solicita una conexión del pool para usarla"""
        if cls._pool is None:
            await cls.init_pool()
        return await cls._pool.acquire()

    @classmethod
    async def release_connection(cls, conn):
        """Devuelve la conexión al pool (IMPORTANTE LLAMAR SIEMPRE)"""
        if cls._pool and conn:
            await cls._pool.release(conn)

    @classmethod
    async def close_pool(cls):
        """Cierra todas las conexiones al apagar la app"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            logger.info("🔒 Pool de PostgreSQL cerrado.")