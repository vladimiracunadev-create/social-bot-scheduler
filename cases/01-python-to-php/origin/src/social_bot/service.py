import json
import logging
import sys
from datetime import datetime
from typing import List, Optional

import requests
from .config import settings
from .models import Post

# ==================================================================================================
# CONFIGURACIÓN DE OBSERVABILIDAD
# ==================================================================================================
# Se configura el logging a stdout para que plataformas como Docker o Kubernetes puedan recolectar
# los logs fácilmente.
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class BotService:
    """
    Servicio de Aplicación: Orquestador principal de la lógica de negocio.

    Responsabilidades:
        1. Persistencia: Leer y escribir el estado de los posts (patrón Repository simplificado).
        2. Lógica de Negocio: Filtrar posts vencidos (`due_posts`).
        3. Integración Externa: Comunicarse con el webhook de destino (Gateway).

    Diseño:
        Sigue un flujo lineal: Load -> Filter -> Process -> Save.
        Diseñado para ser ejecutado periódicamente (cron job) o como un worker de ciclo largo.
    """

    def __init__(self):
        self.posts_path = settings.POSTS_FILE
        # Convertimos a string para requests, manejando el caso de None
        self.webhook_url = str(settings.WEBHOOK_URL) if settings.WEBHOOK_URL else None

    def load_posts(self) -> List[Post]:
        """
        Carga la 'base de datos' de posts desde el sistema de archivos.

        Mecanismo de Tolerancia a Fallos:
        Si el archivo no existe o está corrupto, loguea el error y retorna una lista vacía
        para permitir que el servicio siga corriendo (Graceful Degradation), aunque sin procesar nada.
        """
        if not self.posts_path.exists():
            logger.error(f"Archivo no encontrado: {self.posts_path}")
            return []

        try:
            # Lectura atómica (read_text lee todo en memoria) y parseo JSON
            data = json.loads(self.posts_path.read_text(encoding="utf-8"))
            # Validación de esquema con Pydantic para cada item
            return [Post(**item) for item in data]
        except Exception as e:
            logger.error(f"Error cargando posts: {e}")
            return []

    def save_posts(self, posts: List[Post]) -> None:
        """
        Persiste el estado actualizado de los posts.

        Contexto:
        Se llama solo si hubo cambios (`published=True`). Esto minimiza escrituras en disco.
        """
        try:
            # Serialización a dicts puros
            data = [post.model_dump(mode="json") for post in posts]
            # Escritura con indentación para mantener el archivo legible por humanos
            self.posts_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            logger.info("Base de datos de posts actualizada.")
        except Exception as e:
            logger.error(f"Error guardando posts: {e}")

    def send_post(self, post: Post) -> bool:
        """
        Envía un post al sistema destino vía HTTP POST.

        Manejo de Errores:
        - Si no hay URL configurada, simula el envío (Modo Dry-Run implícito).
        - Captura excepciones de red y codigos HTTP 4xx/5xx (`raise_for_status`).
        - Retorna booleano para indicar éxito/fracaso, permitiendo al caller decidir si actualizar el estado.

        Args:
            post (Post): Instancia del post a enviar.

        Returns:
            bool: True si el envío fue exitoso o simulado, False si falló.
        """
        if not self.webhook_url:
            logger.info(f"[DRY-RUN] Post {post.id} -> {post.channels}")
            return True

        try:
            payload = post.model_dump(mode="json")
            # Timeout explícito de 10s para evitar colgar el proceso indefinidamente
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            resp.raise_for_status()  # Lanza error si status != 200

            logger.info(f"[OK] Post {post.id} enviado exitosamente.")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Fallo al enviar {post.id}: {e}")
            return False

    def run(self):
        """
        Método principal de ejecución (Entry Point del Servicio).

        Flujo:
            1. Cargar estado.
            2. Identificar trabajo pendiente (`should_publish`).
            3. Si no hay trabajo, salir temprano (Early Exit).
            4. Procesar secuencialmente los posts pendientes.
            5. Si hubo cambios exitosos, persistir el nuevo estado.
        """
        logger.info("Iniciando Social Bot Service...")
        all_posts = self.load_posts()
        now = datetime.now()

        # Filtering: Seleccionar candidatos
        due_posts = [p for p in all_posts if p.should_publish(now)]

        if not due_posts:
            logger.info("No hay posts pendientes.")
            return

        logger.info(f"Procesando {len(due_posts)} posts...")

        status_changed = False
        for post in due_posts:
            # Processing: Intentar enviar
            if self.send_post(post):
                # State Mutation: Solo si el envío fue exitoso
                post.published = True
                status_changed = True

        # Persistence: Guardar cambios en lote
        if status_changed:
            self.save_posts(all_posts)

        logger.info("Ciclo de ejecución completado.")
