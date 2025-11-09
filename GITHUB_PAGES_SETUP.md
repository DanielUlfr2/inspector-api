# 🚀 Configuración de GitHub Pages - Inspector API

## Pasos para habilitar el repositorio público

### 1. Hacer el Repositorio Público

1. Ve a: **Settings** → **General** (en el menú lateral izquierdo)
2. Baja hasta la sección **"Danger Zone"** (zona de peligro)
3. Haz click en **"Change repository visibility"**
4. Selecciona **"Make public"**
5. Confirma escribiendo el nombre del repositorio cuando te lo pida

### 2. Configurar GitHub Pages

1. Ve a: **Settings** → **Pages** (en el menú lateral izquierdo)
2. Ahora deberías ver las opciones de configuración
3. En **"Source"** (Origen):
   - Selecciona: **"Deploy from a branch"**
4. En **"Branch"** (Rama):
   - Selecciona: **"main"**
5. En **"Folder"** (Carpeta):
   - Selecciona: **"/frontend/dist"**
6. Haz click en **"Save"** (Guardar)

### 3. Obtener tu URL

Después de guardar, espera 1-2 minutos.

La URL de tu sitio será:
```
https://DanielUlfr2.github.io/inspector-api
```

## ⚠️ Importante

El frontend intentará conectarse al backend en `localhost:8000`, por lo que:
- ✅ Se verá la interfaz visual completa
- ✅ Tu profesor podrá ver menús, diseño, navegación
- ❌ NO funcionarán el login ni la carga de datos (sin backend)

Esto es suficiente para mostrar el diseño y estructura de la aplicación.

## 📝 Notas adicionales

Si el repositorio debe permanecer privado (por la universidad):
- Puedes usar una cuenta GitHub pública personal para este proyecto
- O usar servicios como Vercel, Netlify, o Render que permiten repositorios privados

