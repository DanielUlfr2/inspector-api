import asyncpg
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class PostgresConnector:
    _pool = None
    
    @classmethod
    async def get_connection(cls):
        """
        Obtiene conexión, recreando el pool si el Loop ha cambiado (Celery friendly).
        """
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            # Si no hay loop corriendo, no podemos hacer nada
            return None

        # 1. Si el pool existe pero pertenece a otro loop (o uno cerrado), mátalo.
        if cls._pool:
            if cls._pool._loop.is_closed() or cls._pool._loop is not current_loop:
                logger.warning("⚠️ Pool desincronizado del Loop actual. Reiniciando...")
                cls._pool = None # Lo descartamos brutalmente

        # 2. Crear Pool si no existe
        if cls._pool is None:
            await cls.init_pool()

        return await cls._pool.acquire()

    @classmethod
    async def init_pool(cls):
        """
        Inicializa el pool de conexiones.
        """
        if cls._pool is None:
            logger.info("🔌 Creando nuevo Pool de conexiones...")
            cls._pool = await asyncpg.create_pool(
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                database=os.getenv("POSTGRES_DB"),
                host="postgres_inspector", # Asegúrate que este sea el nombre en docker-compose
                port=os.getenv("POSTGRES_PORT", "5432"),
                min_size=1,
                max_size=5 # Manténlo bajo para workers
            )
            logger.info("✅ Pool de conexiones PostgreSQL creado exitosamente.")

    @classmethod
    async def release_connection(cls, connection):
        """
        Libera la conexión de forma segura. Si el loop está cerrado, no hace nada.
        """
        if not connection:
            return

        try:
            # Si el pool ya no existe o el loop se cerró, no intentamos liberar
            # porque eso lanza el RuntimeError. Simplemente dejamos morir la conexión.
            if cls._pool and not cls._pool._loop.is_closed():
                await cls._pool.release(connection)
        except Exception as e:
            # Ignoramos errores al liberar, lo importante es que la query se haya ejecutado
            logger.warning(f"⚠️ Warning al liberar conexión: {e}")

    @classmethod
    async def close_pool(cls):
        if cls._pool and not cls._pool._loop.is_closed():
            await cls._pool.close()
            logger.info("🔌 Pool cerrado.")