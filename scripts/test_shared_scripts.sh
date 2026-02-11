#!/bin/bash
# Script de prueba para validar scripts compartidos de resiliencia

echo "🧪 Prueba de Scripts Compartidos de Resiliencia"
echo "==============================================="
echo ""

# Test 1: Idempotency
echo "📋 Test 1: Idempotency"
echo "----------------------"

echo "1. Verificar fingerprint inexistente..."
python3 scripts/check_idempotency.py check "test-001_twitter" "01"

echo ""
echo "2. Agregar fingerprint..."
python3 scripts/check_idempotency.py add "test-001_twitter" "01"

echo ""
echo "3. Verificar fingerprint existente (debería ser true)..."
python3 scripts/check_idempotency.py check "test-001_twitter" "01"

echo ""
echo "4. Intentar agregar duplicado (debería fallar)..."
python3 scripts/check_idempotency.py add "test-001_twitter" "01"

echo ""
echo "5. Ver estadísticas..."
python3 scripts/check_idempotency.py stats "01"

echo ""
echo ""

# Test 2: Circuit Breaker
echo "⚡ Test 2: Circuit Breaker"
echo "-------------------------"

echo "1. Estado inicial (debería ser CLOSED)..."
python3 scripts/circuit_breaker.py check "01"

echo ""
echo "2. Registrar 3 fallos..."
for i in {1..3}; do
  echo "   Fallo $i:"
  python3 scripts/circuit_breaker.py record_failure "01"
done

echo ""
echo "3. Verificar estado (aún CLOSED, threshold=5)..."
python3 scripts/circuit_breaker.py check "01"

echo ""
echo "4. Registrar 2 fallos más (total=5, debería abrir)..."
for i in {4..5}; do
  echo "   Fallo $i:"
  python3 scripts/circuit_breaker.py record_failure "01"
done

echo ""
echo "5. Verificar estado (debería ser OPEN)..."
python3 scripts/circuit_breaker.py check "01"

echo ""
echo "6. Registrar éxito (debería cerrar)..."
python3 scripts/circuit_breaker.py record_success "01"

echo ""
echo "7. Verificar estado final (debería ser CLOSED)..."
python3 scripts/circuit_breaker.py check "01"

echo ""
echo "8. Ver estado de todos los circuitos..."
python3 scripts/circuit_breaker.py status

echo ""
echo "✅ Pruebas completadas!"
