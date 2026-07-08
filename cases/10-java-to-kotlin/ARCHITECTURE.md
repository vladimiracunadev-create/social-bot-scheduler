# 📐 Arquitectura — Caso 10: ☕ Java (Spring Boot) → 🌉 n8n → 🟣 Kotlin (Ktor) + PostgreSQL

[![Origen: Java](https://img.shields.io/badge/Origen-Java%2021-007396?logo=openjdk&logoColor=white)](https://openjdk.org/)
[![Destino: Ktor](https://img.shields.io/badge/Destino-Ktor-7F52FF?logo=kotlin&logoColor=white)](https://ktor.io/)
[![Persistencia: PostgreSQL](https://img.shields.io/badge/Persistencia-PostgreSQL-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Emisor **Spring Boot** (MVC bloqueante) que reenvía a **n8n**; el receptor **Ktor** (no-bloqueante, corrutinas) persiste en **PostgreSQL**. Demuestra la interoperabilidad entre dos runtimes JVM con modelos de concurrencia opuestos.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `10` |
| **Origen** | Java 21 / Spring Boot — [`origin/src/main/java/socialbot/OrderPublisher.java`](origin/src/main/java/socialbot/OrderPublisher.java) |
| **Puente** | n8n — [`case-10-java-to-kotlin.json`](../../n8n/workflows/case-10-java-to-kotlin.json) |
| **Destino** | Kotlin / Ktor (Netty) — [`dest/src/main/kotlin/Application.kt`](dest/src/main/kotlin/Application.kt) |
| **Persistencia** | PostgreSQL 16 (`social_posts`) |
| **Puerto (dashboard)** | [`http://localhost:8090`](http://localhost:8090) |
| **Perfil Docker** | `case10` |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}%%
flowchart TB
    subgraph ORIGIN["ORIGEN - Spring Boot (bloqueante)"]
        S["OrderPublisher.java"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia + circuit breaker"}
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - Ktor (no-bloqueante)"]
        FWD --> K["Application.kt (Netty + corrutinas)"]
        K --> DB[("PostgreSQL")]
        DB --> DASH["Dashboard :8090"]
    end

    S -->|POST JSON| C

    classDef origin fill:#007396,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#7F52FF,stroke:#333,color:#fff
    classDef db fill:#336791,stroke:#333,color:#fff
    class S origin
    class C,IDEM,FWD,DLQ bridge
    class K,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':90,'boxMargin':16,'width':180}}}%%
sequenceDiagram
    autonumber
    participant Spring as OrderPublisher (Spring)
    participant N8N as n8n
    participant Ktor as Ktor (corrutina)
    participant PG as PostgreSQL

    Spring->>N8N: POST /webhook (post vencido)
    N8N->>N8N: Circuit breaker + idempotencia
    alt Duplicado o circuito abierto
        N8N-->>Spring: 200 OK (descartado)
    else Nuevo
        N8N->>Ktor: HTTP POST /webhook (reintentos x3)
        Ktor->>PG: INSERT ... ON CONFLICT (idempotente)
        PG-->>Ktor: OK
        Ktor-->>N8N: 200 OK
        N8N-->>Spring: 200 OK
    end
    Note over Ktor,PG: El dashboard :8090 lee vía /logs (SELECT ... ORDER BY created_at)
```

---

## 🧩 Componentes

### ☕ Origen — Spring Boot (MVC bloqueante)

- `OrderPublisher.java` (`@SpringBootApplication` + `CommandLineRunner`) usa `RestTemplate` para reenviar los posts vencidos a n8n. Modelo de un hilo por request.

### 🌉 Puente — n8n

- Guardrails canónicos: fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ.

### 🟣 Destino — Ktor (no-bloqueante)

- `Application.kt` levanta Ktor sobre Netty; cada request se maneja en una **corrutina** suspendible. Persistencia vía JDBC directo con `INSERT ... ON CONFLICT`.
- Empaquetado como **fat-jar** (Shadow) sobre `eclipse-temurin:21-jre-alpine`.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case10 up -d          # PostgreSQL + receptor Ktor
```

Dashboard: [`http://localhost:8090`](http://localhost:8090)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
