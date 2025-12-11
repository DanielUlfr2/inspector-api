import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- PROYECTO ---
    PROJECT_NAME: str = "Inspector API"
    VERSION: str = "1.0.0"          # <--- FALTABA ESTA
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str                 # <--- FALTABA ESTA (Viene del .env)
    
    # --- POSTGRES ---
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # --- REDIS ---
    REDIS_PASSWORD: str
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # --- INTEGRACIONES ---
    # La hacemos opcional (= None) por si en algún entorno no la defines
    KEYCLOAK_SERVER: Optional[str] = None  # <--- FALTABA ESTA

    # --- OPEN BALENA ---
    BALENA_EMAIL: str
    BALENA_PASSWORD: str
    BALENA_URL: str
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        # Esto le dice a Pydantic: "Si encuentras variables extra en el .env que no conozco, IGNÓRALAS en vez de dar error"
        extra = "ignore" 

settings = Settings()