# 📐 Arquitectura — Caso 02: 🐍 Python → 🌉 n8n → 🐹 Go

[![Origen: Python](https://img.shields.io/badge/Origen-Python%203.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Destino: Go](https://img.shields.io/badge/Destino-Go%201.21%20%2F%20Gin-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Persistencia: MariaDB](https://img.shields.io/badge/Persistencia-MariaDB%2010.11-003545?logo=mariadb&logoColor=white)](https://mariadb.org/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor de automatización en **Python + Pydantic** que publica hacia un receptor compilado de alto rendimiento en **Go (Gin)**, orquestado por **n8n** con guardrails de resiliencia (idempotencia, circuit breaker, DLQ) y persistencia en **MariaDB**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `02` |
| **Origen** | Python 3.11 + Pydantic — [`origin/bot.py`](origin/bot.py) |
| **Puente** | n8n — [`case-02-python-to-go.json`](../../n8n/workflows/case-02-python-to-go.json) |
| **Destino** | Go 1.21 con framework Gin — [`dest/main.go`](dest/main.go) |
| **Persistencia** | MariaDB 10.11 |
| **Puerto (dashboard)** | [`http://localhost:8082`](http://localhost:8082) |
| **Perfil Docker** | `case02` |
| **Guardrails** | Idempotencia · Circuit Breaker · Dead Letter Queue |

---

## 🗺️ Diagrama de arquitectura

```mermaid
flowchart LR
    subgraph ORIGIN["ORIGEN - Python"]
        B["bot.py"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia (fingerprint)"}
        IDEM -->|duplicado| DISCARD["200 OK - descarta"]
        IDEM -->|nuevo| CBK{"Circuit Breaker"}
        CBK -->|cerrado| FWD["HTTP forward"]
        CBK -->|abierto| DLQ["Dead Letter Queue"]
    end

    subgraph DEST["DESTINO - Go / Gin"]
        FWD --> H["main.go"]
        H --> DB[("MariaDB 10.11")]
        DB --> DASH["Dashboard :8082"]
    end

    B -->|POST JSON| C
    FWD -.->|error| DLQ

    classDef origin fill:#3776AB,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#00ADD8,stroke:#333,color:#fff
    classDef db fill:#003545,stroke:#333,color:#fff
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
    participant Bot as bot.py (Python)
    participant N8N as n8n
    participant Dest as main.go (Go / Gin)
    participant DB as MariaDB 10.11

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

### 🐍 Origen — Python Event Bus

- Carga `posts.json`, **valida cada entrada con Pydantic** antes del envío y despacha publicaciones programadas hacia el webhook de n8n dirigido específicamente al flujo de receptores Go.
- Resiliencia en el envío (manejo de errores + logs locales de ejecución).

### 🌉 Puente — n8n

- Recibe el webhook, aplica **idempotencia** (descarta duplicados por fingerprint), pasa por el **Circuit Breaker** y reenvía al destino. Ante fallos de red o saturación del servicio Go aplica **reintentos automáticos** (hasta 3 intentos) y los fallos persistentes se enrutan a la **Dead Letter Queue** con el payload original.

### 🐹 Destino — Go / Gin

- `main.go` es un receptor compilado de alto rendimiento y mínima huella de memoria, servido con el framework **Gin**. Implementa `sync.Mutex` para garantizar la integridad en escrituras concurrentes y persiste el payload en **MariaDB**, sirviéndolo en un dashboard web (`:8082`). Diseñado para procesar ráfagas de eventos con baja latencia y sin degradación del servicio.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case02 up -d      # levanta receptor Go + MariaDB + n8n
python hub.py ejecutar 02-python-to-go      # dispara el emisor Python
```

Dashboard: [`http://localhost:8082`](http://localhost:8082)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
