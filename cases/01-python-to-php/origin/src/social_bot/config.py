from pydantic import HttpUrl, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Configuración global de la aplicación gestionada por Pydantic Settings.
    Valida las variables de entorno automáticamente.
    """

    WEBHOOK_URL: Optional[HttpUrl] = None
    POSTS_FILE: Path = Path("posts.json")
    LOG_LEVEL: str = "INFO"

    # Configuración para cargar desde .env
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
