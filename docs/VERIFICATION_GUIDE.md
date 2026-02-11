# 🧪 Guía de Pruebas Manuales: Verificación de Guardrails

Esta guía permite al usuario verificar que la lógica implementada en los flujos de n8n funciona correctamente ante escenarios de estrés y fallos reales.

---

## 1. Prueba de Idempotencia (Evitar Duplicados)

**Escenario**: Se envía el mismo post dos veces en un intervalo corto.
**Acción**: Ejecuta el bot de un caso (ej. Caso 01) dos veces seguidas con el mismo ID de post.

```powershell
# Intento 1
cd cases/01-python-to-php/origin
python bot.py  # Debería mostrar "Payload sent" y verse en el dashboard.

# Intento 2 (Inmediato)
python bot.py  # Debería mostrar "Payload sent", pero en n8n verás "Duplicate Ignored".
```

**Resultado Esperado**:
- El segundo post **no** aparece en el Dashboard de destino.
- En la pestaña "Executions" de n8n, el flujo termina en el nodo "Check Idempotency" ramificando hacia el final sin hacer el posteo.

---

## 2. Prueba de Reintentos (Circuit Breaker Simulado)

**Escenario**: El servicio de destino está caído o responde lento.
**Acción**: Detén el contenedor de destino del caso que estés probando.

```bash
docker-compose stop dest-php
```

**Acción**: Envía un post desde el bot.
**Resultado Esperado**:
- En n8n, verás que el nodo "HTTP Request" se pone en estado "Retrying" (reintentando).
- Intentará 3 veces antes de fallar definitivamente.

---

## 3. Prueba de Dead Letter Queue (DLQ)

**Escenario**: El post falla después de todos los reintentos.
**Acción**: Con el contenedor detenido, deja que pasen los 3 reintentos.

**Resultado Esperado**:
- El flujo activa el nodo "Dead Letter Queue (DLQ)".
- En el servidor de logs (o dashboard de errores), debe aparecer una entrada con el JSON original y el detalle del error (ej: `ECONNREFUSED`).

---

## 4. Validación Estructural Automática

He proporcionado un script para verificar que todos los casos mantengan los estándares de seguridad.

```powershell
python scripts/validate_workflows.py
```

Deberías ver: `[OK] cases\XX-xx\n8n\workflow.json: Estructura de Guardrails correcta.` para los 8 casos.
