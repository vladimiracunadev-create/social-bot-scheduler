# 🚀 Social Bot Scheduler

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-4.11.0-green.svg)](https://github.com/vladimiracunadev-create/social-bot-scheduler/releases)
[![Sitio](https://img.shields.io/badge/Sitio-GitHub%20Pages-6366f1.svg?logo=githubpages&logoColor=white)](https://vladimiracunadev-create.github.io/social-bot-scheduler/)
[![Seguridad](https://img.shields.io/badge/seguridad-hardened-critical.svg?logo=shieldsdotio&logoColor=white)](SECURITY.md)
[![Runtimes sin EOL](https://img.shields.io/badge/runtimes-0%20en%20EOL-success.svg?logo=shieldsdotio&logoColor=white)](docs/VERSION_UPGRADES.md)

Laboratorio de integración industrial **multi-lenguaje** y **multi-servicio**. El **Social Bot Scheduler** actúa como una **Matriz Tecnológica** donde **n8n** orquesta la comunicación entre bots emisores y receptores políglotas.

> [!NOTE]
> **¿Qué significa «hardened»?** Aislamiento runtime (todo publicado solo en `127.0.0.1`, procesos no-root, sin secretos en el código) y una cadena de suministro con auditores **bloqueantes** en CI: `pip-audit`, `pnpm audit`, `govulncheck`, `cargo audit`, `bundler-audit`, `dotnet list package --vulnerable`, más Trivy sobre la imagen y Gitleaks sobre el historial. El detalle, capa por capa, en [SECURITY.md](SECURITY.md).

---

## 📋 Tabla de Contenidos

- [🛡️ Seguridad de versiones: remediación de CVE](#️-seguridad-de-versiones-remediación-de-cve)
- [🚀 Quickstart](#-quickstart)
- [🧩 Casos de Integración (Tech Matrix)](#-casos-de-integración-tech-matrix)
- [🛡️ Modelo de Seguridad Runtime](#️-modelo-de-seguridad-runtime)
- [🏢 Superficies de Riesgo (No exponer a Internet)](#-superficies-de-riesgo-no-exponer-a-internet)
- [🏗️ Arquitectura y Patrones](#️-arquitectura-y-patrones)
- [⚙️ Comandos Útiles](#️-comandos-útiles)
- [📚 Documentación Relacionada](#-documentación-relacionada)

---

## 🛡️ Seguridad de versiones: remediación de CVE

<!-- UPGRADES:INICIO (generado por scripts/build_upgrade_docs.py) -->

**Un runtime en fin de vida no arrastra «un CVE»: arrastra todos los publicados desde su último parche.** Por eso la revisión de la v4.11.0 recorrió los 20 casos lenguaje por lenguaje, hasta que ninguno quedara sobre una versión sin soporte.

| Advisories cerrados | Cambios de runtime | Dependencias revisadas | Runtimes en EOL | Hallazgos abiertos |
| ---: | ---: | ---: | ---: | ---: |
| **78** (41 con CVE) | **51** | **92** | **0** | **5** (declarados) |

«Casos» es a cuántos de los 20 afecta el cambio; cada página lista cuáles. Ahí están también la ventana de soporte con su gráfico, la justificación, la tabla de implementación fichero a fichero y el riesgo de ruptura.

| Cambio | Casos | Advisories | Por qué | Documentación |
| :--- | ---: | ---: | :--- | :--- |
| 🐹 **Go 1.21 / 1.23 → 1.27** | 5 | 12 | EOL desde 2024-08-13; 72 advisories de stdlib | [Ver detalle](docs/upgrades/go.md) |
| 🟩 **Node.js 20 → 24 LTS** | 7 | 31 | EOL desde 2026-04-30 | [Ver detalle](docs/upgrades/nodejs.md) |
| 🐍 **Python 3.11 → 3.13 (Debian 12 → 13)** | 7 | 15 | Solo-seguridad; base Debian 12 → 13 | [Ver detalle](docs/upgrades/python.md) |
| 🐘 **PHP 8.2 → 8.4** | 3 | — | Soporte activo cerrado en 2024-12-31 | [Ver detalle](docs/upgrades/php.md) |
| 💎 **Ruby 3.2 → 3.4** | 1 | 4 | EOL desde 2026-03-31 | [Ver detalle](docs/upgrades/ruby.md) |
| 🟦 **.NET 6 / 9 → 10 (LTS)** | 2 | — | .NET 6 llevaba 2 años sin parches | [Ver detalle](docs/upgrades/dotnet.md) |
| 🏔️ **Alpine 3.20 → 3.23.7** | 5 | — | Sin parches desde 2026-04-01 | [Ver detalle](docs/upgrades/alpine.md) |
| 🦀 **Rust 1.83 → 1.99** | 2 | — | 16 releases de retraso | [Ver detalle](docs/upgrades/rust.md) |
| 💜 **Erlang/OTP 27 → 28 · Elixir 1.17 → 1.18** | 1 | 3 | `cowboy` con 3 advisories, uno HIGH | [Ver detalle](docs/upgrades/beam.md) |
| 💠 **Crystal 1.14 → 1.22** | 1 | — | `kemal` 1.15 exige Crystal ≥ 1.12 | [Ver detalle](docs/upgrades/crystal.md) |
| 🧡 **Swift 6.0 → 6.2** | 1 | — | 2 años de retraso | [Ver detalle](docs/upgrades/swift.md) |
| 🎯 **Dart y Debian: fuera los tags flotantes** | 1 | — | Tags flotantes: build irreproducible | [Ver detalle](docs/upgrades/dart.md) |
| ☕ **JVM: Temurin 21 se queda, Gradle 8.11 → 8.14** | 3 | 13 | Jackson, pgjdbc y Jetty vulnerables | [Ver detalle](docs/upgrades/jvm.md) |
| 📦 **pnpm 10 → 11: npm fuera del laboratorio** | 8 | — | Mitigación Shai-Hulud + npm fuera | [Ver detalle](docs/upgrades/pnpm.md) |
| ⚡ **Zig 0.13: por qué NO se subió** | 1 | — | **No se subió**: sin advisory y rompe el build | [Ver detalle](docs/upgrades/zig.md) |

> 📘 **Procedimiento, historial y hallazgos abiertos**: [docs/VERSION_UPGRADES.md](docs/VERSION_UPGRADES.md) — el documento vivo que explica cómo se hace una subida de versión aquí, para este pase y los siguientes.

<!-- UPGRADES:FIN -->

---

## 🚀 Quickstart

> [!TIP]
> Este repositorio está diseñado para ejecutarse exclusivamente en un entorno de desarrollo local (**localhost**).

### 1. Modo Seguro por Defecto (Default)

```bash
cp .env.example .env
docker compose up -d
```

Este comando levanta el núcleo del laboratorio:

- 🌐 **n8n**: `http://localhost:5678`
- 🖥️ **Master Dashboard**: `http://localhost:8080` *(con detección automática de casos OFFLINE/READY, contadores en vivo, modal con `docker compose --profile caseXX up -d` para levantar lo que falte y badges de RAM por caso)*
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
> **Lote 1** (`v4.5.0`): 11, 16, 17. **Lote 2** (`v4.6.0`): 10, 12, 18. **Lote 3** (`v4.7.0`): 15, 20. **Lote 4** (`v4.8.0`): 13, 14. **Auditoría Docker** (`v4.9.0`): los 19 casos verificados end-to-end uno a uno con Docker (persistencia real por cada motor), corrigiendo bugs reales de arranque y de healthcheck — detalle en [docs/AUDIT_v4.9.0.md](docs/AUDIT_v4.9.0.md). **19 de 20 casos operativos** vía `docker compose --profile caseNN up -d`. Puertos por la regla `8080 + id` (ver [docs/PORTS.md](docs/PORTS.md)).

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
- **Versiones sin deuda**: ningún runtime corre sobre una versión en EOL, cada cambio queda registrado en el `security.yml` de su caso y el guardrail `validate_security_manifests.py` falla el pipeline si la documentación y el código se separan. Ver [Seguridad de versiones](#️-seguridad-de-versiones-remediación-de-cve).
- **Instalación reproducible**: `npm` no se invoca en ninguna superficie — pnpm vía `corepack`, con los scripts de instalación bloqueados y cuarentena sobre publicaciones recientes. Los locks de Python llevan hash SHA256 y los de Node van commiteados y auditados; los builds usan `--frozen-lockfile`.
- **Dependabot**: cubre los manifiestos de los 20 casos en 10 ecosistemas (pip, docker, gomod, cargo, nuget, gradle, bundler, pub, github-actions y `npm` —que rastrea los `pnpm-lock.yaml` sin ejecutar npm—).
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

El sistema no es solo una integración; es un catálogo vivo de patrones. Los que más se notan al leer el código:

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
| 🛡️ **Seguridad** | [SECURITY.md](SECURITY.md) \| [docs/RUNTIME_SECURITY.md](docs/RUNTIME_SECURITY.md) \| [docs/VERSION_UPGRADES.md](docs/VERSION_UPGRADES.md) |
| 🏗️ **Arquitectura** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| ☁️ **Migración a AWS** | [docs/AWS_MIGRATION.md](docs/AWS_MIGRATION.md) |
| 🎓 **Guías** | [docs/INSTALL.md](docs/INSTALL.md) \| [docs/VERIFICATION_GUIDE.md](docs/VERIFICATION_GUIDE.md) |
| 🛠️ **Operación** | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) \| [n8n/README.md](n8n/README.md) |
| 🛣️ **Progreso** | [ROADMAP.md](ROADMAP.md) |
| 🌐 **Sitio publicado** | [vladimiracunadev-create.github.io/social-bot-scheduler](https://vladimiracunadev-create.github.io/social-bot-scheduler/) |

---

*Coded with ❤️ by Vladimir Acuña*
