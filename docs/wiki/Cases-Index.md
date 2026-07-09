# 🧩 Índice de la Matriz Tecnológica

Bienvenidos a la cartografía del **Social Bot Scheduler**. Este laboratorio se compone de **19 ejes de integración implementados** y **1 caso planificado adicional** (ver [PLANNED_CASES](../PLANNED_CASES.md)) que demuestran la ductilidad de la orquestación moderna.

---

## 🏗️ Matriz de Integración (E2E)

| ID | Flujo (Origen -> Puente -> Destino) | Puerto | Persistencia | Nivel de Complejidad |
| :--- | :--- | :--- | :--- | :--- |
| **01** | Python -> **n8n** -> PHP | `8081` | 🐬 **MySQL** | 🟢 Inicial |
| **02** | Python -> **n8n** -> Go | `8082` | 🍃 **MariaDB** | 🟢 Inicial |
| **03** | Go -> **n8n** -> Node.js | `8083` | 🐘 **Postgres** | 🟡 Intermedio |
| **04** | Node.js -> **n8n** -> FastAPI | `8084` | 📂 **SQLite** | 🟡 Intermedio |
| **05** | Laravel -> **n8n** -> React | `8085` | 🍃 **MongoDB** | 🟡 Intermedio |
| **06** | Go -> **n8n** -> Symfony | `8086` | 🏎️ **Redis** | 🟡 Intermedio |
| **07** | Rust -> **n8n** -> Ruby | `8087` | 👁️ **Cassandra**| 🔴 Avanzado |
| **08** | C# (.NET) -> **n8n** -> Flask | `8088` | 🏢 **SQL Server**| 🔴 Avanzado |
| **09** | Python -> **n8n** -> FastAPI Gateway| `8089` | 🦆 **DuckDB** | 🔴 Avanzado |
| **10** | Java (Spring) -> **n8n** -> Kotlin (Ktor) | `8090` | 🐘 **PostgreSQL** | 🔴 Avanzado |
| **11** | Elixir -> **n8n** -> Erlang (Cowboy) | `8091` | 📇 **Mnesia** | 🔴 Avanzado |
| **12** | Python (LLM) -> **n8n** -> FastAPI RAG | `8092` | 🧬 **pgvector** | 🔴 Avanzado |
| **13** | Node + Kafka -> **n8n** -> Go consumer | `8093` | ⚡ **ClickHouse** | 🔴 Avanzado |
| **14** | Next.js -> **n8n** -> Supabase (PostgREST)| `8094` | 🔐 **Postgres + RLS** | 🔴 Avanzado |
| **15** | Go (gRPC) -> **n8n** -> Python (gRPC) | `8095` | 🪳 **CockroachDB** | 🔴 Avanzado |
| **16** | Apollo GraphQL -> **n8n** -> Hasura | `8096` | ⏱️ **TimescaleDB** | 🔴 Avanzado |
| **17** | Rust (MQTT) -> **n8n** -> Node | `8097` | 📈 **InfluxDB** | 🔴 Avanzado |
| **18** | Zig -> **n8n** -> Crystal (Kemal) | `8098` | 🕸️ **Neo4j** | 🔴 Avanzado |
| **19** | F# (.NET) -> **n8n** -> Clojure (Ring) | `8099` | 🕰️ **XTDB** | 📐 Diseñado |
| **20** | Swift -> **n8n** -> Dart (Shelf) | `8100` | 🔥 **Firestore** | 🔴 Avanzado |

---

## 🔬 Caso de Estudio: Integración Gateway (Caso 09)

El **Caso 09** es el pináculo arquitectónico del laboratorio, demostrando:
- **🔐 Seguridad de Bordes**: Verificación de `X-API-Key` y tokens en el gateway.
- **🛡️ Guardrails Totales**: Implementación de circuit breaker, idempotencia y DLQ en un solo flujo.
- **🏗️ Patrón DDD**: Gateway diseñado bajo los principios de *Domain-Driven Design*.
- **📊 Persistencia Analítica**: Uso de **DuckDB** para almacenamiento OLAP ligero.

---

## 🚦 Guía de Exploración

1.  **Añade flujos**: Sigue el [Manual de Activación](../../COMO_ACTIVAR_WORKFLOWS.md).
2.  **Lanza bots**: Utiliza el comando `python hub.py ejecutar <id>`.
3.  **Audita estados**: Verifica la persistencia en los dashboards correspondientes (`:8081-8100`).

---
*Catálogo técnico v4.1 — Social Bot Scheduler*
