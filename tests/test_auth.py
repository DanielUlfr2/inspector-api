"""
Tests unitarios para autenticación
"""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Tests para endpoints de autenticación"""
    
    @pytest.mark.unit
    def test_register_user_success(self, client, sample_user_data):
        """Test registro exitoso de usuario"""
        response = client.post("/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Usuario registrado correctamente"
        assert "id" in data
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert "password" not in data  # No debe devolver la contraseña
    
    @pytest.mark.unit
    def test_register_user_duplicate_username(self, client, sample_user_data):
        """Test registro con username duplicado"""
        # Primer registro
        response1 = client.post("/auth/register", json=sample_user_data)
        assert response1.status_code == status.HTTP_200_OK
        
        # Segundo registro con mismo username
        response2 = client.post("/auth/register", json=sample_user_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "ya está en uso" in response2.json()["detail"]
    
    @pytest.mark.unit
    def test_register_user_invalid_data(self, client):
        """Test registro con datos inválidos"""
        invalid_data = {
            "username": "test",
            "email": "invalid-email",
            "password": "123"  # Contraseña muy corta
        }
        
        response = client.post("/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.unit
    def test_login_success(self, client, sample_user_data):
        """Test login exitoso"""
        # Registrar usuario primero
        client.post("/auth/register", json=sample_user_data)
        
        # Intentar login
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.unit
    def test_login_invalid_credentials(self, client):
        """Test login con credenciales inválidas"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    def test_get_current_user_success(self, client, auth_headers):
        """Test obtener usuario actual con token válido"""
        if not auth_headers:
            pytest.skip("No se pudo obtener token de autenticación")
        
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "id" in data
        assert "username" in data
        assert "email" in data
    
    @pytest.mark.unit
    def test_get_current_user_invalid_token(self, client):
        """Test obtener usuario actual con token inválido"""
        headers = {"Authorization": "Bearer invalid-token"}

        response = client.get("/auth/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.unit
    def test_get_current_user_no_token(self, client):
        """Test obtener usuario actual sin token"""
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAuthService:
    """Tests para el servicio de autenticación"""
    
    @pytest.mark.unit
    def test_hash_password(self):
        """Test hash de contraseña"""
        from app.services.auth import hash_password, verify_password
        
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    @pytest.mark.unit
    def test_password_hashing(self):
        """Test funciones de hash de contraseña"""
        from app.services.auth import hash_password, verify_password
        
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    @pytest.mark.unit
    def test_create_access_token(self):
        """Test creación de token de acceso"""
        from app.services.auth import create_access_token
        
        user_data = {"sub": "testuser", "username": "testuser"}
        token = create_access_token(user_data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    @pytest.mark.unit
    def test_verify_token(self):
        """Test verificación de token"""
        from app.services.auth import create_access_token, decode_access_token
        
        user_data = {"sub": "testuser", "username": "testuser"}
        token = create_access_token(user_data)
        
        # Verificar token válido
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
    
    @pytest.mark.unit
    def test_verify_invalid_token(self):
        """Test verificación de token inválido"""
        from app.services.auth import decode_access_token
        
        # Intentar verificar token inválido
        with pytest.raises(ValueError):
            decode_access_token("invalid-token") 