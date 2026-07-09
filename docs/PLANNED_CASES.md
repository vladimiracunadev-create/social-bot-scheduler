# 🚧 Casos Planificados (v5.0+)

> [!IMPORTANT]
> Este documento es el **single source of truth** para los casos del roadmap (IDs 10–20). Implementados: **11, 16, 17** (`v4.5.0`), **10, 12, 18** (`v4.6.0`), **15, 20** (`v4.7.0`) y **13, 14** (`v4.8.0`). Queda **sólo 1**: el caso **19**, con el código completo (bug de arranque AOT corregido) pero **pendiente de verificación end-to-end**. Cualquier referencia en otros documentos debe enlazar aquí.

Los casos 01–18 y 20 están plenamente operativos (todos menos el 19) — ver [CASES_INDEX.md](CASES_INDEX.md). El único caso reservado como **roadmap arquitectónico** que **no se levanta** desde `docker-compose.yml` es el **19** (no existe perfil `case19` aún); los casos 10–18 y 20 ya tienen su perfil operativo.

---

## 📋 Matriz del Roadmap (18 ya implementados — sólo el caso 19 pendiente)

Los casos **10–18 y 20 ya están implementados y operativos** con cifras de recursos **medidas** (ver [DOCKER_RESOURCES.md](DOCKER_RESOURCES.md) y [CASES_INDEX.md](CASES_INDEX.md)). El único caso que queda como roadmap es el **19**:

| ID | 📤 Origen | 🌉 Puente | 📥 Destino | 📁 Persistencia | Puerto | Δ Caso (est.) | Total con núcleo (est.) | Categoría |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **19** ⏳ pendiente | F# (.NET) | n8n | Clojure (Ring) | ⏳ XTDB | `8099` | ~1.5 GB | ~2.65 GB 🟡 | Funcional |

> [!IMPORTANT]
> Las cifras de los casos **10–18 y 20 ya están MEDIDAS** (imágenes reales, `deploy.resources` del `docker-compose.yml`) y viven en [DOCKER_RESOURCES.md](DOCKER_RESOURCES.md). Sólo el caso **19** conserva una **estimación** previa a su verificación end-to-end.
>
> Sólo resta implementar el caso **19**, que añadiría **~2.65 GB de RAM** sobre el `--profile full` actual.

---

## 🎯 Justificación por bloque

### Bloque A — Tier 1 (alta prioridad, alto impacto) — ✅ implementado
- **10–11**: cubrieron los runtimes JVM y BEAM, los dos huecos más grandes de la matriz original.
- **12**: caso "estrella 2026" — RAG es el patrón más demandado en entrevistas.
- **13**: introdujo streaming real (Kafka) y storage analítico (ClickHouse).
- **14**: primer caso BaaS de la matriz — solicitado expresamente.

### Bloque B — Tier 2 (cobertura técnica) — ✅ implementado
- **15**: protocolo binario gRPC + DB distribuida.
- **16**: dos enfoques GraphQL contrastados + series temporales.
- **17**: pub/sub asíncrono + IoT.

### Bloque C — Tier 3 (exploratorios / nicho)
- **18** ✅: lenguajes emergentes sin GC + grafos.
- **19** ⏳ (único pendiente): funcional puro multi-runtime + DB bitemporal — el siguiente y último caso a implementar.
- **20** ✅: stack mobile-backend con runtimes server-side de Swift/Dart.

---

## ⚠️ Implicaciones operacionales al implementar

- **RAM**: pasar de 19 → 20 casos (sólo el 19 pendiente) añade ~2 contenedores (F#/Clojure/XTDB). Estimación: +2.65 GB sobre el perfil `full`.
- **CI**: cada caso nuevo ejecutará healthchecks, idempotency tests, security scans → tiempo CI puede crecer 2×–3×.
- **Imágenes pesadas**: Swift Linux (~500 MB), Hasura (~300 MB), CockroachDB (~250 MB) requieren multi-stage builds agresivos.
- **Seguridad**: cada caso debe pasar por la auditoría de 8 capas existente (ver [SECURITY.md](../SECURITY.md)).

---

## 🔗 Cómo usar este documento

- Para **implementar el último caso pendiente (19)**: es el único que queda del roadmap (F#/Clojure/XTDB, puerto `8099`).
- Para **referenciar desde otra doc**: enlaza con `[Casos planificados](docs/PLANNED_CASES.md)`. No dupliques la tabla.
- Para **arrancar la implementación** de un caso: sigue el TODO interno del README de cada `cases/{ID}-*/README.md`.

---

*Última actualización: 2026-07-08 — Vladimir Acuña*
