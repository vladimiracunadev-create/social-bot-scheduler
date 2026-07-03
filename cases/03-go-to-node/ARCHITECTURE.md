# 📐 Arquitectura — Caso 03: 🐹 Go → 🌉 n8n → 🟢 Node.js

[![Origen: Go](https://img.shields.io/badge/Origen-Go%201.21-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Destino: Node.js](https://img.shields.io/badge/Destino-Node.js%2020%20%2F%20Express-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Persistencia: PostgreSQL](https://img.shields.io/badge/Persistencia-PostgreSQL%2015-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor concurrente compilado en **Go** que publica hacia un receptor flexible y asíncrono en **Node.js (Express)**, orquestado por **n8n** con guardrails de resiliencia (idempotencia, circuit breaker, DLQ) y persistencia en **PostgreSQL**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `03` |
| **Origen** | Go 1.21 — [`origin/main.go`](origin/main.go) |
| **Puente** | n8n — [`case-03-go-to-node.json`](../../n8n/workflows/case-03-go-to-node.json) |
| **Destino** | Node.js 20 con Express — [`dest/index.js`](dest/index.js) |
| **Persistencia** | PostgreSQL 15 |
| **Puerto (dashboard)** | [`http://localhost:8083`](http://localhost:8083) |
| **Perfil Docker** | `case03` |
| **Guardrails** | Idempotencia · Circuit Breaker · Dead Letter Queue |

---

## 🗺️ Diagrama de arquitectura

```mermaid
flowchart LR
    subgraph ORIGIN["ORIGEN - Go"]
        B["main.go"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia (fingerprint)"}
        IDEM -->|duplicado| DISCARD["200 OK - descarta"]
        IDEM -->|nuevo| CBK{"Circuit Breaker"}
        CBK -->|cerrado| FWD["HTTP forward"]
        CBK -->|abierto| DLQ["Dead Letter Queue"]
    end

    subgraph DEST["DESTINO - Node / Express"]
        FWD --> H["index.js"]
        H --> DB[("PostgreSQL 15")]
        DB --> DASH["Dashboard :8083"]
    end

    B -->|POST JSON| C
    FWD -.->|error| DLQ

    classDef origin fill:#00ADD8,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#339933,stroke:#333,color:#fff
    classDef db fill:#4169E1,stroke:#333,color:#fff
    class B origin
    class C,IDEM,CBK,FWD,DLQ,DISCARD bridge
    class H,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
sequenceDiagram
    autonumber
    participant Bot as main.go (Go)
    participant N8N as n8n
    participant Dest as index.js (Node / Express)
    participant DB as PostgreSQL 15

    Bot->>Bot: Prepara y valida el payload
    Bot->>N8N: POST /webhook (JSON del post)
    N8N->>N8N: Idempotencia (fingerprint)
    alt Duplicado
        N8N-->>Bot: 200 OK (descartado)
    else Nuevo
        N8N->>N8N: Circuit Breaker (estado)
        alt Breaker cerrado
            N8N->>Dest: HTTP forward del payload
            Dest->>DB: INSERT post
            DB-->>Dest: OK
            Dest-->>N8N: 200 + registro
            N8N-->>Bot: 200 OK
        else Breaker abierto / error
            N8N->>N8N: Enruta a Dead Letter Queue
            N8N-->>Bot: 5xx (reintento posterior)
        end
    end
```

---

## 🧩 Componentes

### 🐹 Origen — Go Concurrent Scheduler

- Emisor de alta concurrencia que utiliza **goroutines** para el escaneo de `posts.json` y el despacho inmediato hacia el webhook de n8n.
- Emplea el cliente HTTP nativo de Go, sin dependencias externas pesadas, maximizando eficiencia y velocidad.

### 🌉 Puente — n8n

- Recibe el webhook, aplica **idempotencia** (descarta duplicados por fingerprint), pasa por el **Circuit Breaker** y reenvía al destino. Aplica una política de **3 reintentos** con intervalo de 1s ante fallos; los eventos que fallan tras los reintentos se enrutan a la **Dead Letter Queue** (tabla de auditoría) para recuperación manual.

### 🟢 Destino — Node.js / Express

- `index.js` es un receptor basado en **Express** con optimización de JSON parsing que **valida rigurosamente el schema del payload** antes de la inserción. Persiste los datos de forma relacional avanzada en **PostgreSQL** y los sirve en un dashboard dinámico (`:8083`) con recarga automática de datos.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case03 up -d      # levanta receptor Node.js + PostgreSQL + n8n
python hub.py ejecutar 03-go-to-node        # dispara el emisor Go
```

Dashboard: [`http://localhost:8083`](http://localhost:8083)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
