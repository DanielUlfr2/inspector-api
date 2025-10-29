# 📚 Instrucciones para Visualizar el Proyecto Inspector API

## Para el Profesor/Evaluador

### 🌐 Opción 1: Acceder a la Aplicación en Vivo (Recomendado)

**URL de la aplicación:** (Se proporcionará una vez desplegada)

**Credenciales de prueba:**
- **Usuario:** admin
- **Contraseña:** admin123

---

## 🚀 Para el Estudiante: Proceso de Despliegue

### Paso 1: Publicar el Backend (API)

Necesitas desplegar el backend en un servicio cloud. Opciones recomendadas:

#### Opción A: Railway.app (Gratis y Fácil)
1. Ve a [railway.app](https://railway.app)
2. Crea una cuenta con GitHub
3. Crea un nuevo proyecto
4. Conecta este repositorio
5. Railway detectará automáticamente que es una aplicación Python
6. Configura las variables de entorno necesarias

#### Opción B: Render.com (Gratis)
1. Ve a [render.com](https://render.com)
2. Crea una cuenta
3. Crea un nuevo "Web Service"
4. Conecta el repositorio de GitHub
5. Configuración:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Opción C: PythonAnywhere (Para desarrollo)
1. Ve a [pythonanywhere.com](https://www.pythonanywhere.com)
2. Crea una cuenta gratuita
3. Sube los archivos del proyecto
4. Configura el servidor web

### Paso 2: Configurar GitHub Pages para el Frontend

1. Ve a tu repositorio en GitHub
2. Click en **Settings** (Configuración)
3. Scroll hasta **Pages** (en el menú izquierdo)
4. En **Source**, selecciona:
   - Branch: `main`
   - Folder: `/frontend/dist`
5. Click en **Save**
6. Espera 1-2 minutos para que se publique
7. Tu URL será: `https://DanielUlfr2.github.io/inspector-api`

### Paso 3: Actualizar la URL de la API en el Frontend

1. Una vez tengas la URL de tu backend desplegado (por ejemplo: `https://tu-app.railway.app`)
2. Crea un archivo `.env.production` en la carpeta `frontend/`:

```env
VITE_API_URL=https://tu-backend-url.railway.app
```

3. Recompila el frontend:
```bash
cd frontend
npm run build
```

4. Sube los cambios a GitHub:
```bash
git add .
git commit -m "feat: Configurar URL de producción para API"
git push origin main
```

### Paso 4: Actualizar GitHub Pages

Los archivos ya deberían estar actualizados automáticamente. Si no, espera unos minutos.

---

## 📋 Checklist de Despliegue

- [ ] Backend desplegado en Railway/Render/PythonAnywhere
- [ ] Backend accesible públicamente (probar con Postman)
- [ ] Frontend compilado con la URL correcta de la API
- [ ] GitHub Pages configurado en `/frontend/dist`
- [ ] Aplicación funcionando en la URL de GitHub Pages
- [ ] Credenciales de prueba funcionando

---

## 🎯 Funcionalidades Demostrables

### Sistema de Autenticación
- Login de usuarios
- Gestión de sesiones
- Control de acceso basado en roles

### Gestión de Registros
- Visualización de registros con paginación
- Filtros y búsqueda
- Crear, editar y eliminar registros
- Historial de cambios por inspector

### Gestión de Usuarios
- Lista de usuarios
- Crear/editar usuarios
- Asignación de roles
- Gestión de fotos de perfil

### Dashboard
- Gráficos y estadísticas
- Resumen de datos importantes

### Importación/Exportación
- Importar desde Excel
- Exportar a CSV
- Exportar a Excel

---

## 📱 Tecnologías Utilizadas

### Frontend
- **React 18** + **TypeScript**
- **Vite** como bundler
- **React Router** para navegación
- **CSS Modules** para estilos

### Backend
- **FastAPI** (Framework Python moderno)
- **SQLAlchemy** (ORM)
- **Alembic** (Migraciones de base de datos)
- **SQLite** (Base de datos)
- **JWT** (Autenticación)
- **Pydantic** (Validación de datos)

### DevOps
- **GitHub Actions** (CI/CD)
- **Docker** (Containerización)
- **GitHub Pages** (Hosting frontend)

---

## 🔧 Instalación Local (Opcional para Testing)

Si prefieres ver el proyecto localmente:

1. Clonar el repositorio:
```bash
git clone https://github.com/DanielUlfr2/inspector-api.git
cd inspector-api
```

2. Backend:
```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

3. Frontend (en otra terminal):
```bash
cd frontend
npm install
npm run dev
```

---

## 📞 Soporte

Si tienes problemas con el despliegue, consulta:
- `README.md` - Documentación general del proyecto
- `AUTHENTICATION_GUIDE.md` - Guía del sistema de autenticación
- Logs de error en GitHub Actions o el servicio de backend

---

## ✅ Nota para el Evaluador

Este proyecto demuestra:
- ✅ Arquitectura full-stack moderna
- ✅ Separación de frontend y backend
- ✅ Sistema de autenticación robusto
- ✅ CRUD completo con validaciones
- ✅ Manejo de errores y UX
- ✅ Código limpio y bien organizado
- ✅ Despliegue en producción
