# 🚀 Social Bot Scheduler

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Hub](https://img.shields.io/badge/Docker-Ready-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/)
[![Version](https://img.shields.io/badge/version-4.5.1-green.svg)](https://github.com/vladimiracunadev-create/social-bot-scheduler/releases)
[![Security: Hardened](https://img.shields.io/badge/Security-Hardened-🛡️?color=red&labelColor=black)](SECURITY.md)

Laboratorio de integración industrial **multi-lenguaje** y **multi-servicio**. El **Social Bot Scheduler** actúa como una **Matriz Tecnológica** donde **n8n** orquesta la comunicación entre bots emisores y receptores políglotas.

> [!NOTE]
> **¿Qué significa "🛡️ Security: Hardened"?**
> Este repositorio implementa una política de **Aislamiento Runtime**: Todos los servicios están limitados a `localhost`, usan imágenes base seguras con escaneos de vulnerabilidades manuales (Trivy) y no contienen secretos hardcodeados, mitigando riesgos de cadena de suministro.

---

## 📋 Tabla de Contenidos

- [🚀 Quickstart](#-quickstart)
- [🧩 Casos de Integración](#-casos-de-integración)
- [🛡️ Modelo de Seguridad Runtime](#️-modelo-de-seguridad-runtime)
- [📊 Observabilidad y Riesgo](#-observabilidad-y-riesgo)
- [🏗️ Arquitectura](#️-arquitectura)
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
| **11** | `Elixir` | **n8n** | `Erlang (Cowboy)` | 🟣 **Mnesia** | `case11` | [📐 Ver](cases/11-elixir-to-erlang/ARCHITECTURE.md) |
| **16** | `Apollo (GraphQL)` | **n8n** | `Hasura` | 📈 **TimescaleDB** | `case16` | [📐 Ver](cases/16-graphql-to-hasura/ARCHITECTURE.md) |
| **17** | `Rust (MQTT)` | **n8n** | `Node + InfluxDB` | 📊 **InfluxDB** | `case17` | [📐 Ver](cases/17-mqtt-rust-to-node/ARCHITECTURE.md) |

> [!TIP]
> **Casos 11, 16 y 17** (`v4.5.0`) son el **Lote 1** del roadmap v5.0, ya operativos: `docker-compose --profile case11|case16|case17 up -d` (puertos `8091`, `8096`, `8097`).

### 🚧 Casos planificados (v5.0 — pendientes de implementación)

| ID | 📤 Origen (Emisor) | 🌉 Puente | 📥 Destino (Receptor) | 📁 Persistencia | 📌 Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **10** | `Java (Spring Boot)` | **n8n** | `Kotlin (Ktor)` | 🐘 **PostgreSQL** | 🚧 Planned |
| **12** | `Python (LLM)` | **n8n** | `FastAPI + RAG` | 🧠 **pgvector** | 🚧 Planned |
| **13** | `Node.js + Kafka` | **n8n** | `Go consumer` | 🟡 **ClickHouse** | 🚧 Planned |
| **14** | `Next.js 15` | **n8n** | `Supabase Edge Fn` | 🟢 **Supabase (Postgres + RLS)** | 🚧 Planned |
| **15** | `Go (gRPC)` | **n8n** | `Python (gRPC)` | 🪳 **CockroachDB** | 🚧 Planned |
| **18** | `Zig` | **n8n** | `Crystal (Kemal)` | 🕸️ **Neo4j** | 🚧 Planned |
| **19** | `F# (.NET)` | **n8n** | `Clojure (Ring)` | ⏳ **XTDB** | 🚧 Planned |
| **20** | `Swift (Vapor)` | **n8n** | `Dart (Shelf)` | 🔥 **Firebase Emul.** | 🚧 Planned |

> [!NOTE]
> Los **8 casos restantes** (10, 12–15, 18–20) contienen únicamente scaffolding y documentación de diseño. Ver [docs/PLANNED_CASES.md](docs/PLANNED_CASES.md) como single source of truth, y [ROADMAP.md](ROADMAP.md) para priorización.

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
- **Dependabot**: PRs automáticos para 11 ecosistemas (pip, docker, gomod, cargo, npm, github-actions).
- **Line endings**: `.gitattributes` garantiza LF en scripts shell para evitar `bad interpreter` en contenedores Linux.
- **Proceso no-root**: Todos los contenedores corren como usuario sin privilegios.

---

## 🏢 Superficies de Riesgo (No exponer a Internet)

| Servicio | Puerto | Riesgo |
| :--- | :--- | :--- |
| **n8n** | `5678` | Alto (Orquestación maestra) |
| **Grafana** | `3000` | Medio (Métricas y visualización) |
| **Dashboards** | `8080-8093` | Bajo (Visualización de casos) |
| **cAdvisor** | `9091` | **Muy Alto** (Monta `/var/run/docker.sock`) |

---

## 🏗️ Arquitectura y Patrones

El sistema no es solo una integración; es un catálogo vivo con **11 patrones arquitectónicos**:

1. **Microservicios**: 20+ contenedores independientes.
2. **Event-Driven**: Comunicación 100% vía Webhooks.
3. **Mediador**: n8n centraliza la lógica empresarial.
4. **Resiliencia**: Idempotencia, Circuit Breaker y DLQ.
5. **Persistencia Políglota**: 12 motores de bases de datos distintos.
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
| 🛡️ **Seguridad** | [SECURITY.md](SECURITY.md) \| [docs/RUNTIME_SECURITY.md](docs/RUNTIME_SECURITY.md) |
| 🏗️ **Arquitectura** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| ☁️ **Migración a AWS** | [docs/AWS_MIGRATION.md](docs/AWS_MIGRATION.md) |
| 🎓 **Guías** | [docs/INSTALL.md](docs/INSTALL.md) \| [docs/VERIFICATION_GUIDE.md](docs/VERIFICATION_GUIDE.md) |
| 🛠️ **Operación** | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) \| [n8n/README.md](n8n/README.md) |
| 🛣️ **Progreso** | [ROADMAP.md](ROADMAP.md) |

---

*Coded with ❤️ by Vladimir Acuña*
