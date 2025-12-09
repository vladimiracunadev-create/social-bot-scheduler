import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# Carga variables de entorno desde .env
load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Si no está, trabajamos en modo "dry-run"
POSTS_FILE = Path("posts.json")


@dataclass
class Post:
    id: str
    text: str
    channels: list
    scheduled_at: datetime


def load_posts():
    if not POSTS_FILE.exists():
        raise FileNotFoundError(f"No se encontró {POSTS_FILE}")

    data = json.loads(POSTS_FILE.read_text(encoding="utf-8"))
    posts = []
    for item in data:
        posts.append(
            Post(
                id=item["id"],
                text=item["text"],
                channels=item.get("channels", []),
                scheduled_at=datetime.fromisoformat(item["scheduled_at"]),
            )
        )
    return posts


def get_due_posts(posts, now=None):
    if now is None:
        now = datetime.now()
    # Aquí podrías marcar un margen (ej: ±5 minutos) si lo quieres más flexible
    return [p for p in posts if p.scheduled_at <= now]


def send_to_webhook(post: Post):
    if not WEBHOOK_URL:
        # Modo prueba: no pegamos a n8n, solo mostramos
        print(f"[DRY-RUN] Publicaría {post.id} en {post.channels}:")
        print(f"  {post.text}\n")
        return

    payload = {
        "id": post.id,
        "text": post.text,
        "channels": post.channels,
        "scheduled_at": post.scheduled_at.isoformat(),
    }

    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        print(f"[OK] Enviado {post.id} a n8n. Status: {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Fallo al enviar {post.id} al webhook: {e}")


def main():
    posts = load_posts()
    due = get_due_posts(posts)

    if not due:
        print("No hay posts pendientes para publicar.")
        return

    print(f"Encontrados {len(due)} posts pendientes, enviando...")
    for post in due:
        send_to_webhook(post)


if __name__ == "__main__":
    main()
