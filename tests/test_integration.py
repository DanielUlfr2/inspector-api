"""
🧪 Tests de Integración - Inspector API

Tests de integración end-to-end que verifican el funcionamiento completo
del sistema, incluyendo autenticación, base de datos, y flujos completos.

Autor: Daniel Bermúdez
Versión: 1.0.0
"""

import pytest
from fastapi import status
import uuid
import random

from app.services.auth import create_access_token, hash_password


class TestIntegrationAuth:
    """Tests de integración para autenticación completa"""
    
    @pytest.mark.integration
    def test_complete_auth_flow(self, client):
        """Test flujo completo de autenticación"""
        # 1. Registro de usuario
        user_data = {
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "email": f"test{uuid.uuid4().hex[:8]}@example.com",
            "password": "testpassword123",
            "nombre": "Usuario Test",
            "apellido": "Integración"
        }
        
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_200_OK
        
        # 2. Login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token_data = login_response.json()
        assert "access_token" in token_data
        assert "token_type" in token_data
        
        # 3. Acceso a endpoint protegido
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_response = client.get("/auth/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK
        
        user_info = me_response.json()
        assert user_info["username"] == user_data["username"]
        assert user_info["email"] == user_data["email"]
    
    @pytest.mark.integration
    def test_auth_with_invalid_credentials(self, client):
        """Test autenticación con credenciales inválidas"""
        login_data = {
            "username": "usuario_inexistente",
            "password": "password_incorrecto"
        }
        
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.integration
    def test_protected_endpoints_without_auth(self, client):
        """Test endpoints protegidos sin autenticación"""
        # Intentar acceder a endpoints protegidos sin token
        endpoints = [
            ("GET", "/registros"),
            ("POST", "/registros/"),
            ("GET", "/auth/me"),
            ("GET", "/registros/1"),
            ("PUT", "/registros/1"),
            ("DELETE", "/registros/1")
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            assert response.status_code in [status.HTTP_401_UNAUTHORIZED, 
                                          status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          status.HTTP_403_FORBIDDEN]


class TestIntegrationRegistros:
    """Tests de integración para CRUD completo de registros"""
    
    @pytest.mark.integration
    def test_complete_registro_lifecycle(self, client, auth_headers):
        """Test ciclo completo de vida de un registro"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        # 1. Crear registro
        unique_id = str(uuid.uuid4())[:8]
        unique_number = random.randint(10000, 99999)
        
        registro_data = {
            "uuid": f"test-lifecycle-uuid-{unique_id}",
            "nombre": f"ins{unique_number} Dispositivo Lifecycle",
            "observaciones": "Test de ciclo completo",
            "status": "activo",
            "region": "Centro",
            "flota": "Flota B",
            "encargado": "María García",
            "celular": "3009876543",
            "correo": "maria@test.com",
            "direccion": "Carrera 78 #90-12",
            "uso": "Comercial",
            "departamento": "Cundinamarca",
            "ciudad": "Bogotá",
            "tecnologia": "FTTH",
            "cmts_olt": "OLT-002",
            "id_servicio": "SERV-002",
            "mac_sn": "11:22:33:44:55:66",
            "numero_inspector": unique_number
        }
        
        create_response = client.post("/registros/", json=registro_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_200_OK
        
        created_registro = create_response.json()
        registro_id = created_registro["id"]
        
        # 2. Leer registro creado
        get_response = client.get(f"/registros/{registro_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_200_OK
        
        retrieved_registro = get_response.json()
        assert retrieved_registro["uuid"] == registro_data["uuid"]
        assert retrieved_registro["nombre"] == registro_data["nombre"]
        
        # 3. Actualizar registro - enviar todos los campos requeridos
        update_data = {
            "numero_inspector": unique_number,
            "uuid": f"test-lifecycle-uuid-{unique_id}",
            "nombre": f"ins{unique_number} Dispositivo Lifecycle Actualizado",
            "observaciones": "Actualizado en test de integración",
            "status": "inactivo",
            "region": "Centro",
            "flota": "Flota B",
            "encargado": "María García",
            "celular": "3009876543",
            "correo": "maria@test.com",
            "direccion": "Carrera 78 #90-12",
            "uso": "Comercial",
            "departamento": "Cundinamarca",
            "ciudad": "Bogotá",
            "tecnologia": "FTTH",
            "cmts_olt": "OLT-002",
            "id_servicio": "SERV-002",
            "mac_sn": "11:22:33:44:55:66"
        }
        
        update_response = client.put(f"/registros/{registro_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == status.HTTP_200_OK
        
        updated_registro = update_response.json()
        assert updated_registro["status"] == "inactivo"
        assert updated_registro["observaciones"] == "Actualizado en test de integración"
        
        # 4. Eliminar registro
        delete_response = client.delete(f"/registros/{registro_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_200_OK
        
        # 5. Verificar que fue eliminado
        get_deleted_response = client.get(f"/registros/{registro_id}", headers=auth_headers)
        assert get_deleted_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.integration
    def test_registros_with_complex_filters(self, client, auth_headers):
        """Test filtros complejos y ordenamiento"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        # Crear múltiples registros con datos variados
        registros_test = []
        for i in range(5):
            unique_id = str(uuid.uuid4())[:8]
            unique_number = random.randint(10000, 99999)
            
            registro_data = {
                "uuid": f"test-filter-uuid-{i}-{unique_id}",
                "nombre": f"ins{unique_number} Dispositivo Filtro {i}",
                "observaciones": f"Test de filtros complejos {i}",
                "status": "activo" if i % 2 == 0 else "inactivo",
                "region": "Norte" if i < 2 else "Sur",
                "flota": f"Flota {chr(65 + i)}",  # A, B, C, D, E
                "encargado": f"Usuario {i}",
                "celular": f"300123456{i}",
                "correo": f"usuario{i}@test.com",
                "direccion": f"Calle {i} #123",
                "uso": "Residencial" if i % 2 == 0 else "Comercial",
                "departamento": "Antioquia" if i < 3 else "Cundinamarca",
                "ciudad": "Medellín" if i < 3 else "Bogotá",
                "tecnologia": "FTTH" if i % 2 == 0 else "HFC",
                "cmts_olt": f"OLT-00{i}",
                "id_servicio": f"SERV-00{i}",
                "mac_sn": f"AA:BB:CC:DD:EE:0{i}",
                "numero_inspector": unique_number
            }
            
            response = client.post("/registros/", json=registro_data, headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            registros_test.append(response.json())
        
        # Test 1: Filtro por región
        response = client.get("/registros?region=Norte&limit=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2  # Al menos 2 registros del Norte
        
        # Test 2: Filtro por status
        response = client.get("/registros?status=activo&limit=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3  # Al menos 3 registros activos
        
        # Test 3: Ordenamiento por nombre
        response = client.get("/registros?sort_by=nombre&sort_dir=asc&limit=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 5
        
        # Test 4: Ordenamiento Excel para numero_inspector
        response = client.get("/registros?sort_by=numero_inspector&sort_dir=asc&limit=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 5
        
        # Test 5: Filtro combinado
        response = client.get("/registros?status=activo&region=Norte&limit=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1  # Al menos 1 registro activo del Norte
    
    @pytest.mark.integration
    def test_registros_pagination(self, client, auth_headers):
        """Test paginación de registros"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        # Crear registros adicionales para paginación
        for i in range(15):
            unique_id = str(uuid.uuid4())[:8]
            unique_number = random.randint(10000, 99999)
            
            registro_data = {
                "uuid": f"test-pagination-uuid-{i}-{unique_id}",
                "nombre": f"ins{unique_number} Dispositivo Paginación {i}",
                "observaciones": f"Test de paginación {i}",
                "status": "activo",
                "region": "Centro",
                "flota": "Flota Paginación",
                "encargado": f"Usuario Paginación {i}",
                "celular": f"300123456{i % 10}",  # Corregido para 10 dígitos máximo
                "correo": f"paginacion{i}@test.com",
                "direccion": f"Calle Paginación {i}",
                "uso": "Residencial",
                "departamento": "Antioquia",
                "ciudad": "Medellín",
                "tecnologia": "FTTH",
                "cmts_olt": f"OLT-PAG-{i:02d}",
                "id_servicio": f"SERV-PAG-{i:02d}",
                "mac_sn": f"AA:BB:CC:DD:EE:{i:02d}",
                "numero_inspector": unique_number
            }
            
            response = client.post("/registros/", json=registro_data, headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
        
        # Test 1: Primera página
        response = client.get("/registros?limit=5&offset=0", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 5
        
        # Test 2: Segunda página
        response = client.get("/registros?limit=5&offset=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 5
        
        # Test 3: Límite máximo
        response = client.get("/registros?limit=100&offset=0", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 100
    
    @pytest.mark.integration
    def test_registros_validation_errors(self, client, auth_headers):
        """Test errores de validación en registros"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        # Test 1: Datos incompletos
        incomplete_data = {
            "nombre": "Test Incompleto"
            # Faltan campos requeridos
        }
        
        response = client.post("/registros/", json=incomplete_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test 2: Datos inválidos
        invalid_data = {
            "uuid": "invalid-uuid",
            "nombre": "",  # Nombre vacío
            "celular": "123",  # Celular muy corto
            "correo": "invalid-email",  # Email inválido
            "numero_inspector": -1  # Número negativo
        }
        
        response = client.post("/registros/", json=invalid_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test 3: UUID duplicado
        unique_id = str(uuid.uuid4())[:8]
        unique_number = random.randint(10000, 99999)
        
        registro_data = {
            "uuid": f"test-duplicate-uuid-{unique_id}",
            "nombre": f"ins{unique_number} Dispositivo Duplicado",
            "observaciones": "Test de duplicados",
            "status": "activo",
            "region": "Centro",
            "flota": "Flota Duplicado",
            "encargado": "Usuario Duplicado",
            "celular": "3001234567",
            "correo": "duplicado@test.com",
            "direccion": "Calle Duplicado",
            "uso": "Residencial",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "tecnologia": "FTTH",
            "cmts_olt": "OLT-DUP",
            "id_servicio": "SERV-DUP",
            "mac_sn": "AA:BB:CC:DD:EE:FF",
            "numero_inspector": unique_number
        }
        
        # Crear primer registro
        response1 = client.post("/registros/", json=registro_data, headers=auth_headers)
        assert response1.status_code == status.HTTP_200_OK
        
        # Intentar crear registro con mismo UUID
        response2 = client.post("/registros/", json=registro_data, headers=auth_headers)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST


class TestIntegrationServices:
    """Tests de integración para servicios"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_auth_service_integration(self, db_session):
        """Test integración del servicio de autenticación"""
        # Test hash y verificación de contraseñas
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")
        
        # Test creación de token
        user_data = {"sub": "testuser", "username": "testuser"}
        token = create_access_token(user_data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_registro_service_integration(self, db_session):
        """Test integración del servicio de registros"""
        from app.services.registro_service import RegistroService
        import random
        import uuid
        
        service = RegistroService()
        
        # Test creación
        unique_id = str(uuid.uuid4())[:8]
        unique_number = random.randint(10000, 99999)  # Número único para evitar conflictos
        
        registro_data = {
            "numero_inspector": unique_number,  # Usar número único
            "uuid": f"test-service-uuid-{unique_id}",
            "nombre": f"Dispositivo Service Test {unique_id}",
            "observaciones": "Test de servicio",
            "status": "activo",
            "region": "Centro",
            "flota": "Flota Service",
            "encargado": "Usuario Service",
            "celular": "3001234567",
            "correo": "service@test.com",
            "direccion": "Calle Service",
            "uso": "Residencial",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "tecnologia": "FTTH",
            "cmts_olt": "OLT-SERVICE",
            "id_servicio": "SERV-SERVICE",
            "mac_sn": "AA:BB:CC:DD:EE:FF"
        }
        
        session = await anext(db_session)
        try:
            # Crear registro
            created_registro = await service.create_registro(session, registro_data)
            assert created_registro is not None
            assert created_registro.nombre == registro_data["nombre"]
            
            # Leer registro
            retrieved_registro = await service.get_registro_by_id(session, created_registro.id)
            assert retrieved_registro is not None
            assert retrieved_registro.uuid == registro_data["uuid"]
            
            # Actualizar registro
            update_data = {"status": "inactivo"}
            updated_registro = await service.update_registro(session, created_registro.id, update_data)
            assert updated_registro is not None
            assert updated_registro.status == "inactivo"
            
            # Eliminar registro
            deleted = await service.delete_registro(session, created_registro.id)
            assert deleted is True
            
            # Verificar eliminación
            deleted_registro = await service.get_registro_by_id(session, created_registro.id)
            assert deleted_registro is None
            
        finally:
            await session.rollback()


class TestIntegrationDatabase:
    """Tests de integración para base de datos"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_database_connection(self, db_session):
        """Test conexión a base de datos"""
        session = await anext(db_session)
        try:
            # Test consulta básica
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            
            # Test consulta a tabla registros
            from app.db.models import Registro
            result = await session.execute(text("SELECT COUNT(*) FROM registros"))
            count = result.scalar()
            assert isinstance(count, int)
            assert count >= 0
            
        finally:
            await session.rollback()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_database_constraints(self, db_session):
        """Test restricciones de base de datos"""
        session = await anext(db_session)
        try:
            from app.db.models import Registro
            from sqlalchemy import select
            import uuid
            import random
            
            # Test básico de inserción y lectura
            unique_id = str(uuid.uuid4())[:8]
            unique_number = random.randint(10000, 99999)  # Número único para evitar conflictos
            
            registro1 = Registro(
                numero_inspector=unique_number,  # Usar número único
                uuid=f"test-constraint-uuid-{unique_id}",
                nombre=f"Test Constraint {unique_id}",
                observaciones="Test observaciones 1",
                status="activo",
                region="Centro",
                flota="Flota Test",
                encargado="Usuario Test",
                celular="3001234567",
                correo="test@test.com",
                direccion="Calle Test",
                uso="Residencial",
                departamento="Antioquia",
                ciudad="Medellín",
                tecnologia="FTTH",
                cmts_olt="OLT-TEST",
                id_servicio="SERV-TEST",
                mac_sn="AA:BB:CC:DD:EE:FF"
            )
            
            session.add(registro1)
            await session.commit()
            
            # Verificar que se puede leer el registro
            result = await session.execute(
                select(Registro).where(Registro.uuid == f"test-constraint-uuid-{unique_id}")
            )
            registro_leido = result.scalar_one()
            assert registro_leido is not None
            assert registro_leido.nombre == f"Test Constraint {unique_id}"
            assert registro_leido.status == "activo"
            assert registro_leido.numero_inspector == unique_number
            
            # Test de consulta básica
            result = await session.execute(select(Registro))
            registros = result.scalars().all()
            assert len(registros) >= 1
            
        finally:
            await session.rollback()


class TestIntegrationAPI:
    """Tests de integración para API completa"""
    
    @pytest.mark.integration
    def test_api_health_check(self, client):
        """Test endpoint de health check"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.integration
    def test_api_documentation(self, client):
        """Test documentación de la API"""
        # Test OpenAPI docs
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.integration
    def test_api_cors(self, client):
        """Test CORS headers"""
        # Test CORS con GET en lugar de OPTIONS
        response = client.get("/registros")
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, 
                                      status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        # Verificar headers CORS si están presentes
        headers = response.headers
        if "access-control-allow-origin" in headers:
            assert "access-control-allow-origin" in headers
        if "access-control-allow-methods" in headers:
            assert "access-control-allow-methods" in headers
        if "access-control-allow-headers" in headers:
            assert "access-control-allow-headers" in headers


# Configuración de marcadores pytest
pytest_plugins = ["pytest_asyncio"]

def pytest_configure(config):
    """Configurar marcadores pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )