# Social Bot Scheduler

Laboratorio de integracion multi-lenguaje y multi-servicio donde **n8n** actua como puente central entre bots emisores y dashboards/receptores escritos en Python, Go, Node.js, PHP, Ruby, Flask y FastAPI.

El repositorio sigue siendo un laboratorio real y demostrable, pero ahora separa con mas claridad lo que es:

- `secure-default`: arranque local mas seguro, con puertos publicados solo en `127.0.0.1`, secretos por variables y observabilidad fuera del arranque por defecto.
- `demo-local`: modo reproducible para workshops y demos, usando `.env.demo.example` y el perfil `full`, siempre pensado para **localhost** y nunca para Internet.

## Quickstart

### 1. Modo mas seguro por defecto

```bash
cp .env.example .env
docker-compose up -d
```

Esto levanta el core local del laboratorio:

- `n8n` en `http://localhost:5678`
- dashboard maestro en `http://localhost:8080`
- sin Grafana/Prometheus/cAdvisor por defecto
- sin perfiles de casos completos hasta que tu los actives

Para un caso puntual:

```bash
docker-compose --profile case01 up -d n8n master-dashboard dest-php db-mysql
```

### 2. Demo local completa

```bash
cp .env.demo.example .env
make up
```

`make up` mantiene el valor didactico del repositorio y levanta el laboratorio completo con el perfil `full`, pero sigue publicando puertos solo en `127.0.0.1`.

### 3. Observabilidad bajo demanda

```bash
make up-observability
```

Esto levanta:

- Prometheus `http://localhost:9090`
- Grafana `http://localhost:3000`
- cAdvisor `http://localhost:8089`

### 4. Acceso edge opcional con TLS y basic auth

El perfil `edge` agrega un reverse proxy con Caddy para exponer `n8n`, `Grafana` y el gateway del Caso 09 detras de HTTPS y basic auth, sin alterar el comportamiento local del laboratorio.

```bash
# 1. Genera un hash bcrypt valido para Caddy
docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext 'TuPasswordFuerte'

# 2. Copia el resultado en EDGE_BASIC_AUTH_HASH dentro de .env

# 3. Activa el perfil
make up-edge
```

Hosts por defecto:

- `n8n.localhost`
- `grafana.localhost`
- `gateway.localhost`

El dashboard maestro sigue siendo local-only porque sus pruebas desde navegador usan los puertos `localhost` del laboratorio.

## Casos de integracion

| Caso | Flujo | Persistencia | Perfil |
| --- | --- | --- | --- |
| 01 | Python -> n8n -> PHP | MySQL | `case01` |
| 02 | Python -> n8n -> Go | MariaDB | `case02` |
| 03 | Go -> n8n -> Node.js | PostgreSQL | `case03` |
| 04 | Node.js -> n8n -> FastAPI | SQLite | `case04` |
| 05 | Laravel -> n8n -> React | MongoDB | `case05` |
| 06 | Go -> n8n -> Symfony | Redis | `case06` |
| 07 | Rust -> n8n -> Ruby | Cassandra | `case07` |
| 08 | C# -> n8n -> Flask | SQL Server | `case08` |
| 09 | Python -> n8n -> FastAPI Gateway | DuckDB | `case09` |

El dashboard maestro mantiene la capacidad de disparar pruebas desde el navegador porque los puertos siguen publicados en `localhost`.

## Modelo de seguridad runtime

### Que sigue siendo demo/local

- `master-dashboard`
- los dashboards de cada caso
- el owner inicial de n8n creado por `scripts/n8n_auto_setup.sh`
- credenciales de laboratorio cuando eliges `.env.demo.example`
- los flujos de autoimportacion de n8n

### Que ahora pasa a default mas seguro

- todos los puertos publicados se bindean a `127.0.0.1`
- secretos y passwords salen de `docker-compose.yml` y pasan a variables
- Grafana, Prometheus y cAdvisor ya no arrancan por defecto
- cAdvisor queda como componente opt-in por su visibilidad del host
- Grafana usa credenciales por `.env`, ya no `admin/admin`
- el gateway del Caso 09 exige `INTEGRATION_API_KEY` real desde entorno

## Superficies que NO debes exponer a Internet

- `n8n` (`:5678`)
- `Grafana` (`:3000`)
- `Prometheus` (`:9090`)
- `cAdvisor` (`:8089`)
- `master-dashboard` (`:8080`)
- los dashboards de casos (`:8081` a `:8090`)

Si necesitas publicar algo fuera de localhost, hazlo detras de reverse proxy, TLS, autenticacion fuerte, filtrado de IP y secretos no demo.

## Credenciales y secretos

### Plantillas disponibles

- `.env.example`: plantilla para `secure-default`
- `.env.demo.example`: plantilla para `demo-local`

### Variables importantes

- `N8N_OWNER_EMAIL`
- `N8N_OWNER_PASSWORD`
- `N8N_ENCRYPTION_KEY`
- `GRAFANA_ADMIN_USER`
- `GRAFANA_ADMIN_PASSWORD`
- `CASE01_DB_PASSWORD`
- `CASE02_DB_PASSWORD`
- `CASE03_DB_PASSWORD`
- `CASE08_DB_PASSWORD`
- `MSSQL_IMAGE`
- `INTEGRATION_API_KEY`
- `GITHUB_TOKEN`
- `N8N_HOST`
- `N8N_PORT`
- `N8N_PROTOCOL`
- `N8N_PROXY_HOPS`
- `EDGE_BIND_IP`
- `EDGE_N8N_HOST`
- `EDGE_GRAFANA_HOST`
- `EDGE_CASE09_HOST`
- `EDGE_BASIC_AUTH_USER`
- `EDGE_BASIC_AUTH_HASH`

## Observabilidad y riesgo operativo

### Prometheus y Grafana

- siguen funcionando cuando activas el perfil `observability` o `full`
- se mantienen accesibles desde el host local para conservar la experiencia de laboratorio
- Grafana ya no depende de credenciales hardcodeadas

### cAdvisor

`cAdvisor` conserva montajes del host y acceso a metadatos del runtime Docker para no perder la capacidad de observacion del laboratorio. Precisamente por eso:

- no arranca en `secure-default`
- debe considerarse **alto riesgo** si el host no es confiable
- no debe exponerse a Internet

### Edge Proxy

- no arranca por defecto
- requiere `EDGE_BASIC_AUTH_HASH` explicito
- es la via recomendada cuando realmente necesitas acceso administrativo remoto controlado

## Supply chain e imagenes

Se corrigieron varios tags demasiado mutables:

- `docker-compose.dev.yml` deja de usar `n8nio/n8n:latest`
- Prometheus, Grafana y cAdvisor usan tags versionados por variable de entorno
- SQL Server queda fijado por defecto a `mcr.microsoft.com/mssql/server:2022-CU24-ubuntu-22.04`
- el Dockerfile del Caso 02 deja de usar `alpine:latest`
- el perfil `edge` usa `caddy:2.10.2-alpine`

## Comandos utiles

```bash
make up              # demo completa (perfil full)
make up-secure       # core local mas seguro
make up-observability
make up-edge         # proxy HTTPS/basicauth opcional
make demo            # dispara Caso 01
make demo09          # dispara Caso 09
make logs
make reset-n8n
python verify_n8n.py
python scripts/check_runtime_security.py
```

## Verificacion

Despues de levantar el stack puedes comprobar:

- `http://localhost:5678/healthz`
- `http://localhost:8080`
- `python verify_n8n.py`
- `python scripts/check_runtime_security.py`
- `python verify_all_cases.py` cuando tengas los casos levantados

## Documentacion relacionada

- [SECURITY.md](SECURITY.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/RUNTIME_SECURITY.md](docs/RUNTIME_SECURITY.md)
- [docs/VERIFICATION_GUIDE.md](docs/VERIFICATION_GUIDE.md)
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- [n8n/README.md](n8n/README.md)
- [cases/09-python-to-gateway/README.md](cases/09-python-to-gateway/README.md)
