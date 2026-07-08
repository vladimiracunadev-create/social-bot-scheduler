# 📐 Arquitectura — Caso 16: 🚀 Apollo GraphQL → 🌉 n8n → 🟦 Hasura → 📈 TimescaleDB

[![Origen: Apollo](https://img.shields.io/badge/Origen-Apollo%20GraphQL-311C87?logo=apollographql&logoColor=white)](https://www.apollographql.com/)
[![Destino: Hasura](https://img.shields.io/badge/Destino-Hasura-1EB4D4?logo=hasura&logoColor=white)](https://hasura.io/)
[![Persistencia: TimescaleDB](https://img.shields.io/badge/Persistencia-TimescaleDB-FDB515?logo=timescale&logoColor=black)](https://www.timescale.com/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor **schema-first** en Apollo Server que reenvía posts vencidos a **n8n**; un micro-receiver traduce el contrato REST del laboratorio a **mutaciones/queries GraphQL** contra **Hasura** (**DB-first**), con persistencia en **TimescaleDB** (hypertables particionadas por tiempo).

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `16` |
| **Origen** | Apollo Server 4 (Node.js) — [`origin/index.js`](origin/index.js) |
| **Puente** | n8n — [`case-16-graphql-to-hasura.json`](../../n8n/workflows/case-16-graphql-to-hasura.json) |
| **Destino** | Micro-receiver REST↔GraphQL — [`dest/receiver/index.js`](dest/receiver/index.js) |
| **Motor destino** | Hasura GraphQL Engine |
| **Persistencia** | TimescaleDB (hypertable `social_posts`) |
| **Puerto (dashboard)** | [`http://localhost:8096`](http://localhost:8096) |
| **Perfil Docker** | `case16` |
| **Guardrails** | Fingerprint · Circuit breaker · Idempotencia · HTTP con reintentos · DLQ |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}}%%
flowchart TB
    subgraph ORIGIN["ORIGEN - Apollo GraphQL"]
        A["index.js (Apollo Server)"] --> Q["Query duePosts"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> CB{"Circuit breaker"}
        CB -->|abierto| STOP["Descarta"]
        CB -->|cerrado| IDEM{"Idempotencia (fingerprint)"}
        IDEM -->|duplicado| DISCARD["200 OK - descarta"]
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - Receiver + Hasura"]
        FWD --> R["receiver /webhook"]
        R -->|mutation GraphQL| H["Hasura Engine"]
        H --> DB[("TimescaleDB hypertable")]
        DASH["Dashboard :8096"] -->|query GraphQL /logs| R
        R -->|query GraphQL| H
    end

    Q -->|POST JSON| C

    classDef origin fill:#311C87,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#1EB4D4,stroke:#333,color:#fff
    classDef db fill:#FDB515,stroke:#333,color:#000
    class A,Q origin
    class C,CB,IDEM,FWD,DLQ,DISCARD,STOP bridge
    class R,H,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':90,'boxMargin':16,'width':180}}}%%
sequenceDiagram
    autonumber
    participant Apollo as Apollo (origin)
    participant N8N as n8n
    participant Rec as Receiver
    participant Has as Hasura
    participant TS as TimescaleDB

    Apollo->>N8N: POST /webhook (post vencido)
    N8N->>N8N: Circuit breaker + idempotencia
    alt Duplicado o circuito abierto
        N8N-->>Apollo: 200 OK (descartado)
    else Nuevo
        N8N->>Rec: HTTP POST /webhook (reintentos x3)
        Rec->>Has: mutation insert_social_posts_one
        Has->>TS: INSERT en hypertable
        TS-->>Has: OK
        Has-->>Rec: id
        Rec-->>N8N: 200 OK
        N8N-->>Apollo: 200 OK
    end
    Note over Rec,Has: El dashboard :8096 lee vía query GraphQL (/logs)
```

---

## 🧩 Componentes

### 🚀 Origen — Apollo GraphQL (schema-first)

- `origin/index.js` levanta **Apollo Server 4** con un schema escrito a mano (`ScheduledPost`, queries `scheduledPosts` y `duePosts`) y un daemon de polling que reenvía los posts vencidos al webhook de n8n.

### 🌉 Puente — n8n

- Aplica los guardrails canónicos del laboratorio: **fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ** vía `/errors`.

### 🟦 Destino — Receiver + Hasura (DB-first)

- `dest/receiver/index.js` traduce el contrato REST a GraphQL: en `/webhook` ejecuta una **mutation** contra Hasura; en `/logs` una **query**. Al arrancar, **trackea** la tabla vía Metadata API (idempotente).
- **Hasura** deriva el API GraphQL automáticamente del esquema Postgres, sin resolvers.
- **TimescaleDB** almacena los posts en una **hypertable** particionada por `created_at`.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case16 up -d          # TimescaleDB + Hasura + receiver
```

Dashboard: [`http://localhost:8096`](http://localhost:8096)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
