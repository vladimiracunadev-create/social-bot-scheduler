# 🧩 Caso 12: 🐍 Python (LLM Producer) -> 🌉 n8n -> ⚡ FastAPI + RAG

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Language: Python](https://img.shields.io/badge/Language-Python%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vector DB: pgvector](https://img.shields.io/badge/Vector%20DB-pgvector-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño.

El caso "estrella" de 2026: integración **RAG** (Retrieval-Augmented Generation). Un productor genera embeddings, n8n los rutea a un servicio FastAPI que indexa en `pgvector` y sirve queries semánticas.

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `embed_producer.py` — chunks documentos, llama a un endpoint de embeddings (modelo local con `sentence-transformers` o API externa configurable).
2. **🌉 Puente**: **n8n** — Webhook + transformación + batching.
3. **📥 Destino**: `rag_service.py` (FastAPI) — endpoints `/index` y `/query`.
4. **📁 Persistencia**: **PostgreSQL 16 + pgvector** (alternativa: **Qdrant**).

---

## 🎯 Objetivos didácticos

- Pipeline RAG end-to-end: chunking → embedding → indexing → retrieval.
- Búsqueda por similitud coseno con índice HNSW en `pgvector`.
- Diseño del schema: dimensión del embedding según modelo (384, 768, 1536…).
- Patrón **batch ingestion** vs **streaming ingestion**.
- *Sin* hardcodear API keys de proveedores externos — todo vía `.env`.

---

## ⚠️ Consideraciones de seguridad

- Los embeddings pueden filtrar información sensible si se exponen → endpoint `/query` requiere auth.
- Los modelos locales evitan exfiltración a terceros.
- Validar tamaño máximo de payload para evitar DoS por documentos gigantes.

---

## 📋 TODO de implementación

- [ ] `requirements.txt` con `fastapi`, `pgvector`, `sentence-transformers`, `pydantic`.
- [ ] Migración SQL para extensión `pgvector` y tabla `embeddings`.
- [ ] Workflow n8n `case12-rag.json` con nodo Function para batching.
- [ ] Tests con corpus de prueba reproducible.
- [ ] Dashboard Apache mostrando top-k resultados de queries.
- [ ] Perfil `case12` en `docker-compose.yml`.

---

*Pendiente — parte del roadmap v5.0. Caso de mayor diferenciación competitiva.*
