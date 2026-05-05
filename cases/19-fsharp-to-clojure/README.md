# 🧩 Caso 19: #️⃣ F# (.NET) -> 🌉 n8n -> 🍀 Clojure -> ⏳ XTDB

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Language: F#](https://img.shields.io/badge/Language-F%23-378BBA?logo=dotnet&logoColor=white)](https://fsharp.org/)
[![Language: Clojure](https://img.shields.io/badge/Language-Clojure-5881D8?logo=clojure&logoColor=white)](https://clojure.org/)
[![Database: XTDB](https://img.shields.io/badge/Database-XTDB-1A0033?logo=database&logoColor=white)](https://xtdb.com/)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño.

Caso de **paradigma funcional puro** con persistencia **inmutable y bitemporal**: dos lenguajes funcionales sobre runtimes muy distintos (.NET y JVM) escribiendo en una DB que jamás sobrescribe datos.

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `Publisher.fs` (F# en .NET 9) — emisión con records inmutables y discriminated unions.
2. **🌉 Puente**: **n8n** — webhook + transformación.
3. **📥 Destino**: `server.clj` (Clojure + Ring + Reitit) — handler funcional puro.
4. **📁 Persistencia**: **XTDB 2.0** — DB bitemporal con SQL + Datalog queries.

---

## 🎯 Objetivos didácticos

- Programación funcional pura: inmutabilidad, funciones de orden superior, ADTs.
- F# vs OCaml: ML-family adaptado a .NET, interop total con C#.
- Clojure: macros, REPL-driven development, `core.async`.
- XTDB bitemporal: cada hecho tiene `valid_time` (cuándo ocurrió) y `system_time` (cuándo se registró). Auditoría completa "as-of-then" y "as-of-now".

---

## ⚠️ Consideraciones operacionales

- XTDB 2.0 requiere ≥4 GB RAM y backend JDBC (Postgres) o Kafka.
- Clojure cold-start lento (~5-10s) → usar `clj` con prepped JAR.
- F# en Linux containers: imagen `mcr.microsoft.com/dotnet/sdk:9.0`.

---

## 📋 TODO de implementación

- [ ] Proyecto F# con `Paket` o `dotnet add package`.
- [ ] `deps.edn` Clojure con Ring + Reitit + XTDB client.
- [ ] Schema y ejemplos de queries Datalog vs SQL bitemporal.
- [ ] Workflow n8n `case19-functional.json`.
- [ ] Demo de query "as-of" mostrando estado histórico.
- [ ] Perfil `case19` en `docker-compose.yml`.

---

*Pendiente — parte del backlog exploratorio v5.0+.*
