from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Post(BaseModel):
    """
    Modelo de Dominio: Publicación Social.
    
    Responsabilidad:
        Estandarizar la estructura de datos entre el origen (Python) y el destino (Go).
        Go es estáticamente tipado, por lo que este modelo debe coincidir exactamente
        con el `struct Post` definido en `main.go`.

    Atributos:
        id (str): UUID.
        text (str): Mensaje.
        channels (List[str]): Destinos.
        scheduled_at (datetime): Fecha de publicación.
        published (bool): Estado de sincronización.
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
        Regla de Negocio: Validación de Vencimiento.
        Retorna True si la fecha actual supera la programada y no ha sido publicado.
        """
        return not self.published and self.scheduled_at <= now
