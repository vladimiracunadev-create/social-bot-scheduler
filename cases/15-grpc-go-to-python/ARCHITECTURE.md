# 📐 Arquitectura — Caso 15: 🐹 Go (gRPC) → 🌉 n8n → 🐍 Python (gRPC) + CockroachDB

[![Origen: Go](https://img.shields.io/badge/Origen-Go-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Protocolo: gRPC](https://img.shields.io/badge/Protocolo-gRPC-6933FF?logo=grpc&logoColor=white)](https://grpc.io/)
[![Destino: Python](https://img.shields.io/badge/Destino-Python%2FFastAPI-3776AB?logo=python&logoColor=white)](https://fastapi.tiangolo.com/)
[![Persistencia: CockroachDB](https://img.shields.io/badge/Persistencia-CockroachDB-6933FF?logo=cockroachlabs&logoColor=white)](https://www.cockroachlabs.com/)

> Servidor **gRPC en Go** + cliente **gRPC en Python** sobre un contrato `.proto` compartido, con persistencia en **CockroachDB**. El receiver Python adapta el contrato REST del laboratorio a llamadas gRPC.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `15` |
| **Origen** | Go (servidor gRPC) — [`origin/server.go`](origin/server.go) |
| **Contrato** | [`proto/social.proto`](proto/social.proto) |
| **Puente** | n8n — [`case-15-grpc-go-to-python.json`](../../n8n/workflows/case-15-grpc-go-to-python.json) |
| **Destino** | Python (cliente gRPC + FastAPI) — [`dest/main.py`](dest/main.py) |
| **Persistencia** | CockroachDB 24 (`social_posts`) |
| **Puerto (dashboard)** | [`http://localhost:8095`](http://localhost:8095) |
| **Perfil Docker** | `case15` |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}%%
flowchart TB
    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia + circuit breaker"}
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - Python (cliente gRPC)"]
        FWD --> PY["main.py (FastAPI)"]
        PY -->|gRPC Publish| GO["server.go (gRPC)"]
        GO --> DB[("CockroachDB")]
        DB --> DASH["Dashboard :8095"]
    end

    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#3776AB,stroke:#333,color:#fff
    classDef go fill:#00ADD8,stroke:#333,color:#000
    classDef db fill:#6933FF,stroke:#333,color:#fff
    class C,IDEM,FWD,DLQ bridge
    class PY,DASH dest
    class GO go
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':80,'boxMargin':16,'width':170}}}%%
sequenceDiagram
    autonumber
    participant N8N as n8n
    participant PY as Python (cliente gRPC)
    participant GO as Go (servidor gRPC)
    participant CR as CockroachDB

    N8N->>PY: HTTP POST /webhook (reintentos x3)
    PY->>GO: gRPC Publish(Post)
    GO->>CR: INSERT ... ON CONFLICT
    CR-->>GO: OK
    GO-->>PY: Ack(ok=true)
    PY-->>N8N: 200 OK
    Note over PY,GO: GET /logs -> gRPC ListRecent(Empty) -> SELECT ... LIMIT 20
```

---

## 🧩 Componentes

### 🐹 Servidor — Go (gRPC)

- `origin/server.go` implementa `SocialService` (unary `Publish` y `ListRecent`) y persiste en CockroachDB vía `database/sql` + `lib/pq`. Los stubs se generan con `protoc` en el build.

### 🌉 Puente — n8n

- Guardrails canónicos: fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ.

### 🐍 Cliente — Python (FastAPI + grpcio)

- `dest/main.py` abre un canal gRPC al servidor Go y traduce `/webhook`→`Publish`, `/logs`→`ListRecent`. Adaptador REST↔gRPC porque n8n no habla gRPC nativo.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case15 up -d          # CockroachDB + servidor Go + receiver Python
```

Dashboard: [`http://localhost:8095`](http://localhost:8095)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
