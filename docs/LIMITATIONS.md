# ⚠️ Limitaciones y Consideraciones Técnicas

Este proyecto es un **laboratorio de ingeniería** y, como tal, tiene ciertas decisiones de diseño (trade-offs) que debes conocer.

## 1. Entorno de Simulación
-   **Destinos Locales**: Los receptores (PHP, Go, Node, etc.) son servidores web locales simplificados. No interactúan con las APIs reales de Twitter, LinkedIn o Facebook.
-   **Autenticación**: Se simula un envío exitoso mediante webhooks simples. No se implementa OAuth2 real (necesario para producción en redes sociales).

## 2. Escalabilidad
-   **Persistencia SQLite**: El sistema de idempotencia usa SQLite (`fingerprints.db`). Para un entorno distribuido de alta carga, esto debería migrarse a Redis o PostgreSQL.
-   **n8n Community**: Se utiliza la versión self-hosted gratuita de n8n. Funciones empresariales (SSO, User Management detallado) no están incluidas.

## 3. Seguridad
-   **Secretos en .env**: Aunque el `.env` no se sube al repo, en un entorno de producción real se recomienda usar un Secret Manager (AWS Secrets Manager, HashiCorp Vault).
-   **Tráfico HTTP interno**: La comunicación entre contenedores es HTTP dentro de la red Docker interna (`bot-network`). No está expuesto a la red local gracias al binding `127.0.0.1`. El perfil `edge` añade TLS en el borde con Caddy.
-   **HTTP Security Headers** *(resuelto en v4.2.0)*: Todos los servicios Apache y el proxy Caddy sirven el conjunto completo de headers de seguridad (CSP, X-Frame-Options, Permissions-Policy, etc.).
-   **Fallback de credenciales**: Los valores `change-me-*` en `docker-compose.yml` permiten arrancar el lab sin `.env`. El script `n8n_auto_setup.sh` emite un warning. Riesgo local aceptado — nunca exponer sin el perfil `edge` autenticado.
-   **Lock file con hashes**: `requirements.txt` no incluye hashes SHA. `pip-audit` detecta CVEs en CI. Solución completa: `pip-compile --generate-hashes` (pendiente P-01).

## 4. Orquestación
-   **Docker Compose**: Ideal para desarrollo y pruebas. Para producción, se recomienda trasladar los manifiestos de Kubernetes (`k8s/`) a un clúster real (EKS/AKS).

---
*Estas limitaciones son intencionales para mantener el proyecto portable y educativo.*

## 5. Alcance de Observabilidad (v3.0)
-   **Métricas Técnicas vs de Negocio**: Actualmente exponemos métricas de plataforma (CPU, RAM, Event Loop, Conteo de Workflows). Métricas de negocio específicas (ej. "ROI de posts en LinkedIn") requerirían nodos de n8n personalizados enviando a Pushgateway, lo cual está fuera del alcance actual.

