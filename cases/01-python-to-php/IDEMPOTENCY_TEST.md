# Prueba de Idempotencia - Caso 01

## Objetivo
Verificar que el sistema **NO procesa posts duplicados** usando el fingerprint `{id}_{channel}`.

## Prerequisitos
```bash
# Asegurarse de que n8n y dest-php estén corriendo
docker-compose up -d n8n dest-php
```

## Pasos de Prueba

### 1. Limpiar Estado Previo
```bash
# Limpiar logs y fingerprints
rm -f cases/01-python-to-php/dest/logs/social_bot.log
rm -f cases/01-python-to-php/dest/logs/errors.log
echo "{}" > cases/01-python-to-php/n8n/processed_fingerprints.json
```

### 2. Ejecutar Prueba Automática
```bash
bash cases/01-python-to-php/test_idempotency.sh
```

### 3. Verificar Resultados

#### ✅ Resultado Esperado
**Archivo: `cases/01-python-to-php/dest/logs/social_bot.log`**
```
[2026-02-11 13:00:00] PHP-RECEIVER | id=test-idempotency-001 | channel=twitter | text=Post de prueba para idempotencia
```
→ **SOLO 1 entrada** (el segundo envío fue rechazado)

**Archivo: `cases/01-python-to-php/n8n/processed_fingerprints.json`**
```json
{
  "test-idempotency-001_twitter": "2026-02-11T13:00:00.123456"
}
```
→ Fingerprint registrado con timestamp

#### ❌ Resultado Incorrecto
Si ves **2 entradas** en `social_bot.log`, significa que la idempotencia NO está funcionando.

### 4. Prueba Manual (Alternativa)
```bash
# Envío 1
curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
  -H "Content-Type: application/json" \
  -d '{"id":"manual-001","text":"Test manual","channel":"twitter"}'

# Esperar 2 segundos
sleep 2

# Envío 2 (mismo ID y canal)
curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
  -H "Content-Type: application/json" \
  -d '{"id":"manual-001","text":"Test manual","channel":"twitter"}'

# Verificar
cat cases/01-python-to-php/dest/logs/social_bot.log
# Debería mostrar SOLO 1 entrada
```

## Prueba de TTL (Expiración de Fingerprints)

### Objetivo
Verificar que fingerprints **expiran después de 24 horas**.

### Pasos
1. Agregar un fingerprint con timestamp antiguo:
```bash
python3 << EOF
import json
from datetime import datetime, timedelta

# Crear fingerprint de hace 25 horas (expirado)
old_fp = {
    "old-post-001_twitter": (datetime.now() - timedelta(hours=25)).isoformat()
}

with open('cases/01-python-to-php/n8n/processed_fingerprints.json', 'w') as f:
    json.dump(old_fp, f, indent=2)
EOF
```

2. Enviar post con el mismo ID:
```bash
curl -X POST "http://localhost:5678/webhook/social-bot-scheduler-php" \
  -H "Content-Type: application/json" \
  -d '{"id":"old-post-001","text":"Post expirado","channel":"twitter"}'
```

3. Verificar:
```bash
cat cases/01-python-to-php/dest/logs/social_bot.log
# Debería procesar el post (fingerprint expirado fue limpiado)

cat cases/01-python-to-php/n8n/processed_fingerprints.json
# Debería tener el nuevo timestamp (no el antiguo)
```

## Notas Importantes

### Limitaciones Actuales
- ⚠️ **Persistencia local**: Fingerprints se guardan en archivo JSON (no base de datos)
- ⚠️ **TTL fijo**: 24 horas hardcodeado (no configurable)
- ⚠️ **Sin sincronización**: Si n8n se reinicia durante el procesamiento, puede haber duplicados
- ⚠️ **Solo Caso 01**: Otros casos NO tienen idempotencia implementada

### Próximos Pasos
1. Migrar a SQLite o Redis para mayor robustez
2. Hacer TTL configurable vía variable de entorno
3. Replicar a casos 02-08
