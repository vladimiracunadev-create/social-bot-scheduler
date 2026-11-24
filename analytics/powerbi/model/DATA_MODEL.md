# Modelo de datos para Power BI (contratos v1.0.0)

Este documento es la referencia para construir o rehacer el modelo en Power BI
Desktop.

En `analytics/powerbi/reports/` hay **un `.pbix` por caso**, ya construido y
listo para abrir (`social-bot-caso09.pbix`, `social-bot-caso13.pbix`,
`social-bot-caso16.pbix`). Son binarios, así que un diff no dice nada de ellos:
por eso la fuente de verdad revisable sigue siendo esta pareja de ficheros —los
contratos en `contracts.py` y las medidas en `dax/measures.dax`—, y este
documento permite reconstruir cualquier informe desde cero si uno se corrompe o
queda desfasado.

## 1. Esquema en estrella

```
                 ┌───────────────┐
                 │   dim_date    │
                 │  date_key (1) │
                 └───────┬───────┘
                         │
   ┌───────────────┐     │      ┌──────────────────┐
   │   dim_case    │     │      │   dim_channel    │
   │ case_id  (1)  │     │      │  channel   (1)   │
   └───────┬───────┘     │      └────────┬─────────┘
           │             │               │
           │      ┌──────┴───────────────┴──────┐
           └─────▶│         fact_events         │
                  │  case_id · date_key ·       │
                  │  channel · event_type ·     │
                  │  status · latency_ms ·      │
                  │  http_status · subject      │
                  └─────────────────────────────┘
```

Tablas de detalle (drill-through, sin relación activa obligatoria):
`case09_requests`, `case09_provider_calls`, `case09_repo_snapshots`,
`case13_posts`, `case16_posts`.

## 2. Relaciones a crear

| Desde (1) | Hacia (\*) | Cardinalidad | Dirección del filtro | Activa |
| :--- | :--- | :--- | :--- | :--- |
| `dim_case[case_id]` | `fact_events[case_id]` | uno a varios | única | sí |
| `dim_channel[channel]` | `fact_events[channel]` | uno a varios | única | sí |
| `dim_date[date_key]` | `fact_events[date_key]` | uno a varios | única | sí |
| `case09_requests[request_id]` | `case09_provider_calls[request_id]` | uno a varios | única | sí |
| `case09_requests[request_id]` | `case09_repo_snapshots[request_id]` | uno a varios | única | sí |

En **Modelado → Marcar como tabla de fechas** marcar `dim_date` con la columna
`date_key`. Sin ese paso las medidas de inteligencia de tiempo
(`Events 7D`, `Events Prev Day`, `Failure Rate 7D`) devuelven error.

## 3. Tipos de columna

Los tipos que debe tener cada columna salen del propio contrato; `python -m
analytics.powerbi.cli list` enumera los datasets y
`analytics/powerbi/contracts.py` declara el tipo Power BI de cada columna
(`Text`, `Whole Number`, `Decimal Number`, `Date/Time`, `Date`, `True/False`).

Dos detalles que Power Query no adivina bien y conviene fijar a mano:

- `fact_events[date_key]` y `dim_date[date_key]` → **Date** (no Date/Time), o
  la relación entre ambas no empareja.
- `fact_events[latency_ms]` y `fact_events[http_status]` → **Whole Number**.
  Vienen vacíos en los eventos que no miden latencia (un request o un post), y
  esos vacíos deben quedar como `null`, no como `0`: un `0` falsearía la media
  de latencia.

## 4. Granos y claves

| Dataset | Grano | Clave |
| :--- | :--- | :--- |
| `fact_events` | un evento observable de un caso | `event_id` |
| `case09_requests` | una petición aceptada por el gateway | `request_id` |
| `case09_provider_calls` | una llamada saliente al proveedor | `call_id` |
| `case09_repo_snapshots` | un repositorio observado en una petición | `request_id` + `repo` |
| `case13_posts` | un post proyectado en ClickHouse | `id` |
| `case16_posts` | un post persistido en la hypertable | `id` |

`event_id` se construye con prefijo de caso y tipo (`09-req-…`, `09-call-…`,
`13-post-…`, `16-post-…`), de modo que la unión de los tres casos no colisiona.

## 5. Qué mide cada tipo de evento

| `event_type` | Origen | `status` | Trae latencia |
| :--- | :--- | :--- | :--- |
| `integration_request` | `case09_requests` | el estado real del gateway | no |
| `provider_call` | `case09_provider_calls` | derivado del HTTP (2xx → `SUCCEEDED`) | sí |
| `post` | `case13_posts`, `case16_posts` | `SUCCEEDED` (la fila existe porque se persistió) | no |

Esa última fila es una limitación honesta del modelo: los casos 13 y 16 solo
almacenan los posts que **llegaron**. Un fallo de publicación no deja rastro en
esas tablas, así que la tasa de éxito de 13 y 16 es `100 %` por construcción.
Solo el caso 09 registra sus fallos, y por eso es el único cuya fiabilidad es
medible. Está declarado también en `docs/POWER_BI_INTEGRATION.md`.

## 6. Medidas

En `analytics/powerbi/dax/measures.dax`. Se pegan una a una en Power BI
Desktop (Modelado → Nueva medida).
