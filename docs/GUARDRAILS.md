# 🛡️ n8n Guardrails: Resiliencia y Seguridad

Esta gu?a detalla los "Guardrails" implementados en la capa de **Bridge (n8n)** del ecosistema Social Bot Scheduler. Estos patrones aseguran que el sistema sea resistente a fallos, evite duplicados y maneje errores de forma robusta en **TODOS los 9 casos de integraci?n**.

---

## 🏗️ Arquitectura de Resiliencia (v3.0.0)

El sistema implementa una defensa en profundidad con 4 capas de protección:

1.  **Circuit Breaker**: Protege contra servicios caídos.
2.  **Idempotencia**: Evita duplicados (SQLite).
3.  **Reintentos**: Maneja fallos transitorios de red.
4.  **Dead Letter Queue (DLQ)**: Captura fallos finales para análisis.

Todos los casos (01-09) utilizan scripts compartidos optimizados en `scripts/`.

---

## 1. Idempotencia (SQLite)

**Estado**: ✅ Implementado GLOBALMENTE (Casos 01-09)
**Script**: [`scripts/check_idempotency.py`](file:///c:/dev/social-bot-scheduler/scripts/check_idempotency.py)
**Base de Datos**: `scripts/shared/fingerprints.db`

Mecanismo para evitar que un mismo mensaje sea procesado dos veces.

-   **Backend**: SQLite (Alta concurrencia, transacciones atómicas).
-   **TTL**: 24 horas (Limpieza automática de registros antiguos).
-   **Lógica**:
    1.  Recibir Post ID + Canal.
    2.  Verificar existencia en DB.
    3.  Si existe -> **Ignorar** (200 OK).
    4.  Si no existe -> **Registrar** y procesar.

```bash
# Verificar manualmente
python3 scripts/check_idempotency.py check "post-123_twitter" "01"
```

---

## 2. Circuit Breaker (Cortafuegos)

**Estado**: ✅ Implementado GLOBALMENTE (Casos 01-09)
**Script**: [`scripts/circuit_breaker.py`](file:///c:/dev/social-bot-scheduler/scripts/circuit_breaker.py)
**Estado Compartido**: `scripts/shared/circuit_state.json`

Protege el sistema dejando de enviar peticiones a un servicio que está fallando repetidamente.

### Estados
-   🟢 **CLOSED**: Normal. Peticiones fluyen.
-   🔴 **OPEN**: Fallo detectado (5 errores seguidos). Peticiones rechazadas inmediatamente.
-   🟡 **HALF-OPEN**: Periodo de prueba (después de 5 min). Deja pasar 1 petición para ver si se recuperó.

```bash
# Verificar estado
python3 scripts/circuit_breaker.py check "01"
```

---

## 3. Dead Letter Queue (DLQ)

**Estado**: ✅ Implementado GLOBALMENTE (Casos 01-09)
**Endpoint**: `/errors` en cada servicio de destino.

Si un mensaje falla después de todos los reintentos y protecciones, se envía al DLQ para no perder datos.

-   **Destino**: Archivo de log `errors.log` en el contenedor de destino.
-   **Contenido**: JSON con el error original y el payload del mensaje.

---

## 4. Reintentos Automáticos

**Estado**: ✅ Configurado en todos los Workflows (Json)

Cada nodo "HTTP Request" en n8n está configurado con:
-   **Retry on Fail**: `true`
-   **Max Retries**: 3
-   **Wait Between Retries**: 1000ms

---

## 🧪 Cómo Verificar (Pruebas Reales)

Para validar que estos sistemas funcionan, hemos creado un script de prueba end-to-end:

```bash
# Ejecutar test de scripts compartidos
./scripts/test_shared_scripts.sh
```

### Tabla de Cobertura

| Característica | Caso 01 | Caso 02 | Caso 03 | Caso 04 | Caso 05 | Caso 06 | Caso 07 | Caso 08 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Idempotencia** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Circuit Breaker** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **DLQ** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Reintentos** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

> [!NOTE]
> Esta documentación refleja la implementación actual (v3.0.0) basada en scripts Python compartidos y SQLite, reemplazando las implementaciones anteriores basadas en JSON y caso único.


### Caso 09
El Caso 09 reutiliza todos los guardrails compartidos y a?ade autenticacion saliente desde n8n hacia FastAPI mediante `X-API-Key={{$env.INTEGRATION_API_KEY}}`.
