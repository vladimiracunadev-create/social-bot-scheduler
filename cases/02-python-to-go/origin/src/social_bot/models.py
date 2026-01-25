from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Post(BaseModel):
    """
    Representa una publicación programada en el sistema.
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
        Determina si el post debe ser publicado en el momento dado.
        """
        return not self.published and self.scheduled_at <= now
