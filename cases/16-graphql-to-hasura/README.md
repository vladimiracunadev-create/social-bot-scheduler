# 🧩 Caso 16: 🚀 Apollo GraphQL → 🌉 n8n → 🟦 Hasura → 📈 TimescaleDB

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Protocol: GraphQL](https://img.shields.io/badge/Protocol-GraphQL-E10098?logo=graphql&logoColor=white)](https://graphql.org/)
[![Engine: Hasura](https://img.shields.io/badge/Engine-Hasura-1EB4D4?logo=hasura&logoColor=white)](https://hasura.io/)
[![Database: TimescaleDB](https://img.shields.io/badge/Database-TimescaleDB-FDB515?logo=timescale&logoColor=black)](https://www.timescale.com/)

Demuestra dos enfoques **GraphQL contrastados** en un mismo flujo: **schema-first** (Apollo Server, resolvers escritos a mano) en el origen vs **DB-first** (Hasura auto-genera el API GraphQL desde el esquema Postgres) en el destino, con persistencia en **TimescaleDB** (hypertables particionadas por tiempo).

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/index.js`: **Apollo Server 4** expone la cola de posts como GraphQL tipado (`scheduledPosts`, `duePosts`) y un daemon de polling reenvía los posts vencidos al webhook de n8n.
2. **🌉 Puente** — **n8n**: aplica los guardrails del laboratorio (fingerprint → circuit breaker → idempotencia → HTTP con reintentos → DLQ) y entrega el post al receiver.
3. **📥 Destino** — `dest/receiver/index.js`: micro-receiver Node que traduce el contrato REST (`/webhook`, `/errors`, `/logs`) a **mutaciones y queries GraphQL contra Hasura**. Al arrancar, trackea la tabla vía Metadata API (idempotente).
4. **📁 Persistencia** — **TimescaleDB**: la tabla `social_posts` es una **hypertable** particionada por `created_at`.

> [!NOTE]
> El receiver delgado existe para mantener el **contrato REST homogéneo** que comparten los 20 casos (mismos guardrails, mismo dashboard maestro). La persistencia y las consultas son **GraphQL real contra Hasura**, no una simulación.

---

## 🚀 Cómo levantarlo

```bash
# Núcleo (n8n + dashboard) ya corriendo con: docker-compose up -d
docker-compose --profile case16 up -d
```

Servicios que arranca el perfil `case16`:

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `db-timescaledb-16` | TimescaleDB (hypertable) | interno |
| `hasura-16` | Hasura GraphQL Engine | interno |
| `dest-graphql-16` | Micro-receiver REST↔GraphQL + dashboard | **8096** |

- **Dashboard del caso**: <http://localhost:8096>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-16** → *Probar Integración*.

### Probar el emisor Apollo (opcional)

```bash
cd cases/16-graphql-to-hasura/origin
npm install
WEBHOOK_URL=http://localhost:5678/webhook/social-bot-scheduler-graphql npm start
# Playground GraphQL del emisor en http://localhost:4016
```

---

## 🎯 Objetivos didácticos

- **Schema-first vs DB-first**: escribir resolvers a mano (Apollo) vs derivarlos del esquema (Hasura).
- **TimescaleDB**: hypertables y particionado transparente por tiempo.
- **Puente REST↔GraphQL**: cómo integrar un motor GraphQL en un pipeline con contrato REST homogéneo.

---

## ⚠️ Consideraciones de seguridad (modelo del laboratorio)

- Hasura arranca con `HASURA_GRAPHQL_ADMIN_SECRET` y **consola deshabilitada** por defecto (`HASURA_GRAPHQL_ENABLE_CONSOLE=false`).
- Todos los puertos quedan bindeados a `127.0.0.1` (aislamiento runtime).
- El receiver valida el payload (`id` y `text` obligatorios → HTTP 422) como defensa en profundidad sobre los guardrails de n8n.

---

## ✅ Estado

Implementado y verificado (build + boot + health). Parte del **Lote 1** del roadmap v5.0 → v4.5.
