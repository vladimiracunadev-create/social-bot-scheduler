# 📐 Arquitectura — Caso 06: 🐹 Go → 🌉 n8n → 🎵 Symfony

[![Origen: Go](https://img.shields.io/badge/Origen-Go%201.21-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Destino: Symfony](https://img.shields.io/badge/Destino-Symfony%207%20%2F%20PHP%208.2-000000?logo=symfony&logoColor=white)](https://symfony.com/)
[![Persistencia: Redis](https://img.shields.io/badge/Persistencia-Redis%207-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor concurrente de alta velocidad en **Go** que publica hacia un receptor empresarial en **Symfony 7 / PHP 8.2**, orquestado por **n8n** con guardrails de resiliencia (idempotencia, circuit breaker, DLQ) y persistencia ultra-rápida en **Redis**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `06` |
| **Origen** | Go 1.21 — emisor concurrente — [`origin/main.go`](origin/main.go) |
| **Puente** | n8n — [`case-06-go-to-symfony.json`](../../n8n/workflows/case-06-go-to-symfony.json) |
| **Destino** | Symfony 7 / PHP 8.2 sobre Apache 2.4 — [`dest/index.php`](dest/index.php) |
| **Persistencia** | Redis 7 (In-Memory Key-Value) |
| **Puerto (dashboard)** | [`http://localhost:8086`](http://localhost:8086) |
| **Perfil Docker** | `case06` |
| **Guardrails** | Idempotencia · Circuit Breaker · Dead Letter Queue |

---

## 🗺️ Diagrama de arquitectura

```mermaid
flowchart LR
    subgraph ORIGIN["🐹 ORIGEN · Go"]
        A[posts.json] --> B{main.go<br/>concurrente}
    end

    subgraph BRIDGE["🌉 PUENTE · n8n + Guardrails"]
        C((Webhook)) --> IDEM{Idempotencia<br/>fingerprint}
        IDEM -- duplicado --> DISCARD[200 OK · descarta]
        IDEM -- nuevo --> CB{Circuit<br/>Breaker}
        CB -- cerrado --> FWD[HTTP forward]
        CB -- abierto --> DLQ[[Dead Letter Queue]]
    end

    subgraph DEST["🎵 DESTINO · Symfony / PHP"]
        FWD --> H[index.php]
        H --> DB[(Redis 7)]
        DB --> DASH[Dashboard :8086]
    end

    B -- POST JSON --> C
    FWD -. error .-> DLQ

    classDef origin fill:#00ADD8,stroke:#006680,color:#fff
    classDef bridge fill:#EA4B71,stroke:#8c1c38,color:#fff
    classDef dest fill:#000000,stroke:#000000,color:#fff
    classDef db fill:#DC382D,stroke:#821f18,color:#fff
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
    participant Bot as 🐹 main.go
    participant N8N as 🌉 n8n
    participant SF as 🎵 index.php
    participant DB as 🔴 Redis

    Bot->>Bot: Lee posts.json + dispara goroutines
    Bot->>N8N: POST /webhook (JSON del post)
    N8N->>N8N: Idempotencia (fingerprint)
    alt Duplicado
        N8N-->>Bot: 200 OK (descartado)
    else Nuevo
        N8N->>N8N: Circuit Breaker (estado)
        alt Breaker cerrado
            N8N->>SF: HTTP forward del payload
            SF->>DB: SET post
            DB-->>SF: OK
            SF-->>N8N: 200 + registro
            N8N-->>Bot: 200 OK
        else Breaker abierto / error
            N8N->>N8N: Enruta a Dead Letter Queue
            N8N-->>Bot: 5xx (reintento posterior)
        end
    end
```

---

## 🧩 Componentes

### 🐹 Origen — Go Concurrent Dispatcher

- Carga `posts.json`, calcula los tiempos de envío y **dispara las peticiones HTTP de forma concurrente** hacia el webhook de n8n.
- Optimizado para un consumo de memoria inferior a los 20 MB durante ráfagas de tráfico.

### 🌉 Puente — n8n

- Recibe el webhook, aplica **idempotencia** (descarta duplicados por fingerprint), pasa por el **Circuit Breaker** y reenvía al destino. Los fallos se enrutan a la **Dead Letter Queue**.

### 🎵 Destino — Symfony / PHP

- `index.php` (Symfony 7 sobre Apache 2.4) parsea el payload entrante, lo persiste en **Redis** para acceso instantáneo y lo sirve en un dashboard de administración (`:8086`) para monitorizar los flujos de datos.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case06 up -d      # levanta receptor Symfony + Redis + n8n
python hub.py ejecutar 06-go-to-symfony     # dispara el emisor Go
```

Dashboard: [`http://localhost:8086`](http://localhost:8086)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
