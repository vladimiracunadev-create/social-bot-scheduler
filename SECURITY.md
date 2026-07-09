# Security Policy — Social Bot Scheduler

Este repositorio es un **laboratorio de ingeniería políglota**. La postura de seguridad se enfoca en reducir el riesgo operativo mediante **Hardening por Defecto** y monitoreo constante de la cadena de suministro.

---

## Auditoría de Seguridad — Resultados (v4.2.0 · addendum v4.4.0)

Auditoría completa ejecutada el 2026-04-06 siguiendo el framework de 8 capas.
Cada punto indica su estado: **OK**, **CORREGIDO** (en esta versión) o **RIESGO ACEPTADO**.

> **Addendum v4.4.0 (2026-07-02)** — Los cuatro pendientes priorizados de la
> auditoría (**P-01** hashes SHA, **P-02** rate limiting, **P-03** whitelist de
> owner, **P-04** auditoría CVE multi-lenguaje) pasan de **RIESGO ACEPTADO** a
> **CORREGIDO**. Ver detalle en cada capa y en «Pendientes Priorizados».

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
| Archivo de lock de dependencias | **CORREGIDO** | Los 5 `requirements.txt` se generan desde `requirements.in` con `uv pip compile --universal --generate-hashes --python-version 3.11`; cada dependencia directa y transitiva queda pinneada con hash SHA256 (la resolución universal incluye backports condicionales `python_version < "3.12"` con su marcador), lo que fuerza el modo `pip --require-hashes` en CI y en el build Docker (Python 3.11). (P-01, v4.4.0) |
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

```text
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
| Rate limiting | **CORREGIDO** | `slowapi` aplica throttling por IP de cliente en `/webhook` (30/min) y `/errors` (60/min) del gateway Case 09; ambos límites son configurables por `GATEWAY_WEBHOOK_RATE_LIMIT` / `GATEWAY_ERRORS_RATE_LIMIT`. El excedente devuelve HTTP 429, protegiendo la cuota de la GitHub API y limitando el abuso de una `X-API-Key` filtrada. (P-02, v4.4.0) |
| Whitelist de destinos | **CORREGIDO** | El campo `owner` de `RequestParamsDTO` valida el patrón `^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$` en el borde (pydantic → 422), replicando el value object `Owner` del dominio. Rechaza barras, `@` y encodings que pudieran redirigir la llamada saliente a GitHub (superficie tipo SSRF). (P-03, v4.4.0) |

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
| Auditoría de otras dependencias (Go, Node, Rust, .NET, Ruby) | **CORREGIDO** | CI ejecuta `govulncheck` (Go), `pnpm audit --audit-level high` (Node), `dotnet list package --vulnerable` (.NET), `cargo audit` (Rust) y `bundler-audit` (Ruby) — **todos bloqueantes** desde v4.4.1. (P-04 v4.4.0; P-05/P-06 v4.4.1) |
| SHA-pinning de GitHub Actions | **CORREGIDO** | Las 27 referencias `uses:` de `ci-cd.yml` y `wiki-sync.yml` están pinneadas a SHA de 40 chars con comentario `# vX`. Cierra la ventana de un tag reescrito maliciosamente; Dependabot sigue proponiendo bumps. (P-07, v4.4.1) |
| Escaneo de imagen Docker | **OK** | Trivy `v0.35.0` filtra `CRITICAL,HIGH` antes del push. |
| Dependabot | **CORREGIDO** | Creado `.github/dependabot.yml` con ecosistemas: `github-actions`, `pip` (hub + 3 cases), `docker`, `gomod` (3 cases), `cargo`, `npm` (2 cases, rastrea los `pnpm-lock.yaml` — Dependabot no tiene un ecosistema `pnpm` propio). |

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
| **cAdvisor (Docker socket)** | CRITICO | `9091` | Solo en perfil `observability`. **NUNCA exponer** — acceso root al daemon Docker. |
| **Prometheus / Grafana** | MEDIO | `9090` / `3000` | Solo en perfil `observability`. Cambiar `GRAFANA_ADMIN_PASSWORD` en `.env`. |
| **master-dashboard** | BAJO | `8080` | Sin auth, solo loopback. Activar `edge` para redes compartidas. |
| **Integration Hubs (casos)** | BAJO | `8081–8100` | Endpoints de prueba, loopback únicamente. |

---

## Pendientes Priorizados

### Resueltos en v4.4.0 (2026-07-02)

| ID | Descripción | Prioridad | Estado | Implementación |
| :--- | :--- | :---: | :---: | :--- |
| P-01 | `requirements.txt` sin hashes SHA | Media | ✅ CORREGIDO | `requirements.in` → `uv pip compile --universal --generate-hashes --python-version 3.11` en los 5 archivos; `pip --require-hashes` en CI y Docker. |
| P-02 | Rate limiting en Case 09 gateway | Baja | ✅ CORREGIDO | `slowapi` en `/webhook` (30/min) y `/errors` (60/min); env-configurable; excedente → 429. |
| P-03 | Whitelist de owners en Case 09 | Baja | ✅ CORREGIDO | `owner` valida regex de GitHub en `RequestParamsDTO` (pydantic → 422), defensa en profundidad sobre el VO `Owner`. |
| P-04 | Auditoría CVE Go/Node/Rust/Ruby/.NET en CI | Media | ✅ CORREGIDO | `govulncheck` + `pnpm audit` + `dotnet list package --vulnerable` bloqueantes; `cargo audit` en observación; `bundler-audit` condicional. |

> **Hallazgos reales cerrados por P-04**: al activarse, `pnpm audit` destapó
> **3 HIGH + 1 moderate** en dependencias transitivas, corregidos vía
> `pnpm.overrides` + regeneración de lockfile — `form-data` <4.0.6 (CRLF,
> GHSA-hmw2-7cc7-3qxx, casos 03/04), `path-to-regexp` <0.1.13 (ReDoS,
> GHSA-37ch-88jc-xwx2, caso 05) y `qs` (DoS, GHSA-q8mj-m7cp-5q26, caso 05).
> `govulncheck` forzó subir el toolchain Go de CI a `stable` (stdlib
> GO-2026-5037/5039). Detalle completo en `CHANGELOG.md` (v4.4.0).

### Resueltos en v4.4.1 (2026-07-02)

| ID | Descripción | Prioridad | Estado | Implementación |
| :--- | :--- | :---: | :---: | :--- |
| P-05 | `cargo audit` en modo bloqueante | Baja | ✅ CORREGIDO | Sample `07-rust-to-ruby/origin` modernizado: `dotenv`→`dotenvy` (RUSTSEC-2021-0141) y `reqwest` 0.11→0.12 (elimina `rustls-pemfile`, RUSTSEC-2025-0134). `cargo audit` ahora **bloquea**. |
| P-06 | `bundler-audit` sin cobertura real | Baja | ✅ CORREGIDO | `Gemfile` + `Gemfile.lock` añadidos al caso Ruby (`sinatra`, `cassandra-driver`); `bundler-audit` corre de verdad y en verde. |
| P-07 | Actions de GitHub sin SHA-pinning | Media | ✅ CORREGIDO | Las 27 referencias `uses:` en `ci-cd.yml` y `wiki-sync.yml` pinneadas a SHA de 40 chars con comentario `# vX` (Dependabot las sigue actualizando). |

### Follow-ups abiertos

_Ninguno de la auditoría original._ Gestión continua vía Dependabot (23 PRs abiertos tras el release v4.4.0: bumps de deps + majors como Express 5, Python 3.14, reqwest 0.13 — a triar manualmente por su riesgo de ruptura).

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

_Auditoría gestionada por Vladimir Acuña — Software & Security Engineering_
