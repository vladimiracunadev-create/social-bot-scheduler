# 🧩 Caso 10: ☕ Java (Spring Boot) -> 🌉 n8n -> 🟣 Kotlin (Ktor)

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Language: Java](https://img.shields.io/badge/Language-Java%2021-007396?logo=openjdk&logoColor=white)](https://openjdk.org/)
[![Language: Kotlin](https://img.shields.io/badge/Language-Kotlin-7F52FF?logo=kotlin&logoColor=white)](https://kotlinlang.org/)
[![Database: H2 / Postgres](https://img.shields.io/badge/Database-H2%20%7C%20Postgres-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Este directorio contiene únicamente el scaffolding y la documentación de diseño. El código de origen y destino aún no existe.

Cobertura del ecosistema **JVM** — el hueco más grande de la matriz tecnológica actual. Demuestra interoperabilidad entre el stack enterprise tradicional (**Spring Boot**) y el moderno (**Ktor + Kotlin Coroutines**).

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `OrderPublisher.java` (Spring Boot 3.x con `RestTemplate` o `WebClient`)
2. **🌉 Puente**: **n8n** (Webhook + transformación + retry)
3. **📥 Destino**: `OrderReceiver.kt` (Ktor server con corrutinas)
4. **📁 Persistencia**: **PostgreSQL** vía `Exposed` ORM o JDBC

---

## 🎯 Objetivos didácticos

- Mostrar cómo un servicio JVM "pesado" (Spring) se integra con uno "ligero" (Ktor) sin compartir JVM.
- Contrastar el modelo bloqueante de Spring MVC con el no-bloqueante de Ktor + corrutinas.
- Demostrar serialización JSON con Jackson (Java) y kotlinx.serialization (Kotlin).

---

## 📋 TODO de implementación

- [ ] Dockerfile multi-stage para Spring Boot (JRE 21 slim).
- [ ] Dockerfile multi-stage para Ktor (GraalVM native-image opcional).
- [ ] Workflow n8n `case10-java-kotlin.json`.
- [ ] Healthchecks + readiness probes.
- [ ] Tests de integración con Testcontainers.
- [ ] Perfil `case10` en `docker-compose.yml`.
- [ ] Dashboard Apache en `apache/case10/`.

---

*Pendiente — parte del roadmap v5.0.*
