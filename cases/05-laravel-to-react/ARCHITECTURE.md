# 📐 Arquitectura — Caso 05: 🎼 Laravel → 🌉 n8n → ⚛️ React

[![Origen: Laravel](https://img.shields.io/badge/Origen-Laravel%208.2-FF2D20?logo=laravel&logoColor=white)](https://laravel.com/)
[![Destino: React](https://img.shields.io/badge/Destino-React%20%2F%20Node-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Persistencia: MongoDB](https://img.shields.io/badge/Persistencia-MongoDB%206.0-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor de automatización en **Laravel/Artisan (PHP Streams)** que publica hacia un receptor fullstack **React SPA + Node/Express**, orquestado por **n8n** con guardrails de resiliencia (idempotencia, circuit breaker, DLQ) y persistencia documental en **MongoDB**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `05` |
| **Origen** | Laravel 8.2 (PHP · Artisan) — [`origin/ArtisanPost.php`](origin/ArtisanPost.php) |
| **Puente** | n8n — [`case-05-laravel-to-react.json`](../../n8n/workflows/case-05-laravel-to-react.json) |
| **Destino** | React SPA + Node/Express — [`dest/server.js`](dest/server.js) |
| **Persistencia** | MongoDB 6.0 |
| **Puerto (dashboard)** | [`http://localhost:8085`](http://localhost:8085) |
| **Perfil Docker** | `case05` |
| **Guardrails** | Idempotencia · Circuit Breaker · Dead Letter Queue |

---

## 🗺️ Diagrama de arquitectura

```mermaid
flowchart LR
    subgraph ORIGIN["ORIGEN - Laravel"]
        B["ArtisanPost.php"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia (fingerprint)"}
        IDEM -->|duplicado| DISCARD["200 OK - descarta"]
        IDEM -->|nuevo| CBK{"Circuit Breaker"}
        CBK -->|cerrado| FWD["HTTP forward"]
        CBK -->|abierto| DLQ["Dead Letter Queue"]
    end

    subgraph DEST["DESTINO - React / Node"]
        FWD --> H["server.js"]
        H --> DB[("MongoDB 6.0")]
        DB --> DASH["Dashboard :8085"]
    end

    B -->|POST JSON| C
    FWD -.->|error| DLQ

    classDef origin fill:#FF2D20,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#61DAFB,stroke:#333,color:#fff
    classDef db fill:#47A248,stroke:#333,color:#fff
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
    participant Bot as ArtisanPost.php (Laravel)
    participant N8N as n8n
    participant Dest as server.js (React / Node)
    participant DB as MongoDB 6.0

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

### 🎼 Origen — Laravel Artisan Simulator

- Clase que imita un `Console Command` de Artisan: extrae las publicaciones pendientes de `posts.json` y las despacha hacia el webhook de n8n.
- Emplea **PHP Streams** para envíos HTTP eficientes y ligeros.

### 🌉 Puente — n8n

- Recibe el webhook, aplica **idempotencia** (descarta duplicados por fingerprint), pasa por el **Circuit Breaker** y reenvía al destino. Los fallos se enrutan a la **Dead Letter Queue**.

### ⚛️ Destino — React / Node Fullstack

- `server.js` (Node/Express) recibe el post, lo valida y lo persiste en **MongoDB** preservando su estructura documental. La **Single Page Application** de React (`:8085`) visualiza los posts con actualizaciones periódicas y una estética profesional.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case05 up -d       # levanta receptor React/Node + MongoDB + n8n
python hub.py ejecutar 05-laravel-to-react   # dispara el emisor Laravel
```

Dashboard: [`http://localhost:8085`](http://localhost:8085)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
