"""
==================================================================================================
RECEPTOR RAG (Case 12: Python LLM -> n8n -> FastAPI + pgvector)
==================================================================================================
Pipeline de Retrieval-Augmented Generation a nivel de infraestructura:

    post -> embedding (vector 256d) -> pgvector -> búsqueda semántica por similitud coseno

Cada post entrante se convierte en un vector y se almacena en PostgreSQL con la extensión
**pgvector**. El endpoint `/search` recupera los posts más parecidos a una consulta (el paso
"retrieval" de RAG), que un LLM usaría luego como contexto.

Embedding: función hashing determinista (bag-of-words -> 256d, L2-normalizada). No requiere
descargar modelos ni claves de API — es un stand-in reproducible; en producción se sustituiría
por `sentence-transformers` o un endpoint de embeddings sin tocar el resto del flujo.
"""

import hashlib
import math
import os
import time

import psycopg2
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

DIM = 256
DB_HOST = os.getenv("DB_HOST", "db-pgvector-12")
DB_NAME = os.getenv("DB_NAME", "social_bot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "change-me")


# ==================================================================================================
# EMBEDDING (hashing determinista)
# ==================================================================================================
def embed(text: str) -> list[float]:
    vec = [0.0] * DIM
    for token in text.lower().split():
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        vec[h % DIM] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def to_pgvector(vec: list[float]) -> str:
    return "[" + ",".join(f"{v:.6f}" for v in vec) + "]"


# ==================================================================================================
# BASE DE DATOS (pgvector)
# ==================================================================================================
def connect():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )


def init_db():
    for attempt in range(30):
        try:
            conn = connect()
            with conn, conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                cur.execute(f"""CREATE TABLE IF NOT EXISTS social_posts (
                            id TEXT PRIMARY KEY,
                            text TEXT NOT NULL,
                            channel TEXT NOT NULL DEFAULT 'default',
                            scheduled_at TEXT,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                            embedding vector({DIM})
                        )""")
            conn.close()
            print("[bootstrap] pgvector listo (extension + tabla social_posts).")
            return
        except Exception as e:  # noqa: BLE001
            print(f"[bootstrap] pgvector no listo (intento {attempt + 1}): {e}")
            time.sleep(2)
    raise RuntimeError("No se pudo inicializar pgvector a tiempo.")


app = FastAPI(title="Social Bot RAG Receiver", version="1.0.0")


@app.on_event("startup")
def _startup():
    init_db()


class Post(BaseModel):
    id: str
    text: str
    channel: str = "default"
    scheduled_at: str | None = None


@app.get("/health")
def health():
    return {"ok": True, "engine": "pgvector"}


@app.post("/webhook")
def webhook(post: Post):
    if not post.id or not post.text:
        return JSONResponse(
            status_code=422,
            content={"ok": False, "error": "id y text son obligatorios"},
        )
    vec = to_pgvector(embed(post.text))
    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO social_posts (id, text, channel, scheduled_at, embedding)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (id) DO UPDATE SET text = EXCLUDED.text, embedding = EXCLUDED.embedding""",
            (post.id, post.text, post.channel, post.scheduled_at, vec),
        )
    conn.close()
    print(f"Post embebido y persistido en pgvector: {post.id}")
    return {
        "ok": True,
        "message": "Post embebido en pgvector",
        "case": "12-python-to-rag",
    }


@app.post("/errors")
async def errors(request: Request):
    data = await request.json()
    print(f"Error en DLQ: {data}")
    return {"ok": True, "message": "Error registrado en DLQ"}


@app.get("/logs")
def logs():
    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, channel, text, created_at FROM social_posts ORDER BY created_at DESC LIMIT 20"
        )
        rows = cur.fetchall()
    conn.close()
    out = [
        f"[{r[3]}] PGVECTOR | id={r[0]} | channel={r[1]} | text={r[2]}" for r in rows
    ]
    return {"ok": True, "logs": out}


@app.get("/search")
def search(q: str, k: int = 5):
    """Retrieval semántico: los posts más cercanos a la consulta (coseno)."""
    vec = to_pgvector(embed(q))
    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, text, 1 - (embedding <=> %s) AS score FROM social_posts "
            "ORDER BY embedding <=> %s LIMIT %s",
            (vec, vec, k),
        )
        rows = cur.fetchall()
    conn.close()
    return {
        "ok": True,
        "query": q,
        "matches": [
            {"id": r[0], "text": r[1], "score": round(float(r[2]), 4)} for r in rows
        ],
    }


@app.get("/", response_class=HTMLResponse)
def dashboard():
    if os.path.exists("index.html"):
        with open("index.html", encoding="utf-8") as f:
            return f.read()
    return "<h1>Dashboard no encontrado</h1>"
