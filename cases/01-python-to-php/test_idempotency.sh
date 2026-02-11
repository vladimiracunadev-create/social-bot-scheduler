#!/bin/bash
# Script de prueba para validar idempotencia en Caso 01

echo "🧪 Prueba de Idempotencia - Caso 01"
echo "===================================="
echo ""

# Payload de prueba
PAYLOAD='{
  "id": "test-idempotency-001",
  "text": "Post de prueba para idempotencia",
  "channel": "twitter",
  "scheduled_at": "2026-02-11T13:00:00"
}'

WEBHOOK_URL="http://localhost:5678/webhook/social-bot-scheduler-php"

echo "📤 Enviando post por primera vez..."
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
echo ""
echo ""

echo "⏳ Esperando 2 segundos..."
sleep 2

echo "📤 Enviando el MISMO post por segunda vez (debería ser rechazado)..."
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
echo ""
echo ""

echo "✅ Verificación:"
echo "1. Revisa cases/01-python-to-php/dest/logs/social_bot.log"
echo "   → Debería tener SOLO 1 entrada del post 'test-idempotency-001'"
echo ""
echo "2. Revisa cases/01-python-to-php/n8n/processed_fingerprints.json"
echo "   → Debería contener el fingerprint 'test-idempotency-001_twitter'"
echo ""
echo "3. Revisa los logs de n8n"
echo "   → El segundo envío debería terminar en el nodo 'Is New Post?' sin procesar"
