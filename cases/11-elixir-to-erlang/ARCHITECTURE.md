# 📐 Arquitectura — Caso 11: 💧 Elixir → 🌉 n8n → 🔴 Erlang (Cowboy) + Mnesia

[![Origen: Elixir](https://img.shields.io/badge/Origen-Elixir-4B275F?logo=elixir&logoColor=white)](https://elixir-lang.org/)
[![Destino: Erlang](https://img.shields.io/badge/Destino-Erlang%2FCowboy-A90533?logo=erlang&logoColor=white)](https://www.erlang.org/)
[![Persistencia: Mnesia](https://img.shields.io/badge/Persistencia-Mnesia-6E4A7E?logo=erlang&logoColor=white)](https://www.erlang.org/doc/apps/mnesia/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor **Elixir** que reenvía posts vencidos a **n8n**; el receptor **Erlang/Cowboy** los persiste en **Mnesia**, la BD nativa de la BEAM embebida en el runtime. Demuestra el modelo de actores, la supervisión OTP y el patrón "let it crash".

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `11` |
| **Origen** | Elixir — [`origin/lib/publisher.ex`](origin/lib/publisher.ex) |
| **Puente** | n8n — [`case-11-elixir-to-erlang.json`](../../n8n/workflows/case-11-elixir-to-erlang.json) |
| **Destino** | Erlang/Cowboy 2.12 (release OTP) — [`dest/src/social_bot_dest_app.erl`](dest/src/social_bot_dest_app.erl) |
| **Persistencia** | Mnesia (`ram_copies`, embebida) |
| **Puerto (dashboard)** | [`http://localhost:8092`](http://localhost:8092) |
| **Perfil Docker** | `case11` |
| **Guardrails** | Fingerprint · Circuit breaker · Idempotencia · HTTP con reintentos · DLQ |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}%%
flowchart TB
    subgraph ORIGIN["ORIGEN - Elixir"]
        P["publisher.ex"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> CB{"Circuit breaker"}
        CB -->|abierto| STOP["Descarta"]
        CB -->|cerrado| IDEM{"Idempotencia (fingerprint)"}
        IDEM -->|duplicado| DISCARD["200 OK - descarta"]
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - Erlang/Cowboy (BEAM)"]
        FWD --> SUP["Supervisor OTP"]
        SUP --> WH["webhook_handler"]
        WH --> ST["store (transaccion)"]
        ST --> DB[("Mnesia ram_copies")]
        DB --> DASH["Dashboard :8092"]
    end

    P -->|POST JSON| C

    classDef origin fill:#4B275F,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#A90533,stroke:#333,color:#fff
    classDef db fill:#6E4A7E,stroke:#333,color:#fff
    class P origin
    class C,CB,IDEM,FWD,DLQ,DISCARD,STOP bridge
    class SUP,WH,ST,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':90,'boxMargin':16,'width':180}}}%%
sequenceDiagram
    autonumber
    participant Ex as publisher.ex (Elixir)
    participant N8N as n8n
    participant Cow as Cowboy handler
    participant Mn as Mnesia

    Ex->>N8N: POST /webhook (post vencido)
    N8N->>N8N: Circuit breaker + idempotencia
    alt Duplicado o circuito abierto
        N8N-->>Ex: 200 OK (descartado)
    else Nuevo
        N8N->>Cow: HTTP POST /webhook (reintentos x3)
        Cow->>Cow: Proceso BEAM dedicado por request
        Cow->>Mn: mnesia:transaction(write)
        Mn-->>Cow: {atomic, ok}
        Cow-->>N8N: 200 OK
        N8N-->>Ex: 200 OK
    end
    Note over Cow,Mn: El dashboard :8092 lee via /logs (mnesia:transaction/read)
```

---

## 🧩 Componentes

### 💧 Origen — Elixir

- `origin/lib/publisher.ex` lee `posts.json` y reenvía los posts vencidos a n8n. Sin dependencias: `:httpc` para HTTP y el módulo `:json` de OTP 27.

### 🌉 Puente — n8n

- Guardrails canónicos del laboratorio: **fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ**.

### 🔴 Destino — Erlang/Cowboy + Mnesia

- `social_bot_dest_app` inicializa Mnesia y levanta Cowboy; `social_bot_dest_sup` es el árbol de supervisión OTP.
- `webhook_handler` persiste cada post en una **transacción Mnesia**; `logs_handler` sirve los últimos registros; `dashboard_handler` sirve el HTML desde `priv/`.
- Empaquetado como **release OTP** con ERTS embebido.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case11 up -d          # receptor Erlang/Cowboy + Mnesia (sin BD externa)
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
