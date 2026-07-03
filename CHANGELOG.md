# 📜 Changelog — Social Bot Scheduler

Todos los cambios notables en este proyecto se documentan sistemáticamente en este archivo. Seguimos los principios de [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) y el versionado semántico.

---

## 🔒 [4.4.0] — 2026-07-02

### 🛡️ Seguridad — Cierre de los 4 pendientes priorizados de la auditoría

Los cuatro ítems que quedaban como **RIESGO ACEPTADO** en `SECURITY.md` pasan a **CORREGIDO**.

#### Añadido

- **P-01 · Hashes SHA en dependencias Python**: nuevos `requirements.in` como fuente y `requirements.txt` regenerados con `uv pip compile --universal --generate-hashes --python-version 3.11` en los 5 archivos (root, `01/origin`, `02/origin`, `08/dest`, `09/dest`). Cada dependencia directa y transitiva queda pinneada con hash SHA256, forzando el modo `pip --require-hashes` en CI y en el build Docker (Python 3.11). La resolución **universal** incluye backports condicionales (`python_version < "3.12"`, p.ej. `backports.tarfile`) con su marcador — imprescindible para que `--require-hashes` funcione en 3.11.
- **P-02 · Rate limiting en Case 09**: `slowapi` aplica throttling por IP en `POST /webhook` (30/min) y `POST /errors` (60/min). Límites configurables por `GATEWAY_WEBHOOK_RATE_LIMIT` / `GATEWAY_ERRORS_RATE_LIMIT`; el excedente devuelve **HTTP 429**. Protege la cuota de la GitHub API y contiene el abuso de una `X-API-Key` filtrada.
- **P-03 · Whitelist de owner en Case 09**: el campo `owner` de `RequestParamsDTO` valida el patrón de usuario de GitHub (`^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$`) en el borde (pydantic → **422**), como defensa en profundidad sobre el value object `Owner` del dominio. Cierra la superficie tipo SSRF del parámetro que forma la URL saliente.
- **P-04 · Auditoría CVE multi-lenguaje en CI**: `govulncheck` (Go), `pnpm audit --audit-level high` (Node) y `dotnet list package --vulnerable` (.NET) como pasos **bloqueantes**; `cargo audit` (Rust) en **modo observación** (el sample origin fija `reqwest 0.11` a propósito); `bundler-audit` (Ruby) condicionado a la existencia de `Gemfile.lock`.

#### Corregido — advisories transitivos detectados por el nuevo `pnpm audit` (P-04)

El gate de Node destapó **3 HIGH + 1 moderate** en dependencias transitivas, resueltos vía `pnpm.overrides` + regeneración de lockfile:

- `cases/03-go-to-node/dest` y `cases/04-node-to-fastapi/origin`: **`form-data`** `>=4.0.0 <4.0.6` (CRLF injection, GHSA-hmw2-7cc7-3qxx, vía `axios`) → `>=4.0.6`.
- `cases/05-laravel-to-react/dest`: **`path-to-regexp`** `<0.1.13` (ReDoS, GHSA-37ch-88jc-xwx2, vía `express`) → `>=0.1.13 <0.2.0` (se mantiene la línea 0.1.x que espera Express 4); **`qs`** `>=6.11.1 <=6.15.1` (DoS, GHSA-q8mj-m7cp-5q26) → `>=6.15.2 <7.0.0`.

Además, el gate de Go (`govulncheck`) forzó subir el toolchain de CI a `stable` (cerrando advisories de stdlib GO-2026-5037/5039 en `go1.22.12`).

#### Notas

- **slowapi** es dependencia nueva de Case 09 (añadida a `requirements.in` + lockfile con hashes).
- **Follow-ups** registrados en `SECURITY.md`: **P-05** (`cargo audit` bloqueante), **P-06** (`Gemfile.lock` para Ruby), **P-07** (SHA-pinning de GitHub Actions).
- Verificación local con `fastapi.testclient`: owner malformado → 422, 4ª petición sobre el límite → 429; los 5 lockfiles validan con `pip install --require-hashes`.

---

## 🔒 [4.3.1] — 2026-06-19

### 🛡️ Seguridad — Supply chain (npm → pnpm v11)

Mitigación de la campaña **Shai-Hulud** en npm. pnpm v11 trae `postinstall` scripts bloqueados por defecto y `minimumReleaseAge=24h`, lo que cierra la ventana de explotación típica de los paquetes maliciosos publicados con auto-install hooks.

Casos migrados (todos con `onlyBuiltDependencies: []`):

- `cases/03-go-to-node/dest` (`express`, `pg`, `axios`) — `pnpm-lock.yaml` nuevo
- `cases/04-node-to-fastapi/origin` (`axios`) — `pnpm-lock.yaml` nuevo
- `cases/05-laravel-to-react/dest` (`cors`, `express`, `mongodb`) — `pnpm import` desde `package-lock.json` existente

**NO migrado** (intencional):

- `n8n/data/nodes/package.json` — generado en runtime por el contenedor de n8n; tocarlo no aporta beneficio y puede causar conflictos al arrancar.

### 🔧 Notas operativas

- **CI**: sin cambios — el workflow `node-cases` solo hace `node --check` para syntax, no corre `npm install`.
- **Dependabot**: `package-ecosystem: npm` se mantiene; GitHub Dependabot auto-detecta `pnpm-lock.yaml` en esa misma categoría.
- **Sin impacto en producto**: ningún cambio funcional ni de API; solo manifest + lockfile.

---

## 🎛️ [4.3.0] — 2026-05-05

### ✨ Añadido — Master Dashboard interactivo

- **Detección automática de estado por caso**: cada 20 s el dashboard hace ping (`fetch no-cors`) al puerto del receptor y marca cada tarjeta como 🟢 `READY` o 🔴 `OFFLINE`. Sin backend nuevo, sin agotar RAM al usuario.
- **Modal "Mostrar comando para levantarlo"**: cuando un caso está OFFLINE, el botón se transforma y abre un modal con el comando `docker-compose --profile caseXX up -d`, la RAM estimada y un botón **📋 Copiar al portapapeles** (con fallback `execCommand`).
- **Barra global Docker**: contadores live `🟢 N/9 READY · 🔴 N/9 OFFLINE · 🚧 11 PLANNED`, indicador `Última comprobación: HH:MM:SS` y botón **🔄 Re-comprobar** manual.
- **Sistema de toasts**: notificaciones top-right cuando un caso transiciona ONLINE↔OFFLINE, al copiar comandos o al re-comprobar.
- **Badges de RAM por tarjeta**: `💾 ~X.X GB` en cada uno de los 20 casos (verde para ligeros, rojo ⚠️ para los pesados 07/08/13/14).
- **Separador visual** entre los 9 casos implementados y los 11 planificados, con enlace a `docs/PLANNED_CASES.md`.

### 📚 Documentación de recursos

- `docs/DOCKER_RESOURCES.md`: nueva sección "Consumo de RAM por Caso" con desglose receptor + DB + núcleo (1.13 GB), tabla de combinaciones recomendadas según RAM disponible (2/4/8/16 GB) y estimaciones para los 11 casos planificados.

### 🔧 Fix — Dependabot puede escanear todo el repo

Se añadieron los 4 manifiestos que faltaban desde v4.2.0 (rompían los runs scheduled de Dependabot):

- `cases/02-python-to-go/dest/go.mod` (+ Dockerfile actualizado a `go mod tidy`)
- `cases/03-go-to-node/origin/go.mod` (stdlib only)
- `cases/04-node-to-fastapi/origin/package.json` (axios ^1.7.7)
- `cases/06-go-to-symfony/origin/go.mod` (stdlib only)

### 🔧 Fix — Validador tolera casos planificados

`scripts/validate_case_matrix.py` ahora lee `status: planned` del manifest y excluye esos casos de la comparación estricta. Implementados (01–09) se siguen validando como antes; planificados se reportan como "skipped".

---

## 🚧 [Unreleased] — Roadmap v5.0

### ✨ Añadido — Scaffolding de 11 casos planificados (cases 10–20)

Se incorpora la documentación de diseño y estructura de carpetas para 11 nuevos casos de integración. **Sin implementación funcional**: solo `README.md`, `app.manifest.yml` (con `status: planned`) y carpetas `origin/` + `dest/`.

| ID | Stack | Categoría |
| :--- | :--- | :--- |
| 10 | Java (Spring Boot) → Kotlin (Ktor) + PostgreSQL | JVM |
| 11 | Elixir (Phoenix) → Erlang (Cowboy) + Mnesia | BEAM / Actores |
| 12 | Python LLM → FastAPI + pgvector | RAG / IA |
| 13 | Node + Kafka → Go + ClickHouse | Streaming / OLAP |
| 14 | Next.js 15 → Supabase Edge Functions | BaaS |
| 15 | Go gRPC → Python gRPC + CockroachDB | Protobuf / SQL distribuido |
| 16 | Apollo GraphQL → Hasura + TimescaleDB | GraphQL / Time-series |
| 17 | Rust MQTT → Node MQTT + InfluxDB | IoT / Pub-Sub |
| 18 | Zig → Crystal + Neo4j | Lenguajes emergentes / Grafos |
| 19 | F# (.NET) → Clojure + XTDB | Funcional / Bitemporal |
| 20 | Swift Vapor → Dart Shelf + Firebase emulator | Mobile-backend |

### 📚 Documentación

- Nuevo: `docs/PLANNED_CASES.md` — single source of truth de la matriz planificada.
- Actualizado: `README.md`, `ROADMAP.md`, `CHANGELOG.md`, `index.html` y 10+ MD del catálogo (`docs/CASES_INDEX.md`, `docs/wiki/Cases-Index.md`, `docs/FILE_MAP.md`, `docs/INSTALL.md`, `docs/REQUIREMENTS.md`, `docs/INSIGHTS.md`, `docs/GUARDRAILS.md`, `docs/wiki/Resilience.md`, `docs/wiki/Home.md`, `docs/wiki/Usage-Guide.md`, `COMO_ACTIVAR_WORKFLOWS.md`) con referencias cruzadas a los casos planificados.

> [!NOTE]
> No se ha modificado `docker-compose.yml`, scripts ni código fuente. Los perfiles `case10`–`case20` no existen aún — su implementación se planifica en bloques (Tier 1 → Tier 2 → Tier 3).

---

## 🔒 [4.2.0] — 2026-04-06

### 🛡️ Seguridad — Auditoría de 8 Capas

- **HTTP Security Headers (Capa 4)**: Los tres servicios `php:8.2-apache` (`master-dashboard`, `dest-php`, `dest-symfony`) ahora sirven `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Content-Security-Policy` y `Permissions-Policy`. Se deshabilita el listado de directorios (`Options -Indexes`). Implementado vía `apache/security-headers.conf` montado en `:ro`.
- **CSP + Permissions-Policy en Edge Proxy (Capa 4)**: El proxy Caddy ya incluía HSTS, X-Frame-Options, etc. Se añaden los dos headers faltantes: `Content-Security-Policy` y `Permissions-Policy`.
- **Dependabot (Capa 7)**: Configurado `.github/dependabot.yml` con 11 ecosistemas: `github-actions`, `pip` (hub + 3 cases), `docker`, `gomod` (3 cases), `cargo`, `npm` (2 cases). Abre PRs automáticos ante versiones vulnerables.
- **Line endings LF (Capa 8)**: Creado `.gitattributes` para garantizar que todos los scripts shell, Python, Go, Ruby, Rust y JS se almacenen con LF en Git, independientemente del OS del colaborador. Evita el error `bad interpreter: \r` al ejecutar scripts en contenedores Linux desde un clon Windows.
- **Detección de Unicode bidi/CVE-2021-42574 (Capa 8)**: Nuevo job `supply-chain-checks` en CI que escanea el código fuente completo en busca de caracteres de control bidireccionales (Trojan Source) usando Python puro, sin dependencias externas.
- **Detección de ofuscación base64+eval (Capa 8)**: El mismo job detecta patrones `eval(b64decode(...))` y equivalentes en Python, JS, Ruby, PHP y Shell.

### ✨ Añadido

- `apache/security-headers.conf` — configuración Apache de hardening (headers + `-Indexes`).
- `.gitattributes` — normalización de line endings por tipo de archivo.
- `.github/dependabot.yml` — actualizaciones automáticas de dependencias para 11 ecosistemas.

### ⚙️ Cambiado

- `docker-compose.yml` — `master-dashboard`, `dest-php` y `dest-symfony` montan `apache/security-headers.conf` y ejecutan `a2enmod headers` al arrancar.
- `edge/start-caddy.sh` — añadidos `Content-Security-Policy` y `Permissions-Policy` al bloque de headers.
- `.github/workflows/ci-cd.yml` — nuevo job `supply-chain-checks` (bidi + obfuscación), precede a `build-and-push`.
- `SECURITY.md` — reemplazado por resultados completos de auditoría de 8 capas con estado por punto, riesgos aceptados documentados y tabla de pendientes priorizados.

---

## 🚀 [4.1.0] — 2026-03-24

### 🛡️ Seguridad

- **Fix Crítico**: Mitigación del ataque de cadena de suministro en `aquasecurity/trivy-action`. Upgrade a `v0.35.0`.
- **Hardening CI/CD**: Refuerzo de permisos en los flujos de GitHub Actions.

### ✨ Añadido

- **🔍 Verificación de Recursos**: Nuevo script `check_resources.py` para monitoreo en tiempo real (CPU, RAM, Disco).
- **📊 Health Dashboard**: Interfaz visual de diagnóstico para verificar la preparación del entorno antes de la ejecución.
- **🧹 Deep Clean**: Comandos `make clean` y `hub clean` para purga total de recursos Docker (volúmenes e imágenes).
- **🧩 Docker Profiles**: Soporte para carga selectiva de servicios mediante perfiles (ej: `case01`, `full`).

### ⚙️ Cambiado

- **🏎️ Optimización**: Límites granulares de CPU/RAM para los 20+ contenedores del ecosistema.
- **📂 Alpine Migration**: Todos los servicios de destino ahora utilizan imágenes ligeras basadas en Alpine Linux para reducir la superficie de ataque.

---

## 🏗️ [4.0.0] — 2026-02-18

### 📂 Persistencia Políglota

- **Integración Nativa**: Soporte para **8 motores de bases de datos** distintos: 🐬 MySQL, 🍃 MariaDB, 🐘 PostgreSQL, 📂 SQLite, 🍃 MongoDB, 🏎️ Redis, 👁️ Cassandra y 🏢 SQL Server.
- **Auto-Provisionamiento**: Lógica inteligente de creación de esquemas y tablas en el primer arranque de cada receptor.

### ✨ Añadido

- **🖥️ Master Dashboard v2**: Visualización unificada del estado de las bases de datos y previsualización de posts en tiempo real.
- **🔗 Nuevos Drivers**: Soporte para `pyodbc`, `cassandra-driver`, `pg`, y extensiones de Redis para PHP.

---

## 🛡️ [3.0.0] — 2026-02-11

### 🏗️ Arquitectura de Resiliencia

- **Guardrails Globales**: Implementación de **Idempotencia (SQLite)** y **Circuit Breaker** en todos los ejes tecnológicos.
- **📥 Dead Letter Queue (DLQ)**: Sistema de captura de mensajes fallidos en todos los receptores.
- **📚 Nueva Documentación**: Creación de `docs/GUARDRAILS.md` y guías técnicas de arquitectura profesional.

---

## 🛠️ [2.1.0] — 2026-01-25

### 🔧 Corregido

- **Estandarización de Endpoints**: Todos los receptores ahora escuchan de forma uniforme en `/webhook`.
- **Normalización de Payload**: Los campos de envío se han estandarizado a `id`, `text` y `channel`.
- **CI Fixes**: Aplicación de `black` a todo el repositorio y corrección de dependencias de Ruby en Docker.

---

## 🏁 [1.0.0] — 2026-01-20

- Lanzamiento inicial del laboratorio con 6 casos de integración base.
- Soporte para orquestación multi-contenedor mediante Docker Compose.

---
*Mantenido con rigor técnico por Vladimir Acuña*
