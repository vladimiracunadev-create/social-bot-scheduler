# 🚀 Social Bot Scheduler

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Hub](https://img.shields.io/badge/Docker-Ready-blue.svg?logo=docker&logoColor=white)](https://hub.docker.com/)
[![Version](https://img.shields.io/badge/version-4.0.0-green.svg)](https://github.com/vladimiracunadev-create/social-bot-scheduler/releases)
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
- 🖥️ **Master Dashboard**: `http://localhost:8080`
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

| ID | 📤 Origen (Emisor) | 🌉 Puente | 📥 Destino (Receptor) | 📁 Persistencia | 🏷️ Perfil |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | `Python (Pydantic)` | **n8n** | `PHP Vanilla` | 🐬 **MySQL** | `case01` |
| **02** | `Python` | **n8n** | `Go (Fiber/Gin)` | 🍃 **MariaDB** | `case02` |
| **03** | `Go` | **n8n** | `Node / Express` | 🐘 **PostgreSQL** | `case03` |
| **04** | `Node.js` | **n8n** | `FastAPI` | 📂 **SQLite** | `case04` |
| **05** | `Laravel` | **n8n** | `React / Node` | 🍃 **MongoDB** | `case05` |
| **06** | `Go` | **n8n** | `Symfony` | 🏎️ **Redis** | `case06` |
| **07** | `Rust` | **n8n** | `Ruby (Sinatra)` | 👁️ **Cassandra** | `case07` |
| **08** | `C# (.NET)` | **n8n** | `Flask` | 🏢 **SQL Server** | `case08` |
| **09** | `Python` | **n8n** | `FastAPI Gateway` | 🦆 **DuckDB** | `case09` |

---

## 🛡️ Modelo de Seguridad Runtime

> [!IMPORTANT]
> A partir de la v4.0.0, la seguridad `secure-by-default` es la prioridad del laboratorio.

### ✅ Qué es más seguro ahora:
- **Binding de Red**: Todos los contenedores se publican únicamente en `127.0.0.1`.
- **Secretos**: Las contraseñas (DB, Grafana, API Keys) se gestionan vía `.env` y no están hardcodeadas en el Compose.
- **Opt-in Observability**: Grafana y Prometheus ya no arrancan por defecto para minimizar la superficie de exposición.
- **Caddy Edge Proxy**: Opción de publicar servicios vía HTTPS con Basic Auth si se requiere acceso remoto controlado.

---

## 🏢 Superficies de Riesgo (No exponer a Internet)

| Servicio | Puerto | Riesgo |
| :--- | :--- | :--- |
| **n8n** | `5678` | Alto (Orquestación maestra) |
| **Grafana** | `3000` | Medio (Métricas y visualización) |
| **Dashboards** | `8080-8090` | Bajo (Visualización de casos) |
| **cAdvisor** | `8089` | **Muy Alto** (Monta `/var/run/docker.sock`) |

---

## 🏗️ Arquitectura y Patrones

El sistema no es solo una integración; es un catálogo vivo con **11 patrones arquitectónicos**:

1.  **Microservicios**: 20+ contenedores independientes.
2.  **Event-Driven**: Comunicación 100% vía Webhooks.
3.  **Mediador**: n8n centraliza la lógica empresarial.
4.  **Resiliencia**: Idempotencia, Circuit Breaker y DLQ.
5.  **Persistencia Políglota**: 9 motores de bases de datos distintos.
6.  *...y más!* Lee el detalle en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

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
| 🎓 **Guías** | [docs/INSTALL.md](docs/INSTALL.md) \| [docs/VERIFICATION_GUIDE.md](docs/VERIFICATION_GUIDE.md) |
| 🛠️ **Operación** | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) \| [n8n/README.md](n8n/README.md) |
| 🛣️ **Progreso** | [ROADMAP.md](ROADMAP.md) |

---

*Coded with ❤️ by Vladimir Acuña*
