# Security Policy — Social Bot Scheduler

Este repositorio es un **laboratorio de ingeniería políglota**. La postura de seguridad se enfoca en reducir el riesgo operativo mediante **Hardening por Defecto** y monitoreo constante de la cadena de suministro.

---

## Auditoría de Seguridad — Resultados (v4.2.0)

Auditoría completa ejecutada el 2026-04-06 siguiendo el framework de 8 capas.
Cada punto indica su estado: **OK**, **CORREGIDO** (en esta versión) o **RIESGO ACEPTADO**.

---

### 1. Contenedor y Proceso

| Punto | Estado | Detalle |
| :--- | :---: | :--- |
| Proceso corre como root | **OK** | `Dockerfile` crea `botuser:botgroup` y termina con `USER botuser`. |
| Imágenes con tag `:latest` | **OK** | Servicios principales usan versiones fijas. El guardrail `check_runtime_security.py` rechaza cualquier `:latest` en CI. |
| Healthcheck referencia herramienta inexistente | **OK** | `python -c "import os; ..."` — Python está en la imagen. |
| Directorios de logs/PID accesibles por usuario no-root | **OK** | `/app` se entrega con `chown botuser:botgroup`. |

> **Nota sobre moving tags**: imágenes como `php:8.2-apache`, `node:20-alpine`, `redis:7-alpine` son minor-pinned pero no SHA-pinned. Son renovadas automáticamente por Dependabot. Riesgo aceptado para un laboratorio local.

---

### 2. Red y Exposición de Puertos

| Punto | Estado | Detalle |
| :--- | :---: | :--- |
| Puertos vinculados a `127.0.0.1` | **OK** | Todos usan `${HOST_BIND_IP:-127.0.0.1}`. El guardrail CI verifica que ningún servicio publique en `0.0.0.0`. |
| Bases de datos expuestas en host | **OK** | MySQL, MariaDB, PostgreSQL, MongoDB, Redis, Cassandra, MSSQL no tienen `ports:` — solo accesibles dentro de `bot-network`. |

---

### 3. Credenciales y Variables de Entorno

| Punto | Estado | Detalle |
| :--- | :---: | :--- |
| `.env` en `.gitignore` | **OK** | Línea `.env` y `.env.*` con excepciones explícitas para `!.env.example` y `!.env.demo.example`. |
| `.env.example` commiteado | **OK** | Plantilla sin secretos reales. Nunca en `.gitignore`. |
| Archivo de lock de dependencias | **RIESGO ACEPTADO** | `requirements.txt` usa versiones `>=` sin hashes SHA. `pip-audit` en CI detecta CVEs conocidos. Mitigación completa requeriría `pip-compile --generate-hashes`. |
| Fallback hardcodeado en docker-compose | **RIESGO ACEPTADO** | Los valores `change-me-*` permiten arrancar el lab sin `.env`. El script `n8n_auto_setup.sh` emite warning si detecta placeholders. Riesgo local — nunca exponer sin edge proxy autenticado. |

---

### 4. Configuración del Servidor Web

| Punto | Estado | Detalle |
| :--- | :---: | :--- |
| `Options -Indexes` (listado deshabilitado) | **CORREGIDO** | `apache/security-headers.conf` aplica `Options -Indexes` en todos los servicios `php:8.2-apache`. |
| `X-Frame-Options` | **CORREGIDO** | Aplicado vía `apache/security-headers.conf` (Apache) y `edge/start-caddy.sh` (Caddy). |
| `X-Content-Type-Options: nosniff` | **CORREGIDO** | Ídem. |
| `Referrer-Policy` | **CORREGIDO** | Ídem. |
| `Content-Security-Policy` | **CORREGIDO** | Añadido en Apache y en Caddy edge proxy (faltaba en ambos). |
| `Permissions-Policy` | **CORREGIDO** | Añadido en Apache y en Caddy edge proxy (faltaba en ambos). |
| `display_errors Off` (PHP) | **OK** | `php:8.2-apache` tiene `display_errors = Off` en su `php.ini` de producción por defecto. |
| `AllowOverride` para `.htaccess` | **N/A** | No se usa `.htaccess`; la config se monta directamente en `conf-enabled/`. |

Los tres servicios Apache reciben la misma config montada en `:ro`:
```
./apache/security-headers.conf:/etc/apache2/conf-enabled/security-headers.conf:ro
```
Y habilitan `mod_headers` vía:
```yaml
command: sh -c "a2enmod headers && apache2-foreground"
```

---

### 5. Herramientas con Acceso a Datos Sensibles

| Punto | Estado | Detalle |
| :--- | :---: | :--- |
| Modo solo lectura por defecto | **OK** | `DRY_RUN=true` y `NO_PUBLIC_POSTING=true` en `.env.example`. |
| CSRF en Case 09 (FastAPI) | **OK** | El endpoint `/webhook` requiere `X-API-Key` válido por header — no es un formulario HTML con POST de navegador. |
| Rate limiting | **RIESGO ACEPTADO** | No existe rate limiting explícito en el gateway Case 09. Aceptable para laboratorio local. En producción: añadir SlowAPI o un middleware de throttling. |
| Whitelist de destinos | **RIESGO ACEPTADO** | El parámetro `owner` del gateway se pasa a GitHub API; no está en whitelist. Se valida via `pydantic` (tipo str) y el límite es numérico (`le=50`). En producción: añadir regex whitelist de owners permitidos. |

---

### 6. Autenticación

| Componente | Estado | Detalle |
| :--- | :---: | :--- |
| n8n Orchestrator (`:5678`) | **OK** | Requiere login con `N8N_OWNER_EMAIL` / `N8N_OWNER_PASSWORD`. |
| master-dashboard (`:8080`) | **RIESGO ACEPTADO** | Sin autenticación. Solo accesible en `127.0.0.1`. Para redes compartidas: activar el perfil `edge` con `EDGE_BASIC_AUTH_HASH`. |
| Edge proxy (`:80/:443`) | **OK** | Falla al arrancar si `EDGE_BASIC_AUTH_HASH` está vacío. Basic Auth sobre HTTPS + HSTS. |
| Grafana (`:3000`) | **OK** | `GF_AUTH_ANONYMOUS_ENABLED=false`, `GF_USERS_ALLOW_SIGN_UP=false`. Cambiar credenciales en `.env`. |

**Para exponer el dashboard en una red compartida** sin edge proxy completo:
```bash
# Generar hash de contraseña
docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext 'TuPassword'
# Agregar al .env y activar perfil edge
EDGE_BASIC_AUTH_HASH=<hash>
docker compose --profile edge up -d
```

---

### 7. Pipeline CI/CD

| Punto | Estado | Detalle |
| :--- | :---: | :--- |
| Escaneo de secretos en historial | **OK** | `gitleaks/gitleaks-action@v2` en job `build-and-push`. |
| Auditoría de dependencias Python | **OK** | `pip-audit --ignore-vuln CVE-2026-1703` en job `python-cases`. |
| Auditoría de otras dependencias (Go, Node, Rust, .NET, Ruby) | **RIESGO ACEPTADO** | Solo Python tiene auditoría automática. Go, Node, Rust, .NET y Ruby se validan en sintaxis/build pero no contra CVE DB. Dependabot abre PRs cuando hay versiones vulnerables. |
| Escaneo de imagen Docker | **OK** | Trivy `v0.35.0` filtra `CRITICAL,HIGH` antes del push. |
| Dependabot | **CORREGIDO** | Creado `.github/dependabot.yml` con ecosistemas: `github-actions`, `pip` (hub + 3 cases), `docker`, `gomod` (3 cases), `cargo`, `npm` (2 cases). |

---

### 8. Cadena de Suministro

| Punto | Estado | Detalle |
| :--- | :---: | :--- |
| Line endings LF en scripts shell | **CORREGIDO** | `.gitattributes` creado: `*.sh eol=lf`, `Dockerfile eol=lf`, `*.py eol=lf`, etc. Scripts Windows (`*.ps1`) en CRLF. |
| Detección de Unicode bidi (CVE-2021-42574) | **CORREGIDO** | Job `supply-chain-checks` en CI escanea todos los archivos de código fuente con Python puro (portable, sin dependencias). |
| Detección de ofuscación base64/eval | **CORREGIDO** | Mismo job detecta patrones `eval(b64decode(...))` y equivalentes en Python, JS, Ruby, PHP, Shell. |
| Mitigación Trivy supply chain (Marzo 2026) | **OK** | Migrado de `trivy-action@v0.33.1` (comprometido) a `v0.35.0` verificado. |
| Pre-commit hooks | **OK** | `detect-secrets`, `black`, `flake8`, `check-yaml`, `check-json` activos. |

---

## Matriz de Superficie de Ataque

| Componente | Riesgo | Puerto Local | Acción Recomendada |
| :--- | :---: | :--- | :--- |
| **n8n Orchestrator** | ALTO | `5678` | Cambiar credenciales en `.env`. Usar perfil `edge` para acceso remoto. |
| **cAdvisor (Docker socket)** | CRITICO | `8089` | Solo en perfil `observability`. **NUNCA exponer** — acceso root al daemon Docker. |
| **Prometheus / Grafana** | MEDIO | `9090` / `3000` | Solo en perfil `observability`. Cambiar `GRAFANA_ADMIN_PASSWORD` en `.env`. |
| **master-dashboard** | BAJO | `8080` | Sin auth, solo loopback. Activar `edge` para redes compartidas. |
| **Integration Hubs (casos)** | BAJO | `8081–8090` | Endpoints de prueba, loopback únicamente. |

---

## Pendientes Priorizados

| ID | Descripción | Prioridad | Solución Propuesta |
| :--- | :--- | :---: | :--- |
| P-01 | `requirements.txt` sin hashes SHA | Media | `pip-compile --generate-hashes` → `requirements.txt` con hashes verificables. |
| P-02 | Rate limiting en Case 09 gateway | Baja | Añadir `slowapi` o middleware de throttling en `main.py`. |
| P-03 | Whitelist de owners en Case 09 | Baja | Validar `owner` contra regex `^[a-zA-Z0-9-]{1,39}$` en `RequestParamsDTO`. |
| P-04 | Auditoría CVE para Go/Node/Rust/Ruby/.NET en CI | Media | `govulncheck`, `npm audit`, `cargo audit`, `bundler-audit`, `dotnet list package --vulnerable`. |

---

## Recomendaciones Operativas

| Escenario | Comando | Hardening |
| :--- | :--- | :---: |
| Desarrollo estándar | `make up-secure` | Máximo |
| Auditoría de recursos | `make up-observability` | Medio |
| Acceso remoto controlado | `make up-edge` | Controlado |

---

## Reporte de Vulnerabilidades

Si identificas un riesgo de seguridad:
1. **No abras un Issue público** — usa el sistema de **Security Advisories** de GitHub.
2. Incluye pasos para reproducir y el impacto técnico estimado.

---

*Auditoría gestionada por Vladimir Acuña — Software & Security Engineering*
