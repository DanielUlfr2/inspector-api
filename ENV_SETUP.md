# 🔧 Configuración de Variables de Entorno - Inspector

## 📋 Pasos para Configurar

### 1. **Crear archivo `.env`**

Copia el contenido de `env_template.txt` y crea un archivo `.env` en la raíz del proyecto:

```bash
# En la raíz del proyecto
cp env_template.txt .env
```

### 2. **Editar variables según tu entorno**

Abre el archivo `.env` y ajusta las variables según tu configuración:

```env
# Ejemplo de configuración para desarrollo
DATABASE_URL=sqlite+aiosqlite:///./inspector.db
SECRET_KEY=mi-clave-super-secreta-para-desarrollo
ENVIRONMENT=development
DEBUG=true
```

### 3. **Instalar dependencia**

```bash
pip install python-dotenv
```

## 🔐 Variables Importantes

### **Obligatorias:**
- `DATABASE_URL` - URL de conexión a la base de datos
- `SECRET_KEY` - Clave secreta para JWT (cambiar en producción)

### **Seguridad:**
- `SECRET_KEY` - Debe ser una cadena larga y aleatoria
- `BCRYPT_ROUNDS` - Número de rondas para hash de contraseñas
- `PASSWORD_MIN_LENGTH` - Longitud mínima de contraseñas

### **Desarrollo:**
- `DEBUG` - Habilitar modo debug
- `ENVIRONMENT` - Entorno (development/staging/production)
- `LOG_LEVEL` - Nivel de logging

## 🚀 Configuraciones por Entorno

### **Desarrollo:**
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
CACHE_ENABLED=false
```

### **Producción:**
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
CACHE_ENABLED=true
SECRET_KEY=clave-super-secreta-y-larga
```

### **Testing:**
```env
ENVIRONMENT=testing
TESTING=true
TEST_DATABASE_URL=sqlite+aiosqlite:///./test_inspector.db
```

## 🔒 Seguridad

### **Nunca subir `.env` al repositorio:**
- El archivo `.env` está en `.gitignore`
- Usar `env_template.txt` como plantilla
- Cada desarrollador debe crear su propio `.env`

### **Variables sensibles:**
- `SECRET_KEY` - Cambiar en cada entorno
- `SMTP_PASSWORD` - Solo si usas email
- `REDIS_URL` - Solo si usas Redis

## 📊 Verificación

Para verificar que la configuración funciona:

```python
from app.config import DATABASE_URL, SECRET_KEY, ENVIRONMENT

print(f"Database: {DATABASE_URL}")
print(f"Environment: {ENVIRONMENT}")
print(f"Secret Key configured: {'Yes' if SECRET_KEY != 'your-secret-key-here' else 'No'}")
```

## 🆘 Solución de Problemas

### **Error: "ModuleNotFoundError: No module named 'dotenv'"**
```bash
pip install python-dotenv
```

### **Error: "DATABASE_URL not found"**
- Verificar que el archivo `.env` existe
- Verificar que `load_dotenv()` se ejecuta antes de usar las variables

### **Variables no se cargan**
- Verificar que el archivo `.env` está en la raíz del proyecto
- Verificar que no hay espacios extra en las variables

## 📝 Notas

- Las variables tienen valores por defecto seguros
- El archivo `.env` no se sube al repositorio por seguridad
- Usar `env_template.txt` como referencia para nuevas variables 