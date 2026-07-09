# 📐 Arquitectura — Caso 19: #️⃣ F# (.NET) → 🌉 n8n → 🍀 Clojure (Ring) + XTDB

[![Status: Pendiente](https://img.shields.io/badge/Status-Pendiente_de_verificaci%C3%B3n-yellow.svg)]()
[![Origen: F#](https://img.shields.io/badge/Origen-F%23-378BBA?logo=dotnet&logoColor=white)](https://fsharp.org/)
[![Destino: Clojure](https://img.shields.io/badge/Destino-Clojure%2FRing-5881D8?logo=clojure&logoColor=white)](https://clojure.org/)
[![Persistencia: XTDB](https://img.shields.io/badge/Persistencia-XTDB%20bitemporal-63B132)](https://xtdb.com/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor **F#** (funcional-first sobre .NET) que reenvía a **n8n**; el receptor **Clojure/Ring** persiste en **XTDB**, una BD **bitemporal e inmutable** embebida in-process. Dos runtimes funcionales, cero contenedor de BD.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `19` |
| **Origen** | F# / .NET 9 — [`origin/Publisher.fs`](origin/Publisher.fs) |
| **Puente** | n8n — [`case-19-fsharp-to-clojure.json`](../../n8n/workflows/case-19-fsharp-to-clojure.json) |
| **Destino** | Clojure / Ring — [`dest/src/receiver/core.clj`](dest/src/receiver/core.clj) |
| **Persistencia** | XTDB 1.24 (bitemporal, embebida in-memory) |
| **Puerto (dashboard)** | [`http://localhost:8099`](http://localhost:8099) |
| **Perfil Docker** | `case19` |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}%%
flowchart TB
    subgraph ORIGIN["ORIGEN - F# (.NET)"]
        F["Publisher.fs"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia + circuit breaker"}
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - Clojure/Ring (JVM)"]
        FWD --> CLJ["core.clj (Ring)"]
        CLJ -->|put / q Datalog| DB[("XTDB embebida (bitemporal)")]
        DB --> DASH["Dashboard :8099"]
    end

    F -->|POST JSON| C

    classDef origin fill:#378BBA,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#5881D8,stroke:#333,color:#fff
    classDef db fill:#63B132,stroke:#333,color:#000
    class F origin
    class C,IDEM,FWD,DLQ bridge
    class CLJ,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':90,'boxMargin':16,'width':180}}}%%
sequenceDiagram
    autonumber
    participant FS as Publisher.fs (F#)
    participant N8N as n8n
    participant CLJ as Clojure/Ring
    participant XT as XTDB

    FS->>N8N: POST /webhook (post vencido)
    N8N->>N8N: Circuit breaker + idempotencia
    N8N->>CLJ: HTTP POST /webhook (reintentos x3)
    CLJ->>XT: submit-tx [::xt/put doc] + await-tx
    XT-->>CLJ: tx confirmada
    CLJ-->>N8N: 200 OK
    Note over CLJ,XT: GET /logs -> xt/q Datalog -> ordena por created-at desc, top 20
```

---

## 🧩 Componentes

### #️⃣ Origen — F# (.NET)

- `origin/Publisher.fs` reenvía los posts vencidos a n8n con `HttpClient`. Estilo funcional (inmutable, expresiones).

### 🌉 Puente — n8n

- Guardrails canónicos: fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ.

### 🍀 Destino — Clojure/Ring + XTDB

- `dest/src/receiver/core.clj` levanta Ring/Jetty y un nodo XTDB in-memory. `/webhook` hace `submit-tx` + `await-tx`; `/logs` consulta con Datalog. Empaquetado como uberjar (Leiningen).

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case19 up -d          # receptor Clojure + XTDB embebida
```

Dashboard: [`http://localhost:8099`](http://localhost:8099)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
