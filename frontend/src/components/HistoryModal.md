# HistoryModal Component

## Descripción
Componente modal que muestra el historial de cambios de un inspector específico con mejoras de accesibilidad y validación estricta.

## Características

### ✅ Validación estricta
- Verificación de `inspectorId` antes del render
- Control de render sin verificación
- Tipos TypeScript completos

### ✅ Accesibilidad
- Roles ARIA apropiados (`role="dialog"`, `aria-modal="true"`)
- Etiquetas descriptivas para botones
- Navegación por teclado (Escape para cerrar)
- Focus management

### ✅ Mejoras visuales
- Diseño responsive
- Animaciones suaves
- Scrollbar personalizado
- Estados hover y focus

## Props

```typescript
interface HistoryModalProps {
  isOpen: boolean;           // Controla la visibilidad del modal
  onClose: () => void;       // Función para cerrar el modal
  inspectorId: number | null; // ID del inspector
  historial: HistorialItem[]; // Array de elementos del historial
}
```

## Tipos

```typescript
interface HistorialItem {
  fecha: string;
  descripcion: string;
  autor: string;
  campo?: string;
  valor_anterior?: string;
  valor_nuevo?: string;
  usuario?: string;
}
```

## Uso

```tsx
import HistoryModal from './HistoryModal';

<HistoryModal
  isOpen={isModalOpen}
  onClose={handleCloseModal}
  inspectorId={selectedInspectorId}
  historial={historialData}
/>
```

## Funcionalidades

### Eventos de teclado
- **Escape**: Cierra el modal
- **Tab**: Navegación entre elementos interactivos

### Estructura del contenido
1. **Header**: Título y botón de cierre
2. **Body**: Lista de elementos del historial
3. **Footer**: Botón de cerrar adicional

### Estados visuales
- **Sin datos**: Mensaje informativo
- **Con datos**: Lista estructurada con cambios
- **Hover**: Efectos visuales en elementos
- **Focus**: Indicadores de accesibilidad

## CSS Classes

### Estructura principal
- `.modal`: Contenedor principal
- `.modal-content`: Contenido del modal
- `.modal-header`: Encabezado
- `.modal-body`: Cuerpo del modal
- `.modal-footer`: Pie del modal

### Elementos del historial
- `.historial-container`: Contenedor de la lista
- `.historial-list`: Lista de elementos
- `.historial-item`: Elemento individual
- `.historial-header`: Encabezado del elemento
- `.historial-cambios`: Sección de cambios

### Estados
- `.no-data`: Mensaje sin datos
- `.close-btn`: Botón de cierre
- `.btn-secondary`: Botón secundario

## Responsive Design

### Desktop (>768px)
- Modal centrado con ancho fijo
- Layout horizontal para cambios
- Scrollbar personalizado

### Mobile (≤768px)
- Modal que ocupa 95% de la pantalla
- Layout vertical para cambios
- Botones más grandes para touch

## Mejoras implementadas

1. **Tipos completos**: `HistorialItem` con validación estricta
2. **Control de render**: Verificación de `inspectorId` y `isOpen`
3. **Accesibilidad**: Roles ARIA y navegación por teclado
4. **Estilos mejorados**: CSS puro con animaciones y responsive
5. **Estructura semántica**: HTML semántico con header, body, footer 