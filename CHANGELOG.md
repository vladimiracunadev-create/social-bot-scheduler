# 📜 Changelog — Social Bot Scheduler

Todos los cambios notables en este proyecto se documentan sistemáticamente en este archivo. Seguimos los principios de [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) y el versionado semántico.

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
