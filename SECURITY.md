# Security

Este repositorio es un **laboratorio local** con multiples servicios, paneles administrativos, motores de base de datos y componentes de observabilidad. El objetivo del hardening es reducir riesgo sin romper el valor demostrativo del stack.

## Postura actual

### Secure-default

`docker-compose.yml` ahora aplica estos defaults:

- puertos publicados solo en `127.0.0.1`
- secretos y passwords por variables de entorno
- observabilidad fuera del arranque por defecto
- Grafana con credenciales parametrizadas
- n8n con owner bootstrap desde variables, no desde credenciales fijas en compose
- Caso 09 sin API key demo embebida en codigo
- SQL Server fijado a un tag concreto de MCR
- guardrails CI contra regresiones de `latest`, puertos inseguros y secretos hardcodeados

### Demo-local

`.env.demo.example` existe para workshops y demos reproducibles. Este modo:

- sigue siendo solo para localhost
- conserva credenciales de laboratorio conocidas
- activa el perfil `full`
- no debe reutilizarse en Internet, cloud publica ni entornos compartidos

### Edge profile

Existe un perfil `edge` opcional para acceso administrativo remoto controlado. Este modo:

- no arranca por defecto
- usa Caddy con HTTPS y basic auth
- requiere configurar `EDGE_BASIC_AUTH_HASH` antes de activarlo
- esta pensado para `n8n`, `Grafana` y el gateway del Caso 09
- no sustituye un hardening de produccion completo

## Componentes sensibles

### Superficies administrativas

- `n8n`
- `Grafana`
- `Prometheus`
- `master-dashboard`
- dashboards expuestos por cada caso

### Superficies de alto riesgo

- `cAdvisor`: monta `/`, `/sys`, `/var/lib/docker`, `/var/run` y `dev/kmsg`
- `n8n/data`: persiste estado, credenciales internas y ejecuciones
- `.env`: puede contener tokens reales y passwords de laboratorio

## Lo que no debe exponerse a Internet

No publiques directamente estos puertos:

- `5678`
- `3000`
- `9090`
- `8089`
- `8080`
- `8081` a `8090`

Si necesitas acceso remoto, usa como minimo:

- reverse proxy con TLS
- autenticacion fuerte
- filtrado por IP
- secretos no demo
- rotacion de credenciales
- segmentacion de red

## Secretos

Usa una de estas plantillas:

- `.env.example` para `secure-default`
- `.env.demo.example` para `demo-local`

Si activas el perfil `edge`, define tambien:

- `EDGE_BASIC_AUTH_USER`
- `EDGE_BASIC_AUTH_HASH`
- `EDGE_N8N_HOST`
- `EDGE_GRAFANA_HOST`
- `EDGE_CASE09_HOST`
- `N8N_HOST`
- `N8N_PORT`
- `N8N_PROTOCOL`
- `N8N_PROXY_HOPS`

Nunca subas:

- `.env`
- `.env.local`
- `.env.prod`
- tokens reales de GitHub o redes sociales

## Imagenes y supply chain

El stack reduce tags mutables donde era viable sin romper compatibilidad:

- `n8nio/n8n:2.7.5`
- `prom/prometheus:v2.54.1`
- `grafana/grafana:11.2.0`
- `gcr.io/cadvisor/cadvisor:v0.49.1`
- `mcr.microsoft.com/mssql/server:2022-CU24-ubuntu-22.04`
- `caddy:2.10.2-alpine`
- `alpine:3.20.6` en el destino Go del Caso 02

El pipeline CI valida estas reglas con `scripts/check_runtime_security.py`.

## Reporte de vulnerabilidades

Si encuentras una vulnerabilidad:

1. No la divulgues publicamente antes de coordinar un fix.
2. Abre un issue privado o contacta al mantenedor con:
   - resumen del problema
   - impacto
   - pasos de reproduccion
   - alcance
   - propuesta minima de mitigacion si la tienes

## Recomendaciones operativas

- Usa `make up-secure` para el core local.
- Usa `make up-observability` solo cuando necesites metricas.
- Usa `make up-edge` solo cuando realmente necesites acceso administrativo remoto controlado.
- Usa `make up` o `.env.demo.example` solo para demos locales controladas.
- Si cambias credenciales de n8n tras el primer arranque, recrea su estado persistente.
- Trata cualquier copia del repo con `.env.demo.example` como material de laboratorio, no como base de despliegue real.
