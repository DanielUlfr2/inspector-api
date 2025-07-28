#!/usr/bin/env python3
"""
Script para probar la API directamente
"""
import asyncio
import sys
import os
import httpx

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from fastapi.testclient import TestClient

async def test_api():
    """Probar la API directamente"""
    client = TestClient(app)
    
    # Datos de prueba
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "nombre": "Usuario Test",
        "apellido": "Apellido Test",
        "rol": "admin"
    }
    
    print("Probando registro de usuario...")
    response = client.post("/auth/register", json=user_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 500:
        print("Error 500 detectado")
        try:
            error_detail = response.json()
            print(f"Error detail: {error_detail}")
        except:
            print("No se pudo parsear el error como JSON")

if __name__ == "__main__":
    asyncio.run(test_api()) 