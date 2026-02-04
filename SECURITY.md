# Seguridad

Gracias por tomar en cuenta la seguridad de este proyecto.

## Versiones Soportadas

| Versión | Soportado |
| ------- | --------- |
| 2.2.x   | ✅ |
| 2.1.x   | ❌ |
| < 2.0   | ❌ |

## Cómo reportar una vulnerabilidad

Si encuentra una vulnerabilidad, envíe un correo a **maintainer@example.com** con la siguiente información:
- Resumen claro del problema.
- Pasos para reproducirlo (si aplica).
- Impacto potencial y, si es posible, una prueba de concepto mínima.

Por favor, **no** divulgue públicamente la vulnerabilidad hasta que se haya coordinado un arreglo o hasta que los mantenedores indiquen lo contrario.

## Detalles Técnicos de Hardening

### Validación de Entradas
El **HUB CLI** (`hub.py`) utiliza expresiones regulares estrictas `^[a-zA-Z0-9_\-]+$` para validar los nombres de los casos de uso, mitigando riesgos de inyección de comandos y Path Traversal.

### Aislamiento de Red
Se incluyen `NetworkPolicies` para Kubernetes que implementan un modelo de **Zero Trust**:
- Egress limitado exclusivamente a `n8n` y APIs de redes sociales aprobadas.
- Ingress bloqueado por defecto para todos los pods de bots.

### Seguridad en Imágenes
- Imágenes basadas en `slim-bookworm` para reducir el área de ataque.
- Actualización automática de `pip` en el build para mitigar CVEs conocidos (ej: CVE-2026-1703).
- Ejecución con usuario `botuser` (UID 1000).
