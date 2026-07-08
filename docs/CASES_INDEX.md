# Indice de la Matriz Tecnologica

Descubre por que hemos elegido estas combinaciones y que beneficios aporta cada una a tu flujo de trabajo.

---

## Comparativa de Emisores (Origen)
| Tecnologia | Caso | Ventaja | Uso Recomendado |
| :--- | :--- | :--- | :--- |
| **Python** | 01, 02, 09 | Facilidad de scripting y librerias robustas. | Prototipado rapido, automatizacion y gateways de integracion. |
| **Go** | 03, 06 | Binario unico, ultra-rapido y concurrente. | Sistemas embebidos o servidores de alta carga. |
| **Node.js** | 04 | Manejo asincrono nativo excelente. | Integracion con otros servicios JS existentes. |
| **Laravel** | 05 | Framework PHP ultra-productivo. | Aplicaciones SaaS empresariales. |
| **Rust** | 07 | Seguridad de memoria y rendimiento. | Sistemas criticos y de baja latencia. |
| **C# (.NET)** | 08 | Ecosistema empresarial maduro. | Integraciones corporativas y servicios Windows. |

---

## Comparativa de Receptores (Destino)
| Tecnologia | Dashboard | Persistencia | Por que elegirlo |
| :--- | :--- | :--- | :--- |
| **PHP (Vanilla)** | 8081 | MySQL | Universalidad y simplicidad maxima. |
| **Go** | 8082 | MariaDB | Eficiencia extrema y drivers nativos. |
| **Node.js** | 8083 | PostgreSQL | Flexibilidad y manejo de JSONB. |
| **FastAPI** | 8084 | SQLite | Velocidad Python con BD embebida. |
| **React (Express)** | 8085 | MongoDB | Ecosistema MERN. |
| **Symfony** | 8086 | Redis | Alto rendimiento y estados en memoria. |
| **Ruby (Sinatra)** | 8087 | Cassandra | Escalabilidad lineal y alta disponibilidad. |
| **Flask** | 8088 | SQL Server | Integracion Enterprise robusta. |
| **FastAPI Gateway** | 8089 | DuckDB | Gateway autenticado con X-API-Key, DDD y dashboard operativo. |

---

## Matriz Resumida
| Caso | Flujo | DB | Auth | Externo |
| :--- | :--- | :--- | :--- | :--- |
| 01 | Python -> n8n -> PHP | MySQL | No | No |
| 02 | Python -> n8n -> Go | MariaDB | No | No |
| 03 | Go -> n8n -> Node.js | PostgreSQL | No | No |
| 04 | Node.js -> n8n -> FastAPI | SQLite | No | No |
| 05 | Laravel -> n8n -> React | MongoDB | No | No |
| 06 | Go -> n8n -> Symfony | Redis | No | No |
| 07 | Rust -> n8n -> Ruby | Cassandra | No | No |
| 08 | C# -> n8n -> Flask | SQL Server | No | No |
| 09 | Python -> n8n -> FastAPI Gateway | DuckDB | X-API-Key | GitHub API |
| 10 | Java (Spring) -> n8n -> Kotlin (Ktor) | PostgreSQL | No | JVM |
| 11 | Elixir -> n8n -> Erlang (Cowboy) | Mnesia (embebida) | No | Bus BEAM |
| 12 | Python (LLM) -> n8n -> FastAPI RAG | pgvector | No | Retrieval |
| 13 | Node + Kafka -> n8n -> Go consumer | ClickHouse | No | Streaming / CQRS |
| 14 | Next.js -> n8n -> Supabase (PostgREST) | Postgres + RLS | RLS | BaaS |
| 15 | Go (gRPC) -> n8n -> Python (gRPC) | CockroachDB | No | Protobuf |
| 16 | Apollo GraphQL -> n8n -> Hasura | TimescaleDB | Admin secret | GraphQL |
| 17 | Rust (MQTT) -> n8n -> Node | InfluxDB | No | Mosquitto |
| 18 | Zig -> n8n -> Crystal (Kemal) | Neo4j | No | Cypher / grafo |
| 20 | Swift -> n8n -> Dart (Shelf) | Firestore (emulador) | No | Mobile-backend |

> **19 de 20 casos** implementados (todos menos el 19). Puertos por fórmula `8080 + id` (ver [PORTS.md](PORTS.md)).

---

## Único caso pendiente (19)

Queda **sólo el caso 19** (F# → Clojure/XTDB): código completo pero pendiente de verificación end-to-end. Ver el documento dedicado: [PLANNED_CASES.md](PLANNED_CASES.md).

| ID | Flujo (resumen) | DB | Categoria | Estado |
| :--- | :--- | :--- | :--- | :--- |
| 19 | F# -> Clojure | XTDB | Bitemporal | 🧪 Código listo, verificación pendiente |

---

## El Rol de n8n
En todos los casos, **n8n** actua como la capa de abstraccion y resiliencia. En el Caso 09, ademas de mantener guardrails, inyecta `X-API-Key` desde entorno para proteger el gateway sin exponer secretos en el payload.
