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
-   **Tráfico HTTP**: La comunicación interna entre contenedores es HTTP (puerto 80). En una red pública debería ser HTTPS/TLS.

## 4. Orquestación
-   **Docker Compose**: Ideal para desarrollo y pruebas. Para producción, se recomienda trasladar los manifiestos de Kubernetes (`k8s/`) a un clúster real (EKS/AKS).

---
*Estas limitaciones son intencionales para mantener el proyecto portable y educativo.*
