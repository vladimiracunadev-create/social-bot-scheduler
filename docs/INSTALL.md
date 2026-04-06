# Guia de instalacion

Esta guia refleja el modelo actual del repositorio: laboratorio funcional, local por defecto y con endurecimiento incremental.

## 1. Elegir modo

### Opcion A: secure-default

```bash
cp .env.example .env
docker-compose up -d
```

Levanta:

- `n8n`
- dashboard maestro

Luego activa solo lo que necesites:

```bash
docker-compose --profile case01 up -d n8n master-dashboard dest-php
docker-compose --profile observability up -d prometheus grafana cadvisor
```

### Opcion B: demo-local

```bash
cp .env.demo.example .env
make up
```

Levanta el laboratorio completo con el perfil `full`, manteniendo los puertos publicados solo en `127.0.0.1`.

## 2. Variables de entorno

Configura como minimo:

- `N8N_OWNER_EMAIL`
- `N8N_OWNER_PASSWORD`
- `N8N_ENCRYPTION_KEY`
- `INTEGRATION_API_KEY`
- `GRAFANA_ADMIN_PASSWORD` si vas a usar observabilidad

## 3. Perfil edge opcional

Si necesitas acceso administrativo remoto controlado:

1. Genera hash bcrypt:
   ```bash
   docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext 'TuPasswordFuerte'
   ```
2. Copia el resultado en `EDGE_BASIC_AUTH_HASH`.
3. Ajusta `N8N_HOST`, `N8N_PORT`, `N8N_PROTOCOL`, `N8N_PROXY_HOPS`, `N8N_WEBHOOK_URL` y `N8N_EDITOR_BASE_URL` si vas a publicar n8n detras del proxy.
4. Activa:
   ```bash
   make up-edge
   ```

## 4. Kubernetes

Los manifiestos de `k8s/` siguen disponibles, pero este repositorio se documenta y valida principalmente como laboratorio Docker local.

Si vas a desplegarlo en Kubernetes:

- no reutilices credenciales demo
- define secretos reales
- aplica segmentacion de red
- revisa [SECURITY.md](../SECURITY.md) y [RUNTIME_SECURITY.md](RUNTIME_SECURITY.md)

## 5. Instalacion manual

Para ejecutar bots de origen fuera de Docker:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Luego ejecuta el bot del caso correspondiente desde `cases/*/origin/`.
