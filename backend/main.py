# backend/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from databases.postgres_connector import PostgresConnector
from src.core.config import settings
from src.api.v1.api import api_router

# --- EVENTOS DE INICIO/APAGADO ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando Inspector API...")
    await PostgresConnector.init_pool() # Inicia la DB
    yield
    print("🛑 Apagando aplicación...")
    await PostgresConnector.close_pool() # Cierra la DB

# --- AQUÍ ESTÁ LA VARIABLE 'app' QUE BUSCA DOCKER ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Incluimos el router de la API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "API Operativa 🟢"}