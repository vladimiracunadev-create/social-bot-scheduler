import json
import os
import logging
from datetime import datetime
import sys
from pathlib import Path
from typing import List, Optional

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

# Configuración de Logging profesional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Carga variables de entorno
load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
POSTS_FILE = Path("posts.json")


class Post(BaseModel):
    id: str
    text: str
    channels: List[str] = []
    scheduled_at: datetime
    published: bool = False  # Nuevo campo para gestión de estado


def load_posts() -> List[Post]:
    if not POSTS_FILE.exists():
        logger.error(f"No se encontró el archivo: {POSTS_FILE}")
        return []

    try:
        content = POSTS_FILE.read_text(encoding="utf-8")
        data = json.loads(content)
        posts = [Post(**item) for item in data]
        return posts
    except ValidationError as e:
        logger.error(f"Error de validación en JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error al cargar posts: {e}")
        return []


def save_posts(posts: List[Post]):
    try:
        data = [post.model_dump() for post in posts]
        # Convertimos datetime a string ISO para el JSON
        for item in data:
            if isinstance(item["scheduled_at"], datetime):
                item["scheduled_at"] = item["scheduled_at"].isoformat()

        POSTS_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info("Estado de posts actualizado en el archivo.")
    except Exception as e:
        logger.error(f"Error al guardar posts: {e}")


def get_due_posts(posts: List[Post], now: Optional[datetime] = None) -> List[Post]:
    if now is None:
        now = datetime.now()
    # Solo posts no publicados cuya fecha ya pasó
    return [p for p in posts if not p.published and p.scheduled_at <= now]


def send_to_webhook(post: Post) -> bool:
    if not WEBHOOK_URL:
        logger.info(
            f"[DRY-RUN] Publicaría {post.id} en {post.channels}: {post.text[:30]}..."
        )
        return True

    payload = post.model_dump()
    payload["scheduled_at"] = post.scheduled_at.isoformat()

    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info(f"[OK] Enviado {post.id} a n8n. Status: {resp.status_code}")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Fallo al enviar {post.id} al webhook: {e}")
        return False


def main():
    logger.info("Iniciando Social Bot Scheduler...")
    all_posts = load_posts()

    if not all_posts:
        logger.warning("No se cargaron posts o el archivo está vacío.")
        return

    due_posts = get_due_posts(all_posts)

    if not due_posts:
        logger.info("No hay posts pendientes para publicar.")
        return

    logger.info(f"Encontrados {len(due_posts)} posts pendientes.")

    changes_made = False
    for post in due_posts:
        success = send_to_webhook(post)
        if success:
            post.published = True
            changes_made = True

    if changes_made:
        save_posts(all_posts)

    logger.info("Proceso finalizado.")


if __name__ == "__main__":
    main()
