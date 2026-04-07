# 🛡️ Runtime Security Model — Social Bot Scheduler

Esta guía documenta el modelo operativo y de seguridad aplicado al ecosistema de **Social Bot Scheduler**. Nuestro objetivo es mantener un equilibrio entre el valor didáctico de un laboratorio políglota y la robustez técnica necesaria para evitar riesgos accidentales.

---

## 📐 Filosofía de Seguridad

El sistema se rige por tres pilares fundamentales:
1.  **Funcionalidad Transparente**: El laboratorio debe ser fácil de entender y desplegar.
2.  **Hardening Incremental**: Seguridad que escala desde el núcleo hacia los bordes.
3.  **Local-First**: Reducción drástica de la superficie de ataque mediante aislamiento de red.

---

## 🚦 Modos de Operación y Postura

| Modo | Comando de Activación | Alcance Técnico | Postura de Riesgo |
| :--- | :--- | :--- | :--- |
| **Secure Default** | `make up-secure` | n8n + Master Dashboard | 🛡️ Máxima (Local-only) |
| **Demo Local** | `make up` | Matriz Completa + DBs | 🧪 Didáctica (Perfil `full`) |
| **Observability** | `make up-observability`| Stack CNCF (Prometheus/Grafana) | 📊 Diagnóstica |
| **Edge Proxy** | `make up-edge` | Caddy (HTTPS + Basic Auth) | 🌐 Controlada |

---

## 🛡️ Hardening de la Cadena de Suministro (Supply Chain)

> [!CAUTION]
> **Mitigación Trivy (Marzo 2026)**:
> Tras el compromiso global de las etiquetas de `aquasecurity/trivy-action`, hemos implementado una política de **Verificación Proactiva**:
> 1.  **Pins de Versión**: Se han eliminado todas las referencias a versiones comprometidas (ej. `0.33.1`).
> 2.  **Etiquetas Seguras**: El CI/CD utiliza exclusivamente **`v0.35.0`** o superiores, validadas contra firmas oficiales.
> 3.  **Auditoría de Imágenes**: Todas las imágenes base (Alpine, Ubuntu, Microsoft) están ancladas a versiones específicas para evitar ataques de inyección en tiempo de construcción.

### Medidas adicionales (v4.2.0)

| Control | Implementación | Protege contra |
| :--- | :--- | :--- |
| **Unicode bidi scan** | Job `supply-chain-checks` en CI (Python puro) | CVE-2021-42574 "Trojan Source" — código malicioso camuflado con caracteres invisibles |
| **Obfuscation scan** | Mismo job — detecta `eval(b64decode(...))` | Base64-encoded payloads ejecutados dinámicamente |
| **Dependabot** | `.github/dependabot.yml` — 11 ecosistemas | Versiones de dependencias con CVEs conocidos |
| **Line endings** | `.gitattributes` — `*.sh eol=lf` | Scripts con CRLF que fallan con `bad interpreter` dentro de contenedores Linux |

---

## 🕸️ Aislamiento de Red y Puertos

Por defecto, todos los servicios publican sus puertos exclusivamente en el interfaz de loopback (`127.0.0.1`), impidiendo el acceso desde otros dispositivos en la red local.

| Servicio | Puerto | Exposición Recomendada |
| :--- | :--- | :--- |
| **n8n** | `5678` | Loopback / Proxy Autenticado |
| **Grafana** | `3000` | Loopback |
| **cAdvisor** | `8089` | **NUNCA EXPONER**. Acceso al Socket Docker. |
| **Gateways** | `8080-8090`| Loopback |

---

## 📂 Gestión de Secretos en Runtime

El sistema orquesta más de 40 variables de entorno críticas que deben gestionarse mediante archivos `.env` (nunca persistidos en el repositorio):

### Componentes Clave:
- **Orquestación**: `N8N_ENCRYPTION_KEY`, `N8N_OWNER_PASSWORD`.
- **Persistencia**: `CASE[01-08]_DB_PASSWORD`.
- **Integración**: `INTEGRATION_API_KEY`, `GITHUB_TOKEN`.
- **Edge**: `EDGE_BASIC_AUTH_HASH` (Bcrypt).

---

## ⚙️ Guardrails de Validación Automática

El script `scripts/check_runtime_security.py` actúa como un centinela que bloquea el CI si detecta:
- ❌ Uso de etiquetas `:latest` en Compose o Dockerfiles.
- ❌ Puertos publicados sin vinculación local explícita.
- ❌ Secretos detectados en plano en la configuración del runtime.
- ❌ Ausencia de perfiles de seguridad en componentes críticos.

El job `supply-chain-checks` (CI) bloquea el pipeline si detecta:
- ❌ Caracteres Unicode bidireccionales en archivos de código fuente.
- ❌ Patrones de ofuscación con `eval` + `base64` en Python, JS, Ruby, PHP o Shell.

---

## 🌐 HTTP Security Headers (v4.2.0)

Todos los servicios web del laboratorio sirven el conjunto completo de headers de seguridad:

| Header | Valor | Protege contra |
| :--- | :--- | :--- |
| `X-Frame-Options` | `SAMEORIGIN` | Clickjacking |
| `X-Content-Type-Options` | `nosniff` | MIME sniffing |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Fuga de información a terceros |
| `Content-Security-Policy` | `default-src 'self'; ...` | XSS, inyección de recursos externos |
| `Permissions-Policy` | `geolocation=(), camera=(), ...` | Abuso de APIs del navegador |
| `Strict-Transport-Security` | `max-age=31536000` | Downgrade a HTTP (solo en edge HTTPS) |

**Implementación**:
- **Apache** (`master-dashboard`, `dest-php`, `dest-symfony`): `apache/security-headers.conf` montado en `/etc/apache2/conf-enabled/` con `mod_headers`.
- **Caddy** (perfil `edge`): bloque `header {}` en `edge/start-caddy.sh`.

---
*Modelo de seguridad operativa v4.2 — Social Bot Scheduler*
