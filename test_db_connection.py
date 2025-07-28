#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos de test
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import TEST_DATABASE_URL
from app.db.base import Base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

async def test_db_connection():
    """Probar la conexión a la base de datos de test"""
    print(f"URL de base de datos de test: {TEST_DATABASE_URL}")
    
    try:
        # Crear motor de base de datos
        engine = create_async_engine(TEST_DATABASE_URL, echo=True)
        print("✅ Motor de base de datos creado correctamente")
        
        # Crear tablas
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tablas creadas correctamente")
        
        # Probar sesión
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            print("✅ Sesión de base de datos creada correctamente")
            
        print("✅ Todas las pruebas de base de datos pasaron")
        
    except Exception as e:
        print(f"❌ Error en la base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(test_db_connection()) 