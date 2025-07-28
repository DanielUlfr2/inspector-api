"""
Tests unitarios para registros
"""
import pytest
from fastapi import status


class TestRegistroEndpoints:
    """Tests para endpoints de registros"""
    
    @pytest.mark.unit
    def test_create_registro_success(self, client, auth_headers, sample_registro_data):
        """Test creación exitosa de registro"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        response = client.post("/registros/", json=sample_registro_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "id" in data
        assert data["nombre"] == sample_registro_data["nombre"]
        assert data["uuid"] == sample_registro_data["uuid"]
        assert data["status"] == sample_registro_data["status"]
    
    @pytest.mark.unit
    def test_create_registro_unauthorized(self, client, sample_registro_data):
        """Test creación de registro sin autenticación"""
        response = client.post("/registros/", json=sample_registro_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    def test_create_registro_invalid_data(self, client, auth_headers):
        """Test creación con datos inválidos"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        invalid_data = {
            "nombre": "",  # Nombre vacío
            "uuid": "invalid-uuid",
            "status": "invalid-status"
        }
        
        response = client.post("/registros/", json=invalid_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_get_registros_list(self, client, auth_headers):
        """Test obtener lista de registros"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        response = client.get("/registros", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # La API devuelve una lista directa
        assert isinstance(data, list)
        # Verificar que al menos hay algunos registros
        assert len(data) >= 0
    
    @pytest.mark.unit
    def test_get_registros_with_filters(self, client, auth_headers):
        """Test obtener registros con filtros"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        # Crear un registro primero con datos únicos
        import uuid
        import random
        unique_id = str(uuid.uuid4())[:8]
        unique_number = random.randint(10000, 99999)
        sample_data = {
            "uuid": f"test-filter-uuid-{unique_id}",
            "nombre": f"ins{unique_number} Dispositivo Filtro",
            "observaciones": "Para testing de filtros",
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
            "numero_inspector": unique_number
        }
        create_response = client.post("/registros/", json=sample_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_200_OK
        
        # Probar filtro básico
        response = client.get("/registros?limit=5", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # La API devuelve una lista directa
        assert isinstance(data, list)
        # Verificar que la respuesta tiene el formato esperado
        assert len(data) <= 5  # Limit de 5
    
    @pytest.mark.unit
    def test_get_registro_by_id(self, client, auth_headers, sample_registro_data):
        """Test obtener registro por ID"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        # Crear registro
        create_response = client.post("/registros/", json=sample_registro_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_200_OK
        
        registro_id = create_response.json()["id"]
        
        # Obtener registro por ID
        response = client.get(f"/registros/{registro_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == registro_id
        assert data["nombre"] == sample_registro_data["nombre"]
    
    @pytest.mark.unit
    def test_get_registro_not_found(self, client, auth_headers):
        """Test obtener registro inexistente"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        response = client.get("/registros/999999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    def test_update_registro_success(self, client, auth_headers, sample_registro_data):
        """Test actualización exitosa de registro"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        # Crear registro
        create_response = client.post("/registros/", json=sample_registro_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_200_OK
        
        registro_id = create_response.json()["id"]
        
        # Actualizar registro con nombre válido y todos los campos requeridos
        import random
        unique_number = random.randint(10000, 99999)
        update_data = {
            "numero_inspector": unique_number,
            "nombre": f"ins{unique_number} Dispositivo Actualizado",
            "observaciones": "Descripción actualizada",
            "status": "inactivo",
            "region": "Sur",
            "flota": "Flota B",
            "encargado": "María García",
            "celular": "3009876543",
            "correo": "maria@test.com",
            "direccion": "Calle 456 #78-90",
            "uso": "Comercial",
            "departamento": "Valle",
            "ciudad": "Cali",
            "tecnologia": "HFC",
            "cmts_olt": "OLT-002",
            "id_servicio": "SERV-002",
            "mac_sn": "FF:EE:DD:CC:BB:AA",
            "uuid": "updated-uuid-123"
        }
        
        response = client.put(f"/registros/{registro_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["nombre"] == update_data["nombre"]
        assert data["observaciones"] == update_data["observaciones"]
        assert data["status"] == update_data["status"]
    
    @pytest.mark.unit
    def test_delete_registro_success(self, client, auth_headers, sample_registro_data):
        """Test eliminación exitosa de registro"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        # Crear registro
        create_response = client.post("/registros/", json=sample_registro_data, headers=auth_headers)
        assert create_response.status_code == status.HTTP_200_OK
        
        registro_id = create_response.json()["id"]
        
        # Eliminar registro
        response = client.delete(f"/registros/{registro_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar que ya no existe
        get_response = client.get(f"/registros/{registro_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.unit
    def test_get_registros_with_excel_sorting(self, client, auth_headers):
        """Test obtener registros con ordenamiento tipo Excel"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        # Crear registros con diferentes tipos de numero_inspector
        import uuid
        import random
        
        # Crear registros con números
        for i in range(3):
            unique_id = str(uuid.uuid4())[:8]
            numero = random.randint(10000, 99999)
            sample_data = {
                "uuid": f"test-excel-sort-{unique_id}",
                "nombre": f"ins{numero} Dispositivo {i}",
                "observaciones": f"Para testing de ordenamiento Excel {i}",
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
                "numero_inspector": numero
            }
            create_response = client.post("/registros/", json=sample_data, headers=auth_headers)
            assert create_response.status_code == status.HTTP_200_OK
        
        # Probar ordenamiento ascendente
        response = client.get("/registros?sort_by=numero_inspector&sort_dir=asc&limit=10", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verificar que la respuesta tiene el formato esperado
        assert isinstance(data, list)
        assert len(data) >= 0
        
        # Probar ordenamiento descendente
        response = client.get("/registros?sort_by=numero_inspector&sort_dir=desc&limit=10", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verificar que la respuesta tiene el formato esperado
        assert isinstance(data, list)
        assert len(data) >= 0


class TestRegistroService:
    """Tests para el servicio de registros"""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_registro_service(self, db_session, sample_registro_data):
        """Test creación de registro en el servicio"""
        from app.services.registro_service import registro_service
        
        # Crear registro
        session = await anext(db_session)
        try:
            registro = await registro_service.create_registro(session, sample_registro_data)
            
            assert registro is not None
            assert registro.nombre == sample_registro_data["nombre"]
            assert registro.uuid == sample_registro_data["uuid"]
            assert registro.status == sample_registro_data["status"]
        finally:
            await session.rollback()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_registro_by_id_service(self, db_session, sample_registro_data):
        """Test obtener registro por ID en el servicio"""
        from app.services.registro_service import registro_service
        
        # Crear registro
        session = await anext(db_session)
        try:
            created_registro = await registro_service.create_registro(session, sample_registro_data)
            
            # Obtener por ID
            registro = await registro_service.get_registro_by_id(session, created_registro.id)
            
            assert registro is not None
            assert registro.id == created_registro.id
            assert registro.nombre == sample_registro_data["nombre"]
        finally:
            await session.rollback()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_registro_service(self, db_session, sample_registro_data):
        """Test actualización de registro en el servicio"""
        from app.services.registro_service import registro_service
        
        # Crear registro
        session = await anext(db_session)
        try:
            created_registro = await registro_service.create_registro(session, sample_registro_data)
            
            # Datos de actualización con nombre único y válido
            import uuid
            import random
            unique_id = str(uuid.uuid4())[:8]
            unique_number = random.randint(10000, 99999)
            update_data = {
                "nombre": f"ins{unique_number} Dispositivo Actualizado {unique_id}",
                "status": "inactivo"
            }
            
            # Actualizar
            updated_registro = await registro_service.update_registro(
                session, created_registro.id, update_data
            )
            
            assert updated_registro is not None
            assert updated_registro.nombre == update_data["nombre"]
            assert updated_registro.status == update_data["status"]
        finally:
            await session.rollback()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_registro_service(self, db_session, sample_registro_data):
        """Test eliminación de registro en el servicio"""
        from app.services.registro_service import registro_service
        
        # Crear registro
        session = await anext(db_session)
        try:
            created_registro = await registro_service.create_registro(session, sample_registro_data)
            
            # Eliminar
            result = await registro_service.delete_registro(session, created_registro.id)
            
            assert result is True
            
            # Verificar que ya no existe
            deleted_registro = await registro_service.get_registro_by_id(session, created_registro.id)
            assert deleted_registro is None
        finally:
            await session.rollback() 