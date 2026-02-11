# 🛡️ Hardening de Seguridad

Este proyecto ha sido robustecido para cumplir con estándares de seguridad industrial y garantizar imágenes de contenedor libres de vulnerabilidades.

## Estrategia de Triple Capa

### 1. Inmunidad a CVEs (Dual-Layer Patching)
Nuestras imágenes Docker se limpian en dos niveles:
-   **App Layer**: Uso de Entornos Virtuales (`venv`) con dependencias estrictas y parchadas.
-   **System Layer**: Actualización activa de los paquetes del sistema base (`pip`, `setuptools`, `wheel`) en la etapa final del build.

### 2. Escaneo Proactivo (Triple Scan)
El pipeline de CI/CD realiza tres auditorías automáticas en cada push:
-   **Trivy**: Escaneo de vulnerabilidades en el SO y librerías.
-   **pip-audit**: Auditoría de dependencias de Python.
-   **Gitleaks**: Detección de secretos y llaves filtradas.

### 3. Principio de Menor Privilegio
- El contenedor nunca corre como root (usuario `botuser`).
- Políticas de red (**NetworkPolicies**) Zero Trust que bloquean todo el tráfico entrante por defecto.

## 🛡️ Resiliencia Industrial

Además de la seguridad, el sistema implementa **Guardrails** para tolerancia a fallos:
- **Idempotencia**: Prevención de duplicados.
- **Circuit Breaker**: Protección contra caídas.
- **DLQ**: Manejo de errores irrecuperables.

Consulta la guía completa de [Resiliencia y Guardrails](Resilience.md).
