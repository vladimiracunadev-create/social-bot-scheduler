# Remediación de CVE multi-lenguaje — v4.11.0

**Fecha de la revisión:** 2026-11-01 · **Versión del laboratorio:** 4.11.0

Este documento es el resumen transversal. El detalle por caso vive en
`cases/NN-*/security.yml`, que es la fuente de verdad: las tablas de aquí se
generan a partir de esos 20 ficheros, así que no pueden desincronizarse sin que
el guardrail `scripts/validate_security_manifests.py` lo detecte en CI.

---

## 1. Qué se hizo y por qué

El laboratorio arrastraba runtimes de lenguaje que ya no reciben parches de
seguridad. Un runtime en EOL no tiene "un CVE": tiene todos los que se publiquen
desde su último parche, sin remedio posible salvo subir de versión. Go 1.21, por
ejemplo, acumula **72 advisories de stdlib** según OSV.dev.

Se recorrieron los 20 casos actualizando:

1. **Runtimes de lenguaje** e imágenes base (Dockerfiles + `docker-compose.yml`).
2. **Dependencias directas** de cada caso en su gestor nativo.
3. **Dependencias transitivas** con advisory abierto que la versión parcheada de la
   dependencia directa todavía arrastra (vía `overrides` de pnpm, pin directo en
   Leiningen o propiedad del BOM en Gradle).
4. **Superficie de supply chain**: cero invocaciones de `npm`, locks con hash en
   todos los casos Python y lockfiles commiteados en los 9 paquetes Node.

### Criterio de versión (importante)

No se sube siempre a la última versión publicada. La regla aplicada fue:

| Situación | Qué se hizo |
| :--- | :--- |
| Runtime en EOL o con soporte activo cerrado | Se sube a una rama con soporte vigente |
| Dependencia con advisory abierto | Se sube al menor parche que cierra **todos** sus advisories |
| Advisory que solo se corrige en un major nuevo | Se evalúa caso a caso y se verifica el salto (ver Apollo Server, caso 16) |
| Major nuevo que rompe la API y **sin** advisory abierto | Se conserva el major actual y se documenta (ver sección 5) |

Cada entrada de `security.yml` lleva un `reason` que dice cuál de estas se aplicó.

---

## 2. Resumen numérico

| Métrica | Valor |
| :--- | ---: |
| Casos revisados | 20 / 20 |
| Cambios de runtime / imagen base | 51 |
| Entradas de dependencia registradas | 92 |
| Advisories distintos remediados | 78 |
| · de ellos con identificador CVE | 41 |

Entradas de dependencia agrupadas por la severidad **más alta** que OSV reporta
para esa dependencia:

| Severidad máxima de la dependencia | Entradas |
| :--- | ---: |
| CRITICAL | 12 |
| HIGH | 25 |
| MODERATE | 8 |
| sin advisory (mantenimiento) | 47 |

Motivo de los cambios de runtime:

| `reason` | Cambios | Significado |
| :--- | ---: | :--- |
| `eol` | 20 | El runtime ya no recibe parches de seguridad |
| `endurecimiento` | 10 | Cierra una superficie de ataque, no un CVE concreto |
| `fin-de-soporte-activo` | 7 | En modo solo-seguridad |
| `mantenimiento` | 7 | Sin advisory abierto; se sube para no acumular deuda |
| `sin-cambio` | 4 | Se evaluó y se deja como está (motivo en el `detail`) |
| `fin-de-soporte` | 3 | Sigue recibiendo parches, pero el soporte activo ya cerró |

---

## 3. Runtimes de lenguaje — antes y después

| Caso | Componente | Lenguaje | Antes | Después | Motivo |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 01 | origin | python | `3.11` | `3.13` | `fin-de-soporte-activo` |
| 01 | dest | php | `8.2-apache` | `8.4-apache` | `fin-de-soporte` |
| 02 | origin | python | `3.11` | `3.13` | `fin-de-soporte-activo` |
| 02 | dest | go | `1.21-alpine` | `1.27-alpine` | `eol` |
| 02 | dest | alpine | `3.20.6` | `3.23.7` | `eol` |
| 03 | origin | go | `1.21 (go.mod)` | `1.27 (go.mod)` | `eol` |
| 03 | dest | nodejs | `20-alpine` | `24-alpine` | `eol` |
| 03 | dest | pnpm | `10.0.0` | `11.2.2` | `endurecimiento` |
| 04 | origin | nodejs | `20-alpine` | `24-alpine` | `eol` |
| 04 | origin | pnpm | `10.0.0` | `11.2.2` | `endurecimiento` |
| 04 | dest | python | `3.11-alpine` | `3.13-alpine` | `fin-de-soporte-activo` |
| 05 | origin | php | `8.2-apache` | `8.4-apache` | `fin-de-soporte` |
| 05 | dest | nodejs | `20-alpine` | `24-alpine` | `eol` |
| 05 | dest | pnpm | `10.0.0` | `11.2.2` | `endurecimiento` |
| 06 | origin | go | `1.21 (go.mod)` | `1.27 (go.mod)` | `eol` |
| 06 | dest | php | `8.2-apache` | `8.4-apache` | `fin-de-soporte` |
| 07 | dest | ruby | `3.2-alpine` | `3.4-alpine` | `eol` |
| 07 | origin | rust | `toolchain stable en CI` | `toolchain stable en CI` | `sin-cambio` |
| 08 | origin | dotnet | `net6.0` | `net10.0` | `eol` |
| 08 | dest | python | `3.11-slim (bookworm)` | `3.13-slim-trixie` | `fin-de-soporte-activo` |
| 09 | dest | python | `3.11-slim` | `3.13-slim-trixie` | `fin-de-soporte-activo` |
| 10 | origin+dest | gradle | `8.11-jdk21` | `8.14-jdk21` | `mantenimiento` |
| 10 | origin+dest | java | `eclipse-temurin:21-jre-alpine` | `sin cambio` | `sin-cambio` |
| 11 | origin | elixir | `1.17-otp-27-alpine` | `1.18-otp-28-alpine` | `mantenimiento` |
| 11 | dest | erlang | `27-alpine` | `28-alpine` | `mantenimiento` |
| 12 | dest | python | `3.11-slim` | `3.13-slim-trixie` | `fin-de-soporte-activo` |
| 13 | origin | nodejs | `20-alpine` | `24-alpine` | `eol` |
| 13 | origin | pnpm | `10.0.0` | `11.2.2` | `endurecimiento` |
| 13 | dest | go | `1.23-alpine` | `1.27-alpine` | `eol` |
| 13 | dest | alpine | `3.20` | `3.23.7` | `eol` |
| 14 | origin+dest | nodejs | `20-alpine` | `24-alpine` | `eol` |
| 14 | origin+dest | pnpm | `10.0.0` | `11.2.2` | `endurecimiento` |
| 15 | origin | go | `1.23-alpine` | `1.27-alpine` | `eol` |
| 15 | origin | alpine | `3.20` | `3.23.7` | `eol` |
| 15 | dest | python | `3.11-slim` | `3.13-slim-trixie` | `fin-de-soporte-activo` |
| 16 | origin+dest | nodejs | `20-alpine` | `24-alpine` | `eol` |
| 16 | origin+dest | pnpm | `10.0.0` | `11.2.2` | `endurecimiento` |
| 17 | origin | rust | `1.83-alpine` | `1.99-alpine` | `mantenimiento` |
| 17 | origin | alpine | `3.20` | `3.23.7` | `eol` |
| 17 | dest | nodejs | `20-alpine` | `24-alpine` | `eol` |
| 17 | dest | pnpm | `10.0.0` | `11.2.2` | `endurecimiento` |
| 18 | origin | alpine | `3.20` | `3.23.7` | `eol` |
| 18 | origin | zig | `0.13.0` | `0.13.0` | `sin-cambio` |
| 18 | dest | crystal | `1.14-alpine` | `1.22-alpine` | `mantenimiento` |
| 19 | origin | dotnet | `9.0 (sdk/runtime, net9.0)` | `10.0 (sdk/runtime, net10.0)` | `eol` |
| 19 | dest | java | `clojure:temurin-21-lein + temurin:21-jre-alpine` | `sin cambio` | `sin-cambio` |
| 20 | origin | swift | `6.0 / 6.0-slim` | `6.2 / 6.2-slim` | `mantenimiento` |
| 20 | dest | dart | `dart:stable` | `dart:3.10-sdk` | `endurecimiento` |
| 20 | dest | debian | `debian:stable-slim` | `debian:13-slim` | `endurecimiento` |
| 20 | firebase | java | `eclipse-temurin:21-jdk-jammy` | `eclipse-temurin:21-jdk-noble` | `mantenimiento` |
| 20 | firebase | pnpm | `10.0.0` | `11.2.2` | `endurecimiento` |

---

## 4. Advisories remediados

«Paquetes» es la dependencia que los arrastraba y «Casos» los casos afectados.

> **Sobre la columna de severidad**: es la severidad más alta que OSV reporta para
> la **dependencia**, no la de cada advisory por separado. De los 78 advisories
> listados, solo 31 traen una severidad textual en OSV; el resto publica únicamente
> un vector CVSS, y traducirlo a una etiqueta sería una interpretación nuestra, no un
> dato de la fuente. Para la severidad exacta de un advisory concreto, el enlace
> canónico es `https://osv.dev/vulnerability/<ID>`.

| Severidad (dependencia) | Advisory | Paquete(s) | Casos |
| :--- | :--- | :--- | :--- |
| CRITICAL | CVE-2025-49826 | `npm/next` | 14 |
| CRITICAL | CVE-2025-7783 | `npm/form-data` | 03 |
| CRITICAL | CVE-2026-33186 | `Go/google.golang.org/grpc` | 15 |
| CRITICAL | CVE-2026-44573 | `npm/next` | 14 |
| CRITICAL | CVE-2026-64649 | `npm/next` | 14 |
| CRITICAL | CVE-2026-84303 | `Go/google.golang.org/grpc` | 15 |
| CRITICAL | CVE-2026-84304 | `Go/google.golang.org/grpc` | 15 |
| CRITICAL | CVE-2026-84445 | `Go/google.golang.org/grpc` | 15 |
| CRITICAL | GHSA-2464-fhr4-w9xw | `npm/next` | 14 |
| CRITICAL | GHSA-2xp9-vwfh-vxw4 | `npm/next` | 14 |
| CRITICAL | GHSA-3w57-8xmc-8v26 | `PyPI/anyio` | 09 |
| CRITICAL | GHSA-5p39-cfhj-2xmp | `PyPI/anyio` | 09 |
| CRITICAL | GHSA-6q48-6c7w-9gw2 | `PyPI/certifi` | 01, 02, 09 |
| CRITICAL | GHSA-82r6-8w77-94w6 | `PyPI/anyio` | 09 |
| CRITICAL | GHSA-8h8q-6873-q5fj | `npm/next` | 14 |
| CRITICAL | GHSA-jqcg-44mw-7w3h | `npm/proxy-addr` | 03, 05, 14, 16, 17 |
| CRITICAL | PYSEC-2026-4320 | `PyPI/certifi` | 01 |
| HIGH | CVE-2024-45336 | `Go/stdlib` | 02 |
| HIGH | CVE-2024-45341 | `Go/stdlib` | 02 |
| HIGH | CVE-2024-7708 | `Maven/ring/ring-jetty-adapter` | 19 |
| HIGH | CVE-2024-8184 | `Maven/ring/ring-jetty-adapter` | 19 |
| HIGH | CVE-2025-0913 | `Go/stdlib` | 02 |
| HIGH | CVE-2025-22871 | `Go/stdlib` | 02 |
| HIGH | CVE-2025-4673 | `Go/stdlib` | 02 |
| HIGH | CVE-2025-47906 | `Go/stdlib` | 13, 15 |
| HIGH | CVE-2025-47907 | `Go/stdlib` | 02, 13, 15 |
| HIGH | CVE-2025-49146 | `Maven/org.postgresql:postgresql` | 10 |
| HIGH | CVE-2026-10051 | `Maven/ring/ring-jetty-adapter` | 19 |
| HIGH | CVE-2026-101898 | `npm/axios` | 03, 04 |
| HIGH | CVE-2026-101901 | `npm/axios` | 03, 04 |
| HIGH | CVE-2026-101903 | `npm/axios` | 03, 04 |
| HIGH | CVE-2026-101905 | `npm/axios` | 03, 04 |
| HIGH | CVE-2026-101906 | `npm/axios` | 03, 04 |
| HIGH | CVE-2026-101907 | `npm/axios` | 03, 04 |
| HIGH | CVE-2026-1605 | `Maven/ring/ring-jetty-adapter` | 19 |
| HIGH | CVE-2026-18401 | `Maven/com.fasterxml.jackson.core:jackson-core` | 19 |
| HIGH | CVE-2026-23897 | `npm/@apollo/server` | 16 |
| HIGH | CVE-2026-42198 | `Maven/org.postgresql:postgresql` | 10 |
| HIGH | CVE-2026-43966 | `Hex/cowboy` | 11 |
| HIGH | CVE-2026-54291 | `Maven/org.postgresql:postgresql` | 10 |
| HIGH | CVE-2026-65624 | `Hex/cowboy` | 11 |
| HIGH | CVE-2026-6790 | `Maven/ring/ring-jetty-adapter` | 19 |
| HIGH | CVE-2026-68494 | `Maven/com.fasterxml.jackson.core:jackson-core`, `Maven/com.fasterxml.jackson:jackson-bom` | 10, 19 |
| HIGH | CVE-2026-8466 | `Hex/cowboy` | 11 |
| HIGH | CVE-2026-89407 | `Maven/com.fasterxml.jackson.core:jackson-core`, `Maven/com.fasterxml.jackson:jackson-bom` | 10, 19 |
| HIGH | CVE-2026-89425 | `Maven/com.fasterxml.jackson.core:jackson-core`, `Maven/com.fasterxml.jackson:jackson-bom` | 10, 19 |
| HIGH | CVE-2026-97032 | `Go/stdlib` | 13 |
| HIGH | GHSA-27r3-jxmh-p828 | `npm/body-parser` | 03, 05, 14, 16, 17 |
| HIGH | GHSA-2j8w-xcrc-x985 | `RubyGems/rack` | 07 |
| HIGH | GHSA-37ch-88jc-xwx2 | `npm/path-to-regexp` | 05 |
| HIGH | GHSA-5gvw-p9qm-jgwh | `Maven/com.fasterxml.jackson:jackson-bom` | 10 |
| HIGH | GHSA-5v64-555j-wjxm | `RubyGems/rack` | 07 |
| HIGH | GHSA-6g55-p6wh-862q | `npm/postcss` | 14 |
| HIGH | GHSA-7f5h-v6xp-fcq8 | `PyPI/starlette` | 09 |
| HIGH | GHSA-8988-9cw3-xx77 | `PyPI/urllib3` | 01, 02, 09 |
| HIGH | GHSA-8r9p-f939-6h3c | `npm/follow-redirects` | 03, 04 |
| HIGH | GHSA-9q82-xgwf-vj6h | `npm/@apollo/server` | 16 |
| HIGH | GHSA-fxqj-rqcc-2cmp | `npm/postcss` | 14 |
| HIGH | GHSA-gh4c-6fx4-qh6g | `PyPI/urllib3` | 01 |
| HIGH | GHSA-mrwp-f3q8-3g9p | `npm/follow-redirects` | 03, 04 |
| HIGH | GHSA-p8x9-v4hv-2w4g | `RubyGems/rack` | 07 |
| HIGH | GHSA-q3jh-wrc6-jgq8 | `npm/follow-redirects` | 03, 04 |
| HIGH | GHSA-qx2v-qp2m-jg93 | `npm/postcss` | 14 |
| HIGH | GHSA-r28c-9q8g-f849 | `npm/postcss` | 14 |
| HIGH | GHSA-v422-hmwv-36x6 | `npm/body-parser` | 03, 05, 14, 16, 17 |
| HIGH | GHSA-vxq7-64xx-v4gw | `PyPI/urllib3` | 01, 02, 09 |
| HIGH | GHSA-wqp7-x3pw-xc5r | `PyPI/starlette` | 09 |
| HIGH | GHSA-wvg4-6p58-3gh3 | `RubyGems/rack` | 07 |
| HIGH | GHSA-x746-7m8f-x49c | `PyPI/starlette` | 09 |
| MODERATE | CVE-2024-29041 | `npm/express` | 03 |
| MODERATE | CVE-2024-43796 | `npm/express` | 03 |
| MODERATE | CVE-2026-25645 | `PyPI/requests` | 09 |
| MODERATE | GHSA-4mjr-xmp4-gh2g | `npm/qs` | 03, 05, 14, 16, 17 |
| MODERATE | GHSA-6pq8-jhm2-2vcw | `npm/qs` | 03, 05, 14, 16, 17 |
| MODERATE | GHSA-g6x2-hccm-hh4m | `PyPI/werkzeug` | 08 |
| MODERATE | GHSA-gc5v-m9x4-r6x2 | `PyPI/requests` | 09 |
| MODERATE | GHSA-x5fp-wj9c-mxmx | `npm/qs` | 03, 05, 14, 16, 17 |
| MODERATE | PYSEC-2026-4312 | `PyPI/werkzeug` | 08 |

---

## 5. Lo que NO se cambió, y por qué

Un informe que solo lista lo arreglado es un informe incompleto. Esto es lo que se
evaluó y se dejó como estaba:

| Qué | Versión actual | Por qué se conserva |
| :--- | :--- | :--- |
| **Zig** (caso 18 origin) | 0.13.0 | Sin advisories en OSV. La ruta 0.13 → 0.17 rompe el sistema de build (*Writergate* en 0.15) y no hay toolchain Zig local para verificar el compilado. Lo que sí se parcheó es la Alpine sobre la que compila. |
| **Ktor** (caso 10 dest) | 2.3.13 | Sin advisory. Ktor 3.x cambia la API (migración a kotlinx-io). |
| **XTDB** (caso 19 dest) | 1.24.3 | Sin advisory. La rama 2.x es una reescritura completa. |
| **Express** | línea 4.22.x | Express 5 es ruptura. Los advisories de la línea 4 se cierran con 4.22.3 + los `overrides` de transitivas. |
| **Next.js** (caso 14) | 15.5.28 | Next 16 es ruptura. 15.5.28 está por encima del piso de los 38 advisories, incluidos los dos RCE críticos. |
| **Spring Boot** (caso 10) | 3.5.16 | Spring Boot 4 es ruptura. 3.5.16 es el último parche de la 3.x. |
| **MongoDB driver** (caso 05) | 6.21.0 | El major 7 es ruptura y el 6 no tiene advisory abierto. |
| **reqwest / rumqttc** (casos 07, 17) | 0.12 / 0.24 | Sin advisory en crates.io. Sin toolchain Rust local, un salto de major no es verificable aquí. |
| **Java** (casos 10, 19) | Temurin 21 LTS | Soporte hasta 2029-12-31; el tag ya trae el último parche. |
| **pnpm** | 11.2.2 | Existe pnpm 12.16.1, pero 11.2.2 es la versión instalada localmente, la que se usó para regenerar y auditar los 9 lockfiles. Fijar lo verificado vale más que fijar lo último. |
| **Imágenes de base de datos e infraestructura** | sin cambios | `mysql`, `mariadb`, `postgres`, `mongo`, `redis`, `cassandra`, `influxdb`, `neo4j`, `clickhouse`, `kafka`, `n8n`, `hasura`, `postgrest`, `prometheus`, `grafana`, `cadvisor`, `caddy`, `mosquitto`, `cockroach`, `timescaledb`, `pgvector`, `mssql`. Este pase cubre **lenguajes de programación**, que es lo que se pidió. Varias de esas imágenes están atrasadas (`mongo:6.0` y `influxdb:1.8` son las más llamativas) y merecen un pase propio. |

---

## 6. Método

Nada de esto sale de memoria. Para cada versión que estaba pinneada en el
repositorio se consultó:

- **Advisories**: [OSV.dev](https://osv.dev/), endpoint `POST /v1/query`, con el par
  (ecosistema, nombre, **versión exacta**). No rangos ni heurísticas: se preguntó por
  la versión que estaba escrita en el fichero.
- **Fin de soporte**: [endoflife.date](https://endoflife.date/) (`/api/<producto>.json`).
- **Última versión por rama**: el registro nativo de cada ecosistema — registry.npmjs.org,
  pypi.org, proxy.golang.org, crates.io, rubygems.org, hex.pm, pub.dev, repo1.maven.org,
  repo.clojars.org.
- **Existencia de los tags de imagen**: API de Docker Hub y de MCR, comprobada **antes**
  de escribir cada `FROM`. Ningún tag de este documento es una suposición.

Tras aplicar los cambios se repitió la consulta a OSV sobre las versiones destino
para confirmar que salen limpias.

### Una base de datos no basta

OSV no siempre va primero. Al pasar el pipeline, `bundler-audit` tumbó el job de
Ruby con **cuatro advisories de `rack` 3.2.6** publicados ese mismo día — uno de
ellos HIGH: el parser multipart retiene lo ya parseado en su buffer de scan y
permite agotar la memoria (GHSA-5v64-555j-wjxm). La consulta a OSV para esa misma
versión devolvía **cero**: su `ruby-advisory-db` iba más fresca que el índice de
OSV. Se corrigió subiendo a 3.2.8 y fijando el piso en el `Gemfile`, porque
`sinatra` solo pide `>= 3.0.0, < 4` y sin piso explícito bundler puede volver a
resolver una versión vulnerable.

La conclusión práctica: los auditores nativos de cada ecosistema
(`bundler-audit`, `govulncheck`, `pnpm audit`, `cargo audit`, `pip-audit`) **no son
redundantes** con una consulta a OSV. Se quedan, y bloqueando.

---

## 7. Qué se verificó, y qué no

La distinción importa: el laboratorio tiene 20 stacks y en esta máquina solo hay
Node 24, pnpm 11, Python 3.12, PHP y Docker. Lo que no se pudo ejecutar se declara
como no ejecutado, no como aprobado.

### Verificado con ejecución real

| Comprobación | Resultado |
| :--- | :--- |
| `pnpm audit --prod --audit-level high` en los 9 paquetes Node | `No known vulnerabilities found` en los 9 |
| Regeneración de los 9 `pnpm-lock.yaml` con pnpm 11.2.2 | OK; la política de supply-chain se verifica en cada install |
| `node --check` de los 10 ficheros JS/MJS con Node 24 | 10/10 OK |
| Apollo Server 4 → 5 (caso 16, único salto de major) | Emisor arrancado y query GraphQL real resuelta; el `postinstall` de `@apollo/protobufjs` quedó bloqueado por la nueva política |
| OSV sobre los 8 `requirements.txt` con hash (162 paquetes pinneados) | 0 con advisory |
| `pytest` de los casos Python 01 y 02 | 2 + 2 tests OK |
| `mypy` de los casos 01 y 02 con `python_version = 3.13` | Sin incidencias en 8 ficheros |
| `py_compile` de los 13 ficheros Python del repo y de los casos | OK |
| `php -l` de los 4 ficheros PHP | OK |
| `docker compose config` en los 5 perfiles | OK |
| `actionlint` sobre `ci-cd.yml` | OK |
| `black --check .` | 51 ficheros sin cambios |
| Guardrails del repo (`check_runtime_security`, `validate_case_matrix`, `validate_ports`) | OK |
| `validate_security_manifests.py` (nuevo) | OK, con dos pruebas negativas que confirman que detecta regresiones |
| Existencia de los 26 tags de imagen nuevos en Docker Hub / MCR | 26/26 responden 200 |

### No ejecutado (queda en CI o en el primer `docker compose up`)

| Qué | Por qué |
| :--- | :--- |
| `docker build` de las 29 imágenes | Se pidió expresamente no levantar Docker repetidamente. Los tags están verificados y los `FROM` son correctos, pero el build en sí no se ejecutó. |
| Compilación Go, Rust, Java/Kotlin, Clojure, Erlang/Elixir, Crystal, Zig, Swift, Dart, .NET | No hay toolchain de esos lenguajes en esta máquina. |
| `govulncheck`, `cargo audit`, `bundler-audit`, `dotnet list package --vulnerable` | Ídem: los ejecuta el pipeline. |
| `scripts/validate_workflows.py` | Falla en Windows por la codificación de la consola (`cp1252` vs emoji), no por los cambios de este pase. En CI (Linux) corre normal. |

Los saltos con más riesgo de ruptura en el build son, por orden: **Crystal 1.14 →
1.22** (caso 18), **ring 1.12 → 1.15** por el cambio de Jetty 11 a 12 (caso 19),
**.NET 6 → 10** (caso 08) y **Spring Boot 3.3 → 3.5** (caso 10). Son los cuatro a
mirar primero si el pipeline se pone rojo.

---

## 8. Supply chain: npm fuera del laboratorio

`npm` ya no se invoca en ninguna superficie del repositorio. Lo que quedaba y se cerró:

| Dónde | Antes | Ahora |
| :--- | :--- | :--- |
| `.github/workflows/ci-cd.yml` | `npm install -g pnpm@10` | `corepack enable && corepack prepare pnpm@11.2.2 --activate` |
| `.claude/settings.local.json` | `npx --yes pnpm@10 audit …` | `pnpm audit …` |
| `.gitignore` | solo `cases/*/dest/package-lock.json` | `package-lock.json`, `npm-shrinkwrap.json` y las tres rutas de casos |

El ecosistema de Dependabot sigue llamándose `npm` porque es el nombre del
**registro**, no del gestor: Dependabot lee los `pnpm-lock.yaml` sin ejecutar npm.

Además, pnpm 11 trae la política que antes vivía en el campo `pnpm` de
`package.json` — que **pnpm 11 ya no lee**. Si no se hubiera movido, los `overrides`
de seguridad del repositorio habrían quedado silenciosamente desactivados. Ahora
cada paquete Node tiene su `pnpm-workspace.yaml` con:

```yaml
onlyBuiltDependencies: []   # ningún paquete ejecuta postinstall/preinstall
minimumReleaseAge: 1440     # cuarentena de 24 h antes de instalar una publicación nueva
overrides: …                # pisos de versión por CVE para las transitivas
```

Las dos primeras son la mitigación central contra campañas tipo **Shai-Hulud**: el
vector es un `postinstall` en un paquete recién publicado y comprometido, y aquí no
se ejecutan scripts ni se instala nada con menos de 24 h de vida.

---

## 9. Cobertura de Dependabot

Hasta la v4.10.0 Dependabot vigilaba 9 directorios de 20 casos. Ahora son 31
entradas que cubren los 20 casos:

| Ecosistema | Directorios |
| :--- | ---: |
| npm | 9 |
| pip | 8 |
| gomod | 5 |
| nuget | 2 |
| gradle | 2 |
| cargo | 1 |
| bundler | 1 |
| pub | 1 |
| docker | 1 |
| github-actions | 1 |

El caso 11 (Elixir/Erlang) queda fuera a propósito: `mix.exs` no declara
dependencias externas y `rebar.config` no lleva lockfile, así que Dependabot no
tiene nada que resolver. `cowboy` se revisa a mano — en este pase pasó de 2.12.0 a
2.20.0 por tres advisories.

---

## 10. Cómo se mantiene esto al día

```bash
# 1. Guardrail de los manifiestos (también corre en CI)
python scripts/validate_security_manifests.py

# 2. Recompilar un lock de Python con hashes tras tocar su requirements.in
cd cases/09-python-to-gateway/dest
uv pip compile --upgrade --universal --generate-hashes --python-version 3.13 \
    requirements.in -o requirements.txt

# 3. Regenerar un lockfile de Node y auditarlo
cd cases/03-go-to-node/dest
corepack enable && corepack prepare pnpm@11.2.2 --activate
pnpm install --lockfile-only && pnpm audit --prod --audit-level high
```

Al mover una versión hay que actualizar el `security.yml` del caso en el mismo
commit: el guardrail cruza el manifiesto contra los Dockerfiles, el compose y los
manifiestos de proyecto, y falla si el manifiesto va por delante del código o si
alguien reintroduce una versión declarada abandonada.
