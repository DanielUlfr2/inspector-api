# 🏗️ Lineamientos de Arquitectura - Inspector API

Esta documentación define la **arquitectura estandarizada** que debe seguir todo el desarrollo del sistema `Inspector`.  
El objetivo es mantener una estructura ordenada, escalable y fácil de mantener.

---

## 📁 Estructura General del Proyecto

```
inspector_api/
├── app/
│   ├── config.py                 # Configuración centralizada
│   ├── main.py                   # Punto de entrada de la API
│   ├── db/
│   │   ├── base.py              # Configuración de base de datos
│   │   ├── connection.py        # Conexiones a BD
│   │   └── models.py            # Modelos de datos
│   ├── routes/
│   │   ├── auth.py              # Autenticación
│   │   ├── registros.py         # CRUD de registros
│   │   ├── usuarios.py          # Gestión de usuarios
│   │   ├── view.py              # Vistas optimizadas
│   │   ├── upload_excel.py      # Carga masiva
│   │   └── excel_export.py      # Exportación
│   ├── schemas/
│   │   ├── registro.py          # Esquemas Pydantic
│   │   ├── usuario.py           # Esquemas de usuario
│   │   └── respuesta.py         # Respuestas estandarizadas
│   ├── services/
│   │   ├── auth.py              # Lógica de autenticación
│   │   ├── cache.py             # Sistema de cache
│   │   ├── validation.py        # Validaciones de datos
│   │   └── deps.py              # Dependencias inyectables
│   └── static/
│       └── fotos/               # Archivos estáticos
├── frontend/
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   ├── pages/               # Páginas principales
│   │   ├── services/            # Servicios de API
│   │   ├── hooks/               # Custom hooks
│   │   ├── utils/               # Utilidades
│   │   ├── types/               # Tipos TypeScript
│   │   ├── context/             # Context API
│   │   └── styles/              # Estilos CSS
│   ├── public/                  # Archivos públicos
│   └── package.json             # Dependencias frontend
├── alembic/                     # Migraciones de BD
├── requirements.txt              # Dependencias Python
└── README.md                    # Documentación principal
```

---

## 🏛️ Principios Arquitectónicos

### 1. **Separación de Responsabilidades**
- **Routes:** Solo manejo de HTTP y validación de entrada
- **Services:** Lógica de negocio y operaciones complejas
- **Models:** Estructura de datos y relaciones
- **Schemas:** Validación y serialización de datos

### 2. **Inyección de Dependencias**
- Usar `Depends()` de FastAPI para inyección
- Centralizar configuración en `app/config.py`
- Evitar dependencias circulares

### 3. **Patrón Repository**
- Separar acceso a datos de lógica de negocio
- Usar async/await para operaciones de BD
- Implementar cache para consultas frecuentes

---

## 📂 Detalle por Capa

### **Backend - FastAPI**

#### `app/config.py`
```python
# Configuración centralizada con variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inspector.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
```

#### `app/routes/[module].py`
```python
@router.get("/endpoint")
async def endpoint(
    session: AsyncSession = Depends(get_async_session),
    user: Usuario = Depends(get_current_user)
):
    # Solo validación de entrada y respuesta HTTP
    # Lógica de negocio en services/
```

#### `app/services/[module].py`
```python
# Lógica de negocio centralizada
async def business_logic(data: dict, session: AsyncSession):
    # Validaciones complejas
    # Operaciones de BD
    # Transformaciones de datos
```

#### `app/schemas/[module].py`
```python
# Validación y serialización con Pydantic
class RegistroCreate(BaseModel):
    campo: str = Field(..., min_length=3)
    
    @field_validator('campo')
    def validate_campo(cls, v):
        # Validaciones personalizadas
```

### **Frontend - React + TypeScript**

#### `src/components/[Module]/`
```typescript
// Componentes reutilizables y autocontenidos
interface ComponentProps {
  data: DataType;
  onAction: (id: string) => void;
}

export const Component: React.FC<ComponentProps> = ({ data, onAction }) => {
  // Lógica del componente
};
```

#### `src/services/apiService_[module].ts`
```typescript
// Comunicación HTTP centralizada
export const fetchRegistros = async (params: QueryParams): Promise<Registro[]> => {
  try {
    const response = await apiClient.get('/registros', { params });
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};
```

#### `src/hooks/useCustomLogic_[module].ts`
```typescript
// Custom hooks para lógica reutilizable
export const useRegistros = (filters: Filters) => {
  const [data, setData] = useState<Registro[]>([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    // Lógica de carga y gestión de estado
  }, [filters]);
  
  return { data, loading, refetch };
};
```

#### `src/utils/dataUtils_[module].ts`
```typescript
// Funciones puras para transformación de datos
export const formatRegistroData = (rawData: any): Registro => {
  return {
    id: rawData.id,
    nombre: rawData.nombre?.trim(),
    // Transformaciones de datos
  };
};
```

---

## 🔧 Configuración y Variables de Entorno

### **Backend (.env)**
```env
DATABASE_URL=postgresql://user:pass@localhost/inspector
SECRET_KEY=your-super-secret-key-here
LOG_LEVEL=INFO
CACHE_TTL=300
```

### **Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=Inspector
```

---

## 📊 Patrones de Datos

### **Respuestas API Estandarizadas**
```python
# app/schemas/respuesta.py
class ApiResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None
```

### **Manejo de Errores**
```python
# app/main.py
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "code": exc.status_code
        }
    )
```

---

## 🧪 Testing y Calidad

### **Backend Testing**
```python
# tests/test_registros.py
async def test_crear_registro():
    # Tests unitarios para cada endpoint
    # Usar pytest-asyncio para tests async
```

### **Frontend Testing**
```typescript
// tests/components/Component.test.tsx
import { render, screen } from '@testing-library/react';
import { Component } from '../Component';

test('renders component correctly', () => {
  render(<Component data={mockData} />);
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});
```

---

## 🚀 Deployment y CI/CD

### **Docker**
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **GitHub Actions**
```yaml
# .github/workflows/deploy.yml
name: Deploy Inspector API
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest
```

---

## 📝 Mandamientos del Desarrollador Inspector

1. 🧱 **Modulariza** tu código en componentes y servicios reutilizables
2. ⚡ **Usa asincronismo** para mejorar el rendimiento de la API
3. 📦 **Gestiona configuración** con archivos `.env` y `app/config.py`
4. 🚀 **Aprovecha el paralelismo** en operaciones independientes
5. 🛠️ **Ejecuta procesos pesados** en background tasks
6. 📉 **No uses archivos CSV/XLSX** como base de datos principal
7. 📂 **Utiliza formatos modernos** como JSON, Redis y PostgreSQL
8. 📌 **Normaliza la base de datos** correctamente con relaciones
9. 🚫 **Evita datos vacíos** o nulos en campos críticos
10. ❌🐍 **No uses Jupyter** en entornos de producción
11. 🧹 **Libera recursos** una vez finalizada la ejecución
12. 📖 **Mantén código limpio** y documentado (Git, README, docstrings)
13. 🔒 **Usa autenticación JWT** y evita accesos sin protección
14. 🔑 **Nunca dejes credenciales** visibles en el código
15. 📝 **Muestra logs estructurados** con niveles para debugging
16. 🗑️ **Configura TTL** para logs y cache
17. 🤖 **Usa IA responsablemente** en el desarrollo
18. ⭐ **Aplica MLP** (Minimum Lovable Product) en features
19. 🎨 **Cuida la UX/UI** con diseño consistente
20. 🔄 **Mantén versionado** de APIs y documentación actualizada

---

## ✅ Checklist de Implementación

### **Para Nuevos Módulos:**
- [ ] Crear estructura de carpetas siguiendo el patrón
- [ ] Implementar modelos en `app/db/models.py`
- [ ] Crear esquemas Pydantic en `app/schemas/`
- [ ] Implementar servicios en `app/services/`
- [ ] Crear rutas en `app/routes/`
- [ ] Agregar tests unitarios
- [ ] Documentar endpoints con docstrings
- [ ] Actualizar `app/main.py` con nuevos routers

### **Para Nuevos Componentes Frontend:**
- [ ] Crear componente en `src/components/[Module]/`
- [ ] Implementar servicios en `src/services/`
- [ ] Crear hooks en `src/hooks/`
- [ ] Agregar utilidades en `src/utils/`
- [ ] Implementar tests con React Testing Library
- [ ] Documentar props y funcionalidad
- [ ] Actualizar rutas en `App.tsx`

---

## 📚 Recursos y Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Pydantic Validation](https://pydantic-docs.helpmanual.io/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

---

*Este documento debe actualizarse cada vez que se agreguen nuevas reglas o patrones al proyecto.* 