# 🤖 Social Bot Scheduler: Matriz de Integración Multi-Eje

### *Automatización avanzada: Orquestación de Python, Go, Node.js y PHP mediante n8n.*

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![Ecosystem](https://img.shields.io/badge/Matriz-9_Ejes-blueviolet.svg)]()
[![Security](https://img.shields.io/badge/Security-Hardened-success.svg)]()
[![Latest Release](https://img.shields.io/badge/release-v4.1.0-blue.svg)]()

---

## ⚡ Quickstart: Demo en 60 Segundos

**Objetivo**: Ver la interoperabilidad Python -> PHP en acción ahora mismo.

1. **Levanta todo**: `make up` (o `docker-compose up -d`) — n8n se auto-configura con los 9 workflows ✅
2. **Espera ~30s**: Los workflows se importan y activan automáticamente
3. **Dispara**: `make demo` (o `python3 hub.py ejecutar 01-python-to-php`)
4. **Verifica**: Abre [http://localhost:8081](http://localhost:8081) para ver el dashboard PHP actualizado

> **Zero configuración manual**: No necesitas crear cuentas ni importar workflows en n8n. Todo es automático.

---

## 💡 Sobre el Proyecto
> **[AVISO DE COMPLIANCE](docs/COMPLIANCE.md)**: Este es un laboratorio educativo. Favor de leer nuestra política de uso responsable.

**Social Bot Scheduler** es un laboratorio de ingeniería de software diseñado para demostrar la interoperabilidad entre múltiples lenguajes de programación. Utiliza **n8n** como bus de orquestación central para comunicar emisores (bots) escritos en diversos lenguajes con receptores (dashboards) también agnósticos.

### 🛡️ Hardening de Producción
Este repositorio ha sido auditado y robustecido siguiendo estándares de seguridad industrial:
- **Seguridad en Contenedores**: Imagen escaneada en CI (Trivy), sin vulnerabilidades CRITICAL/HIGH detectadas al build. Ejecución no-root.
- **Validación de Entradas**: El HUB CLI protege contra Path Traversal y ejecución remota de código (RCE).
- **Orquestación Segura**: Manifiestos de Kubernetes con `SecurityContext` restrictivo y `NetworkPolicy` de denegación por defecto.
- **Escaneo Automático**: Integración de `Gitleaks`, `Trivy` y `pip-audit` en el pipeline de CI/CD para una seguridad de triple capa.
- **Capa HUB**: Orquestador centralizado con manifiestos YAML, auditoría y diagnósticos integrados.

---

## 🛡️ Resiliencia y Fiabilidad (Guardrails) - 100% de Cobertura

La capa de n8n actúa como un cortafuegos inteligente entre tus bots y las redes sociales. **TODOS los casos (01-09)** implementan:

| Mecanismo | Descripción | Cobertura |
|-----------|-------------|-----------|
| **Reintentos Autom?ticos** | 3 intentos con 1s de espera | ? 9/9 casos |
| **Dead Letter Queue (DLQ)** | Registro de errores irrecuperables | ? 9/9 casos |
| **Idempotencia** | Prevenci?n de duplicados con SQLite | ? 9/9 casos |
| **Circuit Breaker** | Protecci?n contra servicios ca?dos | ? 9/9 casos |

**Scripts Compartidos:**
- `scripts/check_idempotency.py` - Gestión de fingerprints con SQLite
- `scripts/circuit_breaker.py` - Estados CLOSED/OPEN/HALF_OPEN
- `scripts/generate_workflows.py` - Generador automatizado de workflows

**Documentación:**
- [Guardrails](docs/GUARDRAILS.md) - Conceptos y teoría
- [Guía de Resiliencia](docs/RESILIENCE_GUIDE.md) - Implementación completa y pruebas

---

## 🗄️ Persistencia Multi-Motor (Políglota - v4.0)

Para hacer el laboratorio aún más robusto y realista, cada eje de integración ahora cuenta con su propio motor de base de datos dedicado. El sistema no solo orquesta lenguajes, sino también paradigmas de persistencia:

| Caso | Motor | Tipo | Uso en el Sistema |
| :--- | :--- | :--- | :--- |
| **01** | **MySQL** | Relacional | Almacenamiento Estándar PHP |
| **02** | **MariaDB** | Relacional | Almacenamiento Estándar Go |
| **03** | **PostgreSQL** | Relacional | JSONB y Transacciones Node.js |
| **04** | **SQLite** | Embebido | Persistencia Local Ligera FastAPI |
| **05** | **MongoDB** | NoSQL Documental | Esquemas Flexibles React/Express |
| **06** | **Redis** | In-Memory / KV | Caché y Estados Symfony |
| **07** | **Cassandra** | NoSQL Wide-Column | Alta disponibilidad Ruby |
| **08** | **SQL Server** | Relacional Enterprise | Datos Estructurados Flask |
| **09** | **DuckDB** | Embebido | Integration Gateway FastAPI + Dashboard GitHub |

> **Auto-Migración**: Cada servicio receptor está programado para verificar la conexión, crear la base de datos y generar las tablas/colecciones automáticamente al arrancar.

---

## 🚀 Despliegue y Escalabilidad

### Prerrequisitos
Antes de comenzar, consulta el **[Análisis de Recursos Docker](docs/DOCKER_RESOURCES.md)** para entender el impacto en hardware.
Asegúrate de tener instalado:
1.  **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**: Para ejecutar la infraestructura.
2.  **[Python 3.10+](https://www.python.org/downloads/)**: Para ejecutar el asistente de configuración `setup.py` y los bots emisores.
3.  **[Git](https://git-scm.com/downloads)**: Para clonar este repositorio.

### Paso 1: Instalación
Clona el repositorio en tu máquina local:
```bash
git clone https://github.com/vladimiracunadev-create/social-bot-scheduler.git
cd social-bot-scheduler
```

### Paso 2: Configuración (Elige tu camino)

#### Opción A: Orquestador HUB (Recomendado)
Usa el nuevo HUB para listar y diagnosticar:

```powershell
# Windows
.\hub.ps1 listar-casos
.\hub.ps1 doctor
```

```bash
# Linux
./hub.sh listar-casos
```

#### Opción B: Asistente Legacy
Sigue el flujo tradicional con nuestro asistente interactivo:
```bash
python setup.py
```
1.  Selecciona el **Caso 01 (Python -> PHP)**.
2.  El script generará los archivos `.env` y preparará el entorno.

### Paso 3: Levantar Infraestructura
El asistente te dará el comando exacto al finalizar. Generalmente será:
```bash
docker-compose up -d n8n dest-php
```
*Nota: Esto descargará las imágenes y levantará los servicios en segundo plano.*

### Paso 4: Verificar n8n (Automático)
n8n se auto-configura al arrancar. Solo verifica:
1.  Abre [http://localhost:5678](http://localhost:5678).
2.  Deberías ver los workflows ya importados y activos.
3.  Si pide login: `admin@social-bot.local` / `SocialBot2026!`

> **Nota**: La primera vez, espera ~30 segundos para la auto-configuración. Los 9 workflows se importan desde `n8n/workflows/`.

### Paso 5: ¡Disparar y Monitorear!
Ejecuta el bot emisor desde su carpeta `origin`:
```bash
cd cases/01-python-to-php/origin
python bot.py
```

### 📊 ¿Dónde están mis Logs?
Si los logs aparecen vacíos, sigue estos pasos:
### ❌ Síntoma: El bot dice "Payload sent" pero el Dashboard está vacío
**Verificaciones**:
1.  **¿Workflow Activo?**: Abre n8n y verifica que el switch "Active" esté en verde.
2.  **Webhooks**: n8n por defecto usa URLs dinámicas. Asegúrate de que el path en el nodo Webhook coincida con lo que espera el bot (ej: `social-bot-scheduler-php`).
3.  **Logs de n8n**: Mira la pestaña "Executions" en n8n para ver si hay errores en el nodo HTTP Request.
4.  **Guardrails - Idempotencia**: Si el payload ha sido enviado antes, el sistema lo ignorará silenciosamente para evitar spam. Revisa si el hash ya existe en tu DB de control.
5.  **Guardrails - Circuit Breaker**: Si un proveedor ha fallado mucho, el flujo se desviará al **DLQ**. Revisa la tabla/archivo de fallos (`failed_posts`).

---
6.  **Dashboard Maestro (Global)**: Entra en [http://localhost:8080](http://localhost:8080) para ver el estado de todos los casos.
7.  **Logs en Tiempo Real**: Ejecuta `make logs` en la raíz para ver la actividad de todos los contenedores Docker.
8.  **Logs persistentes (Archivos)**: Revisa carpetas como `cases/01-python-to-php/dest/logs/`. Estos archivos solo se crean si el `WEBHOOK_URL` en tu `.env` es correcto y el post llega al destino.

Verifica el Dashboard del Caso 01: [http://localhost:8081](http://localhost:8081)
Verifica el Dashboard Maestro para ver los registros en cada DB: [http://localhost:8080](http://localhost:8080)

---

## 🩺 Salud y Verificación del Repositorio

Para asegurar que el entorno sea correcto y esté listo para operar:

1.  **Diagnóstico de Salud**: `make doctor` (Verifica Docker, YAMLs y **recursos de hardware**).
2.  **Prueba de Integración (E2E)**: Abre [http://localhost:8080](http://localhost:8080) y pulsa **"🚀 PROBAR INTEGRACIÓN GLOBAL"**.
3.  **Calidad y Seguridad**: 
    - `black --check .` (Formato)
    - Si `black --check .` falla y no es obvio el cambio, usa `black --diff --check <archivo>` para ver el parche exacto que Black quiere aplicar antes de commitear.
    - `pip-audit --ignore-vuln CVE-2026-1703` (Vulnerabilidades)

> **Guía Detallada**: Consulta [VERIFICATION_GUIDE.md](docs/VERIFICATION_GUIDE.md) para un manual completo de pruebas.

---

## 📈 Observabilidad Avanzada y Multi-DB (v4.0)

Este proyecto implementa un **stack de monitoreo industrial** para eliminar la "caja negra" típica de las integraciones.

### ¿Qué componentes usamos?
1.  **Prometheus (`:9090`)**: Es el "recolector". Viaja cada 15 segundos a n8n y a los contenedores para preguntar "¿Cómo estás?" (CPU, RAM, Workflows activos, Errores).
2.  **Grafana (`:3000`)**: Es el "visualizador". Toma los datos matemáticos de Prometheus y los convierte en gráficos hermosos y útiles para tomar decisiones.

### ¿Para qué sirve esto?
-   **Detección de Cuellos de Botella**: ¿n8n está lento porque le falta CPU o porque la red falla? Grafana te lo dice.
-   **Alertas Tempranas**: Ver si la tasa de errores sube antes de que los usuarios se quejen.
-   **Capacidad**: Saber cuándo es hora de escalar la infraestructura.

| Servicio | URL | Credenciales | Descripción |
|----------|-----|--------------|-------------|
| **Grafana** | [http://localhost:3000](http://localhost:3000) | `admin` / `admin` | Dashboards visuales. Configura Datasource `http://prometheus:9090`. |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | (Sin auth) | Explorador de métricas crudas (`n8n_workflow_executions_total`). |

### Métricas Clave a Observar
-   `n8n_workflow_executions_total`: Tráfico total del sistema.
-   `n8n_workflow_failed_executions_total`: Salud de las integraciones.
-   `n8n_nodejs_eventloop_lag_seconds`: "Estrés" interno de n8n (si es alto, n8n está sufriendo).


---

## 🏗️ La Gran Matriz de Integración
Tabla de estado actual de los 9 ejes de integraci?n:

| ID | Eje Tecnológico (Origen -> Puente -> Destino) | Persistencia | Estado |
| :--- | :--- | :--- | :--- |
| [**01**](cases/01-python-to-php/README.md) | 🐍 **Python** -> 🔗 n8n -> 🐘 **PHP** | `MySQL` | ✅ Operativo |
| [**02**](cases/02-python-to-go/README.md) | 🐍 **Python** -> 🔗 n8n -> 🐹 **Go** | `MariaDB` | ✅ Operativo |
| [**03**](cases/03-go-to-node/README.md) | 🐹 **Go** -> 🔗 n8n -> 🍏 **Node.js** | `PostgreSQL` | ✅ Operativo |
| [**04**](cases/04-node-to-fastapi/README.md) | 🍏 **Node.js** -> 🔗 n8n -> 🐍 **FastAPI** | `SQLite` | ✅ Operativo |
| [**05**](cases/05-laravel-to-react/README.md) | 🐘 **Laravel** -> 🔗 n8n -> ⚛️ **React** | `MongoDB` | ✅ Operativo |
| [**06**](cases/06-go-to-symfony/README.md) | 🐹 **Go** -> 🔗 n8n -> 🐘 **Symfony** | `Redis` | ✅ Operativo |
| [**07**](cases/07-rust-to-ruby/README.md) | 🦀 **Rust** -> 🔗 n8n -> 💎 **Ruby** | `Cassandra` | ✅ Operativo |
| [**08**](cases/08-csharp-to-flask/README.md) | ❄️ **C#** -> 🔗 n8n -> 🌶️ **Flask** | `SQL Server` | ✅ Operativo |
| [**09**](cases/09-python-to-gateway/README.md) | Python -> n8n -> FastAPI Gateway | `DuckDB` | OK |

---

## 📖 Documentación Detallada

Accede a las guías específicas para profundizar en cada área del sistema:

- 👔 **[Guía para Reclutadores](docs/RECRUITER.md)**: Evaluación técnica rápida y valor de negocio del proyecto.
- 🐳 **[Análisis de Recursos Docker](docs/DOCKER_RESOURCES.md)**: Informe detallado de uso de RAM y Disco (Stress Test).
- 🗺️ **[Mapa Completo del Sistema](docs/FILE_MAP.md)**: Explicación detallada de **cada archivo** del repositorio, su rol e importancia.

### 🧹 Gestión de Recursos y Limpieza
Dada la complejidad del stack (9 destinos y 8 bases de datos externas m?s DuckDB embebida), es vital saber c?mo liberar recursos:
- **Liberación Total (Nuke)**: `make nuke` (☢️ Borra imágenes base, volúmenes, redes y caché).
- **Limpieza Estándar**: `make clean` (Borra contenedores y volúmenes).

- 🔗 **[Activación de Workflows](COMO_ACTIVAR_WORKFLOWS.md)**: Cómo importar y activar la lógica en n8n automáticamente.
- 🔧 **[Solución de Problemas](docs/TROUBLESHOOTING.md)**: Resolución de errores comunes de Docker, n8n y dependencias.
- 📊 **[Índice de Casos](docs/CASES_INDEX.md)**: Matriz técnica detallada de cada flujo de integración.
- 🏗️ **[Arquitectura](docs/ARCHITECTURE.md)**: Diagramas del sistema y decisiones de diseño.
- 📝 **[Artículo Técnico](articulo/LINKEDIN_ARTICLE.md)**: Análisis de alto nivel para LinkedIn sobre la experiencia políglota.
- 🧪 **[Guía de Verificación](docs/VERIFICATION_GUIDE.md)**: Manual de pruebas para asegurar la salud del repositorio.
- 💻 **[Requisitos del Sistema](docs/REQUIREMENTS.md)**: Especificaciones de hardware y software recomendadas.
- ⚠️ **[Limitaciones](docs/LIMITATIONS.md)**: Trade-offs y decisiones técnicas de diseño.
- 🧑‍💻 **[Guía de Mantenedores](docs/MAINTAINERS.md)**: Información crítica para la evolución y extensión del sistema.
- 🗺️ **[Roadmap](ROADMAP.md)**: Planificación, hitos y futuro del proyecto.

---

## 🤝 Contribución
Las Pull Requests son bienvenidas. Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre nuestro código de conducta y el proceso para enviarnos pull requests.

---
*© 2026 Social Bot Scheduler - Laboratorio de Integración*
