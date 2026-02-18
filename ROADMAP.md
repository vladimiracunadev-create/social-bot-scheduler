# Roadmap — Social Bot Scheduler

Este documento describe la evolución y el futuro del proyecto.

## ✅ Hitos Completados

### v4.0.0 — "Persistencia Políglota" (Actual)
- [x] Integración de 8 motores de bases de datos (SQL, NoSQL, KV).
- [x] Dashboard dinámico con previsualización de datos en tiempo real.
- [x] Auto-provisionamiento de esquemas en 8 lenguajes.

### v3.0.0 — "Observabilidad Industrial"
- [x] Matriz de 8 casos interoperables (Python, Go, Node, PHP, Rust, Ruby, C#, Laravel).
- [x] Sistema de Resiliencia Global: Circuit Breaker, Idempotencia (SQLite), DLQ.
- [x] Hub CLI centralizado para diagnósticos (`make doctor`).
- [x] Infrastructure Monitoring: Prometheus + Grafana.

### v1.0 - v2.0
- [x] Orquestación base con n8n.
- [x] Dashboard unaificado.
- [x] Dockerización completa.

## 🔮 Futuro (v4.0+)

### Infraestructura Cloud
- [ ] **Terraform**: IaC para despliegue en AWS (ECS Fargate).
- [ ] **HTTPS/TLS**: Certificados automáticos con Traefik o Cert Manager.

### Funcionalidad Extendida
- [ ] **K8s Advanced**: Despliegue con Helm Charts y Auto-scaling.
- [ ] **Auth Centralizada**: Keycloak o gestión de usuarios simple.

## Cómo contribuir
Si quieres contribuir, revisa `CONTRIBUTING.md` y busca issues etiquetados como `roadmap`.

