# 🛣️ Roadmap — Social Bot Scheduler

Este documento describe la evolución técnica y los objetivos estratégicos del proyecto.

---

## ✅ Hitos Completados

### `v4.0.0` — "Persistencia Políglota" 🟢 Ready
- [x] **8 Motores de BD**: Integración nativa con SQL (MySQL, PSQL, MSSQL), NoSQL (Mongo, Redis, Cassandra) y DuckDB.
- [x] **Agnosticismo Total**: Casos prácticos en Rust, C#, Go y Laravel conectando a n8n.
- [x] **Hardening de Seguridad**: Puertos bindeados a localhost y secretos vía variables.
- [x] **Matrix Dashboard**: Visualización unificada de los 9 casos.

### `v3.0.0` — "Observabilidad Industrial" 🟢 Ready
- [x] **Stack CNCF**: Despliegue de Prometheus, Grafana y cAdvisor.
- [x] **Resiliencia**: Implementación de Circuit Breaker e Idempotencia en los flujos.
- [x] **CLI Facade**: Creación de `hub.py` para gestión simplificada del laboratorio.

---

## 🚀 En Desarrollo (v4.1+)

### 🌐 Conectividad Edge
- [ ] **Caddy Integration**: Refinamiento del perfil `edge` para acceso remoto seguro.
- [ ] **Auto-TLS**: Gestión de certificados locales para entornos de desarrollo.

---

## 🔮 Futuro (v5.0+)

### ☁️ Cloud & Scalability
- [ ] **Terraform**: IaC para despliegue en AWS ECS Fargate y Google Cloud Run.
- [ ] **Kubernetes Advanced**: Helm Charts oficiales y políticas de red (NetworkPolicies) granulares.
- [ ] **Auth Centralizada**: Integración de Authelia o Keycloak para proteger los dashboards.

### 🧪 Innovación
- [ ] **IA Agents Integration**: Casos de uso con LangChain/n8n AI para programar posts automáticamente.

---

## 🤝 Cómo Contribuir
Si quieres sumar un nuevo lenguaje o motor de base de datos, revisa [CONTRIBUTING.md](CONTRIBUTING.md) y busca issues etiquetados como `roadmap`.

---

*Última actualización: Abril 2026*

