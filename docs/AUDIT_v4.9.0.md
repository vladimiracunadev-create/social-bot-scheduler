# 🔍 Auditoría Docker end-to-end — v4.9.0

> Barrido caso por caso levantando cada stack con Docker (limpieza total de contenedores
> e imágenes **entre cada caso** para evitar falsos positivos por recursos), verificando la
> **persistencia real** en cada motor y no sólo que el contenedor arrancara. Objetivo:
> eliminar incoherencias y **falsas promesas no validadas**.
>
> **Alcance:** casos 01–18 y 20 (los 19 operativos). El **caso 19** (F#/Clojure/XTDB) queda
> excluido por decisión explícita — se revisará en otro momento.
> **Fecha:** 2026-07-08 · **Resultado:** 19/19 casos verificados end-to-end · CI en verde.

---

## 🐛 Bugs reales encontrados y corregidos

| # | Caso | Falla observada (validada con Docker) | Causa raíz | Corrección |
| :-: | :-- | :-- | :-- | :-- |
| 1 | **09** — FastAPI Gateway | `POST /webhook` devolvía `422` y `/openapi.json` daba `500`. **El endpoint nunca funcionó.** | `from __future__ import annotations` + el wrapper de `@limiter.limit` (slowapi): FastAPI no resolvía la anotación `payload: IntegrationRequestDTO` y la trataba como *query param*. | Quitar `from __future__ import annotations` en `cases/09-python-to-gateway/dest/app/api.py` (el archivo usa sintaxis nativa de 3.11). |
| 2 | **11** — Erlang/Cowboy | Contenedor `unhealthy` permanente pese a que `/health` respondía `200`. | El healthcheck usaba `localhost`, que la imagen resuelve a `::1` (IPv6); Cowboy sólo escucha IPv4. | `docker-compose.yml`: healthcheck a `http://127.0.0.1:8080/health`. |
| 3 | **14** — Next.js/Supabase | Ídem: receptor Node `unhealthy` con `/health` `200`. | Mismo patrón IPv6 (imagen node Debian con GNU wget). | `docker-compose.yml`: healthcheck a `127.0.0.1`. |
| 4 | **18** — Crystal/Kemal | Ídem: `unhealthy` con `/health` `200`. | Mismo patrón IPv6 (Kemal escucha `0.0.0.0` IPv4). | `docker-compose.yml`: healthcheck a `127.0.0.1`. |
| 5 | **06** — Symfony/PHP | `Fatal error: Class "Redis" not found` al persistir. | La imagen `php:8.2-apache` no trae la extensión phpredis. | Nuevo `cases/06-go-to-symfony/dest/Dockerfile` con `pecl install redis` + `docker-php-ext-enable redis`; el compose pasa de `image:` a `build:`. |
| 6 | **07** — Ruby/Cassandra | `cannot load such file -- cassandra (LoadError)`. | `cassandra-driver` usa `SortedSet`, removido del stdlib en Ruby 3.2. | Añadir la gema `sorted_set` (Dockerfile + Gemfile + Gemfile.lock). |
| 7 | **08** — Flask/pyodbc | `No matching distribution for click==8.4.2`. | `python:3.9` no resuelve `click>=8.4` (requiere 3.10+). | `python:3.11-slim` + repo mssql `debian/12/prod bookworm`. |
| 8 | **03·14·16·17** — builds Node | Build frágil / contaminación de `node_modules` del host. | Faltaba `.dockerignore`. | `.dockerignore` (`node_modules`, `npm-debug.log`, `.git`) en cada `dest`. |

### Nota sobre el caso 15 (no es bug)
CockroachDB tuvo una caída puntual durante el *init* del clúster (timeout `context deadline exceeded`)
**por starvation de recursos bajo la carga de builds paralelos**, no por un defecto de código. En
máquina ociosa arranca `healthy` de inmediato y el flujo gRPC → CockroachDB persiste correctamente.

---

## ✅ Verificación por caso (evidencia)

Cada caso se probó con su contrato REST homogéneo (`/health`, `/webhook`, `/logs`, `/errors`, `/`)
y con **confirmación directa en el motor**:

- **01–09** — persistencia OK (MySQL, MariaDB, Postgres, SQLite, MongoDB, Redis, Cassandra, SQL Server, DuckDB). Caso 09 llama a la GitHub API real y persiste en DuckDB.
- **10** Ktor → Postgres · **11** Erlang → Mnesia · **12** RAG → pgvector (`/search` semántico rankea correcto).
- **13** Kafka → consumer Go → ClickHouse (filas confirmadas por query directa).
- **14** Supabase/PostgREST con **RLS realmente activo** (`relrowsecurity = t`).
- **15** gRPC → CockroachDB · **16** GraphQL → **hypertable** real de TimescaleDB.
- **17** MQTT → InfluxDB (round-trip) · **18** Cypher → Neo4j · **20** Dart → emulador Firestore.

---

## 🟢 Estado del CI tras la auditoría

`black --check .` (47 archivos OK) · `validate_ports.py` · `validate_case_matrix.py` ·
`docker compose --profile full config` · `flake8`. Todo verde.

---

## 📌 Pendiente

- **Caso 19** (F#/Clojure/XTDB): código presente (bug de arranque AOT ya corregido) pero **sin
  verificación end-to-end**. Es el único caso no operativo de la matriz.
