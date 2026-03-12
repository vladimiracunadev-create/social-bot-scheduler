# 🛡️ Guía Completa de Resiliencia

Esta guía detalla la implementación completa de resiliencia en el Social Bot Scheduler.

---

## 📊 Resumen Ejecutivo

**Cobertura:** 100% en todos los casos (01-09)

| Mecanismo | Descripción | Estado |
|-----------|-------------|--------|
| **Reintentos Autom?ticos** | 3 intentos con 1s de espera | ? 9/9 casos |
| **Dead Letter Queue** | Registro de errores irrecuperables | ? 9/9 casos |
| **Idempotencia** | Prevenci?n de duplicados | ? 9/9 casos |
| **Circuit Breaker** | Protecci?n contra servicios ca?dos | ? 9/9 casos |

---

## 🔧 Arquitectura

### Scripts Compartidos

Todos los casos usan scripts centralizados en `scripts/`:

```
scripts/
├── check_idempotency.py    # Gestión de fingerprints (SQLite)
├── circuit_breaker.py       # Gestión de estados del circuito
├── generate_workflows.py    # Generador de workflows
├── test_shared_scripts.sh   # Pruebas de scripts
└── shared/
    ├── fingerprints.db      # Base de datos SQLite compartida
    └── circuit_state.json   # Estado de todos los circuit breakers
```

### Flujo de Procesamiento

```
1. Webhook recibe post
2. Se genera fingerprint (id_channel)
3. ¿Circuit breaker OPEN? → Rechazar (503)
4. ¿Fingerprint existe? → Duplicado (200 OK)
5. Agregar fingerprint a DB
6. Enviar HTTP Request (con reintentos)
7. ¿Éxito? → Record Success → Fin
8. ¿Error? → Record Failure → DLQ
```

---

## 🔑 Idempotencia

### Implementación

**Script:** `scripts/check_idempotency.py`  
**Tecnología:** SQLite (mejor concurrencia que JSON)  
**TTL:** 24 horas (limpieza automática)

### Uso

```bash
# Verificar fingerprint
python3 scripts/check_idempotency.py check "post-123_twitter" "01"
# Output: {"exists": false, "fingerprint": "post-123_twitter", "case": "01"}

# Agregar fingerprint
python3 scripts/check_idempotency.py add "post-123_twitter" "01"
# Output: {"added": true, "fingerprint": "post-123_twitter", "case": "01"}

# Ver estadísticas
python3 scripts/check_idempotency.py stats "01"
# Output: {"total": 42, "case_id": "01"}

# Limpiar expirados
python3 scripts/check_idempotency.py cleanup
# Output: {"cleaned": 15}
```

### Prueba

```bash
# Enviar mismo post 2 veces
curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
  -H "Content-Type: application/json" \
  -d '{"id":"test-001","text":"Test","channel":"twitter"}'

sleep 2

curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
  -H "Content-Type: application/json" \
  -d '{"id":"test-001","text":"Test","channel":"twitter"}'

# Verificar: solo 1 entrada en logs del servicio
```

---

## ⚡ Circuit Breaker

### Estados

1. **CLOSED** (Normal): Todas las peticiones pasan
2. **OPEN** (Circuito abierto): Rechaza peticiones inmediatamente
3. **HALF_OPEN** (Prueba): Permite 1 petición de prueba

### Transiciones

```
CLOSED --[5 fallos]--> OPEN --[5 min]--> HALF_OPEN --[éxito]--> CLOSED
                                              |
                                          [fallo]
                                              |
                                              v
                                            OPEN
```

### Uso

```bash
# Verificar estado
python3 scripts/circuit_breaker.py check "01"
# Output: {"state": "CLOSED", "failures": 0, "can_proceed": true}

# Registrar fallo
python3 scripts/circuit_breaker.py record_failure "01"
# Output: {"state": "CLOSED", "failures": 1, "threshold_reached": false}

# Registrar éxito
python3 scripts/circuit_breaker.py record_success "01"
# Output: {"state": "CLOSED", "failures": 0}

# Ver todos los circuitos
python3 scripts/circuit_breaker.py status
# Output: {"01": {"state": "CLOSED", ...}, "02": {...}, ...}

# Resetear manualmente
python3 scripts/circuit_breaker.py reset "01"
# Output: {"state": "CLOSED", "reset": true}
```

### Prueba

```bash
# Detener servicio
docker-compose stop dest-php

# Enviar 5 posts para abrir circuito
for i in {1..5}; do
  curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
    -H "Content-Type: application/json" \
    -d "{\"id\":\"test-$i\",\"text\":\"Test\",\"channel\":\"twitter\"}"
  sleep 2
done

# Verificar estado (debería ser OPEN)
python3 scripts/circuit_breaker.py check "01"

# Enviar 6to post (debería rechazarse inmediatamente sin reintentos)
curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
  -H "Content-Type: application/json" \
  -d '{"id":"test-6","text":"Test","channel":"twitter"}'
```

---

## 🚨 Dead Letter Queue (DLQ)

### Implementación

Todos los servicios de destino tienen endpoint `/errors`:

- **Caso 01 (PHP):** `http://dest-php:80/errors.php`
- **Caso 02 (Go):** `http://dest-go:8080/errors`
- **Caso 03 (Node):** `http://dest-node:3000/errors`
- **Caso 04 (FastAPI):** `http://dest-fastapi:8000/errors`
- **Caso 05 (React):** `http://dest-react:4000/errors`
- **Caso 06 (Symfony):** `http://dest-symfony:80/errors`
- **Caso 07 (Ruby):** `http://dest-ruby:4567/errors`
- **Caso 08 (Flask):** `http://dest-flask:5000/errors`
- **Caso 09 (FastAPI Gateway):** `http://dest-gateway-09:8000/errors`

### Formato de Log

```
[2026-02-11 13:00:00] CASE=01 | ERROR={"message":"Connection refused"} | PAYLOAD={"id":"123","text":"..."}
```

### Prueba

```bash
# Detener servicio
docker-compose stop dest-php

# Enviar post (fallará después de 3 reintentos)
curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
  -H "Content-Type: application/json" \
  -d '{"id":"test-dlq","text":"Test DLQ","channel":"twitter"}'

# Verificar DLQ
cat cases/01-python-to-php/dest/logs/errors.log
```

---

## 🔄 Reintentos Automáticos

### Configuración

Todos los workflows tienen reintentos configurados:

```json
"options": {
  "retryOnFail": true,
  "maxRetries": 3,
  "waitBetweenRetries": 1000
}
```

- **Intentos:** 3 (total: 1 inicial + 3 reintentos = 4 intentos)
- **Espera:** 1 segundo entre reintentos
- **Códigos de error:** Todos los errores HTTP y de red

---

## 📁 Archivos Clave

### Scripts
- `scripts/check_idempotency.py` - Idempotencia con SQLite
- `scripts/circuit_breaker.py` - Circuit breaker con estados
- `scripts/generate_workflows.py` - Generador de workflows
- `scripts/test_shared_scripts.sh` - Pruebas de scripts

### Estado Compartido
- `scripts/shared/fingerprints.db` - Base de datos SQLite
- `scripts/shared/circuit_state.json` - Estado de circuitos

### Workflows
- `cases/01-python-to-php/n8n/workflow.json`
- `cases/02-python-to-go/n8n/workflow.json`
- `cases/03-go-to-node/n8n/workflow.json`
- `cases/04-node-to-fastapi/n8n/workflow.json`
- `cases/05-laravel-to-react/n8n/workflow.json`
- `cases/06-go-to-symfony/n8n/workflow.json`
- `cases/07-rust-to-ruby/n8n/workflow.json`
- `cases/08-csharp-to-flask/n8n/workflow.json`
- `n8n/workflows/case-09-python-to-gateway.json`

---

## 🧪 Pruebas Completas

### Script de Prueba de Scripts
```bash
bash scripts/test_shared_scripts.sh
```

Este script prueba:
- Idempotencia (check, add, duplicados)
- Circuit breaker (estados, transiciones)

### Prueba End-to-End

```bash
# 1. Levantar entorno
docker-compose up -d

# 2. Probar idempotencia
curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
  -H "Content-Type: application/json" \
  -d '{"id":"e2e-001","text":"Test E2E","channel":"twitter"}'

# Enviar duplicado (debería rechazarse)
curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
  -H "Content-Type: application/json" \
  -d '{"id":"e2e-001","text":"Test E2E","channel":"twitter"}'

# 3. Probar circuit breaker
docker-compose stop dest-php

for i in {1..5}; do
  curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
    -H "Content-Type: application/json" \
    -d "{\"id\":\"cb-$i\",\"text\":\"Test CB\",\"channel\":\"twitter\"}"
  sleep 2
done

# Verificar estado
python3 scripts/circuit_breaker.py check "01"

# 4. Probar DLQ
cat cases/01-python-to-php/dest/logs/errors.log

# 5. Limpiar
docker-compose up -d dest-php
python3 scripts/circuit_breaker.py reset "01"
```

---

## 🔍 Troubleshooting

### Problema: Fingerprints no se limpian

**Solución:**
```bash
python3 scripts/check_idempotency.py cleanup
```

### Problema: Circuit breaker atascado en OPEN

**Solución:**
```bash
python3 scripts/circuit_breaker.py reset "01"
```

### Problema: DLQ no registra errores

**Verificar:**
1. Endpoint `/errors` existe en el servicio
2. Servicio de destino está corriendo
3. Logs del servicio: `docker-compose logs dest-php`

---

## 📈 Métricas y Monitoreo

### Ver Estadísticas de Idempotencia

```bash
# Por caso
python3 scripts/check_idempotency.py stats "01"

# Todos los casos
for i in {01..09}; do
  echo "Caso $i:"
  python3 scripts/check_idempotency.py stats "$i"
done
```

### Ver Estado de Circuit Breakers

```bash
python3 scripts/circuit_breaker.py status
```

### Ver Errores en DLQ

```bash
# Por caso
cat cases/01-python-to-php/dest/logs/errors.log

# Todos los casos
find cases -name "errors.log" -exec echo {} \; -exec cat {} \;
```
