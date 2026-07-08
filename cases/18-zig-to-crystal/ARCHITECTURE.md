# 📐 Arquitectura — Caso 18: ⚡ Zig → 🌉 n8n → 💎 Crystal (Kemal) + Neo4j

[![Origen: Zig](https://img.shields.io/badge/Origen-Zig-F7A41D?logo=zig&logoColor=black)](https://ziglang.org/)
[![Destino: Crystal](https://img.shields.io/badge/Destino-Crystal%2FKemal-000000?logo=crystal&logoColor=white)](https://crystal-lang.org/)
[![Persistencia: Neo4j](https://img.shields.io/badge/Persistencia-Neo4j-018BFF?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor **Zig** (sin GC) que reenvía a **n8n**; el receptor **Crystal/Kemal** persiste cada post como un nodo `(:Post)` del grafo **Neo4j**, accedido por su API HTTP transaccional con **Cypher**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `18` |
| **Origen** | Zig 0.13 — [`origin/src/main.zig`](origin/src/main.zig) |
| **Puente** | n8n — [`case-18-zig-to-crystal.json`](../../n8n/workflows/case-18-zig-to-crystal.json) |
| **Destino** | Crystal / Kemal — [`dest/src/app.cr`](dest/src/app.cr) |
| **Persistencia** | Neo4j 5 (nodos `(:Post)`, Cypher) |
| **Puerto (dashboard)** | [`http://localhost:8098`](http://localhost:8098) |
| **Perfil Docker** | `case18` |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}%%
flowchart TB
    subgraph ORIGIN["ORIGEN - Zig (sin GC)"]
        Z["main.zig"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia + circuit breaker"}
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - Crystal/Kemal + Neo4j"]
        FWD --> K["app.cr (Kemal)"]
        K -->|Cypher MERGE via HTTP| DB[("Neo4j grafo")]
        DB --> DASH["Dashboard :8098"]
    end

    Z -->|POST JSON| C

    classDef origin fill:#F7A41D,stroke:#333,color:#000
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#018BFF,stroke:#333,color:#fff
    classDef db fill:#0b3d5c,stroke:#333,color:#fff
    class Z origin
    class C,IDEM,FWD,DLQ bridge
    class K,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':90,'boxMargin':16,'width':180}}}%%
sequenceDiagram
    autonumber
    participant Zig as main.zig (Zig)
    participant N8N as n8n
    participant Cry as Crystal/Kemal
    participant Neo as Neo4j

    Zig->>N8N: POST /webhook (post vencido)
    N8N->>N8N: Circuit breaker + idempotencia
    N8N->>Cry: HTTP POST /webhook (reintentos x3)
    Cry->>Neo: POST /db/neo4j/tx/commit (MERGE (:Post))
    Neo-->>Cry: 200 results
    Cry-->>N8N: 200 OK
    Note over Cry,Neo: El dashboard :8098 lee via /logs (MATCH (:Post) ... ORDER BY created_at)
```

---

## 🧩 Componentes

### ⚡ Origen — Zig

- `origin/src/main.zig` lee `posts.json` y reenvía los posts vencidos con `std.http.Client.fetch`. Compilado en `ReleaseSmall` (binario estático mínimo).

### 🌉 Puente — n8n

- Guardrails canónicos: fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ.

### 💎 Destino — Crystal/Kemal + Neo4j

- `dest/src/app.cr` (Kemal) traduce el contrato REST a **Cypher** contra la API HTTP transaccional de Neo4j. `MERGE (:Post {id})` en `/webhook`; `MATCH (:Post)` en `/logs`.
- Compilado con `crystal build --release`.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case18 up -d          # Neo4j + receptor Crystal
```

Dashboard: [`http://localhost:8098`](http://localhost:8098)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
