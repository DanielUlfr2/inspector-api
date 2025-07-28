# 🧪 Guía de Pruebas del Frontend

## 📋 **Checklist de Pruebas**

### **1. 🚀 Inicio y Navegación**
- [ ] **Acceso inicial**: Abrir `http://localhost:5173`
- [ ] **Página de login**: Verificar que aparece el formulario de login
- [ ] **Responsive**: Probar en diferentes tamaños de pantalla
- [ ] **Carga inicial**: Verificar que no hay errores en consola

### **2. 🔐 Autenticación**
- [ ] **Login exitoso**: 
  - Usuario: `DaniB`
  - Contraseña: `wolfyago9246`
  - Verificar redirección al dashboard
- [ ] **Login fallido**: 
  - Usuario: `test`
  - Contraseña: `wrong`
  - Verificar mensaje de error
- [ ] **Persistencia**: Recargar página y verificar que sigue logueado
- [ ] **Logout**: Probar botón de cerrar sesión

### **3. 🏠 Dashboard Principal**
- [ ] **Carga de datos**: Verificar que se cargan los registros
- [ ] **Sidebar**: 
  - Botón hamburguesa visible
  - Menú se abre/cierra correctamente
  - Información de usuario visible
  - Navegación funciona
- [ ] **Header**: Título visible y correcto
- [ ] **Tabla de registros**: 
  - Datos se muestran correctamente
  - Paginación funciona
  - Búsqueda funciona

### **4. 📊 Tabla de Registros (RecordTable)**
- [ ] **Visualización**:
  - Columnas se muestran correctamente
  - Datos se formatean bien
  - Responsive en móvil
- [ ] **Búsqueda**:
  - Input de búsqueda funciona
  - Búsqueda por texto
  - Limpiar búsqueda
- [ ] **Paginación**:
  - Botones anterior/siguiente
  - Indicador de página actual
  - Límite de registros por página

### **5. ✅ Selección Múltiple (Solo Admin)**
- [ ] **Checkboxes individuales**:
  - Seleccionar registros individuales
  - Deseleccionar registros
- [ ] **Checkbox global**:
  - Seleccionar todos los registros
  - Deseleccionar todos
- [ ] **Acciones en lote**:
  - Botones aparecen cuando hay selección
  - Eliminar selección (con confirmación)
  - Exportar selección a CSV

### **6. 🗑️ Confirmaciones Visuales**
- [ ] **Modal de confirmación**:
  - Aparece al eliminar registro individual
  - Aparece al eliminar múltiples registros
  - Botones Confirmar/Cancelar funcionan
  - Cierre con Escape
  - Cierre con clic fuera

### **7. ✏️ Operaciones CRUD**
- [ ] **Crear registro**:
  - Botón "Crear nuevo registro"
  - Modal de creación se abre
  - Formulario válido
  - Guardar registro
- [ ] **Editar registro**:
  - Botón "Editar" en cada fila
  - Modal de edición se abre
  - Datos precargados
  - Guardar cambios
- [ ] **Eliminar registro**:
  - Botón "Eliminar" en cada fila
  - Confirmación antes de eliminar
  - Registro se elimina correctamente

### **8. 📁 Carga Masiva**
- [ ] **Modal de carga**:
  - Botón "Carga CSV" se abre
  - Drag & drop funciona
  - Selección de archivo funciona
  - Validación de archivo CSV
- [ ] **Progreso**:
  - Barra de progreso visible
  - Porcentaje se actualiza
  - Mensaje de éxito/error

### **9. 📜 Historial por Inspector**
- [ ] **Apertura del modal**:
  - Botón "Ver historial" funciona
  - Modal se abre correctamente
- [ ] **Filtros**:
  - Filtro por tipo de cambio
  - Filtro por fecha
  - Filtro por campo
  - Botón "Limpiar filtros"
- [ ] **Paginación interna**:
  - 5 registros por página
  - Navegación entre páginas
  - Información de resultados

### **10. 👤 Menú de Usuario**
- [ ] **Avatar y información**:
  - Foto de perfil o iniciales
  - Nombre de usuario visible
  - Rol visible
- [ ] **Menú desplegable**:
  - Se abre al hacer clic
  - Opciones según rol
  - Navegación a páginas
- [ ] **Logout**:
  - Cerrar sesión funciona
  - Redirección al login

### **11. 📱 Responsive Design**
- [ ] **Desktop** (>1024px):
  - Layout completo
  - Sidebar visible
  - Tabla completa
- [ ] **Tablet** (768px-1024px):
  - Sidebar colapsable
  - Tabla con scroll horizontal
- [ ] **Móvil** (<768px):
  - Sidebar hamburguesa
  - Tabla responsive
  - Modales adaptados

### **12. 🔔 Notificaciones**
- [ ] **Notificaciones de éxito**:
  - Crear registro
  - Editar registro
  - Eliminar registro
  - Carga CSV
- [ ] **Notificaciones de error**:
  - Errores de red
  - Validaciones de formulario
  - Errores de carga
- [ ] **Auto-cierre**:
  - Notificaciones desaparecen automáticamente
  - Botón de cerrar funciona

### **13. 🎨 Estilos y UX**
- [ ] **Colores y temas**:
  - Colores consistentes
  - Estados hover/active
  - Estados disabled
- [ ] **Animaciones**:
  - Transiciones suaves
  - Loading states
  - Feedback visual
- [ ] **Accesibilidad**:
  - Navegación por teclado
  - Focus visible
  - ARIA labels

### **14. 🔒 Control de Roles**
- [ ] **Usuario Admin**:
  - Todas las funcionalidades disponibles
  - Botones de editar/eliminar visibles
  - Acciones en lote disponibles
- [ ] **Usuario Normal**:
  - Solo lectura
  - Botones de editar/eliminar ocultos
  - Acciones en lote ocultas

### **15. 🧪 Casos Edge**
- [ ] **Sin datos**:
  - Mensaje cuando no hay registros
  - Estado de carga
  - Estado de error
- [ ] **Errores de red**:
  - Manejo de errores 401/403
  - Redirección al login
  - Mensajes de error apropiados
- [ ] **Datos inválidos**:
  - Validación de formularios
  - Mensajes de error específicos

## 🚨 **Errores Comunes a Verificar**

### **Consola del Navegador**
- [ ] No hay errores de JavaScript
- [ ] No hay errores de TypeScript
- [ ] No hay warnings de React
- [ ] No hay errores de red (404, 500, etc.)

### **Performance**
- [ ] Carga inicial rápida
- [ ] Transiciones fluidas
- [ ] No hay memory leaks
- [ ] Responsive sin lag

### **Compatibilidad**
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (si es posible)
- [ ] Móviles

## 📝 **Cómo Reportar Problemas**

Si encuentras un error:

1. **Captura de pantalla** del error
2. **Pasos para reproducir**:
   - Qué hice antes
   - Qué hice exactamente
   - Qué esperaba vs qué pasó
3. **Información del navegador**:
   - Versión del navegador
   - Consola de errores
   - Network tab
4. **Datos de prueba** (si aplica)

## ✅ **Criterios de Aceptación**

El frontend está **LISTO** cuando:

- [ ] Todas las funcionalidades principales funcionan
- [ ] No hay errores en consola
- [ ] Es responsive en todos los dispositivos
- [ ] La UX es fluida y intuitiva
- [ ] Los roles funcionan correctamente
- [ ] Las confirmaciones previenen errores
- [ ] Las notificaciones dan feedback claro

---

**¡Manos a la obra! 🚀**
Empieza por la sección 1 y ve marcando cada item conforme lo pruebes. 