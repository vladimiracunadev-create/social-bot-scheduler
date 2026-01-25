# 📜 Catálogo de Funcionalidades

Este documento detalla todas las capacidades actuales del bot y su impacto técnico.

| Funcionalidad | Descripción | Estado |
| :--- | :--- | :--- |
| **Programación ISO** | Soporte para fechas en formato ISO 8601 estándar. | ✅ Estable |
| **Multi-Canal** | Capacidad de enviar un post a múltiples destinos definidos en un array. | ✅ Estable |
| **Modo Dry-Run** | Ejecución de prueba que solo muestra por consola lo que enviaría. | ✅ Estable |
| **Integración n8n** | Compatible con el nodo Webhook de n8n nativamente. | ✅ Estable |
| **Aprovisionamiento K8s** | Despliegue automatizado como Pod en Kubernetes. | 🛠️ En mejora |
| **Logs en Tiempo Real** | Salida estandarizada para monitoreo en contenedores. | ✅ Estable |

## Próximas Incorporaciones
- Validación de archivos JSON mediante JSON Schema.
- Soporte para adjuntos (imágenes/archivos) en el payload.
- Interfaz CLI para añadir posts sin editar manualmente el JSON.
