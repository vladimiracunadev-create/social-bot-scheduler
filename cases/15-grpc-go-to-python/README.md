# 🧩 Caso 15: 🐹 Go (gRPC server) -> 🌉 n8n -> 🐍 Python (gRPC client)

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Protocol: gRPC](https://img.shields.io/badge/Protocol-gRPC-244c5a?logo=grpc&logoColor=white)](https://grpc.io/)
[![Database: CockroachDB](https://img.shields.io/badge/Database-CockroachDB-6933FF?logo=cockroachlabs&logoColor=white)](https://www.cockroachlabs.com/)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño.

Primer caso de la matriz que abandona JSON/HTTP por **protocolo binario** (`gRPC` + Protobuf) y persistencia en una **base SQL distribuida** (CockroachDB, compatible con Postgres wire protocol).

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `server.go` — servidor gRPC con streaming bidireccional.
2. **🌉 Puente**: **n8n** — transcodificación gRPC↔HTTP vía nodo HTTP Request + envoy/grpc-web sidecar.
3. **📥 Destino**: `client.py` (FastAPI con `grpcio`) — cliente gRPC que persiste en CockroachDB.
4. **📁 Persistencia**: **CockroachDB** (multi-region, serializable isolation).

---

## 🎯 Objetivos didácticos

- Definir contratos con `.proto` y generar stubs en Go y Python.
- Demostrar los 4 modos de gRPC: unary, server-streaming, client-streaming, bidi.
- CockroachDB: SQL distribuido con consenso Raft, sin single point of failure.
- Limitaciones: n8n no habla gRPC nativo → se requiere proxy o adaptación.

---

## ⚠️ Consideraciones operacionales

- Generación de stubs debe automatizarse (Makefile o `buf`).
- TLS obligatorio para gRPC en producción; en local usar plaintext con flag explícito.
- CockroachDB requiere ≥3 nodos para HA real (en lab usar single-node `--insecure`).

---

## 📋 TODO de implementación

- [ ] `proto/messages.proto` con servicio + mensajes versionados.
- [ ] `Makefile` con `protoc` para Go y Python.
- [ ] Sidecar `envoy` o `grpcurl` para integración con n8n.
- [ ] Schema CockroachDB con índices secundarios.
- [ ] Workflow n8n `case15-grpc.json`.
- [ ] Perfil `case15` en `docker-compose.yml`.

---

*Pendiente — parte del backlog exploratorio v5.0+.*
