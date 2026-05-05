# 🚧 Casos Planificados (v5.0+)

> [!IMPORTANT]
> Este documento es el **single source of truth** para los 11 casos planificados (IDs 10–20). Únicamente contienen scaffolding (carpeta + README + manifest); **no hay implementación funcional todavía**. Cualquier referencia en otros documentos debe enlazar aquí.

Los casos 01–09 están plenamente operativos — ver [CASES_INDEX.md](CASES_INDEX.md). Los casos descritos abajo están reservados como **roadmap arquitectónico** y **no se levantan** desde `docker-compose.yml` (no hay perfiles `case10`–`case20` aún).

---

## 📋 Matriz de Casos Planificados

| ID | 📤 Origen | 🌉 Puente | 📥 Destino | 📁 Persistencia | Puerto | Δ Caso (est.) | Total con núcleo (est.) | Categoría |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **10** | Java (Spring Boot) | n8n | Kotlin (Ktor) | 🐘 PostgreSQL | `8090` | ~1.0 GB | ~2.15 GB 🟡 | JVM |
| **11** | Elixir (Phoenix) | n8n | Erlang (Cowboy) | 🟣 Mnesia (embebida) | `8091` | ~384 MB | ~1.5 GB 🟢 | BEAM |
| **12** | Python (LLM) | n8n | FastAPI + RAG | 🧠 pgvector | `8092` | ~1.5 GB | ~2.65 GB 🟡 | IA / RAG |
| **13** | Node + Kafka | n8n | Go consumer | 🟡 ClickHouse | `8093` | ~2.2 GB | ~3.35 GB 🔴 | Streaming |
| **14** | Next.js 15 | n8n | Supabase Edge Fn | 🟢 Supabase (Postgres + RLS) | `8094` | ~2.25 GB | ~3.4 GB 🔴 | BaaS |
| **15** | Go (gRPC) | n8n | Python (gRPC) | 🪳 CockroachDB | `8095` | ~832 MB | ~2.0 GB 🟡 | Protobuf |
| **16** | Apollo (GraphQL) | n8n | Hasura | 📈 TimescaleDB | `8096` | ~768 MB | ~1.9 GB 🟢 | GraphQL |
| **17** | Rust (MQTT) | n8n | Node (MQTT) | 📊 InfluxDB | `8097` | ~736 MB | ~1.85 GB 🟢 | IoT |
| **18** | Zig | n8n | Crystal (Kemal) | 🕸️ Neo4j | `8098` | ~608 MB | ~1.75 GB 🟢 | Grafos |
| **19** | F# (.NET) | n8n | Clojure (Ring) | ⏳ XTDB | `8099` | ~1.5 GB | ~2.65 GB 🟡 | Funcional |
| **20** | Swift (Vapor) | n8n | Dart (Shelf) | 🔥 Firebase Emulator | `8100` | ~1.4 GB | ~2.55 GB 🟡 | Mobile-backend |

> [!IMPORTANT]
> Las cifras son **estimaciones** previas a la implementación, basadas en los límites típicos de las imágenes oficiales de cada stack. Los valores reales se medirán al implementarse y se moverán a [DOCKER_RESOURCES.md](DOCKER_RESOURCES.md).
>
> **Casos pesados (>3 GB)**: 13 (Kafka), 14 (Supabase). **Casos medianos (~2-2.7 GB)**: 10, 12, 15, 19, 20. **Casos ligeros (<2 GB)**: 11, 16, 17, 18.
> Implementar los 11 simultáneamente requeriría **~25 GB de RAM** adicionales sobre el `--profile full` actual.

---

## 🎯 Justificación por bloque

### Bloque A — Tier 1 (alta prioridad, alto impacto)
- **10–11**: cubren los runtimes JVM y BEAM, los dos huecos más grandes de la matriz original.
- **12**: caso "estrella 2026" — RAG es el patrón más demandado en entrevistas.
- **13**: introduce streaming real (Kafka) y storage analítico (ClickHouse).
- **14**: primer caso BaaS de la matriz — solicitado expresamente.

### Bloque B — Tier 2 (cobertura técnica)
- **15**: protocolo binario gRPC + DB distribuida.
- **16**: dos enfoques GraphQL contrastados + series temporales.
- **17**: pub/sub asíncrono + IoT.

### Bloque C — Tier 3 (exploratorios / nicho)
- **18**: lenguajes emergentes sin GC + grafos.
- **19**: funcional puro multi-runtime + DB bitemporal.
- **20**: stack mobile-backend con runtimes server-side de Swift/Dart.

---

## ⚠️ Implicaciones operacionales al implementar

- **RAM**: pasar de 9 → 20 casos añade ~22 contenedores (incluyendo brokers Kafka, Mosquitto, Neo4j, Firebase emulator). Estimación: +6–8 GB para perfil `full`.
- **CI**: cada caso nuevo ejecutará healthchecks, idempotency tests, security scans → tiempo CI puede crecer 2×–3×.
- **Imágenes pesadas**: Swift Linux (~500 MB), Hasura (~300 MB), CockroachDB (~250 MB) requieren multi-stage builds agresivos.
- **Seguridad**: cada caso debe pasar por la auditoría de 8 capas existente (ver [SECURITY.md](../SECURITY.md)).

---

## 🔗 Cómo usar este documento

- Para **decidir el siguiente caso a implementar**: usa la columna *Categoría* y prioriza lo que cierre el hueco mayor de tu portfolio.
- Para **referenciar desde otra doc**: enlaza con `[Casos planificados](docs/PLANNED_CASES.md)`. No dupliques la tabla.
- Para **arrancar la implementación** de un caso: sigue el TODO interno del README de cada `cases/{ID}-*/README.md`.

---

*Última actualización: 2026-05-05 — Vladimir Acuña*
