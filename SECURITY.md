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

> **Nota sobre moving tags**: imágenes como `php:8.4-apache`, `node:24-alpine`, `redis:7-alpine` son minor-pinned pero no SHA-pinned. Son renovadas automáticamente por Dependabot. Riesgo aceptado para un laboratorio local.
>
> **v4.11.0** — Se eliminaron los dos tags *flotantes* que quedaban (`dart:stable` y `debian:stable-slim`, caso 20): un tag móvil hace el build irreproducible y deja al guardrail de imágenes sin nada que comprobar. Ahora son `dart:3.10-sdk` y `debian:13-slim`.

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
| SHA-pinning de GitHub Actions | **CORREGIDO** | Las 32 referencias `uses:` de los tres workflows (`ci-cd.yml` 25, `pages.yml` 5, `wiki-sync.yml` 2) están pinneadas a SHA de 40 chars con comentario `# vX`. Cierra la ventana de un tag reescrito maliciosamente; Dependabot sigue proponiendo bumps y el guardrail verifica que no quede ninguna sin pinnear. (P-07, v4.4.1; ampliado a `pages.yml` en v4.11.0) |
| Escaneo de imagen Docker | **OK** | Trivy `v0.35.0` filtra `CRITICAL,HIGH` antes del push. |
| Dependabot | **CORREGIDO** | `.github/dependabot.yml` con **32 entradas** que cubren los 20 casos: `npm` (9), `pip` (8), `gomod` (5), `cargo` (2), `nuget` (2), `gradle` (2), `bundler`, `pub`, `docker` y `github-actions`. El ecosistema se llama `npm` porque es el nombre del **registro**, no del gestor: Dependabot lee los `pnpm-lock.yaml` sin ejecutar npm. Ampliado de 9 a 32 en v4.11.0. |
| Manifiestos de seguridad por caso | **CORREGIDO** | `scripts/validate_security_manifests.py` cruza los 20 `cases/NN-*/security.yml` contra los Dockerfiles, el compose y los manifiestos de proyecto. Falla si el manifiesto va por delante del código o si se reintroduce una versión declarada abandonada. (P-08, v4.11.0) |
| Invocación de `npm` | **CORREGIDO** | Cero invocaciones de `npm`/`npx` en todo el repositorio: CI activa pnpm por `corepack`, los Dockerfiles usan `pnpm install --prod --frozen-lockfile` y `.gitignore` rechaza `package-lock.json` y `npm-shrinkwrap.json`. (v4.11.0) |

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

### Resueltos en v4.11.0 (2026-11-01)

| ID | Descripción | Prioridad | Estado | Implementación |
| :--- | :--- | :---: | :---: | :--- |
| P-08 | Versiones de runtime sin trazabilidad ni guardrail | Alta | ✅ CORREGIDO | Los 20 casos declaran su `security.yml` (runtime y dependencia → versión, advisory y motivo) y `scripts/validate_security_manifests.py` lo cruza en CI contra los Dockerfiles, el compose y los manifiestos de proyecto. |
| P-09 | Runtimes de lenguaje en EOL | Alta | ✅ CORREGIDO | 51 cambios de runtime o imagen base. Go 1.21/1.23 → 1.27, Node 20 → 24 LTS, Python 3.11 → 3.13, PHP 8.2 → 8.4, Ruby 3.2 → 3.4, .NET 6/9 → 10, Alpine 3.20 → 3.23.7, Rust 1.83 → 1.99, OTP 27 → 28, Crystal 1.14 → 1.22, Swift 6.0 → 6.2. |
| P-10 | Tags de imagen flotantes | Media | ✅ CORREGIDO | `dart:stable` → `dart:3.10-sdk` y `debian:stable-slim` → `debian:13-slim` (caso 20). Un tag móvil hace el build irreproducible y deja al guardrail sin nada que comprobar. |
| P-11 | `npm` presente en la superficie del repositorio | Media | ✅ CORREGIDO | Cero invocaciones de `npm`/`npx`. CI activa pnpm por `corepack`; los Dockerfiles usan `pnpm install --prod --frozen-lockfile`; `.gitignore` rechaza `package-lock.json` y `npm-shrinkwrap.json`. |
| P-12 | Política de pnpm desactivada en silencio al subir a pnpm 11 | Alta | ✅ CORREGIDO | pnpm 11 **ya no lee el campo `pnpm` de `package.json`**: los `overrides` y `onlyBuiltDependencies` del repo iban a quedar inertes. Se trasladan a `pnpm-workspace.yaml` en los 9 paquetes Node, con `minimumReleaseAge: 1440` añadido. |
| P-13 | Dependencias instaladas sin pin ni hash | Alta | ✅ CORREGIDO | El caso 04 dest instalaba `fastapi uvicorn pydantic` sueltos desde PyPI. Los casos 04, 12 y 15 pasan a `requirements.in` + `requirements.txt` con hashes SHA256; los casos 13, 14, 16 y 17 ganan `pnpm-lock.yaml` commiteado. |
| P-14 | Dependabot cubría 9 de 20 casos | Media | ✅ CORREGIDO | 32 entradas: `npm` ×9, `pip` ×8, `gomod` ×5, `cargo` ×2, `nuget` ×2, `gradle` ×2, `bundler`, `pub`, `docker`, `github-actions`. |

> **Hallazgos reales cerrados en v4.11.0**: **78 advisories distintos** (41 con identificador
> CVE), de los cuales los críticos son **CVE-2026-33186** (bypass de autorización en gRPC-Go),
> **GHSA-2464-fhr4-w9xw** y **GHSA-2xp9-vwfh-vxw4** (RCE sin autenticar en la Image
> Optimization API de Next.js), **GHSA-jqcg-44mw-7w3h** (spoofing de IP en `proxy-addr`),
> **GHSA-6q48-6c7w-9gw2** (raíces emSign comprometidas en `certifi`) y
> **GHSA-82r6-8w77-94w6** (confusión de certificados TLS en `anyio`). Detalle completo, método
> de obtención y alcance de la verificación en
> [`docs/VERSION_UPGRADES.md`](docs/VERSION_UPGRADES.md).

### Follow-ups abiertos

| Qué | Prioridad | Por qué sigue abierto |
| :--- | :---: | :--- |
| Imágenes de base de datos e infraestructura | Media | El pase v4.11.0 cubrió **lenguajes de programación**. `mongo:6.0` (EOL) e `influxdb:1.8` son las más atrasadas; también conviene revisar `cassandra:4.1`, `mariadb:10.11`, `postgres:15-alpine`, `redis:7-alpine` y `mssql 2022`. |
| `docker build` de las 29 imágenes | Media | Los tags están verificados contra Docker Hub / MCR y los `FROM` son correctos, pero el build no se ejecutó en local. Los saltos con más riesgo son Crystal 1.14 → 1.22, `ring` 1.12 → 1.15 (Jetty 11 → 12), .NET 6 → 10 y Spring Boot 3.3 → 3.5. |
| Saltos de major sin advisory abierto | Baja | Zig 0.13 → 0.17, Ktor 2.3 → 3.x, XTDB 1.24 → 2.x, Express 4 → 5, Next 15 → 16, Spring Boot 3.5 → 4.x, driver MongoDB 6 → 7, `reqwest` 0.12 → 0.13, `rumqttc` 0.24 → 0.25. Ninguno cierra un advisory: todos rompen API y se triarán por separado. |
| pnpm 11.2.2 → 12.x | Baja | pnpm 12.16.1 está publicado, pero 11.2.2 es la versión con la que se regeneraron y auditaron los 9 lockfiles. Se fija lo verificado, no lo último. |
| `scripts/validate_workflows.py` en Windows | Baja | Falla por la codificación de la consola (`cp1252` frente a los emoji del script), no por su lógica. En CI (Linux) corre normal. |


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
