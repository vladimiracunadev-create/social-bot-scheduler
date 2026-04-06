# 🛡️ Guía Maestra de Resiliencia Industrial

Esta guía detalla la implementación de los mecanismos de defensa y recuperación post-fallo integrados en la matriz del **Social Bot Scheduler**. Nuestra arquitectura garantiza que el sistema siga operativo incluso ante interrupciones de servicios externos.

---

## 📊 Cobertura de Resiliencia

El 100% de los **9 casos de integración** cuentan con el siguiente stack de resiliencia:

| Mecanismo | Propósito Técnico | Estado |
| :--- | :--- | :---: |
| **Circuit Breaker** | Evita saturación de servicios caídos o degradados. | 🟢 9/9 |
| **Idempotencia** | Previene el procesamiento de eventos duplicados. | 🟢 9/9 |
| **Dead Letter Queue**| Captura mensajes que fallan tras múltiples reintentos. | 🟢 9/9 |
| **Backoff Exponencial**| Estrategia inteligente de reintentos en n8n. | 🟢 9/9 |

---

## 🏗️ Arquitectura de Defensa (Guardrails)

### Scripts Centralizados
Todos los casos heredan lógica de resiliencia desde el directorio `scripts/`, garantizando uniformidad en el comportamiento del ecosistema:

- **`check_idempotency.py`**: Gestión de fingerprints únicos mediante una base de datos **SQLite** compartida.
- **`circuit_breaker.py`**: Motor de gestión de estados del circuito (CLOSED, OPEN, HALF_OPEN).
- **`shared/fingerprints.db`**: Persistencia volátil para rastro de eventos procesados.

---

## 🔑 Patrón: Idempotencia Permanente

Para evitar la duplicidad de posts en las redes sociales de destino, el sistema genera un **Fingerprint** único por evento.

### Funcionamiento Técnico:
1. El Webhook de n8n extrae el ID y el Canal del post.
2. Consulta el script de idempotencia:
   ```bash
   python3 scripts/check_idempotency.py check "post_123" "twitter"
   ```
3. Si el registro existe, n8n detiene la ejecución inmediatamente (éxito falso).
4. Si es nuevo, procede al envío y registra el rastro en SQLite.

---

## ⚡ Patrón: Circuit Breaker (Disyuntor)

Protege a n8n y a los servicios de destino de una cascada de fallos en el ecosistema.

### Estados del Circuito:
- **🟢 CLOSED**: Funcionamiento nominal. Las peticiones fluyen libremente.
- **🔴 OPEN**: El sistema detectó 5 fallos consecutivos. Se rechazan las peticiones de inmediato por 5 minutos.
- **🟡 HALF_OPEN**: Periodo de prueba. Permite una única petición para validar la recuperación del destino.

### Diagnóstico de Estado:
```bash
python3 scripts/circuit_breaker.py status
```

---

## 🚨 Dead Letter Queue (DLQ)

Cuando la resiliencia proactiva no es suficiente y los reintentos agotan su ciclo, el mensaje se redirige al **DLQ**.

### Gestión de Errores:
- Cada contenedor de destino dispone de un endpoint `/errors`.
- Los fallos se registran con el payload original, el timestamp y el error HTTP recibido para auditoría manual.
- **Inspección**: `cat cases/*/dest/logs/errors.log`.

---
*Manual de arquitectura de resiliencia v4.0 — Social Bot Scheduler*
