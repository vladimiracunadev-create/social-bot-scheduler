# 🧩 Caso 15: 🐹 Go (gRPC server) → 🌉 n8n → 🐍 Python (gRPC client) + CockroachDB

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Language: Go](https://img.shields.io/badge/Language-Go-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Protocol: gRPC](https://img.shields.io/badge/Protocol-gRPC-6933FF?logo=grpc&logoColor=white)](https://grpc.io/)
[![Database: CockroachDB](https://img.shields.io/badge/Database-CockroachDB-6933FF?logo=cockroachlabs&logoColor=white)](https://www.cockroachlabs.com/)

Protocolo binario **gRPC** entre un **servidor Go** y un **cliente Python**, con persistencia en **CockroachDB** (SQL distribuido con consenso Raft, wire-compatible con PostgreSQL). El contrato se define en un `.proto` compartido y se compilan stubs para ambos lenguajes.

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/server.go`: **servidor gRPC** en Go que implementa `SocialService` (`Publish`, `ListRecent`) y persiste en CockroachDB.
2. **🌉 Puente** — **n8n**: guardrails canónicos; entrega vía HTTP al receiver Python.
3. **📥 Destino** — `dest/main.py`: **cliente gRPC** (FastAPI + `grpcio`) que traduce el contrato REST del laboratorio (`/webhook`, `/logs`) a llamadas gRPC unary contra el servidor Go.
4. **📁 Persistencia** — **CockroachDB 24**: tabla `social_posts` con `INSERT ... ON CONFLICT`.

> [!NOTE]
> n8n no habla gRPC nativo; por eso el receiver Python actúa de **adaptador REST↔gRPC**. Los stubs (`social.pb.go`, `social_pb2.py`) se generan **en el build** desde `proto/social.proto` con `protoc` / `grpc_tools`.

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case15 up -d      # CockroachDB + servidor Go + receiver Python
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `cockroach-15` | CockroachDB (single-node) | interno |
| `grpc-server-15` | Servidor gRPC Go | interno (`:50051`) |
| `dest-grpc-15` | Cliente gRPC + receiver REST + dashboard | **8095** |

- **Dashboard del caso**: <http://localhost:8095>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-15**.

---

## 🎯 Objetivos didácticos

- **Contratos `.proto`** y generación de stubs en **dos lenguajes** (Go y Python).
- **gRPC unary** sobre HTTP/2 (binario, tipado) frente al REST/JSON del resto del laboratorio.
- **CockroachDB**: SQL distribuido, serializable, sin single point of failure.

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Puerto `8095` = `8080 + 15` (regla canónica, ver [docs/PORTS.md](../../docs/PORTS.md)).
- CockroachDB en modo `--insecure` (local-only); el receiver valida `id`/`text` (→ HTTP 422).

---

## ✅ Estado

Implementado y verificado (build + boot + health). Parte del **Lote 3** del roadmap v5.0 → v4.7.
