# n8n Auto-Configuration

Esta carpeta contiene la configuracion necesaria para que **n8n se auto-configure** al arrancar con Docker Compose.

## Contenido

### `workflows/`
Los 9 workflows de integracion preconfigurados, listos para importacion automatica.

## Como funciona

Al ejecutar `docker-compose up -d`, el contenedor de n8n usa el entrypoint `scripts/n8n_auto_setup.sh`, que:

1. Arranca n8n en segundo plano.
2. Espera a que el endpoint `/healthz` responda.
3. Crea la cuenta owner usando `N8N_OWNER_EMAIL` y `N8N_OWNER_PASSWORD`.
4. Importa los workflows desde `n8n/workflows/`.
5. Activa los workflows.
6. Deja un marcador local para no duplicar la importacion en reinicios.

## Credenciales

- Las credenciales ya no estan fijas en el compose.
- Define `N8N_OWNER_EMAIL`, `N8N_OWNER_PASSWORD` y `N8N_ENCRYPTION_KEY` en `.env`.
- Para un laboratorio reproducible puedes usar `.env.demo.example`.
- Para un arranque mas seguro parte desde `.env.example` y reemplaza todos los placeholders.

## Notas operativas

- Si cambias las credenciales despues del primer arranque, elimina `n8n/data` o recrea el stack con volumenes limpios para reprovisionar el owner.
- La UI queda publicada solo en `127.0.0.1` por defecto.
- No expongas n8n directamente a Internet sin TLS, reverse proxy y controles adicionales.
- Si activas el perfil `edge`, ajusta tambien `N8N_HOST`, `N8N_PORT`, `N8N_PROTOCOL`, `N8N_PROXY_HOPS`, `N8N_WEBHOOK_URL` y `N8N_EDITOR_BASE_URL`.
