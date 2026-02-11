# Seguridad

Gracias por tomar en cuenta la seguridad de este proyecto.

## Versiones Soportadas

| Versión | Soportado |
| ------- | --------- |
| 2.3.x   | ✅ |
| 2.1.x   | ❌ |
| < 2.0   | ❌ |

## Cómo reportar una vulnerabilidad

Si encuentra una vulnerabilidad, envíe un correo a **maintainer@example.com** con la siguiente información:
- Resumen claro del problema.
- Pasos para reproducirlo (si aplica).
- Impacto potencial y, si es posible, una prueba de concepto mínima.

Por favor, **no** divulgue públicamente la vulnerabilidad hasta que se haya coordinado un arreglo o hasta que los mantenedores indiquen lo contrario.

## Detalles Técnicos de Hardening

Este repositorio implementa una estrategia de **Defensa en Profundidad** para garantizar un entorno de ejecución seguro y libre de vulnerabilidades.

### 🛡️ Estrategia de Imágenes Docker (Dual-Layer Patching)
Nuestras imágenes utilizan un diseño multi-etapa avanzado para eliminar vulnerabilidades (CVEs):
1.  **Aislamiento en App (Virtual Environment)**: La aplicación se instala en un `venv` aislado (`/opt/venv`). Las dependencias críticas como `wheel` y `jaraco.context` están estrictamente bloqueadas a versiones parchadas.
2.  **Hardening del Sistema Base**: En la etapa final del build, realizamos un parcheo activo de los paquetes del sistema (`pip`, `setuptools`, `wheel`) preinstalados en la imagen base `slim-bookworm`.
3.  **Usuario no-root**: Ejecución forzada con el usuario `botuser` (UID 1000) para minimizar el impacto en caso de compromiso.

### 🔍 Auditoría Continua (Triple Scan)
Cada cambio en el código activa un pipeline de CI enriquecido con:
-   **Trivy**: Escaneo de vulnerabilidades en el SO y librerías de la imagen final (Exit code 1 en fallos críticos).
-   **pip-audit**: Auditoría profunda de vulnerabilidades en el árbol de dependencias de Python.
-   **Gitleaks**: Búsqueda proactiva de secretos, llaves API y tokens en el historial de git.

### 🏗️ Aislamiento de Red y Kubernetes
-   **Zero Trust Networking**: `NetworkPolicies` de denegación por defecto (Egress whitelist solo para destinos aprobados).
-   **Validación de Entradas**: El HUB CLI (`hub.py`) valida nombres de casos mediante expresiones regulares estrictas para prevenir Path Traversal y RCE.
