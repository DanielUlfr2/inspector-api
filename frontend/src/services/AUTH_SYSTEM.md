# Sistema de Autenticación y Manejo de Sesión

## Descripción
Sistema centralizado para manejar autenticación, expiración de tokens y redirección automática al login.

## Componentes del Sistema

### 1. apiClient.ts - Cliente HTTP Centralizado
**Ubicación**: `src/services/apiClient.ts`

**Funcionalidades**:
- ✅ Detección automática de expiración de sesión (401/403)
- ✅ Logout automático y redirección al login
- ✅ Notificación visual de sesión expirada
- ✅ Helpers para GET, POST, PUT, DELETE
- ✅ Manejo centralizado de headers de autenticación

**Uso**:
```typescript
import { apiGet, apiPost } from './apiClient';

// GET request
const data = await apiGet('/api/registros');

// POST request
const result = await apiPost('/api/registros', { nombre: 'test' });
```

### 2. authService.ts - Servicios de Autenticación
**Ubicación**: `src/services/authService.ts`

**Funcionalidades**:
- ✅ Gestión de tokens en localStorage
- ✅ Logout completo (limpia token, user, sessionStorage, cookies)
- ✅ Verificación de expiración de token
- ✅ Renovación automática de tokens
- ✅ Funciones de login/logout

**Funciones principales**:
```typescript
// Verificar si está autenticado
const isAuth = isAuthenticated();

// Obtener token actual
const token = getToken();

// Cerrar sesión completamente
logout();

// Verificar si el token expira pronto
const expiringSoon = isTokenExpiringSoon();

// Renovar token
const refreshed = await refreshToken();
```

### 3. useAuth Hook - Hook de Autenticación
**Ubicación**: `src/hooks/useAuth.ts`

**Funcionalidades**:
- ✅ Estado de autenticación en tiempo real
- ✅ Verificación periódica de expiración
- ✅ Renovación automática de tokens
- ✅ Logout con redirección

**Uso**:
```typescript
import { useAuth } from '../hooks/useAuth';

function MyComponent() {
  const { isAuthenticated, user, loading, logout } = useAuth();
  
  if (loading) return <div>Cargando...</div>;
  if (!isAuthenticated) return <div>No autenticado</div>;
  
  return <div>Bienvenido, {user?.username}</div>;
}
```

### 4. ProtectedRoute - Componente de Protección
**Ubicación**: `src/components/ProtectedRoute.tsx`

**Funcionalidades**:
- ✅ Protección automática de rutas
- ✅ Redirección al login si no está autenticado
- ✅ Loading state mientras verifica autenticación

**Uso**:
```typescript
import ProtectedRoute from '../components/ProtectedRoute';

<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>
```

### 5. SessionNotification - Notificaciones de Sesión
**Ubicación**: `src/components/SessionNotification.tsx`

**Funcionalidades**:
- ✅ Notificaciones elegantes de sesión expirada
- ✅ Diferentes tipos: error, warning, info
- ✅ Auto-dismiss con timer
- ✅ Responsive design

## Flujo de Autenticación

### 1. Login
```typescript
// 1. Usuario ingresa credenciales
const credentials = { username: 'user', password: 'pass' };

// 2. Se hace petición al backend
const response = await login(credentials);

// 3. Se guarda token y datos del usuario
setToken(response.access_token);
setCurrentUser(response.user);
```

### 2. Verificación de Autenticación
```typescript
// 1. Se verifica si existe token
const hasToken = isAuthenticated();

// 2. Si hay token, se verifica si expira pronto
if (isTokenExpiringSoon()) {
  // 3. Se intenta renovar automáticamente
  const refreshed = await refreshToken();
  if (!refreshed) {
    // 4. Si no se puede renovar, se hace logout
    logout();
  }
}
```

### 3. Detección de Expiración
```typescript
// 1. Se hace petición API
const response = await apiGet('/api/protected-endpoint');

// 2. Si devuelve 401/403, apiClient detecta automáticamente
if (response.status === 401 || response.status === 403) {
  // 3. Se ejecuta logout automático
  logout();
  
  // 4. Se muestra notificación
  showSessionExpiredMessage();
  
  // 5. Se redirige al login
  window.location.href = '/login';
}
```

## Manejo de Errores

### Errores de Autenticación
- **401 Unauthorized**: Token inválido o expirado
- **403 Forbidden**: Token válido pero sin permisos
- **Token expirado**: Renovación automática o logout

### Respuestas del Sistema
1. **Detección automática**: apiClient detecta 401/403
2. **Logout completo**: Limpia todos los datos de sesión
3. **Notificación visual**: Mensaje claro al usuario
4. **Redirección**: Automática al login

## Configuración

### Variables de Entorno
```env
VITE_API_URL=http://localhost:8000
```

### Endpoints del Backend
```typescript
// Login
POST /auth/login

// Refresh token
POST /auth/refresh

// Logout (opcional)
POST /auth/logout
```

## Beneficios del Sistema

### ✅ Seguridad
- Detección automática de tokens expirados
- Logout completo que limpia todos los datos
- Renovación automática de tokens

### ✅ UX Mejorada
- Notificaciones claras de sesión expirada
- Redirección automática al login
- Estados de loading apropiados

### ✅ Mantenibilidad
- Código centralizado y reutilizable
- Tipos TypeScript completos
- Documentación detallada

### ✅ Robustez
- Manejo de errores consistente
- Verificación periódica de tokens
- Fallbacks apropiados

## Uso en Componentes

### Componente con Autenticación
```typescript
import { useAuth } from '../hooks/useAuth';
import { apiGet } from '../services/apiClient';

function MyComponent() {
  const { isAuthenticated, user } = useAuth();
  const [data, setData] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      // apiClient maneja automáticamente la autenticación
      apiGet('/api/data').then(setData);
    }
  }, [isAuthenticated]);

  return <div>{/* contenido */}</div>;
}
```

### Ruta Protegida
```typescript
import ProtectedRoute from '../components/ProtectedRoute';

function App() {
  return (
    <Router>
      <Route path="/dashboard">
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      </Route>
    </Router>
  );
}
```

## Testing

### Pruebas de Autenticación
```typescript
// Mock de token expirado
localStorage.setItem('token', 'expired-token');

// Hacer petición que debería fallar
try {
  await apiGet('/api/protected');
} catch (error) {
  // Debería hacer logout automático
  expect(isAuthenticated()).toBe(false);
}
```

Este sistema proporciona una solución completa y robusta para el manejo de autenticación en la aplicación. 