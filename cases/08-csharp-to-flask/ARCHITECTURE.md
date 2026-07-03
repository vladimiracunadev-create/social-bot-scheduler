# 📐 Arquitectura — Caso 08: 🟣 C# (.NET) → 🌉 n8n → 🌶️ Flask

[![Origen: C# .NET](https://img.shields.io/badge/Origen-C%23%20.NET%208.0-512BD4?logo=dotnet&logoColor=white)](https://learn.microsoft.com/en-us/dotnet/csharp/)
[![Destino: Flask](https://img.shields.io/badge/Destino-Flask%20%2F%20Python-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Persistencia: SQL Server](https://img.shields.io/badge/Persistencia-SQL%20Server%202022-CC2927?logo=microsoft-sql-server&logoColor=white)](https://www.microsoft.com/sql-server/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor corporativo de alto rendimiento en **C# / .NET 8.0** que despacha vía **HttpClient** hacia un receptor liviano en **Flask/Jinja2**, orquestado por **n8n** con guardrails de resiliencia (idempotencia, circuit breaker, DLQ) y persistencia transaccional en **SQL Server**.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `08` |
| **Origen** | C# / .NET 8.0 — [`origin/Program.cs`](origin/Program.cs) |
| **Puente** | n8n — [`case-08-csharp-to-flask.json`](../../n8n/workflows/case-08-csharp-to-flask.json) |
| **Destino** | Flask (Python) sobre Jinja2 — [`dest/app.py`](dest/app.py) |
| **Persistencia** | SQL Server 2022 |
| **Puerto (dashboard)** | [`http://localhost:8088`](http://localhost:8088) |
| **Perfil Docker** | `case08` |
| **Guardrails** | Idempotencia · Circuit Breaker · Dead Letter Queue |

---

## 🗺️ Diagrama de arquitectura

```mermaid
flowchart LR
    subgraph ORIGIN["🟣 ORIGEN · C# / .NET"]
        A[posts / objetos tipados] --> B{Program.cs<br/>System.Text.Json}
    end

    subgraph BRIDGE["🌉 PUENTE · n8n + Guardrails"]
        C((Webhook)) --> IDEM{Idempotencia<br/>fingerprint}
        IDEM -- duplicado --> DISCARD[200 OK · descarta]
        IDEM -- nuevo --> CB{Circuit<br/>Breaker}
        CB -- cerrado --> FWD[HTTP forward]
        CB -- abierto --> DLQ[[Dead Letter Queue]]
    end

    subgraph DEST["🌶️ DESTINO · Flask / Python"]
        FWD --> H[app.py]
        H --> DB[(SQL Server 2022)]
        DB --> DASH[Dashboard :8088]
    end

    B -- POST JSON --> C
    FWD -. error .-> DLQ

    classDef origin fill:#512BD4,stroke:#2c1873,color:#fff
    classDef bridge fill:#EA4B71,stroke:#8c1c38,color:#fff
    classDef dest fill:#000000,stroke:#000000,color:#fff
    classDef db fill:#CC2927,stroke:#7a1817,color:#fff
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
    participant Bot as 🟣 Program.cs
    participant N8N as 🌉 n8n
    participant Flask as 🌶️ app.py
    participant DB as 🗄️ SQL Server

    Bot->>Bot: Serializa objetos tipados (System.Text.Json)
    Bot->>N8N: POST /webhook (JSON del post)
    N8N->>N8N: Idempotencia (fingerprint)
    alt Duplicado
        N8N-->>Bot: 200 OK (descartado)
    else Nuevo
        N8N->>N8N: Circuit Breaker (estado)
        alt Breaker cerrado
            N8N->>Flask: HTTP forward del payload
            Flask->>DB: INSERT post (transaccional)
            DB-->>Flask: OK
            Flask-->>N8N: 200 + registro
            N8N-->>Bot: 200 OK
        else Breaker abierto / error
            N8N->>N8N: Enruta a Dead Letter Queue
            N8N-->>Bot: 5xx (reintento posterior)
        end
    end
```

---

## 🧩 Componentes

### 🟣 Origen — .NET Enterprise Dispatcher

- `Program.cs` define objetos anónimos tipados, los **serializa con System.Text.Json** y los despacha vía **HttpClient** hacia el webhook de n8n.
- Uso de inyección de dependencias y clientes HTTP optimizados para rendimiento masivo del ecosistema corporativo de Microsoft .NET.

### 🌉 Puente — n8n

- Recibe el webhook, aplica **idempotencia** (descarta duplicados por fingerprint), pasa por el **Circuit Breaker** con política de reintentos (3 intentos, intervalo 1s) y reenvía al destino. Los fallos se enrutan a la **Dead Letter Queue** para auditoría y recuperación.

### 🌶️ Destino — Flask / Python

- `app.py` recibe el payload con **Flask**, lo procesa de forma asíncrona y lo persiste en **SQL Server 2022**, garantizando la integridad relacional transaccional. El motor de plantillas **Jinja2** lo sirve en un dashboard web (`:8088`).

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case08 up -d          # levanta receptor Flask + SQL Server + n8n
python hub.py ejecutar 08-csharp-to-flask       # dispara el emisor C# / .NET
```

Dashboard: [`http://localhost:8088`](http://localhost:8088)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
