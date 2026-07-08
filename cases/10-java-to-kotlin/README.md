# 🧩 Caso 10: ☕ Java (Spring Boot) → 🌉 n8n → 🟣 Kotlin (Ktor) + PostgreSQL

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Language: Java](https://img.shields.io/badge/Language-Java%2021-007396?logo=openjdk&logoColor=white)](https://openjdk.org/)
[![Language: Kotlin](https://img.shields.io/badge/Language-Kotlin-7F52FF?logo=kotlin&logoColor=white)](https://kotlinlang.org/)
[![Database: PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

Cobertura del ecosistema **JVM** — el hueco más grande de la matriz original. Contrasta el stack enterprise **bloqueante** (Spring Boot MVC) con el moderno **no-bloqueante** (Ktor + corrutinas sobre Netty), persistiendo en **PostgreSQL**.

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/src/main/java/socialbot/OrderPublisher.java`: app **Spring Boot** (MVC + `RestTemplate`) que lee `posts.json` y reenvía los posts vencidos al webhook de n8n.
2. **🌉 Puente** — **n8n**: guardrails canónicos (fingerprint → circuit breaker → idempotencia → HTTP con reintentos → DLQ).
3. **📥 Destino** — `dest/src/main/kotlin/Application.kt`: servidor **Ktor** (Netty, corrutinas) que expone el contrato REST y persiste vía JDBC.
4. **📁 Persistencia** — **PostgreSQL 16**: tabla `social_posts` con `INSERT ... ON CONFLICT` (idempotente).

> [!NOTE]
> El receptor se empaqueta como **fat-jar** (plugin Shadow) sobre un runtime `eclipse-temurin:21-jre-alpine`.

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case10 up -d      # PostgreSQL + receptor Ktor
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `db-postgres-10` | PostgreSQL 16 | interno |
| `dest-ktor-10` | Ktor + dashboard | **8090** |

- **Dashboard del caso**: <http://localhost:8090>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-10**.

### Probar el emisor Spring Boot (opcional)

```bash
cd cases/10-java-to-kotlin/origin
WEBHOOK_URL=http://localhost:5678/webhook/social-bot-scheduler-ktor gradle bootRun
```

---

## 🎯 Objetivos didácticos

- **Bloqueante vs no-bloqueante**: Spring MVC (un hilo por request) frente a Ktor (corrutinas sobre event-loop).
- **Interoperabilidad JVM**: dos runtimes JVM independientes hablando por HTTP, sin compartir JVM.
- **PostgreSQL idempotente**: `ON CONFLICT (id) DO UPDATE` a nivel de BD.

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Puerto `8090` = `8080 + 10` (regla canónica, ver [docs/PORTS.md](../../docs/PORTS.md)).
- Bind a `127.0.0.1`; el receptor valida `id`/`text` (→ HTTP 422) como defensa en profundidad.

---

## ✅ Estado

Implementado y verificado (build + boot + health). Parte del **Lote 2** del roadmap v5.0 → v4.6.
