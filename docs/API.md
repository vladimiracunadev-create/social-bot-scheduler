# 🔌 Referencia de API (Webhook)

Aunque el bot es principalmente un consumidor, la comunicación con el webhook saliente sigue un contrato estricto.

## Estructura del Payload Saliente

Cuando el bot encuentra un post pendiente, realiza una petición **POST** a la `WEBHOOK_URL` con el siguiente cuerpo JSON:

```json
{
  "id": "string",
  "text": "string",
  "channels": ["string"],
  "scheduled_at": "ISO8601 Timestamp"
}
```

### Detalle de Campos
| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | UUID/String | Identificador único para evitar duplicados en n8n. |
| `text` | String | El mensaje que será publicado. |
| `channels` | Array | Lista de identificadores de canales (identificados en n8n). |
| `scheduled_at` | DateTime | Fecha original programada. |

## Respuestas Esperadas
- **200 OK**: El bot marcará el envío como exitoso.
- **4xx/5xx**: El bot registrará un error en los logs. Se recomienda implementar lógica de reintento en el servidor del webhook si es necesario.

## Seguridad
- Se recomienda el uso de `HTTPS` para la `WEBHOOK_URL`.
- En futuras versiones se implementará soporte para headers de autenticación (API Keys/Bearer Tokens).
