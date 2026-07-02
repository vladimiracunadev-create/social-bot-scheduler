# 🛣️ Roadmap — Social Bot Scheduler

Este documento describe la evolución técnica y los objetivos estratégicos del proyecto. Seguimos un enfoque de mejora continua en seguridad y observabilidad.

---

## ✅ Hitos Completados

### `v4.4.0` — "Cierre de Pendientes de Seguridad" 🔒 Ready

- [x] **Hashes SHA en dependencias (P-01)**: `requirements.in` + `pip-compile --generate-hashes` en los 5 archivos Python; `pip --require-hashes` en CI y build Docker.
- [x] **Rate limiting (P-02)**: `slowapi` en el gateway Case 09 (`/webhook` 30/min, `/errors` 60/min), configurable por env, excedente → HTTP 429.
- [x] **Whitelist de owner (P-03)**: validación regex en el borde (`RequestParamsDTO` → 422) como defensa en profundidad sobre el value object `Owner`.
- [x] **Auditoría CVE multi-lenguaje (P-04)**: `govulncheck`, `pnpm audit` y `dotnet list package --vulnerable` bloqueantes en CI; `cargo audit` en observación; `bundler-audit` condicional.

### `v4.3.0` — "Master Dashboard Interactivo" 🎛️ Ready

- [x] **Detección automática de OFFLINE/READY** por caso vía ping cada 20 s.
- [x] **Modal con `docker-compose --profile caseXX up -d`** + copy-to-clipboard cuando un caso está caído.
- [x] **Barra global Docker** con contadores live + última comprobación + botón Re-comprobar.
- [x] **Toast notifications** para transiciones online↔offline.
- [x] **Badges de RAM** en cada una de las 20 tarjetas (9 implementadas + 11 planificadas).
- [x] **Doc `DOCKER_RESOURCES.md`** con desglose por caso y estimaciones.
- [x] **Fix Dependabot**: añadidos los 4 manifiestos faltantes (go.mod, package.json) + validador tolera casos planificados.

### `v4.2.0` — "Auditoría de Seguridad de 8 Capas" 🛡️ Ready

- [x] **HTTP Security Headers**: `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, `Referrer-Policy`, `Permissions-Policy` y `Options -Indexes` en todos los servicios Apache y en el edge proxy Caddy.
- [x] **Dependabot**: Configurado para 11 ecosistemas (pip, docker, gomod, cargo, npm, github-actions).
- [x] **Line endings LF**: `.gitattributes` fuerza LF en scripts shell/Python/Go para eliminar errores `bad interpreter` en Windows.
- [x] **Detección Trojan Source**: CI detecta caracteres Unicode bidireccionales (CVE-2021-42574) en todo el código fuente.
- [x] **Detección de ofuscación**: CI detecta patrones `eval(base64_decode(...))` y equivalentes.
- [x] **Auditoría documentada**: `SECURITY.md` reemplazado por informe completo con estado, riesgos aceptados y pendientes priorizados.

### `v4.1.0` — "Hardening Industrial" 🛡️ Ready

- [x] **Mitigación Supply Chain**: Resolución proactiva del compromiso de `trivy-action` (v0.35.0).
- [x] **Docs Professionalization**: Rediseño visual de toda la base de conocimientos del laboratorio.
- [x] **Audit Trail**: Refuerzo de logs de auditoría en el HUB CLI.
- [x] **Security Badging**: Estandarización de badges "Hardened" en toda la matriz.

### `v4.0.0` — "Persistencia Políglota" 🟢 Ready

- [x] **8 Motores de BD**: Integración con MySQL, Postgres, MSSQL, MongoDB, Redis, Cassandra y DuckDB.
- [x] **Agnosticismo Total**: Casos prácticos en Rust, C#, Go y Laravel conectando a n8n.
- [x] **Matrix Dashboard**: Visualización unificada de los 9 casos en tiempo real.

### `v3.0.0` — "Observabilidad y Resiliencia" 🟢 Ready

- [x] **Stack CNCF**: Despliegue de Prometheus, Grafana y cAdvisor.
- [x] **Guardrails**: Implementación de Circuit Breaker e Idempotencia en los 9 flujos.

---

## 🚀 En Desarrollo (v4.3+)

### 🔒 Seguridad — Pendientes Priorizados

- [x] **Lock file con hashes SHA** (P-01): `pip-compile --generate-hashes` para verificación criptográfica de dependencias Python. ✅ v4.4.0
- [x] **Rate limiting en Case 09** (P-02): `slowapi` con throttling por IP en el FastAPI gateway. ✅ v4.4.0
- [x] **Whitelist de owners en Case 09** (P-03): `owner` validado con regex de GitHub en `RequestParamsDTO`. ✅ v4.4.0
- [x] **Auditoría CVE multi-lenguaje** (P-04): `govulncheck`, `pnpm audit`, `cargo audit`, `bundler-audit`, `dotnet list package --vulnerable` en CI. ✅ v4.4.0
- [ ] **`cargo audit` bloqueante** (P-05): modernizar el sample `07-rust-to-ruby/origin` (hoy `reqwest 0.11`) para exigir cero advisories.
- [ ] **SHA-pinning de GitHub Actions** (P-07): pinnear las actions de `ci-cd.yml` por SHA de 40 chars.

### 🌐 Conectividad Edge y Avanzada

- [ ] **Auto-TLS**: Gestión de certificados locales (mTLS) para entornos críticos.
- [ ] **Playwright E2E**: Pruebas automatizadas de interfaz para validar la matriz total.

---

## 🔮 Futuro (v5.0+)

### 🧩 Expansión de la Matriz Tecnológica (casos 10-14 — scaffolding ya creado)

- [ ] **Caso 10 — JVM**: Java (Spring Boot) → Kotlin (Ktor) + PostgreSQL. Cubre el hueco enterprise JVM.
- [ ] **Caso 11 — BEAM**: Elixir (Phoenix) → Erlang (Cowboy) + Mnesia. Modelo de actores y supervisión OTP.
- [ ] **Caso 12 — RAG/IA**: Python LLM → FastAPI + pgvector. Pipeline embeddings + retrieval semántico.
- [ ] **Caso 13 — Streaming**: Node + Kafka → Go consumer + ClickHouse. Event streaming real + OLAP columnar.
- [ ] **Caso 14 — BaaS**: Next.js 15 → Supabase (Edge Functions + RLS + Realtime). Primer caso BaaS de la matriz.

### 🧩 Tier 2/3 — Scaffolding también creado (cases 15-20)

- [ ] **Caso 15 — gRPC**: Go server ↔ Python client + CockroachDB (protocolo binario + SQL distribuido).
- [ ] **Caso 16 — GraphQL**: Apollo Server ↔ Hasura + TimescaleDB (schema-first vs DB-first + series temporales).
- [ ] **Caso 17 — IoT**: Rust MQTT publisher ↔ Node subscriber + InfluxDB (pub/sub + telemetría).
- [ ] **Caso 18 — Grafos**: Zig ↔ Crystal (Kemal) + Neo4j (lenguajes emergentes sin GC + Cypher).
- [ ] **Caso 19 — Funcional**: F# (.NET) ↔ Clojure (Ring/Reitit) + XTDB (paradigma puro + DB bitemporal).
- [ ] **Caso 20 — Mobile-backend**: Swift Vapor ↔ Dart Shelf + Firebase emulator local.

### 🧪 Casos exploratorios (sin scaffolding — solo brainstorm)

- [ ] WebAssembly: Rust → WASM module → Wasmtime/Wasmer host runtime.
- [ ] Blockchain: Solidity contract → Web3 listener.
- [ ] CRDT collaborative: Yjs / Automerge sobre WebSocket.
- [ ] OpenTelemetry: pipeline completo de traces, metrics y logs.

### ☁️ Cloud Native & Scalability

- [ ] **Terraform/IaC**: Despliegue automatizado en AWS ECS Fargate y Google Cloud Run.
- [ ] **Kubernetes Heavy**: Helm Charts oficiales y NetworkPolicies granulares.
- [ ] **Auth Centralizada**: Integración de Authelia o Keycloak para proteger los hubs.

---
*Última actualización: Julio 2026 — Vladimir Acuña*
