from pydantic import HttpUrl, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Configuración global de la aplicación gestionada por Pydantic Settings.
    
    Contexto:
        Centraliza todas las variables de entorno y constantes del sistema.
        Utiliza `pydantic-settings` para validar tipos automáticamente al inicio (Fail Fast).

    Atributos:
        WEBHOOK_URL (HttpUrl): URL del endpoint destino (ej: el script PHP).
                               Si es None, el bot funcionará en modo "solo lectura" o "local".
        POSTS_FILE (Path): Ruta al archivo JSON que actúa como base de datos local.
        LOG_LEVEL (str): Nivel de verbosidad del logging (DEBUG, INFO, WARNING, ERROR).
    """

    WEBHOOK_URL: Optional[HttpUrl] = None
    POSTS_FILE: Path = Path("posts.json")
    LOG_LEVEL: str = "INFO"

    # Configuración del modelo Pydantic
    # - env_file: Busca un archivo .env para cargar secretos en desarrollo local.
    # - extra="ignore": Permite que existan variables extra en el environment sin lanzar error.
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"], 
        env_file_encoding="utf-8", 
        extra="ignore"
    )


# Instancia única (Singleton) de configuración para ser importada en otros módulos.
settings = Settings()
