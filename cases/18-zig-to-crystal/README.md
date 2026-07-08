# 🧩 Caso 18: ⚡ Zig → 🌉 n8n → 💎 Crystal (Kemal) + Neo4j

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Language: Zig](https://img.shields.io/badge/Language-Zig-F7A41D?logo=zig&logoColor=black)](https://ziglang.org/)
[![Language: Crystal](https://img.shields.io/badge/Language-Crystal-000000?logo=crystal&logoColor=white)](https://crystal-lang.org/)
[![Database: Neo4j](https://img.shields.io/badge/Database-Neo4j-018BFF?logo=neo4j&logoColor=white)](https://neo4j.com/)

Cobertura de **lenguajes emergentes**: **Zig** (lenguaje de sistemas sin recolector de basura) como emisor y **Crystal** (sintaxis tipo Ruby, rendimiento compilado LLVM) con **Kemal** como receptor, persistiendo en la base de **grafos Neo4j**.

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/src/main.zig`: emisor **Zig** que reenvía los posts vencidos a n8n con el cliente HTTP de la stdlib (`std.http.Client.fetch`). Sin GC, gestión de memoria explícita.
2. **🌉 Puente** — **n8n**: guardrails canónicos (fingerprint → circuit breaker → idempotencia → HTTP con reintentos → DLQ).
3. **📥 Destino** — `dest/src/app.cr`: receptor **Crystal/Kemal** que persiste cada post como un nodo `(:Post)` del grafo.
4. **📁 Persistencia** — **Neo4j 5**: se accede vía su **API HTTP transaccional** (`/db/neo4j/tx/commit`) con **Cypher** (`MERGE`), sin driver Bolt nativo.

> [!NOTE]
> Neo4j arranca una JVM y tarda ~2-3 min la primera vez. El receptor Crystal reintenta la conexión hasta que el grafo está listo; el `healthcheck` del compose usa un chequeo TCP ligero (cypher-shell excedería cualquier timeout por el arranque de su propia JVM).

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case18 up -d      # Neo4j + receptor Crystal (Neo4j tarda en arrancar)
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `neo4j-18` | Neo4j 5 (grafo) | interno |
| `dest-crystal-18` | Crystal/Kemal + dashboard | **8098** |

- **Dashboard del caso**: <http://localhost:8098>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-18**.

---

## 🎯 Objetivos didácticos

- **Lenguajes sin GC / emergentes**: Zig (control explícito) y Crystal (Ruby-like compilado).
- **Base de grafos**: modelar posts como nodos `(:Post)` y consultarlos con **Cypher**.
- **Integración sin driver nativo**: hablar con Neo4j por su API HTTP transaccional.

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Puerto `8098` = `8080 + 18` (regla canónica, ver [docs/PORTS.md](../../docs/PORTS.md)).
- Bind a `127.0.0.1`; el receptor valida `id`/`text` (→ HTTP 422).
- Neo4j es el servicio más pesado del caso (~1 GB); evita levantarlo junto a los otros casos pesados si tienes <8 GB de RAM.

---

## ✅ Estado

Implementado y verificado (build + boot + health). Parte del **Lote 2** del roadmap v5.0 → v4.6.
