# Indice de la Matriz Tecnologica

[![Ecosystem](https://img.shields.io/badge/Matriz-9_Ejes-blueviolet.svg)]()
[![Latest Release](https://img.shields.io/badge/release-v4.1.0-blue.svg)]()

[? Volver al Inicio](Home)

---

## Casos Implementados
| Caso | Flujo | Puerto | Persistencia | Nota |
| :--- | :--- | :--- | :--- | :--- |
| 01 | Python -> n8n -> PHP | 8081 | MySQL | Caso demo por defecto |
| 02 | Python -> n8n -> Go | 8082 | MariaDB | Receptor Go minimalista |
| 03 | Go -> n8n -> Node.js | 8083 | PostgreSQL | Event loop + JSONB |
| 04 | Node.js -> n8n -> FastAPI | 8084 | SQLite | FastAPI asincrono |
| 05 | Laravel -> n8n -> React | 8085 | MongoDB | BFF + UI reactiva |
| 06 | Go -> n8n -> Symfony | 8086 | Redis | Estados en memoria |
| 07 | Rust -> n8n -> Ruby | 8087 | Cassandra | Caso de alta complejidad |
| 08 | C# -> n8n -> Flask | 8088 | SQL Server | Integracion .NET |
| 09 | Python -> n8n -> FastAPI Gateway | 8090 | DuckDB | X-API-Key + GitHub API + dashboard |

## Caso 09 en foco
- Origen: bot Python que envia payload operativo compatible con el fingerprint actual.
- Puente: n8n con circuit breaker, idempotencia SQLite, reintentos y DLQ.
- Destino: FastAPI Integration Gateway con DDD, DuckDB embebida y dashboard HTML.
