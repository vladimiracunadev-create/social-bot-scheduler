"""
==================================================================================================
CLIENTE gRPC + RECEIVER REST (Case 15: Go gRPC -> n8n -> Python gRPC client -> CockroachDB)
==================================================================================================
El puente n8n habla el contrato REST homogéneo del laboratorio (/webhook, /errors, /logs). Este
servicio Python lo traduce a **gRPC**: en cada request abre un canal al servidor Go (SocialService)
y llama `Publish`/`ListRecent`. La persistencia real vive en CockroachDB, detrás del servidor Go.

Los stubs `social_pb2` / `social_pb2_grpc` se generan en el build desde `social.proto`.
"""

import os

import grpc
import social_pb2
import social_pb2_grpc
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

GRPC_TARGET = os.getenv("GRPC_TARGET", "grpc-server-15:50051")

app = FastAPI(title="Social Bot gRPC Receiver", version="1.0.0")

# Canal gRPC perezoso (conecta en la primera llamada, reintenta solo).
_channel = grpc.insecure_channel(GRPC_TARGET)
_stub = social_pb2_grpc.SocialServiceStub(_channel)


class Post(BaseModel):
    id: str
    text: str
    channel: str = "default"
    scheduled_at: str | None = None


@app.get("/health")
def health():
    return {"ok": True, "engine": "cockroachdb"}


@app.post("/webhook")
def webhook(post: Post):
    if not post.id or not post.text:
        return JSONResponse(
            status_code=422,
            content={"ok": False, "error": "id y text son obligatorios"},
        )
    ack = _stub.Publish(
        social_pb2.Post(
            id=post.id,
            text=post.text,
            channel=post.channel,
            scheduled_at=post.scheduled_at or "",
        ),
        timeout=10,
    )
    return {"ok": ack.ok, "message": ack.message, "case": "15-grpc-go-to-python"}


@app.post("/errors")
async def errors(request: Request):
    data = await request.json()
    print(f"Error en DLQ: {data}")
    return {"ok": True, "message": "Error registrado en DLQ"}


@app.get("/logs")
def logs():
    resp = _stub.ListRecent(social_pb2.Empty(), timeout=10)
    return {"ok": True, "logs": [line.line for line in resp.logs]}


@app.get("/", response_class=HTMLResponse)
def dashboard():
    if os.path.exists("index.html"):
        with open("index.html", encoding="utf-8") as f:
            return f.read()
    return "<h1>Dashboard no encontrado</h1>"
