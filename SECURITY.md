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

## Hardening Aplicado
- **Aislamiento**: Ejecución como usuario no-root en contenedores.
- **Validación**: Filtros contra Path Traversal y RCE en el CLI.
- **Red**: NetworkPolicies restrictivas para limitar el tráfico lateral.
- **Escaneo**: Análisis automático de dependencias y secretos en CI/CD.
