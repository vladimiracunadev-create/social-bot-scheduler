# 📐 Arquitectura — Caso 04: 🟢 Node.js → 🌉 n8n → ⚡ FastAPI

[![Origen: Node.js](https://img.shields.io/badge/Origen-Node.js%2020-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Destino: FastAPI](https://img.shields.io/badge/Destino-FastAPI%20%2F%20Uvicorn-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Persistencia: SQLite](https://img.shields.io/badge/Persistencia-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor de automatización en **Node.js asíncrono (Axios)** que publica hacia un receptor de alto rendimiento en **FastAPI/Uvicorn**, orquestado por **n8n** con guardrails de resiliencia (idempotencia, circuit breaker, DLQ) y persistencia embebida en **SQLite**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `04` |
| **Origen** | Node.js 20 + Axios — [`origin/index.js`](origin/index.js) |
| **Puente** | n8n — [`case-04-node-to-fastapi.json`](../../n8n/workflows/case-04-node-to-fastapi.json) |
| **Destino** | FastAPI + Uvicorn (Python) — [`dest/main.py`](dest/main.py) |
| **Persistencia** | SQLite (embebido) |
| **Puerto (dashboard)** | [`http://localhost:8084`](http://localhost:8084) |
| **Perfil Docker** | `case04` |
| **Guardrails** | Idempotencia · Circuit Breaker · Dead Letter Queue |

---

## 🗺️ Diagrama de arquitectura

```mermaid
flowchart LR
    subgraph ORIGIN["🟢 ORIGEN · Node.js"]
        A[posts.json] --> B{index.js<br/>Axios}
    end

    subgraph BRIDGE["🌉 PUENTE · n8n + Guardrails"]
        C((Webhook)) --> IDEM{Idempotencia<br/>fingerprint}
        IDEM -- duplicado --> DISCARD[200 OK · descarta]
        IDEM -- nuevo --> CB{Circuit<br/>Breaker}
        CB -- cerrado --> FWD[HTTP forward]
        CB -- abierto --> DLQ[[Dead Letter Queue]]
    end

    subgraph DEST["⚡ DESTINO · FastAPI / Uvicorn"]
        FWD --> H[main.py]
        H --> DB[(SQLite)]
        DB --> DASH[Dashboard :8084]
    end

    B -- POST JSON --> C
    FWD -. error .-> DLQ

    classDef origin fill:#339933,stroke:#1c521c,color:#fff
    classDef bridge fill:#EA4B71,stroke:#8c1c38,color:#fff
    classDef dest fill:#009688,stroke:#004d45,color:#fff
    classDef db fill:#003B57,stroke:#001d2b,color:#fff
    class A,B origin
    class C,IDEM,CB,FWD,DLQ,DISCARD bridge
    class H,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
sequenceDiagram
    autonumber
    participant Node as 🟢 index.js
    participant N8N as 🌉 n8n
    participant API as ⚡ main.py
    participant DB as 🗄️ SQLite

    Node->>Node: Lee posts.json + envía async (Axios)
    Node->>N8N: POST /webhook (JSON del post)
    N8N->>N8N: Idempotencia (fingerprint)
    alt Duplicado
        N8N-->>Node: 200 OK (descartado)
    else Nuevo
        N8N->>N8N: Circuit Breaker (estado)
        alt Breaker cerrado
            N8N->>API: HTTP forward del payload
            API->>API: Validación Pydantic (tipado estricto)
            API->>DB: INSERT post
            DB-->>API: OK
            API-->>N8N: 200 + registro
            N8N-->>Node: 200 OK
        else Breaker abierto / error
            N8N->>N8N: Enruta a Dead Letter Queue
            N8N-->>Node: 5xx (reintento posterior)
        end
    end
```

---

## 🧩 Componentes

### 🟢 Origen — Node.js Async Dispatcher

- Carga `posts.json`, itera sobre las publicaciones pendientes y las envía de forma **asíncrona con Axios** (cliente HTTP basado en promesas).
- Optimizado para operaciones de E/S no bloqueantes y gestión eficiente de flujos.

### 🌉 Puente — n8n

- Recibe el webhook, aplica **idempotencia** (descarta duplicados por fingerprint), pasa por el **Circuit Breaker** y reenvía al destino. Los fallos se enrutan a la **Dead Letter Queue**.

### ⚡ Destino — FastAPI / Uvicorn

- `main.py` recibe el payload sobre el servidor ASGI **Uvicorn**, lo valida con modelos **Pydantic** (tipado estricto) y lo persiste en **SQLite**. El dashboard web (`:8084`) sirve las publicaciones registradas.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case04 up -d      # levanta receptor FastAPI + SQLite + n8n
python hub.py ejecutar 04-node-to-fastapi   # dispara el emisor Node.js
```

Dashboard: [`http://localhost:8084`](http://localhost:8084)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
