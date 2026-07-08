# 📐 Arquitectura — Caso 17: 🦀 Rust (MQTT) → 🌉 n8n → 🟢 Node → 📊 InfluxDB

[![Origen: Rust](https://img.shields.io/badge/Origen-Rust-000000?logo=rust&logoColor=white)](https://www.rust-lang.org/)
[![Protocolo: MQTT](https://img.shields.io/badge/Protocolo-MQTT-660066?logo=mqtt&logoColor=white)](https://mqtt.org/)
[![Destino: Node](https://img.shields.io/badge/Destino-Node.js-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Persistencia: InfluxDB](https://img.shields.io/badge/Persistencia-InfluxDB-22ADF6?logo=influxdb&logoColor=white)](https://www.influxdata.com/)

> Emisor **Rust** que publica por **MQTT** en Mosquitto; un **subscriber Node** persiste en **InfluxDB**. El receiver REST reinyecta la entrega de n8n en el mismo bus, unificando ambas entradas en un único sink de series temporales.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `17` |
| **Origen** | Rust (`rumqttc`) — [`origin/src/main.rs`](origin/src/main.rs) |
| **Puente** | n8n — [`case-17-mqtt-rust-to-node.json`](../../n8n/workflows/case-17-mqtt-rust-to-node.json) |
| **Broker** | Mosquitto 2.x (topic `social/posts`, QoS 1) |
| **Destino** | Node subscriber + receiver REST — [`dest/index.js`](dest/index.js) |
| **Persistencia** | InfluxDB 1.8 (measurement `social_posts`) |
| **Puerto (dashboard)** | [`http://localhost:8097`](http://localhost:8097) |
| **Perfil Docker** | `case17` |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}%%
flowchart TB
    subgraph ORIGIN["ORIGEN - Rust (MQTT)"]
        R["main.rs (rumqttc)"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia + circuit breaker"}
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - Node + InfluxDB"]
        MQ(["Mosquitto topic social/posts"])
        FWD --> REC["receiver /webhook"]
        REC -->|publish| MQ
        MQ -->|subscribe| SINK["subscriber"]
        SINK --> DB[("InfluxDB")]
        DB --> DASH["Dashboard :8097"]
    end

    R -->|MQTT publish| MQ
    R -.->|via n8n opcional| C

    classDef origin fill:#000000,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#339933,stroke:#333,color:#fff
    classDef db fill:#22ADF6,stroke:#333,color:#fff
    class R origin
    class C,IDEM,FWD,DLQ bridge
    class REC,SINK,MQ,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación vía n8n)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':80,'boxMargin':16,'width':170}}}%%
sequenceDiagram
    autonumber
    participant Rust as main.rs (Rust)
    participant N8N as n8n
    participant Rec as receiver
    participant MQ as Mosquitto
    participant Sub as subscriber
    participant Inf as InfluxDB

    Rust->>N8N: POST /webhook (post vencido)
    N8N->>N8N: Circuit breaker + idempotencia
    N8N->>Rec: HTTP POST /webhook (reintentos x3)
    Rec->>MQ: publish social/posts (QoS 1)
    Rec-->>N8N: 200 OK
    MQ->>Sub: deliver mensaje
    Sub->>Inf: write line protocol
    Inf-->>Sub: 204 No Content
    Note over Rust,MQ: El emisor Rust también puede publicar MQTT directo al broker
```

---

## 🧩 Componentes

### 🦀 Origen — Rust (MQTT publisher)

- `origin/src/main.rs` usa `rumqttc` (síncrono, sin TLS) para publicar los posts en `social/posts`. Perfil release con LTO + strip → binario mínimo.

### 🌉 Puente — n8n

- Guardrails canónicos: fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ.

### 🟢 Destino — Node + InfluxDB

- `dest/index.js` es a la vez **subscriber** (MQTT → InfluxDB) y **receiver REST** (`/webhook` publica en MQTT). Un único sink, dos entradas.
- **InfluxDB 1.8** almacena `social_posts` como serie temporal; `/logs` consulta con InfluxQL.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case17 up -d          # Mosquitto + InfluxDB + receiver Node
```

Dashboard: [`http://localhost:8097`](http://localhost:8097)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
