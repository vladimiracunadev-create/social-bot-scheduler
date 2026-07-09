# 🧩 Caso 19: #️⃣ F# (.NET) → 🌉 n8n → 🍀 Clojure (Ring) + XTDB

[![Status: Pendiente](https://img.shields.io/badge/Status-Pendiente_de_verificaci%C3%B3n-yellow.svg)]()
[![Language: F#](https://img.shields.io/badge/Language-F%23-378BBA?logo=dotnet&logoColor=white)](https://fsharp.org/)
[![Language: Clojure](https://img.shields.io/badge/Language-Clojure-5881D8?logo=clojure&logoColor=white)](https://clojure.org/)
[![Database: XTDB](https://img.shields.io/badge/Database-XTDB%20(bitemporal)-63B132)](https://xtdb.com/)

Paradigma **funcional puro** multi-runtime: emisor **F#** (.NET, funcional-first) y receptor **Clojure** (Lisp sobre la JVM) con **Ring**, persistiendo en **XTDB** — una base de datos **bitemporal e inmutable** embebida in-process.

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/Publisher.fs`: emisor F# (.NET 9) que reenvía los posts vencidos al webhook de n8n con `HttpClient`.
2. **🌉 Puente** — **n8n**: guardrails canónicos (fingerprint → circuit breaker → idempotencia → HTTP con reintentos → DLQ).
3. **📥 Destino** — `dest/src/receiver/core.clj`: receptor **Clojure/Ring** que cumple el contrato REST del laboratorio.
4. **📁 Persistencia** — **XTDB 1.24** embebida in-process (nodo in-memory): cada `put` es una versión inmutable, consultable con **Datalog**.

> [!NOTE]
> XTDB corre **dentro del proceso** del receptor Clojure (como Mnesia en el caso 11): no hay contenedor de base de datos separado. Es **bitemporal** — versiona por tiempo de validez y de transacción.

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case19 up -d      # sólo el receptor Clojure (XTDB embebida)
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `dest-clojure-19` | Clojure/Ring + XTDB + dashboard | **8099** |

- **Dashboard del caso**: <http://localhost:8099>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-19**.

---

## 🎯 Objetivos didácticos

- **Funcional puro en dos runtimes**: F# (.NET) y Clojure (JVM).
- **XTDB bitemporal**: inmutabilidad, historial de versiones, consultas Datalog.
- **BD embebida**: persistencia sin servicio externo, en el proceso de la app.

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Puerto `8099` = `8080 + 19` (regla canónica, ver [docs/PORTS.md](../../docs/PORTS.md)).
- Bind a `127.0.0.1`; el receptor valida `id`/`text` (→ HTTP 422).
- Nodo XTDB in-memory (los datos no persisten entre reinicios); en producción se usarían módulos con RocksDB/Kafka.

---

## 🚧 Estado

**Pendiente de verificación end-to-end.** El código y el scaffolding están completos (emisor F#, receptor Clojure/Ring + XTDB, workflow n8n) y se corrigió el bug de arranque AOT, pero el caso **aún no ha sido validado con Docker** (build + boot + health) como los otros 19 casos del laboratorio. Parte del **Lote 3** del roadmap v5.0 → v4.7; queda como único caso pendiente hasta completar su verificación.
