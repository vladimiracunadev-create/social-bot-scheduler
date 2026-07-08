# 📐 Arquitectura — Caso 20: 🍎 Swift → 🌉 n8n → 🎯 Dart (Shelf) + 🔥 Firestore emulator

[![Origen: Swift](https://img.shields.io/badge/Origen-Swift-FA7343?logo=swift&logoColor=white)](https://www.swift.org/)
[![Destino: Dart](https://img.shields.io/badge/Destino-Dart%2FShelf-0175C2?logo=dart&logoColor=white)](https://dart.dev/)
[![Persistencia: Firestore](https://img.shields.io/badge/Persistencia-Firestore%20emulator-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com/docs/emulator-suite)
[![Puente: n8n](https://img.shields.io/badge/Puente-n8n-EA4B71?logo=n8n&logoColor=white)](https://n8n.io/)

> Stack mobile-backend server-side: emisor **Swift** (Linux) y receptor **Dart/Shelf** que persiste en el **emulador de Firestore** vía su API REST v1. Firebase local, sin nube.

---

## 🧭 Ficha técnica

| Atributo | Valor |
| :--- | :--- |
| **ID** | `20` |
| **Origen** | Swift (Linux) — [`origin/Sources/Publisher/main.swift`](origin/Sources/Publisher/main.swift) |
| **Puente** | n8n — [`case-20-swift-to-dart.json`](../../n8n/workflows/case-20-swift-to-dart.json) |
| **Destino** | Dart / Shelf (AOT) — [`dest/bin/server.dart`](dest/bin/server.dart) |
| **Persistencia** | Firestore (Firebase Emulator Suite) |
| **Puerto (dashboard)** | [`http://localhost:8100`](http://localhost:8100) |
| **Perfil Docker** | `case20` |

---

## 🗺️ Diagrama de arquitectura

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'26px','fontFamily':'Segoe UI, Arial, sans-serif'},'flowchart':{'useMaxWidth':true,'htmlLabels':false,'nodeSpacing':55,'rankSpacing':70,'padding':16,'diagramPadding':16}}%%
flowchart TB
    subgraph ORIGIN["ORIGEN - Swift (Linux)"]
        S["main.swift"]
    end

    subgraph BRIDGE["PUENTE - n8n + Guardrails"]
        C(["Webhook"]) --> IDEM{"Idempotencia + circuit breaker"}
        IDEM -->|nuevo| FWD["HTTP forward + reintentos"]
        FWD -.->|error| DLQ["Dead Letter Queue (/errors)"]
    end

    subgraph DEST["DESTINO - Dart/Shelf + Firestore"]
        FWD --> D["server.dart (Shelf)"]
        D -->|REST v1 PATCH/GET| DB[("Firestore emulator")]
        DB --> DASH["Dashboard :8100"]
    end

    S -->|POST JSON| C

    classDef origin fill:#FA7343,stroke:#333,color:#fff
    classDef bridge fill:#EA4B71,stroke:#333,color:#fff
    classDef dest fill:#0175C2,stroke:#333,color:#fff
    classDef db fill:#FFCA28,stroke:#333,color:#000
    class S origin
    class C,IDEM,FWD,DLQ bridge
    class D,DASH dest
    class DB db
```

---

## 🔁 Diagrama de secuencia (ciclo de una publicación)

```mermaid
%%{init: {'theme':'base','themeVariables':{'fontSize':'24px','fontFamily':'Segoe UI, Arial, sans-serif'},'sequence':{'useMaxWidth':true,'actorFontSize':22,'messageFontSize':20,'noteFontSize':18,'actorMargin':90,'boxMargin':16,'width':180}}}%%
sequenceDiagram
    autonumber
    participant SW as main.swift (Swift)
    participant N8N as n8n
    participant DART as Dart/Shelf
    participant FS as Firestore emulator

    SW->>N8N: POST /webhook (post vencido)
    N8N->>N8N: Circuit breaker + idempotencia
    N8N->>DART: HTTP POST /webhook (reintentos x3)
    DART->>FS: PATCH /v1/.../social_posts/{id} (upsert)
    FS-->>DART: 200 documento
    DART-->>N8N: 200 OK
    Note over DART,FS: GET /logs -> GET /v1/.../social_posts -> ordena por created_at desc
```

---

## 🧩 Componentes

### 🍎 Origen — Swift (Linux)

- `origin/Sources/Publisher/main.swift` reenvía los posts vencidos a n8n con `URLSession` (Foundation). Swift Package Manager, binario nativo.

### 🌉 Puente — n8n

- Guardrails canónicos: fingerprint → circuit breaker → idempotencia → HTTP forward con reintentos → DLQ.

### 🎯 Destino — Dart/Shelf + Firestore

- `dest/bin/server.dart` (Shelf, compilado AOT) traduce el contrato REST a la API REST v1 de Firestore: `PATCH` para upsert, `GET` para listar. Documentos con `fields` tipados.

---

## ▶️ Cómo levantarlo

```bash
docker-compose --profile case20 up -d          # emulador Firestore + receptor Dart
```

Dashboard: [`http://localhost:8100`](http://localhost:8100)

---

## 🔗 Enlaces

- 📄 [README del caso](README.md)
- 🗺️ [Arquitectura global del laboratorio](../../docs/ARCHITECTURE.md)
- 🛡️ [Guardrails de resiliencia](../../docs/GUARDRAILS.md)
- 🧩 [Índice de casos](../../docs/CASES_INDEX.md)

---

*Diagramas en [Mermaid](https://mermaid.js.org/) — se renderizan nativamente en GitHub. Parte de **Social Bot Scheduler**.*
