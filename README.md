# 🚀 Social Bot Scheduler

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Hub](https://img.shields.io/badge/Docker-Ready-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/)
[![Version](https://img.shields.io/badge/version-4.11.0-green.svg)](https://github.com/vladimiracunadev-create/social-bot-scheduler/releases)
[![Sitio](https://img.shields.io/badge/Sitio-GitHub%20Pages-6366f1.svg?logo=githubpages&logoColor=white)](https://vladimiracunadev-create.github.io/social-bot-scheduler/)
[![Security: Hardened](https://img.shields.io/badge/Security-Hardened-🛡️?color=red&labelColor=black)](SECURITY.md)
[![CVE remediados](https://img.shields.io/badge/CVE%20remediados-78%20advisories-success.svg?logo=shieldsdotio&logoColor=white)](docs/CVE_REMEDIATION_v4.11.0.md)
[![Runtimes](https://img.shields.io/badge/Runtimes-0%20en%20EOL-success.svg)](docs/CVE_REMEDIATION_v4.11.0.md)

Laboratorio de integración industrial **multi-lenguaje** y **multi-servicio**. El **Social Bot Scheduler** actúa como una **Matriz Tecnológica** donde **n8n** orquesta la comunicación entre bots emisores y receptores políglotas.

> 🌐 **Sitio del laboratorio**: <https://vladimiracunadev-create.github.io/social-bot-scheduler/> — la matriz de casos y toda esta documentación navegable como HTML (se regenera desde el repositorio en cada push a `main`).

> [!NOTE]
> **¿Qué significa "🛡️ Security: Hardened"?**
> Este repositorio implementa una política de **Aislamiento Runtime**: Todos los servicios están limitados a `localhost`, usan imágenes base seguras con escaneos de vulnerabilidades manuales (Trivy) y no contienen secretos hardcodeados, mitigando riesgos de cadena de suministro.

---

## 🛡️ Remediación de CVE — ningún runtime en EOL (v4.11.0)

**Un runtime en fin de vida no arrastra "un CVE": arrastra todos los publicados desde su último parche.** Por eso la revisión de la v4.11.0 no fue un bump de rutina — se recorrieron los **20 casos**, lenguaje por lenguaje, hasta que ninguno quedara sobre una versión sin soporte.

| | |
| :--- | ---: |
| 🔴 **Advisories cerrados** | **78** (41 con identificador CVE) |
| 🔧 **Cambios de runtime / imagen base** | **51** |
| 📦 **Entradas de dependencia revisadas** | **92** |
| ✅ **Runtimes en EOL que quedan** | **0** |

### Los runtimes que estaban sin parches

| Runtime | Antes | Ahora | Por qué era urgente |
| :--- | :--- | :--- | :--- |
| **Go** | 1.21 / 1.23 | **1.27** | EOL desde 2024-08-13. OSV reportaba **72 advisories de stdlib** |
| **Node.js** | 20 | **24 LTS** | EOL desde 2026-04-30 |
| **.NET** | net6.0 / net9.0 | **net10.0** | .NET 6 llevaba **2 años sin parches** |
| **Ruby** | 3.2 | **3.4** | EOL desde 2026-03-31 |
| **Alpine** | 3.20 | **3.23.7** | Sin parches desde 2026-04-01 |
| **PHP** | 8.2 | **8.4** | Soporte activo cerrado en 2024-12-31 |
| **Python** | 3.11 (Debian 12) | **3.13** (Debian 13) | En modo solo-seguridad |

Y además: Rust 1.83 → 1.99, Erlang/OTP 27 → 28, Elixir 1.17 → 1.18, Crystal 1.14 → 1.22, Swift 6.0 → 6.2, Gradle 8.11 → 8.14.

### Los agujeros más graves que se cerraron

- **RCE sin autenticar** en la Image Optimization API de Next.js — dos vías distintas, vía SVG y vía AVIF (`GHSA-2464-fhr4-w9xw`, `GHSA-2xp9-vwfh-vxw4`).
- **Bypass de autorización en gRPC** por falta de barra inicial en `:path` (`CVE-2026-33186`, CRITICAL).
- **Spoofing de IP** con direcciones IPv4 mapeadas en IPv6 (`GHSA-jqcg-44mw-7w3h`, CRITICAL) — lo arrastraba `express` incluso en su última versión 4.x, así que se fija por `override`.
- **Raíces de CA comprometidas** en el bundle de `certifi` (`GHSA-6q48-6c7w-9gw2`, CRITICAL).
- **Confusión de certificados TLS** por codificación IDNA 2003 en `anyio` (`GHSA-82r6-8w77-94w6`, CRITICAL).

### Cadena de suministro: `npm` fuera del laboratorio

`npm` **no se invoca en ninguna superficie** del repositorio. pnpm 11 se activa por `corepack`, y la política vive en un `pnpm-workspace.yaml` por paquete:

```yaml
onlyBuiltDependencies: []   # ningún paquete ejecuta postinstall/preinstall
minimumReleaseAge: 1440     # cuarentena de 24 h antes de instalar algo recién publicado
```

Esas dos líneas son la defensa concreta contra campañas tipo **Shai-Hulud**: el vector es un `postinstall` en un paquete recién comprometido, y aquí no se ejecutan scripts ni se instala nada con menos de 24 h de vida. Los **9 paquetes Node** cierran con `pnpm audit` sin vulnerabilidades, y los **8 locks de Python** llevan hash SHA256 en sus 162 paquetes.

### Una base de datos de advisories no basta

Al pasar el pipeline, `bundler-audit` tumbó el job de Ruby con **cuatro advisories de `rack` 3.2.6 publicados ese mismo día** — uno de ellos HIGH, agotamiento de memoria en el parser multipart. La consulta a OSV para esa misma versión devolvía **cero**: su `ruby-advisory-db` iba más fresca. Se corrigió subiendo a 3.2.8 y fijando el piso en el `Gemfile`.

Por eso los auditores nativos de cada ecosistema (`bundler-audit`, `govulncheck`, `pnpm audit`, `cargo audit`, `pip-audit`) siguen en CI y **bloqueando**: no son redundantes con una consulta centralizada.

### Cómo se evita que esto vuelva a envejecer

Cada caso declara su propio **manifiesto de seguridad** (`cases/NN-*/security.yml`): de qué versión viene cada runtime y cada dependencia, a cuál va, qué advisories cierra y por qué. El guardrail `scripts/validate_security_manifests.py` lo cruza en CI contra los Dockerfiles, el compose y los manifiestos de proyecto, y **falla el pipeline** si el manifiesto va por delante del código o si alguien reintroduce una versión declarada abandonada.

> 📄 **Informe completo, método de verificación y alcance**: [docs/CVE_REMEDIATION_v4.11.0.md](docs/CVE_REMEDIATION_v4.11.0.md) — incluye qué **no** se cambió y por qué, y separa lo verificado con ejecución real de lo que queda en manos del pipeline.

---

## 📋 Tabla de Contenidos

- [🛡️ Remediación de CVE — ningún runtime en EOL (v4.11.0)](#️-remediación-de-cve--ningún-runtime-en-eol-v4110)
- [🚀 Quickstart](#-quickstart)
- [🧩 Casos de Integración (Tech Matrix)](#-casos-de-integración-tech-matrix)
- [🛡️ Modelo de Seguridad Runtime](#️-modelo-de-seguridad-runtime)
- [🏢 Superficies de Riesgo (No exponer a Internet)](#-superficies-de-riesgo-no-exponer-a-internet)
- [🏗️ Arquitectura y Patrones](#️-arquitectura-y-patrones)
- [⚙️ Comandos Útiles](#️-comandos-útiles)
- [📚 Documentación Relacionada](#-documentación-relacionada)

---

## 🚀 Quickstart

> [!TIP]
> Este repositorio está diseñado para ejecutarse exclusivamente en un entorno de desarrollo local (**localhost**).

### 1. Modo Seguro por Defecto (Default)

```bash
cp .env.example .env
docker-compose up -d
```

Este comando levanta el núcleo del laboratorio:

- 🌐 **n8n**: `http://localhost:5678`
- 🖥️ **Master Dashboard**: `http://localhost:8080` *(con detección automática de casos OFFLINE/READY, contadores en vivo, modal con `docker-compose --profile caseXX up -d` para levantar lo que falte y badges de RAM por caso — v4.3.0)*
- 🔒 **Seguridad**: Puertos bindeados solo a `127.0.0.1`.

### 2. Demo Local Completa (Mode: Full)

```bash
cp .env.demo.example .env
make up
```

`make up` activa el perfil `full`, activando todos los casos y servicios de observabilidad (Prometheus/Grafana).

---

## 🧩 Casos de Integración (Tech Matrix)

El ecosistema demuestra cómo n8n puede actuar como un puente agnóstico entre cualquier tecnología.

| ID | 📤 Origen (Emisor) | 🌉 Puente | 📥 Destino (Receptor) | 📁 Persistencia | 🏷️ Perfil | 📐 Diagrama |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | `Python (Pydantic)` | **n8n** | `PHP Vanilla` | 🐬 **MySQL** | `case01` | [📐 Ver](cases/01-python-to-php/ARCHITECTURE.md) |
| **02** | `Python` | **n8n** | `Go (Fiber/Gin)` | 🍃 **MariaDB** | `case02` | [📐 Ver](cases/02-python-to-go/ARCHITECTURE.md) |
| **03** | `Go` | **n8n** | `Node / Express` | 🐘 **PostgreSQL** | `case03` | [📐 Ver](cases/03-go-to-node/ARCHITECTURE.md) |
| **04** | `Node.js` | **n8n** | `FastAPI` | 📂 **SQLite** | `case04` | [📐 Ver](cases/04-node-to-fastapi/ARCHITECTURE.md) |
| **05** | `Laravel` | **n8n** | `React / Node` | 🍃 **MongoDB** | `case05` | [📐 Ver](cases/05-laravel-to-react/ARCHITECTURE.md) |
| **06** | `Go` | **n8n** | `Symfony` | 🏎️ **Redis** | `case06` | [📐 Ver](cases/06-go-to-symfony/ARCHITECTURE.md) |
| **07** | `Rust` | **n8n** | `Ruby (Sinatra)` | 👁️ **Cassandra** | `case07` | [📐 Ver](cases/07-rust-to-ruby/ARCHITECTURE.md) |
| **08** | `C# (.NET)` | **n8n** | `Flask` | 🏢 **SQL Server** | `case08` | [📐 Ver](cases/08-csharp-to-flask/ARCHITECTURE.md) |
| **09** | `Python` | **n8n** | `FastAPI Gateway` | 🦆 **DuckDB** | `case09` | [📐 Ver](cases/09-python-to-gateway/ARCHITECTURE.md) |
| **10** | `Java (Spring)` | **n8n** | `Kotlin (Ktor)` | 🐘 **PostgreSQL** | `case10` | [📐 Ver](cases/10-java-to-kotlin/ARCHITECTURE.md) |
| **11** | `Elixir` | **n8n** | `Erlang (Cowboy)` | 🟣 **Mnesia** | `case11` | [📐 Ver](cases/11-elixir-to-erlang/ARCHITECTURE.md) |
| **12** | `Python (LLM)` | **n8n** | `FastAPI RAG` | 🧠 **pgvector** | `case12` | [📐 Ver](cases/12-python-to-rag/ARCHITECTURE.md) |
| **13** | `Node + Kafka` | **n8n** | `Go consumer` | 📊 **ClickHouse** | `case13` | [📐 Ver](cases/13-node-to-go-kafka/ARCHITECTURE.md) |
| **14** | `Next.js 15` | **n8n** | `Supabase (PostgREST)` | 🟢 **Postgres + RLS** | `case14` | [📐 Ver](cases/14-nextjs-to-supabase/ARCHITECTURE.md) |
| **15** | `Go (gRPC)` | **n8n** | `Python (gRPC)` | 🪳 **CockroachDB** | `case15` | [📐 Ver](cases/15-grpc-go-to-python/ARCHITECTURE.md) |
| **16** | `Apollo (GraphQL)` | **n8n** | `Hasura` | 📈 **TimescaleDB** | `case16` | [📐 Ver](cases/16-graphql-to-hasura/ARCHITECTURE.md) |
| **17** | `Rust (MQTT)` | **n8n** | `Node + InfluxDB` | 📊 **InfluxDB** | `case17` | [📐 Ver](cases/17-mqtt-rust-to-node/ARCHITECTURE.md) |
| **18** | `Zig` | **n8n** | `Crystal (Kemal)` | 🕸️ **Neo4j** | `case18` | [📐 Ver](cases/18-zig-to-crystal/ARCHITECTURE.md) |
| **20** | `Swift` | **n8n** | `Dart (Shelf)` | 🔥 **Firestore (emu)** | `case20` | [📐 Ver](cases/20-swift-to-dart/ARCHITECTURE.md) |

> [!TIP]
> **Lote 1** (`v4.5.0`): 11, 16, 17. **Lote 2** (`v4.6.0`): 10, 12, 18. **Lote 3** (`v4.7.0`): 15, 20. **Lote 4** (`v4.8.0`): 13, 14. **Auditoría Docker** (`v4.9.0`): los 19 casos verificados end-to-end uno a uno con Docker (persistencia real por cada motor), corrigiendo bugs reales de arranque y de healthcheck — detalle en [docs/AUDIT_v4.9.0.md](docs/AUDIT_v4.9.0.md). **19 de 20 casos operativos** vía `docker-compose --profile caseNN up -d`. Puertos por la regla `8080 + id` (ver [docs/PORTS.md](docs/PORTS.md)).

### 🧪 Único caso pendiente

| ID | 📤 Origen (Emisor) | 🌉 Puente | 📥 Destino (Receptor) | 📁 Persistencia | 📌 Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **19** | `F# (.NET)` | **n8n** | `Clojure (Ring)` | ⏳ **XTDB** | 🧪 Código listo, verificación pendiente |

> [!NOTE]
> El **caso 19** tiene el código completo (bug de arranque AOT ya corregido) pero queda pendiente de verificación end-to-end. Ver [docs/PLANNED_CASES.md](docs/PLANNED_CASES.md) y [ROADMAP.md](ROADMAP.md).

---

## 🛡️ Modelo de Seguridad Runtime

> [!IMPORTANT]
> A partir de la v4.2.0, el laboratorio ha pasado por una auditoría completa de 8 capas (contenedor, red, credenciales, servidor web, herramientas, autenticación, CI/CD y cadena de suministro).

### ✅ Qué está protegido

- **Binding de Red**: Todos los contenedores se publican únicamente en `127.0.0.1`.
- **Secretos**: Contraseñas y API Keys gestionadas vía `.env`, nunca hardcodeadas. Gitleaks detecta fugas en el historial.
- **Opt-in Observability**: Grafana y Prometheus solo se activan con `--profile observability`.
- **HTTP Security Headers**: Todos los servicios Apache sirven `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, `Referrer-Policy` y `Permissions-Policy`. Listado de directorios deshabilitado.
- **Caddy Edge Proxy**: HTTPS + Basic Auth + HSTS + CSP + Permissions-Policy completos.
- **Supply Chain**: Trivy v0.35.0, pip-audit, Gitleaks, detección de Unicode bidi (CVE-2021-42574) y ofuscación base64 en CI.
- **Versiones de runtime sin deuda**: ningún lenguaje del laboratorio corre sobre una versión en EOL, y el guardrail `validate_security_manifests.py` falla el pipeline si alguna vuelve a quedarse atrás. Ver [Remediación de CVE](#️-remediación-de-cve--ningún-runtime-en-eol-v4110).
- **Cero `npm`**: pnpm 11 vía `corepack`, con scripts de instalación bloqueados y cuarentena de 24 h sobre publicaciones nuevas (mitigación Shai-Hulud). Builds con `--frozen-lockfile`.
- **Dependencias con hash**: los 8 `requirements.txt` se compilan con `uv --generate-hashes`, lo que fuerza el modo `--require-hashes` de pip; los 9 paquetes Node llevan `pnpm-lock.yaml` commiteado y auditado.
- **Dependabot**: PRs automáticos para **31 manifiestos en 10 ecosistemas** (pip, docker, gomod, cargo, nuget, gradle, bundler, pub, github-actions y `npm` —que rastrea los `pnpm-lock.yaml` sin ejecutar npm—), cubriendo los 20 casos.
- **Line endings**: `.gitattributes` garantiza LF en scripts shell para evitar `bad interpreter` en contenedores Linux.
- **Proceso no-root**: Todos los contenedores corren como usuario sin privilegios.

---

## 🏢 Superficies de Riesgo (No exponer a Internet)

| Servicio | Puerto | Riesgo |
| :--- | :--- | :--- |
| **n8n** | `5678` | Alto (Orquestación maestra) |
| **Grafana** | `3000` | Medio (Métricas y visualización) |
| **Dashboards** | `8080-8100` | Bajo (Visualización de casos) |
| **cAdvisor** | `9091` | **Muy Alto** (Monta `/var/run/docker.sock`) |

---

## 🏗️ Arquitectura y Patrones

El sistema no es solo una integración; es un catálogo vivo con **11 patrones arquitectónicos**:

1. **Microservicios**: 40+ contenedores independientes.
2. **Event-Driven**: Comunicación 100% vía Webhooks.
3. **Mediador**: n8n centraliza la lógica empresarial.
4. **Resiliencia**: Idempotencia, Circuit Breaker y DLQ.
5. **Persistencia Políglota**: 18+ motores de bases de datos distintos.
6. *...y más!* Lee el detalle en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## ⚙️ Comandos Útiles

| Comando | Acción |
| :--- | :--- |
| `make up` | Levanta demo completa (full) |
| `make up-secure` | Levanta core mínimo y seguro |
| `make demo` | Lanza una prueba del Caso 01 |
| `make doctor` | Diagnóstico de salud del entorno |
| `python verify_n8n.py` | Verifica workflows instalados |

---

## 📚 Documentación Relacionada

| Tipo | Documento |
| :--- | :--- |
| 🛡️ **Seguridad** | [SECURITY.md](SECURITY.md) \| [docs/RUNTIME_SECURITY.md](docs/RUNTIME_SECURITY.md) \| [docs/CVE_REMEDIATION_v4.11.0.md](docs/CVE_REMEDIATION_v4.11.0.md) |
| 🏗️ **Arquitectura** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| ☁️ **Migración a AWS** | [docs/AWS_MIGRATION.md](docs/AWS_MIGRATION.md) |
| 🎓 **Guías** | [docs/INSTALL.md](docs/INSTALL.md) \| [docs/VERIFICATION_GUIDE.md](docs/VERIFICATION_GUIDE.md) |
| 🛠️ **Operación** | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) \| [n8n/README.md](n8n/README.md) |
| 🛣️ **Progreso** | [ROADMAP.md](ROADMAP.md) |
| 🌐 **Sitio publicado** | [vladimiracunadev-create.github.io/social-bot-scheduler](https://vladimiracunadev-create.github.io/social-bot-scheduler/) |

---

*Coded with ❤️ by Vladimir Acuña*
