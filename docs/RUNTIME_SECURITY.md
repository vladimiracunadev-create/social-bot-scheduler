# Runtime Security Model

Esta guia documenta el modelo operativo y de seguridad aplicado al runtime de **Social Bot Scheduler** despues del hardening incremental y de la fase 2.

## Objetivo

Mantener el laboratorio:

- funcional
- demostrable
- util para docencia
- mas dificil de reutilizar de forma insegura por accidente

## Modos de operacion

| Modo | Como se activa | Que levanta | Postura |
| --- | --- | --- | --- |
| `secure-default` | `cp .env.example .env` + `docker-compose up -d` | `n8n` + dashboard maestro | local-only, sin observabilidad por defecto |
| `demo-local` | `cp .env.demo.example .env` + `make up` | laboratorio completo (`full`) | local-only, credenciales demo reproducibles |
| `observability` | `make up-observability` o `python hub.py up --observability` | Prometheus, Grafana, cAdvisor | opt-in, solo localhost |
| `edge` | `make up-edge` o `python hub.py up --edge` | Caddy reverse proxy | opt-in, HTTPS + basic auth |

## Perfiles Docker Compose

| Perfil | Uso |
| --- | --- |
| `case01` ... `case09` | activa un caso puntual |
| `full` | activa laboratorio completo |
| `observability` | activa Prometheus, Grafana y cAdvisor |
| `edge` | activa el reverse proxy seguro |

## Puertos y exposicion

Por defecto, los puertos publicados quedan en loopback:

- `127.0.0.1:5678` -> n8n
- `127.0.0.1:8080` -> dashboard maestro
- `127.0.0.1:8081` a `127.0.0.1:8090` -> dashboards y destinos de casos
- `127.0.0.1:3000` -> Grafana
- `127.0.0.1:9090` -> Prometheus
- `127.0.0.1:8089` -> cAdvisor

## Secretos y variables criticas

### n8n

- `N8N_OWNER_EMAIL`
- `N8N_OWNER_PASSWORD`
- `N8N_ENCRYPTION_KEY`
- `N8N_HOST`
- `N8N_PORT`
- `N8N_PROTOCOL`
- `N8N_PROXY_HOPS`
- `N8N_WEBHOOK_URL`
- `N8N_EDITOR_BASE_URL`

### Observabilidad

- `GRAFANA_ADMIN_USER`
- `GRAFANA_ADMIN_PASSWORD`

### Bases de datos

- `CASE01_DB_PASSWORD`
- `CASE02_DB_PASSWORD`
- `CASE03_DB_PASSWORD`
- `CASE08_DB_PASSWORD`
- `MSSQL_IMAGE`

### Integraciones

- `INTEGRATION_API_KEY`
- `GITHUB_TOKEN`

### Edge profile

- `EDGE_BIND_IP`
- `EDGE_N8N_HOST`
- `EDGE_GRAFANA_HOST`
- `EDGE_CASE09_HOST`
- `EDGE_BASIC_AUTH_USER`
- `EDGE_BASIC_AUTH_HASH`

## Edge profile

El perfil `edge` usa `caddy:2.10.2-alpine` y renderiza su configuracion en arranque mediante [edge/start-caddy.sh](../edge/start-caddy.sh).

### Que publica

- `n8n`
- `Grafana` si el perfil `observability` esta activo
- gateway del Caso 09 si `case09` o `full` esta activo

### Que NO publica

- el dashboard maestro

Motivo:

El dashboard maestro ejecuta pruebas desde el navegador hacia `localhost` y, por diseño actual, es una herramienta de laboratorio local.

### Como habilitarlo

1. Genera un hash bcrypt:
   ```bash
   docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext 'TuPasswordFuerte'
   ```
2. Copia el hash en `EDGE_BASIC_AUTH_HASH`.
3. Si vas a usar n8n detras del proxy, ajusta tambien:
   - `N8N_HOST`
   - `N8N_PORT=443`
   - `N8N_PROTOCOL=https`
   - `N8N_PROXY_HOPS=1`
   - `N8N_WEBHOOK_URL`
   - `N8N_EDITOR_BASE_URL`
4. Arranca:
   ```bash
   make up-edge
   ```

## Supply chain

### Pins aplicados

- `n8nio/n8n:2.7.5`
- `prom/prometheus:v2.54.1`
- `grafana/grafana:11.2.0`
- `gcr.io/cadvisor/cadvisor:v0.49.1`
- `mcr.microsoft.com/mssql/server:2022-CU24-ubuntu-22.04`
- `caddy:2.10.2-alpine`
- `alpine:3.20.6` en el destino Go del Caso 02

## Guardrails automaticos

El script [scripts/check_runtime_security.py](../scripts/check_runtime_security.py) falla si detecta:

- tags `latest` en Compose o Dockerfiles
- puertos publicados sin bind local o variable controlada
- secretos hardcodeados en variables sensibles del runtime
- perfiles faltantes en `prometheus`, `grafana`, `cadvisor` o `edge-proxy`

El pipeline CI lo ejecuta en cada push y PR, junto con `docker compose config` de los perfiles principales.

## Validacion recomendada

### Minima

```bash
python scripts/check_runtime_security.py
docker-compose config
docker-compose --profile observability config
docker-compose --profile edge config
python verify_n8n.py
```

### Funcional

```bash
make up-secure
make up-observability
make demo
make demo09
```

### Completa

```bash
cp .env.demo.example .env
make up
python verify_all_cases.py
```

## Riesgos residuales

- `cAdvisor` sigue siendo un componente sensible por sus montajes del host.
- `demo-local` sigue incluyendo credenciales conocidas para fines didacticos.
- n8n mantiene estado persistente; cambiar credenciales tras bootstrap puede requerir recrear `n8n/data`.
- el dashboard maestro sigue siendo una herramienta local, no un frontend listo para edge publishing.
