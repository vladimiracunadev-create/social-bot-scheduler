# 🧩 Caso 18: ⚡ Zig -> 🌉 n8n -> 💎 Crystal -> 🕸️ Neo4j

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Language: Zig](https://img.shields.io/badge/Language-Zig-F7A41D?logo=zig&logoColor=white)](https://ziglang.org/)
[![Language: Crystal](https://img.shields.io/badge/Language-Crystal-000000?logo=crystal&logoColor=white)](https://crystal-lang.org/)
[![Database: Neo4j](https://img.shields.io/badge/Database-Neo4j-008CC1?logo=neo4j&logoColor=white)](https://neo4j.com/)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño.

Caso "exótico" de la matriz: dos **lenguajes emergentes** sin GC (Zig) o con sintaxis Ruby + tipado estático (Crystal), conectados a una **base de grafos** para modelar relaciones complejas.

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `publisher.zig` — binario nativo ultraligero con cliente HTTP propio.
2. **🌉 Puente**: **n8n** — webhook estándar.
3. **📥 Destino**: `server.cr` (Crystal + `kemal` framework) — modela y persiste nodos/aristas.
4. **📁 Persistencia**: **Neo4j 5.x** con queries Cypher.

---

## 🎯 Objetivos didácticos

- Zig: gestión manual de memoria sin GC, comptime, cross-compilation trivial.
- Crystal: rendimiento similar a C con DX similar a Ruby; compile-time type checking.
- Neo4j: cuándo el modelo de grafos vence al relacional (recomendaciones, fraude, redes sociales).
- Cypher: pattern-matching declarativo `MATCH (a)-[:KNOWS]->(b)`.

---

## ⚠️ Consideraciones operacionales

- Zig en alpha (v0.11+); breaking changes frecuentes → fijar versión exacta.
- Crystal aún sin Windows production-ready → solo Linux/macOS containers.
- Neo4j Community Edition: 1 sola DB activa; usar Enterprise para multi-tenant.

---

## 📋 TODO de implementación

- [ ] `build.zig` con dependencias mínimas.
- [ ] `shard.yml` para Crystal con `crystal-lang/crystal-db` driver.
- [ ] Schema Cypher con constraints y índices.
- [ ] Workflow n8n `case18-graph.json`.
- [ ] Dashboard con Neo4j Browser embebido.
- [ ] Perfil `case18` en `docker-compose.yml`.

---

*Pendiente — parte del backlog exploratorio v5.0+.*
