# 📐 Arquitectura — Caso 12: 🧠 Python (LLM) → 🌉 n8n → ⚡ FastAPI RAG + pgvector

[![Origen: Python](https://img.shields.io/badge/Origen-Python%203.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Destino: FastAPI](https://img.shields.io/badge/Destino-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Persistencia: pgvector](https://img.shields.io/badge/Persistencia-pgvector-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor Python que reenvía a **n8n**; el receptor **FastAPI** embebe cada post e indexa el vector en **pgvector**, exponiendo búsqueda semántica por similitud coseno (`/search`) — el paso *retrieval* de un pipeline RAG.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `12` |
| **Origen** | Python 3.11 — [`origin/bot.py`](origin/bot.py) |
| **Puente** | n8n — [`case-12-python-to-rag.json`](../../n8n/workflows/case-12-python-to-rag.json) |
| **Destino** | FastAPI — [`dest/main.py`](dest/main.py) |
| **Persistencia** | pgvector (PostgreSQL 16, `vector(256)`) |
| **Puerto (dashboard)** | [`http://localhost:8092`](http://localhost:8092) |
| **Perfil Docker** | `case12` |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}%%
flowchart TB
    subgraph ORIGIN["ORIGEN - Python"]
        B["bot.py"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia + circuit breaker"}
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - FastAPI RAG"]
        FWD --> API["main.py"]
        API --> EMB["embed() 256d"]
        EMB --> DB[("pgvector")]
        DB --> SRCH["/search (coseno <=>)"]
        DB --> DASH["Dashboard :8092"]
    end

    B -->|POST JSON| C

    classDef origin fill:#3776AB,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#009688,stroke:#333,color:#fff
    classDef db fill:#336791,stroke:#333,color:#fff
    class B origin
    class C,IDEM,FWD,DLQ bridge
    class API,EMB,SRCH,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ingesta + retrieval)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':90,'boxMargin':16,'width':180}}}%%
sequenceDiagram
    autonumber
    participant Bot as bot.py (Python)
    participant N8N as n8n
    participant API as FastAPI
    participant PV as pgvector

    Bot->>N8N: POST /webhook (post vencido)
    N8N->>N8N: Circuit breaker + idempotencia
    N8N->>API: HTTP POST /webhook (reintentos x3)
    API->>API: embed(text) -> vector 256d
    API->>PV: INSERT ... embedding (ON CONFLICT)
    PV-->>API: OK
    API-->>N8N: 200 OK
    Note over API,PV: GET /search?q=... -> ORDER BY embedding <=> q LIMIT k (retrieval)
```

---

## 🧩 Componentes

### 🧠 Origen — Python

- `origin/bot.py` reenvía los posts vencidos a n8n con la stdlib (`urllib`), sin dependencias.

### 🌉 Puente — n8n

- Guardrails canónicos: fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ.

### ⚡ Destino — FastAPI RAG + pgvector

- `dest/main.py` embebe el texto (hashing determinista 256d) y lo indexa en pgvector. `/search` hace retrieval por coseno; `/logs` lista los últimos posts.
- La función de embedding es un **punto de extensión aislado** (swappable por un modelo real).

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case12 up -d          # pgvector + receptor FastAPI
```

Dashboard: [`http://localhost:8092`](http://localhost:8092)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
