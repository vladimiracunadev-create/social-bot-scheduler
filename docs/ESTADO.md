# 📍 Estado del repositorio

**Última revisión: 2026-11-01 · versión 4.11.0**

Dónde están las cosas ahora mismo, qué decisiones se tomaron y por qué, y qué
queda pendiente. Está pensado para leerse al volver después de semanas sin tocar
el repositorio, o para que alguien que llega nuevo no tenga que reconstruirlo del
historial de git.

Cada afirmación lleva el comando que la verifica. Si al correrlo no cuadra, el
documento está desactualizado y manda el comando.

---

## Lo que hay que saber en 30 segundos

| | |
| :--- | :--- |
| **Runtimes en EOL** | 0 — ningún lenguaje corre sobre una versión sin soporte |
| **Advisories cerrados en la v4.11.0** | 78 (41 con identificador CVE) |
| **Hallazgos abiertos** | **5**, todos en los `Cargo.lock` de los casos Rust |
| **PRs abiertos** | 0 |
| **Issues abiertos** | 0 |
| **Ramas** | solo `main`, protegida |
| **Pipeline** | verde |

```bash
# Comprobarlo de una vez
python scripts/validate_security_manifests.py
gh pr list --state open | wc -l      # 0
gh run list --workflow=ci-cd.yml --limit 1
```

---

## 1. Lo que sigue vulnerable (y por qué no se arregló)

**Cinco crates de los dos casos Rust.** No están corregidos y no se finge que lo
estén: viven en el `security.yml` de su caso bajo `open_findings`, una clave que
el guardrail obliga a rellenar con severidad, versión de corrección y qué lo
bloquea.

| Caso | Crate | Está en | Corrige en |
| :--- | :--- | :--- | :--- |
| 07 | `rustls` | 0.23.41 | 0.23.46 |
| 07 | `h2` | 0.4.15 | 0.4.16 |
| 07 | `rustls-webpki` | 0.103.13 | 0.103.16 |
| 07, 17 | `tokio` | 1.52.3 | 1.53.3 |

**Qué lo bloquea**: el `Cargo.lock` lleva un checksum por crate y la lista de
dependencias de cada versión. Editarlo a mano no es verificable y rompería el
build. La corrección correcta es un `cargo update` que los cubra a la vez, y no
hay toolchain Rust en la máquina donde se hizo este pase.

**Qué hacer cuando haya una máquina con Rust**:

```bash
cd cases/07-rust-to-ruby/origin
cargo update -p rustls -p h2 -p rustls-webpki -p tokio
cargo audit
cd ../../17-mqtt-rust-to-node/origin && cargo update -p tokio && cargo audit
```

Después hay que mover esas entradas de `open_findings` a `dependencies` en el
`security.yml` de cada caso y regenerar la documentación.

> **Cómo se encontraron, que es la parte interesante**: `cargo audit` pasó en
> **verde** en CI. Fue la consulta a OSV sobre las versiones exactas del lock la
> que los vio. Y al revés con `rack`: ahí OSV devolvía cero y fue `bundler-audit`
> quien destapó cuatro advisories publicados ese mismo día, uno HIGH. **Ninguna
> base de datos de advisories basta sola**, y por eso los auditores nativos de
> cada ecosistema siguen en CI y bloqueando.

---

## 2. Versiones que se decidió NO subir

No son olvidos. Cada una tiene una regla `ignore` en `.github/dependabot.yml`
con su motivo como comentario, para que Dependabot no reabra el mismo PR cada
semana y la decisión no se pierda.

| Qué | Se queda en | Motivo |
| :--- | :--- | :--- |
| Zig | 0.13.0 | Sin advisory. 0.13 → 0.17 rompe el build (*Writergate* en 0.15) y no hay toolchain para verificar |
| Ktor | 2.3.13 | Sin advisory. Ktor 3 migra a `kotlinx-io` |
| XTDB | 1.24.3 | Sin advisory. La 2.x es una reescritura completa |
| Express | 4.22.x | Express 5 es ruptura; los advisories de la 4 se cierran con 4.22.3 + `overrides` |
| Next.js | 15.5.28 | Next 16 es ruptura; la 15.5.28 está sobre el piso de sus 38 advisories |
| Spring Boot | 3.5.16 | Boot 4 es ruptura |
| Driver MongoDB | 6.21.0 | El 7 es ruptura y el 6 no tiene advisory |
| `reqwest` / `rumqttc` | 0.12 / 0.24 | Ruptura de API en crates 0.x, sin advisory |
| Kotlin + `plugin.serialization` | 2.0.21 | Kotlin 2.4 arrastra Gradle 9 |
| `logback` | línea 1.5 | La 1.6 abre línea nueva; la 1.5 está al día |
| Shadow | línea 8.3 | Shadow 9 obliga a revisar el toolchain |
| Python (imagen) | 3.13 | 3.14+ reduce las ruedas precompiladas para los locks con hash |
| Java | Temurin 21 LTS | Soporte hasta 2029-12-31 |
| pnpm | 11.2.2 | Existe 12.x, pero 11.2.2 es la versión con la que se auditaron los 9 lockfiles |

> Una regla `ignore` es una decisión, no una forma de callar al bot: **solo
> cubren el tipo de salto rechazado**. Los parches de esas mismas líneas siguen
> llegando, y se aplican. Pasó durante el propio pase con `logback` 1.5.38 y
> `shadow` 8.3.11.

Si aparece un advisory que justifique alguno de estos saltos, se quita la regla y
se sube. El detalle de cada uno, en [VERSION_UPGRADES.md](VERSION_UPGRADES.md).

---

## 3. Fuera de alcance: bases de datos e infraestructura

El pase de la v4.11.0 cubrió **lenguajes de programación**. Las imágenes de
infraestructura **no se tocaron** y algunas están atrasadas:

| Imagen | Situación |
| :--- | :--- |
| `mongo:6.0` | **EOL** desde julio de 2025 |
| `influxdb:1.8` | Rama muy antigua |
| `cassandra:4.1`, `mariadb:10.11`, `postgres:15-alpine`, `redis:7-alpine` | Conviene revisarlas |

Merecen un pase propio, con el mismo método: consultar la versión exacta contra
OSV, el fin de soporte contra endoflife.date y comprobar que el tag existe antes
de escribirlo.

---

## 4. Qué se verificó de verdad y qué no

La distinción importa: el laboratorio tiene 20 stacks y la máquina donde se hizo
el pase solo tenía Node, pnpm, Python, PHP y Docker.

**Verificado con ejecución real**: `pnpm audit` limpio en los 9 paquetes Node;
OSV sin advisories sobre los 162 paquetes de los 8 locks de Python; `node --check`;
`pytest` y `mypy` de los casos 01 y 02; `php -l`; `docker compose config` en los
5 perfiles; los guardrails del repo; y el **build real de la imagen del hub** en
el job `Build & Push to GHCR`.

**NO ejecutado**: el `docker build` de las otras 28 imágenes de caso, y la
compilación de Go, Rust, JVM, Clojure, BEAM, Crystal, Zig, Swift, Dart y .NET,
por no haber toolchain local de esos lenguajes.

Los saltos con más riesgo si algo falla, por orden:

1. **Crystal 1.14 → 1.22** (caso 18) — ocho menores de golpe
2. **ring 1.12 → 1.15** (caso 19) — cambia de Jetty 11 a Jetty 12
3. **.NET 6 → 10** (caso 08) — cuatro majors
4. **Spring Boot 3.3 → 3.5** (caso 10)

---

## 5. Configuración del repositorio

**`main` está protegida** desde el 2026-11-01:

| Regla | Estado | Por qué |
| :--- | :--- | :--- |
| Force-push | **bloqueado** | Reescribir el historial es lo único verdaderamente irreversible |
| Borrado de la rama | **bloqueado** | Ídem |
| Exigir PR | no | Rompería el flujo de trabajo directo sobre `main` |
| Exigir checks | no | Los nombres de job cambian: renombrar uno bloquearía todos los PRs hasta actualizar la regla a mano. Pasó en este pase al renombrar `Node Cases (03-05)` |
| Aplicar a admins | no | El dueño puede arreglar una urgencia sin pelearse con la configuración |

```bash
# Ver el estado
gh api repos/vladimiracunadev-create/social-bot-scheduler/branches/main/protection

# Quitarla, si algún día molesta
gh api -X DELETE repos/vladimiracunadev-create/social-bot-scheduler/branches/main/protection
```

---

## 6. Lo que NO hay que editar a mano

Estos ficheros **se generan**. Un paso de CI falla si alguien los toca o si
cambia un manifiesto sin regenerarlos:

- `docs/upgrades/*.md`
- `docs/VERSION_UPGRADES.md`
- el bloque del `README.md` entre `UPGRADES:INICIO` y `UPGRADES:FIN`

```bash
python scripts/build_upgrade_docs.py
```

La fuente de verdad son los 20 `cases/NN-*/security.yml`. Al mover una versión
hay que actualizar el manifiesto **en el mismo commit**: el guardrail cruza lo
que dicen contra los Dockerfiles, el compose y los manifiestos de proyecto, y
comprueba que cada ruta citada en `applied_in` exista de verdad.

---

## 7. Deuda conocida

| Qué | Dónde |
| :--- | :--- |
| Los 5 crates vulnerables de Rust | Sección 1 |
| Las imágenes de BD e infraestructura | Sección 3 |
| Las 28 imágenes de caso sin construir | Sección 4 |
| El caso 19 sin verificación end-to-end | [PLANNED_CASES.md](PLANNED_CASES.md) |
| `scripts/validate_workflows.py` falla en Windows | Codificación de consola (`cp1252` vs emoji), no su lógica. En CI corre bien |
| Un `node_modules` con enlaces rotos en `cases/05-laravel-to-react/dest` | Residuo del bind-mount de compose. Es `.gitignore`, pero revienta los recorridos de ficheros en Windows con `WinError 1920` |

---

## Dónde seguir

| Para qué | Documento |
| :--- | :--- |
| Cómo se hace una subida de versión aquí | [VERSION_UPGRADES.md](VERSION_UPGRADES.md) |
| El detalle de un cambio concreto | `docs/upgrades/<stack>.md` |
| La postura de seguridad capa por capa | [../SECURITY.md](../SECURITY.md) |
| Qué pasó en cada release | [../CHANGELOG.md](../CHANGELOG.md) |
| Qué viene después | [../ROADMAP.md](../ROADMAP.md) |
