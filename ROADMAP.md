# 🛣️ Roadmap — Social Bot Scheduler

Este documento describe la evolución técnica y los objetivos estratégicos del proyecto. Seguimos un enfoque de mejora continua en seguridad y observabilidad.

---

## ✅ Hitos Completados

### `v4.2.0` — "Auditoría de Seguridad de 8 Capas" 🛡️ Ready
- [x] **HTTP Security Headers**: `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, `Referrer-Policy`, `Permissions-Policy` y `Options -Indexes` en todos los servicios Apache y en el edge proxy Caddy.
- [x] **Dependabot**: Configurado para 11 ecosistemas (pip, docker, gomod, cargo, npm, github-actions).
- [x] **Line endings LF**: `.gitattributes` fuerza LF en scripts shell/Python/Go para eliminar errores `bad interpreter` en Windows.
- [x] **Detección Trojan Source**: CI detecta caracteres Unicode bidireccionales (CVE-2021-42574) en todo el código fuente.
- [x] **Detección de ofuscación**: CI detecta patrones `eval(base64_decode(...))` y equivalentes.
- [x] **Auditoría documentada**: `SECURITY.md` reemplazado por informe completo con estado, riesgos aceptados y pendientes priorizados.

### `v4.1.0` — "Hardening Industrial" 🛡️ Ready
- [x] **Mitigación Supply Chain**: Resolución proactiva del compromiso de `trivy-action` (v0.35.0).
- [x] **Docs Professionalization**: Rediseño visual de toda la base de conocimientos del laboratorio.
- [x] **Audit Trail**: Refuerzo de logs de auditoría en el HUB CLI.
- [x] **Security Badging**: Estandarización de badges "Hardened" en toda la matriz.

### `v4.0.0` — "Persistencia Políglota" 🟢 Ready
- [x] **8 Motores de BD**: Integración con MySQL, Postgres, MSSQL, MongoDB, Redis, Cassandra y DuckDB.
- [x] **Agnosticismo Total**: Casos prácticos en Rust, C#, Go y Laravel conectando a n8n.
- [x] **Matrix Dashboard**: Visualización unificada de los 9 casos en tiempo real.

### `v3.0.0` — "Observabilidad y Resiliencia" 🟢 Ready
- [x] **Stack CNCF**: Despliegue de Prometheus, Grafana y cAdvisor.
- [x] **Guardrails**: Implementación de Circuit Breaker e Idempotencia en los 9 flujos.

---

## 🚀 En Desarrollo (v4.3+)

### 🔒 Seguridad — Pendientes Priorizados
- [ ] **Lock file con hashes SHA** (P-01): `pip-compile --generate-hashes` para verificación criptográfica de dependencias Python.
- [ ] **Rate limiting en Case 09** (P-02): Añadir `slowapi` o middleware de throttling al FastAPI gateway.
- [ ] **Whitelist de owners en Case 09** (P-03): Validar el parámetro `owner` con regex `^[a-zA-Z0-9-]{1,39}$`.
- [ ] **Auditoría CVE multi-lenguaje** (P-04): `govulncheck`, `npm audit --audit-level=high`, `cargo audit`, `bundler-audit`, `dotnet list package --vulnerable` en CI.

### 🌐 Conectividad Edge y Avanzada
- [ ] **Auto-TLS**: Gestión de certificados locales (mTLS) para entornos críticos.
- [ ] **Playwright E2E**: Pruebas automatizadas de interfaz para validar la matriz total.

---

## 🔮 Futuro (v5.0+)

### ☁️ Cloud Native & Scalability
- [ ] **Terraform/IaC**: Despliegue automatizado en AWS ECS Fargate y Google Cloud Run.
- [ ] **Kubernetes Heavy**: Helm Charts oficiales y NetworkPolicies granulares.
- [ ] **Auth Centralizada**: Integración de Authelia o Keycloak para proteger los hubs.

---
*Última actualización: Abril 2026 — Vladimir Acuña*

