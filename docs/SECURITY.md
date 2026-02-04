# 🛡️ Seguridad y Buenas Prácticas

La seguridad es primordial al manejar automatizaciones que interactúan con plataformas externas.

## Gestión de Secretos
- **Nunca** subas tu archivo `.env` o archivos con claves reales al repositorio.
- Utiliza **Kubernetes Secrets** o sistemas de gestión de secretos (como AWS Secrets Manager o Vault) en entornos de producción.

## Protección del Webhook
- Tu instancia de n8n debe estar protegida.
- Utiliza URLs con tokens de autenticación únicos generados por n8n.
- Limita el acceso por IP si tu infraestructura lo permite.

## Validación de Datos
El bot realiza una validación básica de tipos, pero se recomienda:
- Validar la integridad del archivo `posts.json` antes de levantarlo en producción.
- Configurar alertas en n8n para detectar fallos en la publicación final después de que el bot entregue el payload.

## Reporte de Vulnerabilidades
Si encuentras un problema de seguridad, por favor abre un **Issue** con la etiqueta `security` o contacta al mantenedor directamente.

## Hardening Técnico
Para detalles sobre nuestra estrategia de imágenes Docker no-root, aislamiento con `venv` y el pipeline de escaneo continuo, consulta el archivo principal de [Seguridad](../SECURITY.md).
