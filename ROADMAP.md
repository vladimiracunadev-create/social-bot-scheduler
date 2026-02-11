# Roadmap — Social Bot Scheduler

Este documento describe la evolución y el futuro del proyecto.

## ✅ Hitos Completados

### v2.3.0 — "Resiliencia Industrial" (Actual)
- [x] Matriz de 8 casos interoperables (Python, Go, Node, PHP, Rust, Ruby, C#, Laravel).
- [x] Sistema de Resiliencia Global: Circuit Breaker, Idempotencia (SQLite), DLQ.
- [x] Hub CLI centralizado para diagnósticos (`make doctor`).
- [x] Hardening de Seguridad (Trivy scan, User permissions).

### v1.0 - v2.0
- [x] Orquestación base con n8n.
- [x] Dashboard unificado.
- [x] Dockerización completa.

---

## 🔮 Futuro (v3.0+)

### Observabilidad Avanzada
- [ ] **Prometheus Exporter**: Exponer métricas de n8n y contenedores.
- [ ] **Grafana Dashboard**: Visualización de latencia, tasa de errores y volumen de mensajes.

### Infraestructura Cloud
- [ ] **Terraform**: IaC para despliegue en AWS (ECS Fargate).
- [ ] **HTTPS/TLS**: Certificados automáticos con Traefik o Cert Manager.

### Funcionalidad Extendida
- [ ] **APIs Reales**: Adaptadores opcionales para conectar con APIs (Sandbox) de Twitter/LinkedIn.
- [ ] **Auth Centralizada**: Keycloak o gestión de usuarios simple.

## Cómo contribuir
Si quieres contribuir, revisa `CONTRIBUTING.md` y busca issues etiquetados como `roadmap`.

