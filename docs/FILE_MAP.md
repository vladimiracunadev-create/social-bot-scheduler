# 🗺️ Mapa Completo del Sistema — Archivo por Archivo

> **Propósito**: Este documento explica cada archivo y directorio del repositorio, su rol en la arquitectura, y por qué existe. Diseñado para que cualquier persona (desarrollador, reclutador o auditor) entienda el sistema completo sin necesidad de leer el código fuente.

---

## 📐 Estructura General

```
social-bot-scheduler/
├── 🏠 Raíz ................... Configuración, orquestación y entrada principal
├── 📦 cases/ ................. 8 Casos de Integración (Origen → n8n → Destino)
├── 📚 docs/ .................. Documentación técnica y guías
├── 🔄 n8n/ ................... Workflows de orquestación (JSON exportados)
├── 📊 grafana/ ............... Dashboards y datasources de monitoreo
├── 📈 prometheus/ ............ Configuración de métricas
├── ☸️ k8s/ ................... Manifiestos de Kubernetes (producción)
├── 📝 articulo/ .............. Artículo técnico para LinkedIn
└── 🔧 .github/ ............... CI/CD (GitHub Actions)
```

---

## 🏠 Archivos Raíz (Orquestación y Configuración)

### Infraestructura Docker

| Archivo | Importancia | Descripción |
|---------|:-----------:|-------------|
| `docker-compose.yml` | 🔴 **Crítico** | Define los servicios del ecosistema completo: 9 receptores, 8 bases de datos externas, n8n, Grafana, Prometheus, cAdvisor, Caddy edge proxy y el dashboard maestro. Contiene perfiles `caseXX`, `full`, `observability` y `edge`. |
| `docker-compose.dev.yml` | 🟡 Media | Override para desarrollo local. Añade hot-reload y puertos de depuración. |
| `Dockerfile` | 🟡 Media | Imagen Docker para el dashboard maestro (`master-dashboard`). |
| `Makefile` | 🟢 Alta | Automatización de comandos frecuentes: `make up`, `make up-secure`, `make up-observability`, `make up-edge`, `make clean` y `make nuke`. |

### Automatización y CLI

| Archivo | Importancia | Descripción |
|---------|:-----------:|-------------|
| `hub.py` | 🔴 **Crítico** | **HUB CLI** — Centro de control del sistema. Permite diagnosticar, levantar, limpiar y auditar todo el ecosistema con comandos como `python hub.py up --full`, `--observability` o `--edge`. Es el "cerebro operacional" del proyecto. |
| `hub.sh` | 🟡 Media | Wrapper Bash del HUB CLI para sistemas Linux/Mac. |
| `hub.ps1` | 🟡 Media | Wrapper PowerShell del HUB CLI para Windows. |
| `setup.py` | 🟢 Alta | Asistente interactivo de configuración inicial. Genera archivos `.env` con credenciales y URLs de webhook para cada caso. |
| `check_resources.py` | 🟡 Media | Script de diagnóstico que analiza el uso de RAM y disco de los contenedores Docker en ejecución. |

### Workflows n8n (Gestión)

| Archivo | Importancia | Descripción |
|---------|:-----------:|-------------|
| `import_workflows.py` | ?? Alta | Importa autom?ticamente los 9 workflows JSON al motor n8n v?a API REST. Esencial para el primer despliegue. |
| `generate_workflows.py` | 🟡 Media | Genera plantillas base de workflows n8n para nuevos casos de integración. |
| `check_workflows.py` | 🟡 Media | Verifica que los workflows importados estén activos y sus webhooks registrados. |
| `diagnose_n8n.py` | 🟡 Media | Diagnóstico profundo del estado de n8n: nodos registrados, credenciales, errores de arranque. |

### Verificación y Testing

| Archivo | Importancia | Descripción |
|---------|:-----------:|-------------|
| `verify_all_cases.py` | 🟢 Alta | Ejecuta una verificación end-to-end de los 8 casos: levanta el bot, envía un payload al webhook, y comprueba la respuesta del receptor. |
| `run_all_verifications.py` | 🟢 Alta | Orquestador maestro de verificaciones: ejecuta tests unitarios, de integración, y análisis de seguridad en secuencia. |
| `verify_n8n.py` | 🟡 Media | Verifica que n8n esté operativo y que los webhooks de cada caso estén accesibles. |
| `audit_schema.py` | 🟡 Media | Auditoría de esquemas JSON de los workflows para detectar incompatibilidades. |

### Configuración del Proyecto

| Archivo | Importancia | Descripción |
|---------|:-----------:|-------------|
| `pyproject.toml` | 🟡 Media | Configuración de herramientas Python (Black, pytest, mypy). Define reglas de formato y testing. |
| `requirements.txt` | 🟢 Alta | Dependencias Python del proyecto raíz (`requests`, `pydantic`, `python-dotenv`). |
| `.gitignore` | 🟡 Media | Define qué archivos NO se suben a Git: `node_modules/`, `venv/`, `n8n/data/`, `.env`. |

### Documentación Raíz

| Archivo | Importancia | Descripción |
|---------|:-----------:|-------------|
| `README.md` | 🔴 **Crítico** | Puerta de entrada principal al proyecto. Contiene visión general, instrucciones de despliegue, arquitectura resumida y enlaces a toda la documentación. |
| `CHANGELOG.md` | 🟢 Alta | Historial de cambios por versión (`v1.0.0` → `v4.0.x`). Documenta cada feature, fix y breaking change. |
| `ROADMAP.md` | 🟡 Media | Planificación a futuro: migración a K8s, integración con LangChain, soporte multi-tenant. |
| `CONTRIBUTING.md` | 🟡 Media | Guía para contribuidores: convenciones de commits, branching strategy, y code review. |
| `CODE_OF_CONDUCT.md` | 🟢 Baja | Código de conducta estándar para la comunidad del proyecto. |
| `SECURITY.md` | 🟢 Alta | Política de seguridad: cómo reportar vulnerabilidades de forma responsable. |
| `LICENSE` | 🟡 Media | Licencia del proyecto (MIT/Apache). |
| `NOTICE` | 🟢 Baja | Atribuciones legales de dependencias de terceros. |
| `index.html` | 🟢 Alta | **Dashboard Maestro** — Interfaz web unificada que muestra el estado de los 9 casos en tiempo real. |
| `llms.txt` | 🟢 Baja | Metadatos del proyecto optimizados para consumo por modelos de lenguaje (LLMs). |
| `COMO_ACTIVAR_WORKFLOWS.md` | 🟢 Alta | Guía paso a paso para importar y activar los workflows de n8n. |
| `IMPORT_WORKFLOWS.md` | 🟡 Media | Documentación técnica del proceso de importación de workflows. |
| `killed.md` | 🟢 Baja | Log de servicios terminados por el OOM Killer durante el stress test. |

---

## 📦 Casos de Integración (`cases/`)

Cada caso sigue la misma estructura de 3 carpetas:

```
cases/XX-origen-to-destino/
├── origin/     → Bot Emisor (código fuente del lenguaje de origen)
├── n8n/        → Workflow JSON del caso (lógica de orquestación)
└── dest/       → Servicio Receptor (código fuente del lenguaje destino + DB)
```

### Case 01: Python → PHP (MySQL)

| Archivo | Rol | Descripción |
|---------|-----|-------------|
| `origin/bot.py` | 🚀 Entry Point | Wrapper que manipula `PYTHONPATH` y delega a `main.py`. |
| `origin/src/social_bot/main.py` | 🧠 Bootstrap | Punto de arranque arquitectónico. Inicializa `BotService`. |
| `origin/src/social_bot/service.py` | ⚙️ Core | **Servicio de dominio**: carga posts, filtra pendientes, envía vía HTTP, persiste estado. Implementa Repository Pattern y Transaction Script. |
| `origin/src/social_bot/config.py` | 🔧 Config | Carga de variables de entorno con Pydantic Settings. |
| `origin/src/social_bot/models.py` | 📋 Modelo | DTO `Post` con validación Pydantic (id, text, channels, scheduled_at). |
| `origin/posts.json` | 💾 DB | Base de datos local en JSON con los posts a publicar. |
| `dest/index.php` | 📥 Receiver | Receptor PHP con routing manual, validación, logging y persistencia en MySQL. Implementa DLQ. |
| `dest/index.html` | 🖥️ Dashboard | Interfaz web del receptor que muestra logs en tiempo real. |
| `dest/errors.php` | 🚨 DLQ | Manejo de errores y Dead Letter Queue. |
| `n8n/*.json` | 🔄 Workflow | Lógica de transformación y enrutamiento en n8n. |

### Case 02: Python → Go (MariaDB)

| Archivo | Rol | Descripción |
|---------|-----|-------------|
| `origin/src/social_bot/main.py` | 🧠 Bootstrap | Arranque orientado a alto rendimiento. Go como receptor escala verticalmente. |
| `origin/src/social_bot/service.py` | ⚙️ Core | Cliente HTTP para el backend Go. Payload JSON estricto para `json.Unmarshal`. |
| `dest/main.go` | 📥 Receiver | **Receptor de alto rendimiento**: Goroutines, `sync.Mutex` para escritura thread-safe, reintentos de conexión a MariaDB. SQL parametrizado contra Injection. `ON DUPLICATE KEY UPDATE` para idempotencia. |
| `dest/Dockerfile` | 🐳 Build | Compilación del binario Go dentro del contenedor. |
| `dest/index.html` | 🖥️ Dashboard | Interfaz web con polling de logs. |

### Case 03: Go → Node.js (PostgreSQL)

| Archivo | Rol | Descripción |
|---------|-----|-------------|
| `origin/main.go` | 🚀 Daemon | Bot en Go con bucle infinito (30s). Binario estático sin dependencias. 12-Factor App. |
| `dest/index.js` | 📥 Receiver | **Receptor asíncrono**: Express.js + Pool PostgreSQL. Responde antes de persistir (async DB write). `ON CONFLICT DO UPDATE` para idempotencia. |
| `dest/index.html` | 🖥️ Dashboard | Dashboard Node.js con polling AJAX. |

### Case 04: Node.js → FastAPI (SQLite)

| Archivo | Rol | Descripción |
|---------|-----|-------------|
| `origin/index.js` | 🚀 Daemon | Bot en Node.js con `setInterval` y Axios. Polling no-bloqueante. |
| `dest/main.py` | 📥 Receiver | **Receptor ASGI**: FastAPI + Pydantic para validación automática de esquema. SQLite zero-config. `INSERT OR REPLACE` para idempotencia. |
| `dest/index.html` | 🖥️ Dashboard | Dashboard con fetch API. |

### Case 05: Laravel → React (MongoDB)

| Archivo | Rol | Descripción |
|---------|-----|-------------|
| `origin/ArtisanPost.php` | 🚀 Worker | Simulación de comando Artisan (`php artisan post:send`). HTTP POST con `stream_context_create` nativo (sin Guzzle). |
| `dest/server.js` | 📥 BFF | **Backend-for-Frontend**: Express + CORS + MongoDB. `upsert: true` para idempotencia. Responde antes de escribir en DB. |
| `dest/App.jsx` | 🖥️ Frontend | Componente React que consume la API `/api/logs` y renderiza el feed en tiempo real. |

### Case 06: Go → Symfony (Redis)

| Archivo | Rol | Descripción |
|---------|-----|-------------|
| `origin/main.go` | 🚀 Daemon | Bot Go compacto (estilo one-liner). Demuestra la flexibilidad sintáctica del lenguaje. |
| `dest/index.php` | 📥 Receiver | **Diseño Dual**: Clase OOP `SocialBotController` (Symfony real) + Script Procedural (Symfony Lite). Persistencia en Redis con TTL de 24h. |

### Case 07: Rust → Ruby (Cassandra)

| Archivo | Rol | Descripción |
|---------|-----|-------------|
| `origin/src/main.rs` | 🚀 Producer | **Emisor de máxima seguridad**: Ownership, `match` exhaustivo, `reqwest::blocking`. Si Rust puede enviar datos, cualquier lenguaje puede. |
| `origin/Cargo.toml` | 📦 Build | Dependencias Rust: `serde`, `reqwest`, `dotenv`. |
| `dest/app.rb` | 📥 Receiver | **Receptor minimalista**: Sinatra + Cassandra. Cola FIFO en memoria (20 posts). Rack::Protection desactivado para Docker. |
| `dest/Dockerfile` | 🐳 Build | Instalación de gems (`sinatra`, `cassandra-driver`). |

### Case 08: C# → Flask (MSSQL)

| Archivo | Rol | Descripción |
|---------|-----|-------------|
| `origin/Program.cs` | 🚀 Producer | **Emisor .NET**: `HttpClient` estático (evita Socket Exhaustion), `async/await`, `System.Text.Json`. |
| `origin/SocialBot.csproj` | 📦 Build | Configuración del proyecto .NET (target framework, dependencias). |
| `dest/app.py` | 📥 Receiver | **Receptor WSGI**: Flask + pyodbc + MSSQL. UPSERT manual con T-SQL. Retry con backoff para esperar a SQL Server. |
| `dest/Dockerfile` | 🐳 Build | Imagen Debian (no Alpine) por compatibilidad con ODBC Driver 18 de Microsoft. |

---

## 📚 Documentación Técnica (`docs/`)

| Archivo | Audiencia | Descripción |
|---------|-----------|-------------|
| `ARCHITECTURE.md` | 🏗️ Arquitectos | Diagramas del sistema, flujo de datos, y decisiones de diseño. |
| `RECRUITER.md` | 👔 Reclutadores | Evaluación técnica rápida: valor de negocio, complejidad demostrada, skills cubiertos. |
| `BEGINNERS_GUIDE.md` | 🐣 Novatos | Guía paso a paso para entender el proyecto sin experiencia previa. |
| `CASES_INDEX.md` | 📊 Referencia | Matriz técnica de los 8 casos: lenguajes, DBs, puertos, y estado. |
| `DOCKER_RESOURCES.md` | 🐳 DevOps | Análisis detallado de uso de RAM y disco. Incluye el **Stress Test Report**. |
| `RESILIENCE_GUIDE.md` | 🛡️ SREs | Guía de resiliencia: Circuit Breakers, DLQ, Idempotencia, y reintentos. |
| `GUARDRAILS.md` | 🔒 Seguridad | Implementación de guardrails: validación, sanitización, rate limiting. |
| `TROUBLESHOOTING.md` | 🔧 Soporte | Resolución de errores comunes (Docker, n8n, dependencias). |
| `VERIFICATION_GUIDE.md` | 🧪 QA | Manual de pruebas para verificar la salud del repositorio. |
| `REQUIREMENTS.md` | 💻 Instalación | Especificaciones de hardware y software recomendadas. |
| `LIMITATIONS.md` | ⚠️ Transparencia | Trade-offs y decisiones técnicas documentadas honestamente. |
| `HUB.md` | 🖥️ CLI | Documentación del HUB CLI (`hub.py`): comandos, flags, y ejemplos. |
| `INSTALL.md` | 📦 Setup | Instrucciones de instalación detalladas. |
| `API.md` | 🔌 Integradores | Documentación de los endpoints expuestos por cada receptor. |
| `HEALTH_CHECK.md` | 🏥 Monitoreo | Endpoints de health check y métricas de cada servicio. |
| `INSIGHTS.md` | 💡 Análisis | Insights técnicos y lecciones aprendidas durante el desarrollo. |
| `COMPLIANCE.md` | 📋 Auditoría | Cumplimiento de estándares (OWASP, 12-Factor App). |
| `SECURITY.md` | 🔐 Seguridad | Política de seguridad y auditoría de dependencias. |
| `SYSTEMS_CATALOG.md` | 📖 Inventario | Catálogo de todos los sistemas y tecnologías utilizados. |
| `USER_MANUAL.md` | 📘 Usuarios | Manual de usuario final del sistema. |
| `MAINTAINERS.md` | 👥 Mantenedores | Lista de mantenedores y áreas de responsabilidad. |
| `DOCKER_REPORT.md` | 📊 Informes | Reporte generado por el script de análisis de recursos Docker. |
| `FILE_MAP.md` | 🗺️ **Este doc** | El documento que estás leyendo ahora. |

---

## 🔄 Orquestación n8n (`n8n/`)

| Archivo/Dir | Descripción |
|-------------|-------------|
| `workflows/*.json` | 9 archivos JSON, uno por caso. Contienen la lógica de transformación, enrutamiento y manejo de errores del bus de eventos. |
| `data/` | Datos persistentes de n8n (base de datos SQLite interna, credenciales, ejecuciones). Excluido de Git. |
| `README.md` | Documentación específica de la configuración de n8n. |

---

## 📊 Observabilidad (`grafana/` + `prometheus/`)

| Archivo/Dir | Descripción |
|-------------|-------------|
| `grafana/provisioning/datasources/` | Configuración automática de Prometheus como datasource en Grafana. |
| `prometheus/prometheus.yml` | Configuración de scraping: targets, intervalos, y reglas de alerta. |

---

## ☸️ Kubernetes (`k8s/`)

| Archivo/Dir | Descripción |
|-------------|-------------|
| `k8s/base/` | Manifiestos base (Deployments, Services, ConfigMaps) para despliegue en K8s. |
| `k8s/overlays/dev/` | Overlay de Kustomize para el entorno de desarrollo (réplicas reducidas, sin TLS). |

---

## 🔧 CI/CD (`.github/`)

| Archivo/Dir | Descripción |
|-------------|-------------|
| `.github/workflows/` | GitHub Actions: linting (Black, ESLint), tests, auditoría de seguridad (Trivy, Gitleaks, pip-audit), y deploy automático. |

---

## 📝 Artículo Profesional (`articulo/`)

| Archivo | Descripción |
|---------|-------------|
| `LINKEDIN_ARTICLE.md` | Artículo de alto nivel técnico para LinkedIn sobre la experiencia de orquestación políglota. |

---

## 🔑 Archivos Utilitarios (Raíz)

| Archivo | Descripción |
|---------|-------------|
| `fix_json.py` | Script para reparar JSON malformados en workflows de n8n. |
| `check_n8n_db.js` | Script Node.js para inspeccionar la base de datos interna de n8n (SQLite). |
| `list_nodes_internal.js` | Lista los tipos de nodos registrados en la instancia de n8n. |
| `test_node_type.json` | Fixture de test para validar la estructura de nodos n8n. |
| `test_node_v2.py` | Test unitario para verificar la compatibilidad de versión de nodos. |
| `resources.json` | Archivo generado con el snapshot de recursos Docker (RAM, disco). |
| `hub.audit.log` | Log de auditoría generado por el HUB CLI. |
| `cookies.txt` | Archivo temporal para sesiones HTTP (generado durante tests). |

---

> **💡 Tip**: Usa `Ctrl+F` para buscar cualquier archivo específico. Cada fila enlaza directamente al concepto arquitectónico que justifica la existencia del archivo.
