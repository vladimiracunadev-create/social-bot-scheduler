# 📜 Changelog — Social Bot Scheduler

Todos los cambios notables en este proyecto se documentan sistemáticamente en este archivo. Seguimos los principios de [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) y el versionado semántico.

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
