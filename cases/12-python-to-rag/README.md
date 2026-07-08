# 🧩 Caso 12: 🧠 Python (LLM) → 🌉 n8n → ⚡ FastAPI RAG + pgvector

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Language: Python](https://img.shields.io/badge/Language-Python%203.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Pattern: RAG](https://img.shields.io/badge/Pattern-RAG-10a37f)](https://www.pinecone.io/learn/retrieval-augmented-generation/)
[![Database: pgvector](https://img.shields.io/badge/Database-pgvector-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)

Pipeline **RAG (Retrieval-Augmented Generation)** a nivel de infraestructura: cada post se convierte en un **embedding** y se indexa en **pgvector**; el endpoint `/search` recupera los posts más parecidos a una consulta por **similitud coseno** — el paso *retrieval* que alimentaría a un LLM.

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/bot.py`: emisor Python (stdlib `urllib`) que reenvía los posts vencidos a n8n.
2. **🌉 Puente** — **n8n**: guardrails canónicos (fingerprint → circuit breaker → idempotencia → HTTP con reintentos → DLQ).
3. **📥 Destino** — `dest/main.py`: **FastAPI** que embebe el texto (vector 256d) y lo persiste en pgvector con `INSERT ... ON CONFLICT`.
4. **📁 Persistencia** — **pgvector** (PostgreSQL 16 + extensión `vector`): búsqueda por operador coseno `<=>`.

> [!NOTE]
> El embedding es una **función hashing determinista** (bag-of-words → 256d, L2-normalizada): sin descargar modelos ni claves de API. Es un stand-in reproducible; se sustituye por `sentence-transformers` o un endpoint de embeddings **sin tocar el resto del flujo**.

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case12 up -d      # pgvector + receptor FastAPI
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `db-pgvector-12` | PostgreSQL 16 + pgvector | interno |
| `dest-rag-12` | FastAPI RAG + dashboard | **8092** |

- **Dashboard del caso** (con búsqueda semántica): <http://localhost:8092>
- **Retrieval directo**: `curl "http://localhost:8092/search?q=embeddings"`
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-12**.

---

## 🎯 Objetivos didácticos

- **RAG end-to-end**: embed → index → retrieve por similitud coseno.
- **pgvector**: columnas `vector(N)` y el operador de distancia `<=>` en SQL.
- **Desacople del modelo**: la función de embedding es un punto de extensión aislado.

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Puerto `8092` = `8080 + 12` (regla canónica, ver [docs/PORTS.md](../../docs/PORTS.md)).
- Bind a `127.0.0.1`; el receptor valida `id`/`text` (→ HTTP 422).

---

## ✅ Estado

Implementado y verificado (build + boot + health + retrieval). Parte del **Lote 2** del roadmap v5.0 → v4.6.
