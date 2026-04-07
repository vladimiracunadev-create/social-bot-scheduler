## 🛡️ Guardrails Implementados

Este caso incluye mecanismos de resiliencia en la capa de n8n:

### Reintentos Automáticos
- El nodo HTTP Request está configurado con **3 reintentos** (backoff de 1 segundo).
- Si el servicio de destino está caído, n8n intentará 3 veces antes de marcar el envío como fallido.

### Dead Letter Queue (DLQ)
- Si todos los reintentos fallan, el payload se envía a un endpoint `/errors` del servicio de destino.
- Los errores se registran con timestamp, caso, error y payload completo.
- Esto permite auditoría y reintentos manuales posteriores.

### Idempotencia
- Implementada globalmente en todos los casos (01-09) mediante `scripts/check_idempotency.py`.
- Genera un hash del payload y lo persiste en SQLite (`fingerprints.db`).
- Si el hash ya existe, retorna `200 OK` sin reenviar el mensaje.

Para más detalles, consulta la guía de [Guardrails](../../docs/GUARDRAILS.md).
