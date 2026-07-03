# 📐 Arquitectura — Caso 01: 🐍 Python → 🌉 n8n → 🐘 PHP

[![Origen: Python](https://img.shields.io/badge/Origen-Python%203.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Destino: PHP](https://img.shields.io/badge/Destino-PHP%208.2%20%2F%20Apache-777BB4?logo=php&logoColor=white)](https://www.php.net/)
[![Persistencia: MySQL](https://img.shields.io/badge/Persistencia-MySQL%208.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor de automatización en **Python + Pydantic** que publica hacia un receptor web clásico en **PHP/Apache**, orquestado por **n8n** con guardrails de resiliencia (idempotencia, circuit breaker, DLQ) y persistencia en **MySQL**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `01` |
| **Origen** | Python 3.11 + Pydantic — [`origin/bot.py`](origin/bot.py) |
| **Puente** | n8n — [`case-01-python-to-php.json`](../../n8n/workflows/case-01-python-to-php.json) |
| **Destino** | PHP 8.2 sobre Apache 2.4 — [`dest/index.php`](dest/index.php) |
| **Persistencia** | MySQL 8.0 |
| **Puerto (dashboard)** | [`http://localhost:8081`](http://localhost:8081) |
| **Perfil Docker** | `case01` |
| **Guardrails** | Idempotencia · Circuit Breaker · Dead Letter Queue |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}}%%
flowchart TB
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

    subgraph DEST["DESTINO - PHP / Apache"]
        FWD --> H["index.php"]
        H --> DB[("MySQL 8.0")]
        DB --> DASH["Dashboard :8081"]
    end

    B -->|POST JSON| C
    FWD -.->|error| DLQ

    classDef origin fill:#3776AB,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#777BB4,stroke:#333,color:#fff
    classDef db fill:#4479A1,stroke:#333,color:#fff
    class B origin
    class C,IDEM,CBK,FWD,DLQ,DISCARD bridge
    class H,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':90,'boxMargin':16,'width':180}}}%%
sequenceDiagram
    autonumber
    participant Bot as bot.py (Python)
    participant N8N as n8n
    participant Dest as index.php (PHP / Apache)
    participant DB as MySQL 8.0

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

### 🐍 Origen — Python Bot

- Lee `posts.json`, **valida la estructura con Pydantic** y dispara hacia el webhook de n8n.
- Resiliencia en el envío (manejo de errores + logs locales de ejecución).

### 🌉 Puente — n8n

- Recibe el webhook, aplica **idempotencia** (descarta duplicados por fingerprint), pasa por el **Circuit Breaker** y reenvía al destino. Los fallos se enrutan a la **Dead Letter Queue**.

### 🐘 Destino — PHP / Apache

- `index.php` recibe el payload, lo persiste en **MySQL** y lo sirve en un dashboard web (`:8081`). Apache aplica los security headers del laboratorio (`Options -Indexes`, CSP, X-Frame-Options, etc.).

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case01 up -d      # levanta receptor PHP + MySQL + n8n
python hub.py ejecutar 01-python-to-php     # dispara el emisor Python
```

Dashboard: [`http://localhost:8081`](http://localhost:8081)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
