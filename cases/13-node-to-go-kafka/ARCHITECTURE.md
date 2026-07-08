# 📐 Arquitectura — Caso 13: 🟢 Node+Kafka → 🌉 n8n → 🐹 Go → 📊 ClickHouse

[![Origen: Node](https://img.shields.io/badge/Origen-Node%2FKafka-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Broker: Kafka](https://img.shields.io/badge/Broker-Kafka%20KRaft-231F20?logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Destino: Go](https://img.shields.io/badge/Destino-Go-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Persistencia: ClickHouse](https://img.shields.io/badge/Persistencia-ClickHouse-FAFF69?logo=clickhouse&logoColor=black)](https://clickhouse.com/)

> Emisor **Node/kafkajs** produce eventos a **Kafka**; un consumer **Go** los proyecta ("sink") en **ClickHouse** (OLAP columnar). Patrón CQRS con dos entradas (Node directo y n8n→receiver) convergiendo en un único sink.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `13` |
| **Origen** | Node/kafkajs — [`origin/producer.js`](origin/producer.js) |
| **Broker** | Kafka 3.8 (KRaft, topic `social-posts`) |
| **Puente** | n8n — [`case-13-node-to-go-kafka.json`](../../n8n/workflows/case-13-node-to-go-kafka.json) |
| **Destino** | Go (`kafka-go`) — [`dest/main.go`](dest/main.go) |
| **Persistencia** | ClickHouse 24 (`ReplacingMergeTree`) |
| **Puerto (dashboard)** | [`http://localhost:8093`](http://localhost:8093) |
| **Perfil Docker** | `case13` |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}%%
flowchart TB
    subgraph ORIGIN["ORIGEN - Node + Kafka"]
        N["producer.js (kafkajs)"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia + circuit breaker"}
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - Go + ClickHouse"]
        K(["Kafka topic social-posts"])
        FWD --> REC["receiver /webhook"]
        REC -->|produce| K
        K -->|consume| SINK["consumer goroutine"]
        SINK --> DB[("ClickHouse")]
        DB --> DASH["Dashboard :8093"]
    end

    N -->|produce| K
    N -.->|via n8n| C

    classDef origin fill:#339933,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#00ADD8,stroke:#333,color:#000
    classDef db fill:#FAFF69,stroke:#333,color:#000
    class N origin
    class C,IDEM,FWD,DLQ bridge
    class REC,SINK,K,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación vía n8n)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':80,'boxMargin':16,'width':170}}}%%
sequenceDiagram
    autonumber
    participant Node as producer.js (Node)
    participant N8N as n8n
    participant Rec as receiver (Go)
    participant K as Kafka
    participant Sub as consumer (Go)
    participant CH as ClickHouse

    Node->>N8N: POST /webhook (post vencido)
    N8N->>N8N: Circuit breaker + idempotencia
    N8N->>Rec: HTTP POST /webhook (reintentos x3)
    Rec->>K: produce social-posts
    Rec-->>N8N: 200 OK
    K->>Sub: deliver evento
    Sub->>CH: INSERT (JSONEachRow)
    Note over Sub,CH: GET /logs -> SELECT ... ORDER BY created_at DESC LIMIT 20
```

---

## 🧩 Componentes

### 🟢 Origen — Node + Kafka

- `origin/producer.js` (kafkajs) produce los posts en el topic `social-posts` y los reenvía a n8n.

### 🌉 Puente — n8n

- Guardrails canónicos: fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ.

### 🐹 Destino — Go + ClickHouse

- `dest/main.go` (`kafka-go`) es **producer** en `/webhook` y **consumer** en una goroutine que hace sink a ClickHouse vía su interfaz HTTP. Idempotente por `id` (`ReplacingMergeTree`).

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case13 up -d          # Kafka + ClickHouse + consumer Go
```

Dashboard: [`http://localhost:8093`](http://localhost:8093)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
