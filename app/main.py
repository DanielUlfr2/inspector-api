"""
🏗️ Inspector API - Punto de entrada principal

Este módulo contiene la configuración principal de la aplicación FastAPI para el sistema
de gestión de inventario de registros de inspección.

Características principales:
- Configuración de CORS y middleware
- Manejo centralizado de errores
- Registro de rutas de la aplicación
- Configuración de logging
- Endpoints de monitoreo

Autor: Daniel Bermúdez
Versión: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
from fastapi.exception_handlers import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
import sys
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.routes import registros
from app.routes import view
from app.routes import upload_excel  # Corregido: era excel_upload
from app.routes import excel_export  # ✅ sin cambios
from app.routes import usuarios
from app.routes import auth

try:
    from app.routes import historial
    HAS_HISTORIAL = True
except ImportError:
    HAS_HISTORIAL = False

# Configuración de la aplicación FastAPI
app = FastAPI(
    title="Inspector API",
    description="API para gestión de inventario de registros de inspección",
    version="1.0.0",
    openapi_tags=[
        {"name": "autenticación", "description": "Operaciones de login y autenticación"},
    ],
    openapi_url="/openapi.json"
)

# Esquema OAuth2 Password para Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de compresión Gzip para mejorar rendimiento
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configuración centralizada del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Registro de rutas
app.include_router(registros.router)
app.include_router(view.router)
app.include_router(upload_excel.router)  # Corregido: era excel_upload.router
app.include_router(excel_export.router)
app.include_router(usuarios.router)
app.include_router(auth.router)

if HAS_HISTORIAL:
    app.include_router(historial.router)

# Montar la carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """
    Evento de inicio de la aplicación.
    
    Se ejecuta cuando la aplicación FastAPI se inicia y registra información
    sobre el estado de la aplicación y las rutas disponibles.
    
    Returns:
        None
    """
    logger.info("Aplicación FastAPI iniciada correctamente")
    logger.info("CORS habilitado")
    logger.info("Rutas montadas: /registros, /view, /upload_excel, /excel_export, /usuarios, /auth" + (", /historial" if HAS_HISTORIAL else ""))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador de errores de validación de datos.
    
    Captura errores de validación de Pydantic y devuelve una respuesta
    estructurada con detalles de los errores encontrados.
    
    Args:
        request (Request): Objeto de solicitud FastAPI
        exc (RequestValidationError): Excepción de validación
        
    Returns:
        JSONResponse: Respuesta con errores de validación estructurados
    """
    errors = [
        {"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    logger.warning(f"Error de validación: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Error de validación de datos.",
            "code": 422,
            "errors": errors
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Manejador de errores generales.
    
    Captura cualquier excepción no manejada y devuelve una respuesta
    de error genérica para evitar exponer detalles internos.
    
    Args:
        request (Request): Objeto de solicitud FastAPI
        exc (Exception): Excepción no manejada
        
    Returns:
        JSONResponse: Respuesta de error genérica
    """
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor.",
            "code": 500
        }
    )

@app.get("/health", tags=["monitoring"], summary="Health check", description="Endpoint de monitoreo para verificar que la API está activa.")
async def health():
    """
    Endpoint de verificación de salud de la API.
    
    Utilizado por sistemas de monitoreo para verificar que la aplicación
    está funcionando correctamente.
    
    Returns:
        dict: Estado de salud de la aplicación
    """
    return {
        "status": "healthy",
        "message": "Inspector API está funcionando correctamente",
        "version": "1.0.0"
    }

def custom_openapi():
    """
    Personalización del esquema OpenAPI.
    
    Modifica el esquema OpenAPI generado automáticamente para incluir
    información adicional y mejorar la documentación de la API.
    
    Returns:
        dict: Esquema OpenAPI personalizado
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Inspector API",
        version="1.0.0",
        description="API completa para gestión de inventario de registros de inspección",
        routes=app.routes,
    )
    
    # Personalizaciones adicionales del esquema
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
