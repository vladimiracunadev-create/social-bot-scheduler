# 🛡️ n8n Guardrails: Resiliencia y Seguridad

Esta guía detalla los "Guardrails" obligatorios para la capa de **Bridge (n8n)** en el ecosistema Social Bot Scheduler. Estos patrones aseguran que el sistema sea resistente a fallos de red, límites de API (Rate Limits) y evite la duplicación de contenido.

---

## 1. Idempotencia (Idempotency)

La idempotencia garantiza que realizar la misma operación varias veces produzca el mismo resultado que realizarla una sola vez.

### Mecanismo: "Post Fingerprint"
Cada petición al Webhook de n8n debe ser validada contra un registro persistente para evitar duplicados en una ventana de tiempo.

- **Hash del Payload**: `SHA256(payload + target_platform + timestamp_bucket)`
- **Lógica en n8n**:
    1.  Recibir Webhook.
    2.  Calcular Hash.
    3.  Consultar en DB (SQLite/Redis) si el Hash ya existe.
    4.  Si existe: Responder `200 OK` (Duplicado ignorado).
    5.  Si no existe: Registrar Hash y proceder.

> [!TIP]
> Usa un `timestamp_bucket` (ej: hora actual) para permitir reintentos legítimos después de un largo periodo si es necesario, pero bloquear ráfagas accidentales.

---

## 2. Circuit Breaker (Cortafuegos)

Evita que n8n siga intentando peticiones fallidas a un proveedor que está caído o limitando conexiones, protegiendo así el sistema y evitando baneos de IP.

### Estados:
- **CLOSED (Cerrado)**: Funcionamiento normal. Las peticiones pasan.
- **OPEN (Abierto)**: El proveedor ha fallado `X` veces. n8n desvía las peticiones al **DLQ** inmediatamente sin intentar la API.
- **HALF-OPEN (Semi-Abierto)**: Después de un tiempo de espera, se permite una petición de prueba. Si tiene éxito, se vuelve a **CLOSED**.

### Configuración sugerida:
- **Threshold**: 5 fallos consecutivos (HTTP 429, 500, 503).
- **Timeout de espera**: 5 minutos antes de pasar a Half-Open.

---

## 3. Dead Letter Queue (DLQ)

La "Cola de Mensajes Muertos" es el lugar donde terminan las peticiones que no pudieron ser procesadas después de los reintentos automáticos.

### Implementación Logica:
1.  **Captura de Errores**: Todo nodo de social API debe tener una salida de "Error" conectada al DLQ.
2.  **Almacenamiento**: Guardar el JSON original, el error y la hora del fallo en una tabla `failed_posts`.
3.  **Gestión**:
    -   **Reintento Automático**: Un flujo programado (Cron) intenta procesar el DLQ cada 30 minutos (solo si el Circuit Breaker está CLOSED).
    -   **Alerta**: Notificar al dashboard de destino sobre el fallo.

---

## 🔑 Idempotencia Real (Caso 01)

### Implementación

**Archivo**: `cases/01-python-to-php/n8n/check_idempotency.py`

Script Python que verifica y agrega fingerprints con TTL de 24 horas:

```python
# Verificar si un fingerprint ya fue procesado
python3 check_idempotency.py check "post-123_twitter"
# Output: {"exists": false, "fingerprint": "post-123_twitter"}

# Agregar fingerprint al registro
python3 check_idempotency.py add "post-123_twitter"
# Output: {"added": true, "fingerprint": "post-123_twitter"}
```

**Persistencia**: `cases/01-python-to-php/n8n/processed_fingerprints.json`

```json
{
  "post-123_twitter": "2026-02-11T13:00:00.123456",
  "post-456_facebook": "2026-02-11T13:05:00.789012"
}
```

### Workflow n8n

```
Webhook → Set Fingerprint → Check Idempotency → Is New Post?
                                                      │
                                                      └─ (if new) → Add Fingerprint → HTTP Request
                                                      │
                                                      └─ (if duplicate) → END (no procesa)
```

### Pruebas

Ver guía completa: [IDEMPOTENCY_TEST.md](file:///c:/dev/social-bot-scheduler/cases/01-python-to-php/IDEMPOTENCY_TEST.md)

**Prueba rápida:**
```bash
bash cases/01-python-to-php/test_idempotency.sh
```

### Limitaciones

- ⚠️ **Solo Caso 01**: Otros casos NO tienen idempotencia
- ⚠️ **Archivo JSON**: No es escalable para alto volumen
- ⚠️ **TTL fijo**: 24 horas hardcodeado
- ⚠️ **Sin transacciones**: Race conditions posibles en alta concurrencia

### Próximos Pasos

1. Migrar a SQLite o Redis
2. Hacer TTL configurable
3. Replicar a casos 02-08

---

## 🚀 Resumen de Flujo Seguro

1.  **Identificar**: ¿Es este post un duplicado? (Implementado a nivel de aplicación)
2.  **Protección**: ¿Está el servicio de destino disponible? (Reintentos automáticos)
3.  **Acción**: Publicar.
4.  **Respaldo**: Si falla, mover al DLQ.

---

## 🧪 Implementación Real (Caso 01)

El **Caso 01 (Python → PHP)** sirve como prueba de concepto de estos guardrails:

### Reintentos Configurados
```json
"options": {
  "retryOnFail": true,
  "maxRetries": 3,
  "waitBetweenRetries": 1000
}
```

### DLQ Funcional
- **Endpoint**: `POST http://dest-php:80/errors`
- **Registro**: `cases/01-python-to-php/dest/logs/errors.log`
- **Formato**: `[timestamp] CASE=01 | ERROR={...} | PAYLOAD={...}`

### Cómo Probar
1. Levantar entorno: `docker-compose up -d`
2. Detener destino: `docker-compose stop dest-php`
3. Ejecutar bot: `python cases/01-python-to-php/origin/bot.py`
4. Observar en n8n: 3 reintentos fallidos → envío a DLQ
5. Verificar: `cat cases/01-python-to-php/dest/logs/errors.log`
