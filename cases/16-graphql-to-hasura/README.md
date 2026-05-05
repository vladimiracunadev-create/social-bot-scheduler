# 🧩 Caso 16: 🚀 Apollo Server (GraphQL) -> 🌉 n8n -> 🟦 Hasura -> 📈 TimescaleDB

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Protocol: GraphQL](https://img.shields.io/badge/Protocol-GraphQL-E10098?logo=graphql&logoColor=white)](https://graphql.org/)
[![Engine: Hasura](https://img.shields.io/badge/Engine-Hasura-1EB4D4?logo=hasura&logoColor=white)](https://hasura.io/)
[![Database: TimescaleDB](https://img.shields.io/badge/Database-TimescaleDB-FDB515?logo=timescale&logoColor=black)](https://www.timescale.com/)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño.

Demuestra dos enfoques GraphQL contrastados: **schema-first** (Apollo manual) vs **DB-first** (Hasura auto-generado), con persistencia en una BD optimizada para **series temporales**.

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `server.ts` (Apollo Server v4) — schema GraphQL escrito a mano con resolvers.
2. **🌉 Puente**: **n8n** — recibe mutaciones, normaliza, reenvía a Hasura.
3. **📥 Destino**: **Hasura** — GraphQL API auto-derivada del schema Postgres + permisos por rol.
4. **📁 Persistencia**: **TimescaleDB** (extensión Postgres) — hypertables particionadas por tiempo.

---

## 🎯 Objetivos didácticos

- Schema-first vs DB-first: cuándo conviene cada uno.
- TimescaleDB: hypertables, continuous aggregates, retention policies.
- GraphQL subscriptions sobre WebSocket para dashboards en tiempo real.
- Métricas reales: ingestión de telemetría con downsampling automático.

---

## ⚠️ Consideraciones de seguridad

- Hasura debe ejecutarse con `HASURA_GRAPHQL_ADMIN_SECRET` y RLS.
- Limitar profundidad de queries con `depth-limit` para mitigar DoS.
- Apollo server: rate limiting con `graphql-rate-limit-directive`.

---

## 📋 TODO de implementación

- [ ] Apollo Server con TypeScript y `@apollo/server` v4.
- [ ] Hasura con migraciones SQL versionadas en `dest/hasura/migrations/`.
- [ ] Hypertables TimescaleDB con `chunk_time_interval = 1 day`.
- [ ] Workflow n8n `case16-graphql.json`.
- [ ] Dashboard Grafana con datasource TimescaleDB.
- [ ] Perfil `case16` en `docker-compose.yml`.

---

*Pendiente — parte del backlog exploratorio v5.0+.*
