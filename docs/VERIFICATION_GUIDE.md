# Guia de verificacion

Esta guia cubre la validacion del laboratorio despues del hardening de runtime.

## 1. Validacion de configuracion

```bash
python scripts/check_runtime_security.py
docker-compose config
docker-compose --profile observability config
docker-compose --profile edge config
docker-compose -f docker-compose.dev.yml config
```

Esto valida:

- ausencia de `latest` en runtime
- binds a loopback o variables controladas
- secretos sensibles parametrizados
- perfiles obligatorios para observabilidad y edge

## 2. Validacion de n8n

```bash
python verify_n8n.py
```

Comprueba:

- `/healthz`
- login si el `.env` tiene credenciales no placeholder
- listado de workflows importados

## 3. Validacion funcional minima

```bash
make up-secure
make demo
make demo09
```

Verifica:

- `http://localhost:5678`
- `http://localhost:8080`
- `http://localhost:8081`
- `http://localhost:8090`

## 4. Validacion de observabilidad

```bash
make up-observability
```

Verifica:

- `http://localhost:9090`
- `http://localhost:3000`
- `http://localhost:8089`

## 5. Validacion completa del laboratorio

```bash
cp .env.demo.example .env
make up
python verify_all_cases.py
```

## 6. Validacion del perfil edge

Antes de activarlo debes definir `EDGE_BASIC_AUTH_HASH`.

```bash
make up-edge
```

Comprueba:

- `https://n8n.localhost`
- `https://grafana.localhost` si observabilidad esta activa
- `https://gateway.localhost` si Caso 09 esta activo

## 7. Notas practicas

- Si cambias credenciales de n8n despues del primer arranque, recrea `n8n/data`.
- Si el daemon Docker no esta disponible, limita la validacion a `docker-compose config`, `py_compile` y `scripts/check_runtime_security.py`.
- El dashboard maestro sigue siendo una herramienta local; no se usa como frontend edge-aware.
