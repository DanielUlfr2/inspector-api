"""
Configuración de pytest para Inspector API
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.main import app
from app.db.base import Base
from app.db.connection import get_async_session
from app.config import DATABASE_URL  # Usar la base de datos principal

# Crear motor de base de datos usando la principal
TEST_ENGINE = create_async_engine(DATABASE_URL, echo=False)

# Crear session factory para tests
TestingSessionLocal = async_sessionmaker(
    TEST_ENGINE, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(scope="session")
def event_loop():
    """Crear event loop para la sesión de tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Crear sesión de base de datos para cada test"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client() -> Generator:
    """Cliente de prueba para FastAPI"""
    
    async def override_get_session():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_async_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# Crear tablas al inicio de la sesión de tests
@pytest.fixture(scope="session", autouse=True)
async def ensure_tables_exist():
    """Asegurar que las tablas existan antes de cualquier test"""
    print("🔄 Verificando tablas de test...")
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas verificadas/creadas")
    yield


# Fixtures para datos de prueba
@pytest.fixture
def sample_user_data():
    """Datos de ejemplo para usuario"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "testpassword123",
        "nombre": "Usuario Test",
        "apellido": "Apellido Test",
        "rol": "admin"
    }


@pytest.fixture
def sample_registro_data():
    """Datos de ejemplo para registro"""
    import uuid
    import random
    unique_id = str(uuid.uuid4())[:8]
    unique_number = random.randint(10000, 99999)
    return {
        "numero_inspector": unique_number,
        "nombre": f"ins{unique_number} Dispositivo Test {unique_id}",
        "observaciones": "Dispositivo de prueba",
        "status": "activo",
        "region": "Norte",
        "flota": "Flota A",
        "encargado": "Juan Pérez",
        "celular": "3001234567",
        "correo": "juan@test.com",
        "direccion": "Calle 123 #45-67",
        "uso": "Residencial",
        "departamento": "Antioquia",
        "ciudad": "Medellín",
        "tecnologia": "FTTH",
        "cmts_olt": "OLT-001",
        "id_servicio": "SERV-001",
        "mac_sn": "AA:BB:CC:DD:EE:FF",
        "uuid": f"test-uuid-{unique_id}"
    }


@pytest.fixture
def auth_headers(client, sample_user_data):
    """Obtener headers de autenticación"""
    try:
        # Registrar usuario
        register_response = client.post(
            "/auth/register", json=sample_user_data
        )
        if register_response.status_code != 200:
            return None
        
        # Hacer login
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        login_response = client.post("/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        else:
            return None
    except Exception:
        return None


def pytest_configure(config):
    """Configurar pytest"""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow tests"
    )
    config.addinivalue_line(
        "markers", "auth: marks tests as authentication tests"
    )
    config.addinivalue_line(
        "markers", "registros: marks tests as registro tests"
    ) 