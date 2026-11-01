# 🔼 Mejoras de versión y remediación de CVE

> Documento **vivo**. El índice de abajo se regenera desde los 20 `cases/NN-*/security.yml` con `python scripts/build_upgrade_docs.py`.

Aquí está el detalle de cada cambio de versión del laboratorio: qué se movió, contra qué advisory, dónde quedó escrito y qué riesgo tiene. El README lleva el resumen; esto es el expediente.

---

## Índice de cambios

| Stack | Cambio | Casos | Advisories | Detalle |
| :--- | :--- | :--- | ---: | :--- |
| 🐹 | **Go 1.21 / 1.23 → 1.27** | 02, 03, 06, 13, 15 | 12 | [Ver documentación](upgrades/go.md) |
| 🟩 | **Node.js 20 → 24 LTS** | 03, 04, 05, 13, 14, 16, 17 | 31 | [Ver documentación](upgrades/nodejs.md) |
| 🐍 | **Python 3.11 → 3.13 (Debian 12 → 13)** | 01, 02, 04, 08, 09, 12, 15 | 15 | [Ver documentación](upgrades/python.md) |
| 🐘 | **PHP 8.2 → 8.4** | 01, 05, 06 | — | [Ver documentación](upgrades/php.md) |
| 💎 | **Ruby 3.2 → 3.4** | 07 | 4 | [Ver documentación](upgrades/ruby.md) |
| 🟦 | **.NET 6 / 9 → 10 (LTS)** | 08, 19 | — | [Ver documentación](upgrades/dotnet.md) |
| 🏔️ | **Alpine 3.20 → 3.23.7** | 02, 13, 15, 17, 18 | — | [Ver documentación](upgrades/alpine.md) |
| 🦀 | **Rust 1.83 → 1.99** | 07, 17 | — | [Ver documentación](upgrades/rust.md) |
| 💜 | **Erlang/OTP 27 → 28 · Elixir 1.17 → 1.18** | 11 | 3 | [Ver documentación](upgrades/beam.md) |
| 💠 | **Crystal 1.14 → 1.22** | 18 | — | [Ver documentación](upgrades/crystal.md) |
| 🧡 | **Swift 6.0 → 6.2** | 20 | — | [Ver documentación](upgrades/swift.md) |
| 🎯 | **Dart y Debian: fuera los tags flotantes** | 20 | — | [Ver documentación](upgrades/dart.md) |
| ☕ | **JVM: Temurin 21 se queda, Gradle 8.11 → 8.14** | 10, 19, 20 | 13 | [Ver documentación](upgrades/jvm.md) |
| 📦 | **pnpm 10 → 11: npm fuera del laboratorio** | 03, 04, 05, 13, 14, 16, 17, 20 | — | [Ver documentación](upgrades/pnpm.md) |
| ⚡ | **Zig 0.13: por qué NO se subió** | 18 | — | [Ver documentación](upgrades/zig.md) |

Cada página lleva: ventanas de soporte con gráfico, la justificación del cambio, la tabla de implementación fichero a fichero, las dependencias del stack con sus advisories, el riesgo de ruptura y las fuentes.

---

## Cómo se hace una subida de versión en este repositorio

Este documento **no es el registro de un release concreto**: es el procedimiento, y se
amplía con cada pase. El de abajo es el orden que se siguió y el que hay que seguir.

### 1. Inventariar lo que hay, no lo que se recuerda

```bash
# Imágenes base de cada caso
grep -rn "^FROM" --include=Dockerfile cases/ Dockerfile
grep -n "image:" docker-compose.yml

# Manifiestos de dependencias por ecosistema
find cases -name "go.mod" -o -name "package.json" -o -name "requirements.in" \
     -o -name "build.gradle.kts" -o -name "project.clj" -o -name "Cargo.toml" \
     -o -name "Gemfile" -o -name "rebar.config" -o -name "shard.yml" \
     -o -name "pubspec.yaml" | grep -v node_modules
```

### 2. Preguntar por la versión EXACTA, no por rangos

La consulta se hace con la versión que está escrita en el fichero, no con una
aproximación. Un rango oculta justo el caso que importa.

```bash
# Advisories de una versión concreta
curl -s https://api.osv.dev/v1/query -d '{
  "package": {"ecosystem": "npm", "name": "express"},
  "version": "4.18.2"
}'

# Fin de soporte del runtime
curl -s https://endoflife.date/api/nodejs.json
```

### 3. Elegir la versión destino con un criterio escrito

| Situación | Qué se hace |
| :--- | :--- |
| Runtime en EOL o con soporte activo cerrado | Se sube a una rama con soporte vigente |
| Dependencia con advisory abierto | Se sube al **menor** parche que cierra **todos** sus advisories |
| El advisory solo se corrige en un major nuevo | Se evalúa caso a caso y **se verifica el salto** |
| Major nuevo que rompe la API y **sin** advisory abierto | Se conserva el major y se documenta el por qué |

La última fila es la que más disciplina exige: subir de major sin un fallo que lo
justifique es cambio por el cambio, y en un laboratorio de 20 stacks el coste de una
ruptura es alto.

### 4. Comprobar que el tag existe ANTES de escribir el `FROM`

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  https://hub.docker.com/v2/repositories/library/node/tags/24-alpine/
```

Un `FROM` con un tag inventado falla en el build, no en la revisión.

### 5. Cerrar también las transitivas

La versión parcheada de una dependencia directa **sigue arrastrando** transitivas
vulnerables. Cada ecosistema tiene su mecanismo, y todos están en uso aquí:

| Ecosistema | Mecanismo | Dónde |
| :--- | :--- | :--- |
| npm / pnpm | `overrides` | `pnpm-workspace.yaml` de cada paquete |
| Gradle | propiedad del BOM | `ext["jackson-bom.version"]` |
| Leiningen | dependencia directa que pisa la transitiva | `project.clj` |
| Bundler | piso de versión explícito | `Gemfile` |
| pip | lock con hash recompilado | `requirements.in` → `requirements.txt` |

### 6. Registrar el cambio donde el guardrail lo vea

Cada caso lleva su `cases/NN-*/security.yml`. Toda entrada declara `from`, `to`,
`reason`, los `advisories` que cierra y **`applied_in`**: el fichero y el mecanismo
concretos. Lo que sigue vulnerable va en `open_findings`, nunca en `dependencies`.

```bash
python scripts/validate_security_manifests.py
```

El guardrail falla si el manifiesto va por delante del código, si cita un fichero que
no existe, si se reintroduce una versión declarada abandonada o si un hallazgo abierto
no dice qué lo bloquea.

### 7. Verificar lo que se pueda y declarar lo que no

```bash
# Node: lockfile + auditoría, por paquete
corepack enable && corepack prepare pnpm@11.2.2 --activate
pnpm install --lockfile-only && pnpm audit --prod --audit-level high

# Python: recompilar el lock con hashes y auditarlo
uv pip compile --upgrade --universal --generate-hashes --python-version 3.13 \
    requirements.in -o requirements.txt
```

Lo que no se pudo ejecutar **se declara como no ejecutado**, no como aprobado. Un build
en verde no es prueba de que un caso funcione; es prueba de que compila.

### 8. Regenerar esta documentación

```bash
python scripts/build_upgrade_docs.py
```

Reescribe `docs/upgrades/*.md`, el índice de este fichero y el bloque del README a
partir de los 20 `security.yml`. No se editan a mano: se regeneran.


---

## Historial de pases

### v4.11.0 — 2026-11-01

Primer pase sistemático. Ningún runtime del laboratorio queda en EOL.

| | |
| :--- | ---: |
| Casos revisados | 20 / 20 |
| Cambios de runtime / imagen base | 51 |
| Entradas de dependencia revisadas | 92 |
| Advisories cerrados | 78 |
| · de ellos con identificador CVE | 41 |
| Hallazgos declarados ABIERTOS | 5 |

Detalle por stack en el índice de arriba. Entrada completa en [CHANGELOG.md](../CHANGELOG.md).

---

## Hallazgos ABIERTOS

Un informe que solo lista lo cerrado no es un informe de seguridad. Esto sigue vulnerable y está declarado como `open_findings` en el `security.yml` de su caso, de modo que el guardrail no puede presentarlo como resuelto.

| Caso | Paquete | Versión | Corrige en | Severidad | Advisories |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 07 | `crates.io/rustls` | 0.23.41 | **0.23.46** | MODERATE | RUSTSEC-2026-0285, RUSTSEC-2026-0346, RUSTSEC-2026-0348, RUSTSEC-2026-0349, GHSA-2mjx-qc3c-rqvc, GHSA-c8m5-c952-6cm4, GHSA-h2v8-394m-p7vv, GHSA-w44r-93j7-qv28 |
| 07 | `crates.io/h2` | 0.4.15 | **0.4.16** | SIN-CLASIFICAR | RUSTSEC-2026-0258 |
| 07 | `crates.io/rustls-webpki` | 0.103.13 | **0.103.16** | SIN-CLASIFICAR | RUSTSEC-2026-0382 |
| 07 | `crates.io/tokio` | 1.52.3 | **1.53.3** | SIN-CLASIFICAR | RUSTSEC-2026-0386 |
| 17 | `crates.io/tokio` | 1.52.3 | **1.53.3** | SIN-CLASIFICAR | RUSTSEC-2026-0386 |

Los cinco son transitivas de los `Cargo.lock` de los dos casos Rust y requieren `cargo update -p <crate>` en una máquina con toolchain Rust: el lock lleva un checksum por crate, así que editarlo a mano no es verificable. Contexto completo en [la página de Rust](upgrades/rust.md).

---

## Lo que NO se subió, y por qué

| Qué | Versión actual | Por qué se conserva |
| :--- | :--- | :--- |
| **Zig** | 0.13.0 | Sin advisories. 0.13 → 0.17 rompe el sistema de build (*Writergate* en 0.15) y no hay toolchain para verificar. [Detalle](upgrades/zig.md) |
| **Ktor** | 2.3.13 | Sin advisory. Ktor 3.x migra a `kotlinx-io`. [Detalle](upgrades/jvm.md) |
| **XTDB** | 1.24.3 | Sin advisory. La rama 2.x es una reescritura completa |
| **Express** | 4.22.x | Express 5 es ruptura; los advisories de la 4 se cierran con 4.22.3 + `overrides`. [Detalle](upgrades/nodejs.md) |
| **Next.js** | 15.5.28 | Next 16 es ruptura; 15.5.28 está sobre el piso de los 38 advisories. [Detalle](upgrades/nodejs.md) |
| **Spring Boot** | 3.5.16 | Boot 4 es ruptura. [Detalle](upgrades/jvm.md) |
| **Driver MongoDB** | 6.21.0 | El major 7 es ruptura y el 6 no tiene advisory |
| **`reqwest` / `rumqttc`** | 0.12 / 0.24 | Sin advisory en la crate directa. [Detalle](upgrades/rust.md) |
| **Java** | Temurin 21 LTS | Soporte hasta 2029-12-31. [Detalle](upgrades/jvm.md) |
| **pnpm** | 11.2.2 | Existe 12.16.1, pero 11.2.2 es la versión con la que se auditaron los 9 lockfiles. [Detalle](upgrades/pnpm.md) |
| **Imágenes de BD e infraestructura** | sin cambios | Este pase cubre **lenguajes**. `mongo:6.0` e `influxdb:1.8` son las más atrasadas y merecen un pase propio |

