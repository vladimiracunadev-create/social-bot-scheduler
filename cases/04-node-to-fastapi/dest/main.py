"""
==================================================================================================
RECEPTOR ASGI DE ALTA VELOCIDAD (Case 04: Node.js -> n8n -> FastAPI + SQLite)
==================================================================================================
¿Por qué FastAPI para este rol?
FastAPI es uno de los frameworks más rápidos para Python gracias al uso de ASGI (Asynchronous 
Server Gateway Interface) y Tipado Estático vía Pydantic. En este caso, aprovechamos la 
validación automática de esquemas: si el bot de Node.js envía datos mal formados, FastAPI 
devuelve un error 422 sin que el desarrollador escriba una sola línea de validación manual.

Persistencia en SQLite:
SQLite es la elección ideal para este microservicio por su naturaleza "Zero-Config". 
Almacena los datos en un solo archivo local (.db), eliminando la necesidad de un servidor 
de base de datos externo y simplificando drásticamente el despliegue en contenedores.

Patrones aplicados:
- DTO (Data Transfer Object): Pydantic valida y transforma el JSON entrante.
- INSERT OR REPLACE: Garantía de Idempotencia a nivel de base de datos.
- ASGI: Rendimiento superior al WSGI tradicional (Django/Flask).
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os
import sqlite3

# ==================================================================================================
# CONFIGURACIÓN DE BASE DE DATOS (SQLite)
# ==================================================================================================
DB_FILE = "social_bot.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS social_posts
                 (id TEXT PRIMARY KEY, text TEXT, channel TEXT, scheduled_at TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    )
    conn.commit()
    conn.close()


init_db()

# ==================================================================================================
# CONFIGURACIÓN APP FASTAPI
# ==================================================================================================
app = FastAPI(
    title="Social Bot Receiver - FastAPI",
    description="Microservicio receptor de posts migrado a Python asíncrono.",
    version="1.0.0",
)

LOG_FILE = "social_bot_fastapi.log"


# ==================================================================================================
# MODELOS DE DATOS (DTOs)
# ==================================================================================================
class Post(BaseModel):
    """
    Data Transfer Object (DTO) para la validación automática del payload JSON.
    FastAPI usa Pydantic para validar tipos y requerimientos (id y text obligatorios).
    """

    id: str
    text: str
    channel: str = "default"  # Valor por defecto si no se envía
    scheduled_at: str = None  # Opcional


# ==================================================================================================
# ENDPOINTS
# ==================================================================================================


@app.post("/webhook")
async def receive_post(post: Post):
    """
    Webhook Principal: Recibe y procesa los posts entrantes.

    Flujo:
        1. FastAPI valida el JSON contra el esquema `Post`. Si falla, retorna 422 automáticamente.
        2. Se construye la línea de log.
        3. Se escribe en disco (simulando persistencia DB).
        4. Retorna confirmación JSON.
    """
    log_line = f"[{datetime.now().isoformat()}] FASTAPI-RECEIVER | id={post.id} | channel={post.channel} | text={post.text}\n"

    # Escritura de archivo
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

    # Persistencia en SQLite
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO social_posts (id, text, channel, scheduled_at) VALUES (?, ?, ?, ?)",
            (post.id, post.text, post.channel, post.scheduled_at),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error guardando en SQLite: {e}")

    print(f"Post recibido en FastAPI: {post.id}")
    return {
        "ok": True,
        "message": "Post recibido por FastAPI",
        "case": "04-node-to-fastapi",
    }


@app.get("/logs")
async def get_logs():
    """
    API de Consulta: Retorna los logs almacenados para el Dashboard.
    """
    if not os.path.exists(LOG_FILE):
        return {"ok": True, "logs": []}

    # Lectura completa en memoria. Cuidado con logs de gran tamaño.
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = f.readlines()

    return {"ok": True, "logs": [line.strip() for line in logs]}


@app.post("/errors")
async def receive_error(request: Request):
    """
    Dead Letter Queue (DLQ): Endpoint genérico para reportar fallos.
    Recibe un JSON arbitrario (sin validación estricta de esquema Pydantic) usando `Request`.
    """
    error_data = await request.json()
    ERROR_LOG_FILE = "errors.log"

    log_line = f"[{datetime.now().isoformat()}] CASE={error_data.get('case', 'unknown')} | ERROR={error_data.get('error', 'no error info')} | PAYLOAD={error_data.get('payload', 'no payload')}\n"

    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)

    print(f"Error logged to DLQ: {error_data.get('case')}")
    return {"ok": True, "message": "Error logged to DLQ"}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """
    Sirve el archivo estático HTML del Dashboard.
    """
    # En producción, esto se serviría vía Nginx o CDN, no desde la API.
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Dashboard no encontrado</h1>"


if __name__ == "__main__":
    # Inicia el servidor ASGI Uvicorn
    # host="0.0.0.0" permite acceso desde fuera del contenedor/máquina local.
    uvicorn.run(app, host="0.0.0.0", port=8000)
