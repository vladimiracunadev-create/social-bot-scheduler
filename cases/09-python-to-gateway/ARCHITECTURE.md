# 📐 Arquitectura — Caso 09: 🐍 Python → 🌉 n8n → ⚡ FastAPI Gateway

[![Origen: Python](https://img.shields.io/badge/Origen-Python%203.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Destino: FastAPI](https://img.shields.io/badge/Destino-FastAPI%20Gateway-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Persistencia: DuckDB](https://img.shields.io/badge/Persistencia-DuckDB-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor operativo en **Python** que publica hacia un **Integration Gateway** en **FastAPI** — el caso más endurecido del laboratorio —, orquestado por **n8n** con guardrails de resiliencia y un borde de seguridad reforzado (autenticación `X-API-Key`, rate limiting, whitelist de `owner`, idempotencia y DLQ), con persistencia embebida en **DuckDB** y proveedor externo **GitHub API**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `09` |
| **Origen** | Python 3.11 — [`origin/bot.py`](origin/bot.py) |
| **Puente** | n8n — [`case-09-python-to-gateway.json`](../../n8n/workflows/case-09-python-to-gateway.json) |
| **Destino** | Integration Gateway en FastAPI — [`dest/app/api.py`](dest/app/api.py) |
| **Persistencia** | DuckDB (embebida) + GitHub API (proveedor externo) |
| **Puerto (dashboard)** | [`http://localhost:8090`](http://localhost:8090) |
| **Perfil Docker** | `case09` |
| **Guardrails** | Autenticación `X-API-Key` · Rate limiting (429) · Whitelist `owner` (422) · Idempotencia · Dead Letter Queue |

---

## 🗺️ Diagrama de arquitectura

```mermaid
flowchart LR
    subgraph ORIGIN["🐍 ORIGEN · Python"]
        A[posts.json] --> B{bot.py<br/>emisor}
    end

    subgraph BRIDGE["🌉 PUENTE · n8n + Guardrails"]
        C((Webhook)) --> IDEM{Idempotencia<br/>fingerprint}
        IDEM -- duplicado --> DISCARD[200 OK · descarta]
        IDEM -- nuevo --> FWD[HTTP forward<br/>+ X-API-Key]
        FWD -. error .-> DLQ[[Dead Letter Queue<br/>/errors]]
    end

    subgraph DEST["⚡ DESTINO · FastAPI Gateway"]
        FWD --> AUTH{X-API-Key<br/>válida?}
        AUTH -- no --> E401[401 Unauthorized]
        AUTH -- sí --> RL{Rate limit<br/>30/min}
        RL -- excede --> E429[429 Too Many Requests]
        RL -- ok --> WL{Whitelist owner<br/>regex pydantic}
        WL -- inválido --> E422[422 Unprocessable]
        WL -- válido --> API[api.py]
        API --> GH[[🐙 GitHub API]]
        API --> DB[(DuckDB embebida)]
        DB --> DASH[Dashboard :8090]
    end

    B -- POST JSON --> C

    classDef origin fill:#3776AB,stroke:#1b3a5c,color:#fff
    classDef bridge fill:#EA4B71,stroke:#8c1c38,color:#fff
    classDef dest fill:#009688,stroke:#00544c,color:#fff
    classDef db fill:#FFF000,stroke:#8c8400,color:#000
    class A,B origin
    class C,IDEM,FWD,DLQ,DISCARD bridge
    class AUTH,RL,WL,API,DASH,E401,E429,E422,GH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
sequenceDiagram
    autonumber
    participant Bot as 🐍 bot.py
    participant N8N as 🌉 n8n
    participant GW as ⚡ FastAPI Gateway
    participant GitHub as 🐙 GitHub API
    participant DB as 🦆 DuckDB

    Bot->>Bot: Lee posts.json + prepara payload
    Bot->>N8N: POST /webhook (JSON del post)
    N8N->>N8N: Idempotencia (fingerprint)
    alt Duplicado
        N8N-->>Bot: 200 OK (descartado)
    else Nuevo
        N8N->>GW: HTTP forward + header X-API-Key
        alt X-API-Key ausente o inválida
            GW-->>N8N: 401 Unauthorized
        else Autenticado
            alt Rate limit excedido (30/min)
                GW-->>N8N: 429 Too Many Requests
            else Dentro del límite
                GW->>GW: Valida owner (whitelist regex GitHub)
                alt owner inválido
                    GW-->>N8N: 422 Unprocessable Entity
                else owner válido
                    GW->>GitHub: Llamada saliente (publicación real)
                    GitHub-->>GW: Respuesta del proveedor
                    GW->>DB: INSERT post (idempotente)
                    DB-->>GW: OK
                    GW-->>N8N: 200 + registro
                    N8N-->>Bot: 200 OK
                end
            end
        end
        N8N-->>DLQ: Errores → POST /errors (60/min · DLQ)
    end
```

---

## 🧩 Componentes

### 🐍 Origen — Python Bot

- `bot.py` lee `posts.json`, prepara el payload y dispara hacia el webhook de n8n como emisor operativo del ciclo de integración.

### 🌉 Puente — n8n

- Recibe el webhook, aplica **idempotencia** (descarta duplicados por fingerprint) y **reenvía al Gateway inyectando el header `X-API-Key`**. Los fallos se enrutan a la **Dead Letter Queue** mediante el endpoint `/errors`.

### ⚡ Destino — FastAPI Integration Gateway

Este es el caso **más endurecido** del laboratorio; su borde concentra las defensas de seguridad:

- **🔑 Autenticación obligatoria `X-API-Key`**: todo acceso a `POST /webhook` exige la clave `INTEGRATION_API_KEY` (sin valores demo embebidos). Su ausencia o invalidez devuelve **401**.
- **🚦 Rate limiting (`slowapi`)**: límite por IP de **30/min** en `/webhook` y **60/min** en `/errors`; el excedente devuelve **HTTP 429**. Contiene el agotamiento de la cuota de la GitHub API y el abuso de una `X-API-Key` filtrada.
- **✅ Whitelist de `owner`**: el campo `owner` se valida en el borde contra el patrón de usuario de GitHub (`^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$`) vía **pydantic → 422**, como defensa en profundidad sobre el value object `Owner` del dominio. Rechaza barras, `@` y encodings que pudieran redirigir la llamada saliente.
- **♻️ Idempotencia por fingerprint**: evita el reprocesamiento de eventos duplicados.
- **📥 DLQ vía `/errors`**: los mensajes fallidos se derivan a la cola de auditoría para su recuperación.
- **🐙 Proveedor externo GitHub API**: realiza la publicación real saliente cuando `GITHUB_TOKEN` está configurado.
- **🦆 Persistencia DuckDB**: base OLAP in-process que permite consultas analíticas sobre el histórico de posts con latencia casi nula, servidas en el dashboard (`:8090`).

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case09 up -d          # levanta Gateway FastAPI + DuckDB + n8n
python hub.py ejecutar 09-python-to-gateway     # dispara el emisor Python
```

Dashboard: [`http://localhost:8090`](http://localhost:8090)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
