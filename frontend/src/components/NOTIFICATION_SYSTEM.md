# Sistema de Notificaciones y Feedback al Usuario

## Descripción
Sistema centralizado para mostrar mensajes de feedback al usuario de forma elegante y consistente.

## Componentes del Sistema

### 1. Notification.tsx - Componente de Notificación
**Ubicación**: `src/components/Notification.tsx`

**Funcionalidades**:
- ✅ Diferentes tipos: success, error, warning, info
- ✅ Auto-dismiss con timer configurable
- ✅ Animaciones suaves de entrada y salida
- ✅ Diseño responsive
- ✅ Accesibilidad con roles ARIA

**Tipos de notificación**:
```typescript
type NotificationType = 'success' | 'error' | 'warning' | 'info';
```

**Uso**:
```typescript
import Notification from './Notification';

<Notification
  message="Registro eliminado con éxito"
  type="success"
  duration={5000}
  onClose={() => console.log('Cerrado')}
/>
```

### 2. useNotification Hook - Hook de Notificaciones
**Ubicación**: `src/hooks/useNotification.ts`

**Funcionalidades**:
- ✅ Estado centralizado de notificaciones
- ✅ Métodos específicos para cada tipo
- ✅ Control de visibilidad
- ✅ Callbacks para cerrar

**Métodos disponibles**:
```typescript
const {
  notification,
  showNotification,
  hideNotification,
  showSuccess,
  showError,
  showWarning,
  showInfo,
} = useNotification();
```

**Uso**:
```typescript
import { useNotification } from '../hooks/useNotification';

function MyComponent() {
  const { showSuccess, showError } = useNotification();
  
  const handleAction = async () => {
    try {
      await someAction();
      showSuccess('Acción completada con éxito');
    } catch (error) {
      showError('Error al completar la acción');
    }
  };
}
```

### 3. Notification.css - Estilos
**Ubicación**: `src/components/Notification.css`

**Características**:
- ✅ Colores semánticos por tipo
- ✅ Animaciones CSS suaves
- ✅ Diseño responsive
- ✅ Estados hover y focus
- ✅ Accesibilidad visual

## Implementación en RecordTable

### Feedback en Acciones Destructivas
```typescript
const handleDelete = async (registroId: number) => {
  const confirmado = window.confirm("¿Estás seguro?");
  if (!confirmado) return;

  try {
    await deleteRegistro(registroId);
    showSuccess("Registro eliminado con éxito.");
    fetchRegistros(); // refrescar tabla
  } catch (error) {
    showError("Error al eliminar el registro. Intenta nuevamente.");
  }
};
```

### Feedback en Carga de Datos
```typescript
const fetchRegistros = async () => {
  try {
    const data = await getRegistros({ limit, offset });
    setRegistros(data);
  } catch (error) {
    showError("Error al cargar los registros. Intenta más tarde.");
  }
};
```

### Feedback en Acciones de Historial
```typescript
const handleOpenModal = async (numero_inspector: number) => {
  try {
    const historialData = await getHistorialInspector(numero_inspector);
    setHistorial(historialData);
    setIsModalOpen(true);
  } catch (error) {
    showError("Error al cargar el historial del inspector.");
  }
};
```

## Tipos de Mensajes

### Success (Éxito)
- **Color**: Verde (#10b981)
- **Icono**: ✅
- **Uso**: Acciones completadas exitosamente
- **Ejemplo**: "Registro eliminado con éxito"

### Error (Error)
- **Color**: Rojo (#ef4444)
- **Icono**: ❌
- **Uso**: Errores en operaciones
- **Ejemplo**: "Error al eliminar el registro"

### Warning (Advertencia)
- **Color**: Amarillo (#f59e0b)
- **Icono**: ⚠️
- **Uso**: Advertencias importantes
- **Ejemplo**: "Sesión próxima a expirar"

### Info (Información)
- **Color**: Azul (#3b82f6)
- **Icono**: ℹ️
- **Uso**: Información general
- **Ejemplo**: "Cargando datos..."

## Configuración

### Duración por Defecto
```typescript
// 5 segundos para notificaciones automáticas
duration={5000}

// Sin auto-dismiss para notificaciones importantes
duration={0}
```

### Posición
```css
/* Esquina superior derecha */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
}
```

### Responsive
```css
@media (max-width: 768px) {
  .notification {
    top: 10px;
    right: 10px;
    left: 10px;
  }
}
```

## Beneficios del Sistema

### ✅ UX Mejorada
- Feedback inmediato al usuario
- Mensajes claros y específicos
- Animaciones suaves y profesionales
- Auto-dismiss para no interrumpir

### ✅ Consistencia
- Mismo estilo en toda la aplicación
- Colores semánticos por tipo
- Comportamiento uniforme

### ✅ Accesibilidad
- Roles ARIA apropiados
- Navegación por teclado
- Contraste de colores adecuado
- Etiquetas descriptivas

### ✅ Mantenibilidad
- Código centralizado
- Fácil de extender
- Tipos TypeScript completos
- Reutilizable en toda la app

## Uso en Otros Componentes

### Componente de Login
```typescript
const handleLogin = async (credentials) => {
  try {
    await login(credentials);
    showSuccess('Inicio de sesión exitoso');
    // redirigir al dashboard
  } catch (error) {
    showError('Credenciales incorrectas');
  }
};
```

### Componente de Creación
```typescript
const handleCreate = async (data) => {
  try {
    await createRegistro(data);
    showSuccess('Registro creado exitosamente');
    onClose();
  } catch (error) {
    showError('Error al crear el registro');
  }
};
```

### Componente de Actualización
```typescript
const handleUpdate = async (id, data) => {
  try {
    await updateRegistro(id, data);
    showSuccess('Registro actualizado exitosamente');
    onClose();
  } catch (error) {
    showError('Error al actualizar el registro');
  }
};
```

## Testing

### Pruebas de Notificaciones
```typescript
// Mock del hook
const mockShowSuccess = jest.fn();
const mockShowError = jest.fn();

// Verificar que se muestre notificación de éxito
await handleDelete(1);
expect(mockShowSuccess).toHaveBeenCalledWith('Registro eliminado con éxito');

// Verificar que se muestre notificación de error
await handleDelete(999); // ID inexistente
expect(mockShowError).toHaveBeenCalledWith('Error al eliminar el registro');
```

## Mejoras Futuras

### 1. Sistema de Cola
- Múltiples notificaciones simultáneas
- Cola automática cuando hay muchas
- Priorización por tipo

### 2. Persistencia
- Notificaciones que persisten entre páginas
- Historial de notificaciones
- Configuración de usuario

### 3. Temas
- Modo oscuro/claro
- Colores personalizables
- Animaciones configurables

### 4. Integración con Backend
- Notificaciones push del servidor
- Sincronización en tiempo real
- Notificaciones de sistema

Este sistema proporciona una experiencia de usuario profesional y consistente en toda la aplicación. 