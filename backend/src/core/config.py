import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Inspector API"
    API_V1_STR: str = "/api/v1"
    
    # Postgres (Docker inyectará esto desde backend/.env)
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_PASSWORD: str
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    class Config:
        case_sensitive = True
        # Esto es útil si corres local sin docker, 
        # pero en Docker tomará las vars del sistema primero.
        env_file = ".env" 

settings = Settings()