"""
==================================================================================================
EMISOR PYTHON (Case 12: Python (LLM) -> n8n -> FastAPI RAG + pgvector)
==================================================================================================
Publica los posts programados hacia n8n. Representa el lado "productor de conocimiento" del
pipeline RAG: cada post es un documento que el receptor embeberá e indexará en pgvector para
recuperación semántica posterior. Sin dependencias externas: HTTP vía urllib (stdlib).

Modo dry-run si WEBHOOK_URL no está definido.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

POSTS_FILE = Path(__file__).with_name("posts.json")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")


def send(post: dict) -> bool:
    if not WEBHOOK_URL:
        print(f"[DRY-RUN] Post {post['id']} reenviado.")
        return True
    payload = json.dumps(
        {
            "id": post["id"],
            "text": post["text"],
            "channel": post.get("channel", "default"),
            "scheduled_at": post.get("scheduled_at", ""),
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if 200 <= resp.status < 300:
                print(f"[OK] Post {post['id']} aceptado por n8n ({resp.status}).")
                return True
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] Fallo reenviando {post['id']}: {e}")
    return False


def main():
    posts = json.loads(POSTS_FILE.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    changed = False
    for post in posts:
        if post.get("published"):
            continue
        scheduled = post.get("scheduled_at")
        due = True
        if scheduled:
            try:
                due = datetime.fromisoformat(scheduled.replace("Z", "+00:00")) <= now
            except ValueError:
                due = True
        if due and send(post):
            post["published"] = True
            changed = True
    if changed:
        POSTS_FILE.write_text(
            json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
