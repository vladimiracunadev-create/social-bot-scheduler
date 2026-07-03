# 📐 Arquitectura — Caso 07: 🦀 Rust → 🌉 n8n → 💎 Ruby

[![Origen: Rust](https://img.shields.io/badge/Origen-Rust%201.7x-DEA584?logo=rust&logoColor=white)](https://www.rust-lang.org/)
[![Destino: Ruby](https://img.shields.io/badge/Destino-Ruby%203.2%20%2F%20Sinatra-CC342D?logo=ruby&logoColor=white)](https://www.ruby-lang.org/)
[![Persistencia: Cassandra](https://img.shields.io/badge/Persistencia-Cassandra%204.1-1287B1?logo=apache-cassandra&logoColor=white)](https://cassandra.apache.org/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor asíncrono fuertemente tipado en **Rust** (cliente `reqwest` 0.12 + `dotenvy`) que publica hacia un receptor ágil en **Ruby 3.2 / Sinatra**, orquestado por **n8n** con guardrails de resiliencia (idempotencia, circuit breaker, DLQ) y persistencia distribuida en **Cassandra**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `07` |
| **Origen** | Rust 1.7x — cliente `reqwest` 0.12 + `dotenvy` — [`origin/src/main.rs`](origin/src/main.rs) |
| **Puente** | n8n — [`case-07-rust-to-ruby.json`](../../n8n/workflows/case-07-rust-to-ruby.json) |
| **Destino** | Ruby 3.2 / Sinatra sobre Puma — [`dest/app.rb`](dest/app.rb) |
| **Persistencia** | Cassandra 4.1 (Columnar Distribuido) |
| **Puerto (dashboard)** | [`http://localhost:8087`](http://localhost:8087) |
| **Perfil Docker** | `case07` |
| **Guardrails** | Idempotencia · Circuit Breaker · Dead Letter Queue |

---

## 🗺️ Diagrama de arquitectura

```mermaid
flowchart LR
    subgraph ORIGIN["🦀 ORIGEN · Rust"]
        A[posts.json] --> B{main.rs<br/>reqwest async}
    end

    subgraph BRIDGE["🌉 PUENTE · n8n + Guardrails"]
        C((Webhook)) --> IDEM{Idempotencia<br/>fingerprint}
        IDEM -- duplicado --> DISCARD[200 OK · descarta]
        IDEM -- nuevo --> CB{Circuit<br/>Breaker}
        CB -- cerrado --> FWD[HTTP forward]
        CB -- abierto --> DLQ[[Dead Letter Queue]]
    end

    subgraph DEST["💎 DESTINO · Ruby / Sinatra"]
        FWD --> H[app.rb]
        H --> DB[(Cassandra 4.1)]
        DB --> DASH[Dashboard :8087]
    end

    B -- POST JSON --> C
    FWD -. error .-> DLQ

    classDef origin fill:#DEA584,stroke:#8a6440,color:#000
    classDef bridge fill:#EA4B71,stroke:#8c1c38,color:#fff
    classDef dest fill:#CC342D,stroke:#7a1f1b,color:#fff
    classDef db fill:#1287B1,stroke:#0a4f68,color:#fff
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
    participant Bot as 🦀 main.rs
    participant N8N as 🌉 n8n
    participant RB as 💎 app.rb
    participant DB as 🟦 Cassandra

    Bot->>Bot: Lee posts.json + serializa (Serde)
    Bot->>N8N: POST /webhook (JSON del post)
    N8N->>N8N: Idempotencia (fingerprint)
    alt Duplicado
        N8N-->>Bot: 200 OK (descartado)
    else Nuevo
        N8N->>N8N: Circuit Breaker (estado)
        alt Breaker cerrado
            N8N->>RB: HTTP forward del payload
            RB->>DB: INSERT post
            DB-->>RB: OK
            RB-->>N8N: 200 + registro
            N8N-->>Bot: 200 OK
        else Breaker abierto / error
            N8N->>N8N: Enruta a Dead Letter Queue
            N8N-->>Bot: 5xx (reintento posterior)
        end
    end
```

---

## 🧩 Componentes

### 🦀 Origen — Rust Safety Dispatcher

- Utiliza estructuras (`structs`) y **Serde** para una serialización ultra rápida de los posts, garantizando la integridad de los datos antes del envío mediante su sistema de tipos.
- Cliente **`reqwest` 0.12** asíncrono (con `dotenvy` para la configuración) para despachos masivos sin bloqueo hacia el webhook de n8n.

### 🌉 Puente — n8n

- Recibe el webhook, aplica **idempotencia** (descarta duplicados por fingerprint), pasa por el **Circuit Breaker** y reenvía al destino. Los fallos se enrutan a la **Dead Letter Queue**.

### 💎 Destino — Ruby / Sinatra

- `app.rb` (Sinatra DSL sobre el servidor Puma) gestiona los eventos entrantes, los persiste en **Cassandra** —ideal para flujos de alta escritura— y renderiza un dashboard dinámico con plantillas **ERB** (`:8087`).

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case07 up -d      # levanta receptor Ruby + Cassandra + n8n
python hub.py ejecutar 07-rust-to-ruby      # dispara el emisor Rust
```

Dashboard: [`http://localhost:8087`](http://localhost:8087)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
