from pydantic import HttpUrl, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Configuración global de la aplicación (Caso 02).
    
    Contexto:
        Define parámetros operativos críticos. 
        En este caso, la carga de .env es más estricta (solo busca ".env" local).

    Atributos:
        WEBHOOK_URL (HttpUrl): Endpoint del receptor en Go.
        POSTS_FILE (Path): Base de datos JSON.
        LOG_LEVEL (str): Nivel de detalle del log.
    """

    WEBHOOK_URL: Optional[HttpUrl] = None
    POSTS_FILE: Path = Path("posts.json")
    LOG_LEVEL: str = "INFO"

    # Configuración pydantic-settings
    model_config = SettingsConfigDict(
        env_file=".env",            # Solo busca .env en el CWD
        env_file_encoding="utf-8", 
        extra="ignore"
    )


settings = Settings()
