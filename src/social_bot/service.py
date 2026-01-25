import json
import logging
import sys
from datetime import datetime
from typing import List, Optional

import requests
from .config import settings
from .models import Post

# Configuración de Logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class BotService:
    """
    Servicio principal que coordina la carga, envío y actualización de posts.
    """
    
    def __init__(self):
        self.posts_path = settings.POSTS_FILE
        self.webhook_url = str(settings.WEBHOOK_URL) if settings.WEBHOOK_URL else None

    def load_posts(self) -> List[Post]:
        """Carga y valida los posts desde el archivo JSON."""
        if not self.posts_path.exists():
            logger.error(f"Archivo no encontrado: {self.posts_path}")
            return []

        try:
            data = json.loads(self.posts_path.read_text(encoding="utf-8"))
            return [Post(**item) for item in data]
        except Exception as e:
            logger.error(f"Error cargando posts: {e}")
            return []

    def save_posts(self, posts: List[Post]) -> None:
        """Guarda el estado actual de los posts en el disco."""
        try:
            data = [post.model_dump(mode="json") for post in posts]
            self.posts_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), 
                encoding="utf-8"
            )
            logger.info("Base de datos de posts actualizada.")
        except Exception as e:
            logger.error(f"Error guardando posts: {e}")

    def send_post(self, post: Post) -> bool:
        """Envía un post individual al webhook configurado."""
        if not self.webhook_url:
            logger.info(f"[DRY-RUN] Post {post.id} -> {post.channels}")
            return True

        try:
            payload = post.model_dump(mode="json")
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info(f"[OK] Post {post.id} enviado exitosamente.")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Fallo al enviar {post.id}: {e}")
            return False

    def run(self):
        """Ejecuta el ciclo principal del bot."""
        logger.info("Iniciando Social Bot Service...")
        all_posts = self.load_posts()
        now = datetime.now()
        
        due_posts = [p for p in all_posts if p.should_publish(now)]
        
        if not due_posts:
            logger.info("No hay posts pendientes.")
            return

        logger.info(f"Procesando {len(due_posts)} posts...")
        
        status_changed = False
        for post in due_posts:
            if self.send_post(post):
                post.published = True
                status_changed = True

        if status_changed:
            self.save_posts(all_posts)
        
        logger.info("Ciclo de ejecución completado.")
