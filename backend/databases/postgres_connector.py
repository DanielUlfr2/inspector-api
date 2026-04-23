import asyncpg
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class PostgresConnector:
    _pool = None
    
    @classmethod
    async def get_connection(cls):
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            return None

        if cls._pool:
            if cls._pool._loop.is_closed() or cls._pool._loop is not current_loop:
                logger.warning("⚠️ Pool desincronizado del Loop actual. Reiniciando...")
                cls._pool = None

        if cls._pool is None:
            await cls.init_pool()

        return await cls._pool.acquire()

    @classmethod
    async def init_pool(cls):
        if cls._pool is None:
            logger.info("🔌 Creando nuevo Pool de conexiones...")

            host = os.getenv("POSTGRES_SERVER", "postgres")
            port = int(os.getenv("POSTGRES_PORT", "5432"))
            user = os.getenv("POSTGRES_USER")
            password = os.getenv("POSTGRES_PASSWORD")
            database = os.getenv("POSTGRES_DB")

            logger.info(f"📡 Conectando a PostgreSQL en host={host} port={port} db={database} user={user}")

            cls._pool = await asyncpg.create_pool(
                user=user,
                password=password,
                database=database,
                host=host,
                port=port,
                min_size=1,
                max_size=5
            )
            logger.info("✅ Pool de conexiones PostgreSQL creado exitosamente.")

    @classmethod
    async def release_connection(cls, connection):
        if not connection:
            return

        try:
            if cls._pool and not cls._pool._loop.is_closed():
                await cls._pool.release(connection)
        except Exception as e:
            logger.warning(f"⚠️ Warning al liberar conexión: {e}")

    @classmethod
    async def close_pool(cls):
        if cls._pool and not cls._pool._loop.is_closed():
            await cls._pool.close()
            logger.info("🔌 Pool cerrado.")
