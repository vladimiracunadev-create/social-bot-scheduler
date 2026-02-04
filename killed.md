# Guardrails Anti-Abuso (killed.md)

Este documento detalla las medidas de seguridad y límites implementados para prevenir el abuso y garantizar la estabilidad del sistema.

## 1. Modo "NO_PUBLIC_POSTING"
Por defecto, el sistema opera con `NO_PUBLIC_POSTING=true`. 
- **Efecto**: Los conectores de salida (Social Media APIs) simularán el envío pero no persistirán datos en plataformas públicas.
- **Cómo desactivar**: Cambiar explícitamente a `false` en el entorno de producción controlado.

## 2. Rate Limiting
El HUB y los emisores implementan un límite de velocidad:
- **Límite**: Máximo 5 solicitudes por minuto por caso.
- **Implementación**: Controlado en el `bot.py` de cada caso y supervisado por el orquestador n8n.

## 3. Allowlist de Destinos
Solo se permite la comunicación con destinos pre-aprobados:
- Dominios permitidos: `*.n8n.cloud`, `localhost`, `api.twitter.com` (HTTPS port 443).
- Cualquier otro destino será bloqueado por la `NetworkPolicy` de Kubernetes o el firewall del contenedor.

## 4. Contenedores Hardened
- **Non-Root**: Las imágenes corren bajo el usuario `botuser`.
- **Read-Only**: El sistema de archivos de Kubernetes está montado como `readOnlyRootFilesystem: true` (excepto volúmenes de datos).
- **Límites**: CPU (500m) y Memoria (512Mi) estrictos para prevenir ataques DoS por consumo de recursos.

## 4. Logs de Auditoría
Todas las ejecuciones via `hub run` son registradas.
- **Campos**: Timestamp, Usuario (si aplica), Caso, Parámetros, Resultado.
- **Ubicación**: `.logs/audit.log` (rotativo).

## 5. Prevención de Secretos
- Uso de `detect-secrets` en el pre-commit.
- Auditoría periódica de dependencias con `pip audit` y `npm audit`.
