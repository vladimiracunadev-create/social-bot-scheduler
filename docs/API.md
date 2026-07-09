# 🔌 Referencia de API (Webhook) — Contract Documentation

Esta guía documenta el contrato de comunicación asíncrona entre los motores de origen (bots políglotas) y el orquestador central (**n8n**). El cumplimiento de este esquema es mandatorio para garantizar la integridad de los datos en toda la matriz.

---

## 📡 Protocolo de Comunicación

Todas las integraciones utilizan el protocolo **HTTPS/POST** para el envío de payloads. Los servicios de origen actúan como clientes de un Webhook efímero o persistente expuesto por el mediador.

### Estructura del Payload Estándar

Campos universales en toda la matriz: `id`, `text`, `scheduled_at`. El campo de canal tiene **dos formas** según la generación del caso (ver nota abajo).

**Matriz políglota (casos 10–20) — canal singular:**

```json
{
  "id": "uuid-v4-string",
  "text": "Contenido del post o mensaje a programar",
  "channel": "graphql",
  "scheduled_at": "2026-04-06T14:30:00Z"
}
```

**Núcleo original (casos 01–06) — multi-canal (array):**

```json
{
  "id": "uuid-v4-string",
  "text": "Contenido del post o mensaje a programar",
  "channels": ["twitter", "linkedin", "telegram"],
  "scheduled_at": "2026-04-06T14:30:00Z"
}
```

---

## 📋 Especificación de Atributos

| Atributo | Tipo | Restricción | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` / `String` | Único | Identificador de trazabilidad para evitar duplicados en n8n (fingerprint/idempotencia). |
| `text` | `String` | Máx. 280-3000 | El contenido real que será publicado en el destino final. |
| `channel` | `String` | — | Identificador de canal único. **Contrato de los casos 10–20.** |
| `channels` | `Array` | No vacío | Lista de canales para ruteo multi-destino. **Contrato del núcleo (casos 01–06).** |
| `scheduled_at` | `DateTime` | ISO8601 | Marca de tiempo original de programación del evento. |

> [!NOTE]
> El laboratorio arrastra **dos convenciones de canal**: el núcleo original (01–06) usa `channels` (array, multi-destino); la matriz políglota (10–20) usa `channel` (string). Los casos 07–09 no incluyen campo de canal. Unificar ambas convenciones queda como deuda técnica pendiente.

---

## 🛡️ Control de Errores y Seguridad

### Códigos de Respuesta
- **🟢 200/201 (Created)**: Éxito. El bot marcará el post como procesado exitosamente.
- **🟡 429 (Too Many Requests)**: El mediador está saturado. Se activa el **Circuit Breaker** en el origen.
- **🔴 500 (Internal Error)**: Fallo en el orquestador. El mensaje se redirige automáticamente al **DLQ (Dead Letter Queue)** si está configurado.

> [!IMPORTANT]
> **Hardening de API**: En entornos de producción, todas las peticiones deben incluir un encabezado `X-API-KEY` o `Authorization: Bearer` para validar la autenticidad del origen.

---
*Especificación técnica v4.9.0 — Social Bot Scheduler*
