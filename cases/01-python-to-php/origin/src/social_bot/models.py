from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Post(BaseModel):
    """
    Modelo de Dominio que representa una publicación social.

    Contexto:
        Define la estructura de datos para los posts almacenados en `posts.json` y
        los payloads enviados al webhook. Utiliza Pydantic para garantizar la integridad de los datos.

    Atributos:
        id (str): UUID o identificador único del post.
        text (str): El contenido del mensaje a publicar.
        channels (List[str]): Plataformas destino (ej: ["twitter", "linkedin"]).
        scheduled_at (datetime): Timestamp ISO-8601 de cuándo debe publicarse.
        published (bool): Flag de estado. True si ya fue enviado exitosamente.
    """

    id: str = Field(..., description="Identificador único del post")
    text: str = Field(..., description="Contenido textual del post")
    channels: List[str] = Field(
        default_factory=list, description="Lista de canales de destino"
    )
    scheduled_at: datetime = Field(
        ..., description="Fecha y hora programada para la publicación"
    )
    published: bool = Field(default=False, description="Estado de publicación")

    def should_publish(self, now: datetime) -> bool:
        """
        Lógica de Dominio: Determina si el post es elegible para publicación inmediata.

        Criterios:
            1. No debe haber sido publicado previamente (`not self.published`).
            2. Su fecha programada debe ser menor o igual al momento actual (`now`).

        Args:
            now (datetime): Fecha/hora actual de referencia.

        Returns:
            bool: True si debe ser procesado, False en caso contrario.
        """
        return not self.published and self.scheduled_at <= now
