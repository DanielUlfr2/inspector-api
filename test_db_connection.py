#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos PostgreSQL
"""

import asyncio
import asyncpg
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()


async def test_postgresql_connection():
    """Prueba la conexión a PostgreSQL usando asyncpg"""
    try:
        # Obtener URL desde variables de entorno
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL no encontrada en .env")
            return False
            
        print(f"🔍 Probando conexión a: {database_url}")
        
        # Probar con asyncpg
        conn = await asyncpg.connect(database_url)
        print("✅ Conexión exitosa con asyncpg")
        await conn.close()
        
        # Probar con SQLAlchemy async
        engine = create_async_engine(database_url)
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version();")
            version = result.scalar()
            print(f"✅ SQLAlchemy async funcionando - PostgreSQL {version}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def test_sqlalchemy_sync():
    """Prueba la conexión síncrona con SQLAlchemy"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL no encontrada en .env")
            return False
            
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute("SELECT version();")
            version = result.scalar()
            print(f"✅ SQLAlchemy sync funcionando - PostgreSQL {version}")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión síncrona: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Probando conexiones a base de datos...")
    
    # Probar conexión síncrona
    print("\n📡 Probando SQLAlchemy síncrono:")
    test_sqlalchemy_sync()
    
    # Probar conexión asíncrona
    print("\n📡 Probando SQLAlchemy asíncrono:")
    asyncio.run(test_postgresql_connection())
    
    print("\n✅ Pruebas completadas") 