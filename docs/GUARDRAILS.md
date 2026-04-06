# 🛡️ n8n Guardrails: Resiliencia y Seguridad

Esta guía detalla los **Guardrails** (mecanismos de protección) implementados en la capa del **Bridge (n8n)**. Estos patrones aseguran que el ecosistema sea resistente a fallos, evite duplicados y maneje errores de forma robusta en **TODOS los 9 casos de integración**.

---

## 🏗️ Arquitectura de Resiliencia (v4.0.0)

El sistema implementa una **defensa en profundidad** con 4 capas críticas de protección:

1.  **⚡ Circuit Breaker**: Protege contra servicios externos caídos o saturados.
2.  **✅ Idempotencia**: Evita el procesamiento de mensajes duplicados (basado en SQLite).
3.  **🔄 Reintentos**: Gestiona fallos transitorios de red con backoff exponencial.
4.  **📥 Dead Letter Queue (DLQ)**: Captura fallos definitivos para auditoría y recuperación.

> [!IMPORTANT]
> Todos los casos (01-09) comparten una lógica de protección centralizada ubicada en el directorio `scripts/`.

---

## 1. ✅ Idempotencia (SQLite)

- **Estado**: Operativo Globalmente (Casos 01-09)
- **Script**: [`scripts/check_idempotency.py`](../scripts/check_idempotency.py)
- **Motor**: SQLite (Transacciones atómicas y alta concurrencia)

Previene que un post sea procesado más de una vez, incluso si el emisor reintenta el envío por error.
1. Genera un hash del mensaje.
2. Verifica si el hash ya existe en la base de datos de huellas.
3. Si existe, retorna `200 OK` inmediatamente sin disparar el flujo.

---

## 2. ⚡ Circuit Breaker (Cortafuegos)

- **Estado**: Operativo Globalmente (Casos 01-09)
- **Script**: [`scripts/circuit_breaker.py`](../scripts/circuit_breaker.py)
- **Almacenamiento**: `scripts/shared/circuit_state.json`

Protege la salud del sistema abriendo el circuito si un destino falla repetidamente.

| Estado | Descripción | Acción |
| :--- | :--- | :--- |
| 🟢 **CLOSED** | Funcionamiento normal. | Las peticiones fluyen hacia el destino. |
| 🔴 **OPEN** | Fallo detectado (5 errores seguidos). | Peticiones rechazadas inmediatamente (Fail-Fast). |
| 🟡 **HALF-OPEN** | Periodo de recuperación (5 minutos). | Se permite una petición de prueba para verificar salud. |

---

## 3. 📥 Dead Letter Queue (DLQ)

- **Estado**: Operativo Globalmente (Casos 01-09)
- **Endpoint**: `/errors` en cada microservicio de destino.

Si una publicación falla tras agotar todos los reintentos, el payload completo se deriva al DLQ.
- **Auditoría**: Los errores se registran en `errors.log` con el contexto completo del fallo.
- **Recuperación**: Permite el reintento manual una vez solucionado el problema de infraestructura.

---

## 4. 🔄 Reintentos Automáticos

Configurado nativamente en los nodos de **n8n**:
- **Máximo de Reintentos**: 3
- **Intervalo**: 1000ms con incremento exponencial.
- **Objetivo**: Superar micro-cortes de red o latencias temporales de los receptores.

---

## 🧪 Verificación de Guardrails

Puedes validar la salud de los mecanismos de protección mediante el CLI maestro:

```bash
# Diagnóstico de salud general
python hub.py doctor

# Test específico de scripts de resiliencia
./scripts/test_shared_scripts.sh
```

---

## 📊 Matriz de Cobertura de Seguridad

| Caso | Idempotencia | Circuit Breaker | DLQ | Reintentos |
| :--- | :---: | :---: | :---: | :---: |
| **01-08** | ✅ | ✅ | ✅ | ✅ |
| **09 (Gateway)** | ✅ | ✅ | ✅ | ✅ |

> [!TIP]
> El Caso 09 añade una capa extra: **Autenticación X-API-Key** entre n8n y el Gateway de FastAPI.

---

*Documentación de Resiliencia creada para Social Bot Scheduler v4.0*
