# 📜 Catálogo de Funcionalidades

Este documento detalla todas las capacidades actuales del bot y su impacto técnico.

| Funcionalidad | Descripción | Estado |
| :--- | :--- | :--- |
| **Programación ISO** | Soporte para fechas en formato ISO 8601 estándar. | ✅ Estable |
| **Multi-Canal** | Capacidad de enviar un post a múltiples destinos definidos en un array. | ✅ Estable |
| **Gestión de Estado** | Marcado automático de posts enviados para evitar duplicidad. | ✅ Estable |
| **Integración n8n** | Compatible con el nodo Webhook de n8n nativamente. | ✅ Estable |
| **Aprovisionamiento K8s** | Despliegue automatizado como **CronJob** en Kubernetes. | ✅ Estable |
| **Logs en Tiempo Real** | Salida estandarizada con `logging` para monitoreo. | ✅ Estable |
| **Validación Pydantic** | Validación estricta de esquemas antes de procesar archivos. | ✅ Estable |

## Próximas Incorporaciones
- Validación de archivos JSON mediante JSON Schema mejorado.
- Soporte para adjuntos (imágenes/archivos) en el payload.
- Interfaz CLI para añadir posts sin editar manualmente el JSON.
