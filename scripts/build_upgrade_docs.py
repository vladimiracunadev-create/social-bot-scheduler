#!/usr/bin/env python3
"""Genera la documentacion de mejoras de version del laboratorio.

Produce, SIEMPRE a partir de los 20 `cases/NN-*/security.yml`:

  * `docs/upgrades/<stack>.md`  una pagina por cambio de version, con ventanas de
    soporte y grafico, justificacion, tabla de implementacion fichero a fichero,
    dependencias del stack con sus advisories, riesgo de ruptura y fuentes.
  * `docs/VERSION_UPGRADES.md`  indice vivo + procedimiento + historial de pases +
    hallazgos abiertos + lo que no se subio y por que.
  * el bloque del `README.md` entre los marcadores `UPGRADES:INICIO` / `UPGRADES:FIN`.

Nada de esto se edita a mano: se regenera. Asi el README, el indice y las paginas no
pueden afirmar algo distinto de lo que dicen los manifiestos, que es como envejecen
las documentaciones de seguridad.

Los datos de soporte (fechas de EOL, justificacion, riesgo, fuentes) viven en LANGS,
aqui abajo, y se verificaron el 2026-11-01 contra endoflife.date y los registros
nativos de cada ecosistema. Al anadir un pase nuevo se actualizan ahi.

    python scripts/build_upgrade_docs.py
"""

from __future__ import annotations

import pathlib

import yaml

# La raiz se deriva de la ubicacion del script, nunca de una ruta absoluta ni del
# directorio de trabajo: asi funciona igual en cualquier maquina y en el runner de CI.
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "upgrades"

# slug del fichero -> metadatos del cambio
#   languages: valores de `language` en los security.yml que agrupa esta pagina
#   title, headline, eol: tabla de soporte; why: justificacion; risk: riesgo real
LANGS: dict[str, dict] = {
    "go": {
        "languages": ["go"],
        "title": "Go 1.21 / 1.23 → 1.27",
        "icon": "🐹",
        "headline": "El cambio de mayor impacto del pase: dos ramas en EOL con 72 y 59 "
        "advisories de la biblioteca estándar.",
        "eol": [
            ("1.21", "2023-08-08", "2024-08-13", "EOL hace mas de 2 años"),
            ("1.23", "2024-08-13", "2025-08-12", "EOL hace mas de 1 año"),
            ("1.25", "2025-08-12", "2026-08-19", "EOL"),
            ("1.26", "2026-02-10", "con soporte", "soportada"),
            ("1.27", "2026-08-19", "con soporte", "**adoptada**"),
        ],
        "why": [
            "Go mantiene **solo las dos ramas mas recientes**. Cuando sale 1.27, la 1.25 "
            'deja de recibir parches: no hay backports y no hay versión "estable antigua".',
            "Esto hace que una rama EOL no acumule *un* CVE, sino **todos** los de la "
            "stdlib publicados desde su último parche. OSV reporta **72 advisories** para "
            "`stdlib` 1.21.13 y **59** para 1.23.12.",
            "Entre ellos hay fallos explotables en remoto sin autenticación: request "
            "smuggling por aceptar chunked inválido (`CVE-2025-22871`), cabeceras "
            "sensibles no limpiadas al redirigir cross-origin (`CVE-2025-4673`, "
            "`CVE-2024-45336`) y resultados incorrectos en `database/sql` "
            "(`CVE-2025-47907`).",
        ],
        "risk": "Bajo. El código de los casos usa `net/http`, `database/sql` y drivers "
        "estándar; no hay API retirada entre 1.21 y 1.27 que afecte a este "
        "laboratorio. El job `Go Cases (02,03,06)` del pipeline compila los tres "
        "casos y corre `govulncheck`, y pasó en verde.",
        "sources": ["https://endoflife.date/go", "https://go.dev/doc/devel/release"],
    },
    "nodejs": {
        "languages": ["nodejs"],
        "title": "Node.js 20 → 24 LTS",
        "icon": "🟩",
        "headline": "Node 20 dejó de recibir parches el 2026-04-30. Su último "
        "release de seguridad fue el 20.20.2, de marzo de 2026.",
        "eol": [
            ("20 «Iron»", "2023-04-18", "2026-04-30", "**EOL**"),
            ("22 «Jod»", "2024-04-24", "2027-04-30", "Maintenance LTS"),
            ("24", "2025-04-22", "2028-04-30", "**adoptada** (LTS)"),
            ("26", "2026-10-28", "2029-04-30", "Current → LTS"),
        ],
        "why": [
            "La rama 20 quedó fuera del calendario de releases de seguridad: el del "
            "2026-07 ya solo cubrio 22.x, 24.x y 26.x.",
            "Subir a 24 tiene un segundo efecto, deliberado: **pnpm 11 exige Node >= "
            "22.13** (usa `node:sqlite`). Con Node 20 el laboratorio estaba atascado en "
            "pnpm 10 y no podia activar las defensas de supply-chain de pnpm 11.",
            "Se elige 24 y no 26 porque 24 ya esta en LTS con soporte hasta 2028, "
            "mientras 26 acaba de entrar: para un laboratorio que se reproduce en "
            "máquinas ajenas, la rama rodada vale mas que la recien salida.",
        ],
        "risk": "Bajo. Los receptores usan `express`, `pg`, `mqtt` y APIs de `node:*` "
        "estables. El job `Node Cases` hace `node --check` de los 10 ficheros y "
        "`pnpm audit` de los 9 paquetes; verde en ambos.",
        "sources": ["https://endoflife.date/nodejs", "https://github.com/nodejs/LTS"],
    },
    "python": {
        "languages": ["python"],
        "title": "Python 3.11 → 3.13 (Debian 12 → 13)",
        "icon": "🐍",
        "headline": "3.11 sigue recibiendo parches, pero solo de seguridad. El cambio "
        "de verdad esta debajo: la imagen pasa de bookworm a trixie.",
        "eol": [
            ("3.11", "2022-10-24", "2027-10-31", "solo-seguridad"),
            ("3.12", "2023-10-02", "2028-10-31", "solo-seguridad"),
            ("3.13", "2024-10-07", "2029-10-31", "**adoptada**"),
            ("3.14", "2025-10-07", "2030-10-31", "bleeding edge"),
        ],
        "why": [
            "Python 3.11 esta en modo **solo correcciones de seguridad** desde abril de "
            "2024: no recibe correcciones de fallos normales. 3.13 da cuatro años mas de "
            "margen y sigue en soporte completo.",
            "El salto de base del sistema operativo pesa mas que el de Python: "
            "`python:3.11-slim-bookworm` es Debian 12, que ya es *oldstable*. "
            "`python:3.13-slim-trixie` es Debian 13, la estable actual, con ventanas de "
            "parches de OS mas largas para `openssl`, `zlib` y compania.",
            "No se va a 3.14 a propósito: los 8 locks del repositorio se compilan con "
            "`--generate-hashes`, y cuanto mas nueva es la versión menos ruedas "
            "precompiladas hay para `pydantic-core` o `grpcio`, lo que obligaria a "
            "compilar desde fuente dentro de la imagen.",
        ],
        "risk": "Bajo, y verificado mas que el resto: el job `Build & Push to GHCR` "
        "**construye de verdad** la imagen del hub sobre 3.13-trixie y pasa. "
        "`mypy` con `python_version = 3.13` y los tests de los casos 01 y 02 "
        "también estan en verde.",
        "sources": [
            "https://endoflife.date/python",
            "https://www.debian.org/releases/",
        ],
        "extra": [
            (
                "Una trampa que casi se cuela",
                (
                    "El `Dockerfile` del hub borra `pip` de la imagen de runtime para dejar "
                    "limpio el escaneo de Trivy, y lo hacia con **rutas hardcodeadas** "
                    "`/usr/local/lib/python3.11/...`. Al cambiar la base, esos `rm -rf` "
                    "habrían dejado de encontrar nada **sin fallar**, `pip` habría vuelto a "
                    "la imagen y los hallazgos HIGH de Trivy habrían reaparecido en silencio. "
                    "Las rutas se actualizaron a `python3.13`."
                ),
            ),
        ],
    },
    "php": {
        "languages": ["php"],
        "title": "PHP 8.2 → 8.4",
        "icon": "🐘",
        "headline": "El soporte activo de 8.2 cerro el 2024-12-31 y su EOL total es el "
        "2026-12-31: quedaban ocho semanas.",
        "eol": [
            ("8.2", "2022-12-08", "2026-12-31", "**solo-seguridad, EOL inminente**"),
            ("8.3", "2023-11-23", "2027-12-31", "solo-seguridad"),
            ("8.4", "2024-11-21", "2028-12-31", "**adoptada**"),
            ("8.5", "2025-11-20", "2029-12-31", "recien salida"),
        ],
        "why": [
            "PHP da dos años de soporte activo y dos mas de solo-seguridad. La 8.2 estaba "
            "en el último tramo del segundo, con EOL el 2026-12-31.",
            "Se elige 8.4 y no 8.5 por disponibilidad de extensiones: el caso 06 instala "
            "`phpredis` por `pecl` sobre la imagen oficial, y la 8.4 lleva un año de "
            "rodaje con el ecosistema de extensiones al día.",
        ],
        "risk": "Bajo. Los tres destinos PHP son scripts de dashboard con PDO y "
        "`phpredis`; no usan nada retirado en 8.3 ni 8.4. El job "
        "`PHP Cases (01,05,06)` hace `php -l` sobre PHP 8.4 y pasa.",
        "sources": [
            "https://endoflife.date/php",
            "https://www.php.net/supported-versions.php",
        ],
    },
    "ruby": {
        "languages": ["ruby"],
        "title": "Ruby 3.2 → 3.4",
        "icon": "💎",
        "headline": "3.2 quedó EOL el 2026-03-31. Y el pipeline destapo algo peor en sus "
        "gemas que en el propio intérprete.",
        "eol": [
            ("3.2", "2022-12-25", "2026-03-31", "**EOL**"),
            ("3.3", "2023-12-25", "2027-03-31", "con soporte"),
            ("3.4", "2024-12-25", "2028-03-31", "**adoptada**"),
            ("4.0", "2025-12-25", "2029-03-31", "recien salida"),
        ],
        "why": [
            "La rama 3.2 dejó de recibir parches en marzo de 2026. 3.4 llega a 2028.",
            "Se queda en 3.4 en lugar de 4.0 porque el caso depende de "
            "`cassandra-driver`, una gema poco mantenida: cuanto mas nuevo el intérprete, "
            "mas probable es topar con una incompatibilidad que no tiene quien la arregle.",
            "`sorted_set` sigue siendo necesario: `SortedSet` salió de la biblioteca "
            "estándar en Ruby 3.2 y `cassandra-driver` lo usa.",
        ],
        "risk": "Bajo para el intérprete. El riesgo real estaba en `rack` — ver el "
        "apartado siguiente.",
        "sources": ["https://endoflife.date/ruby"],
        "extra": [
            (
                "El hallazgo que no vio OSV",
                (
                    "Con el intérprete ya actualizado, el job de Ruby se puso **rojo**: "
                    "`bundler-audit` encontró **cuatro advisories de `rack` 3.2.6 publicados "
                    "ese mismo día**, uno de ellos HIGH (`GHSA-5v64-555j-wjxm`, el parser "
                    "multipart retiene lo ya parseado en su buffer de scan y permite agotar "
                    "la memoria).\n\n"
                    "La consulta a OSV para esa misma versión devolvia **cero**: su "
                    "`ruby-advisory-db` iba mas fresca que el índice de OSV. Se corrigió "
                    "subiendo a 3.2.8 y, sobre todo, **fijando el piso en el `Gemfile`**: "
                    "`sinatra` solo pide `>= 3.0.0, < 4`, así que sin piso explícito bundler "
                    "puede volver a resolver una versión vulnerable manana.\n\n"
                    "Lección que queda en el repositorio: los auditores nativos de cada "
                    "ecosistema no son redundantes con una consulta centralizada. Se quedan "
                    "en CI y bloqueando."
                ),
            ),
        ],
    },
    "dotnet": {
        "languages": ["dotnet"],
        "title": ".NET 6 / 9 → 10 (LTS)",
        "icon": "🟦",
        "headline": "El caso 08 llevaba **dos años** sobre un runtime sin parches, y el "
        "caso 19 estaba a nueve días de quedarse igual.",
        "eol": [
            ("6 (LTS)", "2021-11-08", "2024-11-12", "**EOL hace 2 años**"),
            ("8 (LTS)", "2023-11-14", "2026-11-10", "EOL en días"),
            ("9 (STS)", "2024-11-12", "2026-11-10", "**EOL en días**, no es LTS"),
            ("10 (LTS)", "2025-11-11", "2028-11-14", "**adoptada**"),
        ],
        "why": [
            "El `TargetFramework` del caso 08 era `net6.0`: EOL el 2024-11-12. Dos años "
            "sin un solo parche de runtime.",
            "El caso 19 estaba en `net9.0`, que **no es LTS** y cuyo EOL es el "
            "2026-11-10. Subirlo a 9 otra vez habría sido trabajo tirado.",
            ".NET alterna LTS (impares... en realidad pares: 6, 8, 10) y STS. Ir a **10** "
            "da soporte hasta 2028-11-14 y evita volver a tocar esto en un año.",
        ],
        "risk": "Medio. Es el salto de mas majors del pase (6 → 10). El emisor del caso "
        "08 es una consola con `HttpClient` y el del 19 un publicador F#, ambos "
        "sin API retirada conocida. El job `Dotnet Origin (08)` compila sobre el "
        "SDK 10 y pasa; el caso 19 solo se compila dentro de su imagen Docker, "
        "que **no se construyo** en este pase.",
        "sources": [
            "https://endoflife.date/dotnet",
            "https://dotnet.microsoft.com/platform/support/policy",
        ],
    },
    "alpine": {
        "languages": ["alpine"],
        "title": "Alpine 3.20 → 3.23.7",
        "icon": "🏔️",
        "headline": "La capa de sistema operativo de cinco imagenes estaba sin parches "
        "desde el 2026-04-01.",
        "eol": [
            ("3.20", "2024-05-22", "2026-04-01", "**EOL**"),
            ("3.21", "2024-12-05", "2026-11-01", "EOL hoy"),
            ("3.22", "2025-05-29", "2027-05-01", "con soporte"),
            ("3.23", "2025-11-?", "2027-11-01", "**adoptada**"),
            ("3.24", "2026-06-?", "2028-06-01", "recien salida"),
        ],
        "why": [
            "Alpine mantiene cada rama estable **dos años**. La 3.20 salió de soporte el "
            "2026-04-01: `openssl`, `musl`, `busybox` y `zlib` dejaron de recibir "
            "parches en esas imagenes.",
            "Afecta a las imagenes de runtime de los casos 02, 13, 15, 17 y 18, que son "
            "binarios estaticos sobre `alpine` desnuda — precisamente donde la única "
            "superficie de ataque **es** el sistema operativo.",
            "Se pinnea al parche exacto (`3.23.7`) y no a `3.23`, para que el build sea "
            "reproducible y el guardrail de imagenes tenga algo concreto que comprobar.",
        ],
        "risk": "Muy bajo. Las imagenes solo copian un binario estatico y, en el caso 11, "
        "instalan `libstdc++` y `ncurses` por `apk`.",
        "sources": [
            "https://endoflife.date/alpine",
            "https://alpinelinux.org/releases/",
        ],
    },
    "rust": {
        "languages": ["rust"],
        "title": "Rust 1.83 → 1.99",
        "icon": "🦀",
        "headline": "Sin advisories en el toolchain, pero 16 releases de retraso. Y el "
        "`Cargo.lock` esconde cuatro hallazgos abiertos.",
        "eol": [
            ("1.83", "2024-11-28", "sin EOL formal", "16 releases atrás"),
            ("1.99", "2026-10-01", "última estable", "**adoptada**"),
        ],
        "why": [
            "Rust no tiene ramas de soporte: hay una estable cada seis semanas y la "
            "corrección llega en la siguiente. Quedarse en 1.83 (noviembre de 2024) no "
            "deja CVE abierto en el compilador, pero si deuda de dos años.",
            "El motivo real para moverlo es que el toolchain antiguo limita las versiones "
            "de crates que se pueden resolver, lo que a su vez bloquea las correcciones "
            "de seguridad de las dependencias.",
        ],
        "risk": "Bajo para el compilador; la edicion `2021` sigue soportada. Pero ver el "
        "apartado de hallazgos abiertos: lo que si esta vulnerable son crates "
        "transitivas del lock.",
        "sources": ["https://endoflife.date/rust", "https://releases.rs/"],
        "extra": [
            (
                "Hallazgos ABIERTOS en los Cargo.lock",
                (
                    "`cargo audit` pasó en **verde** en CI. La consulta a OSV sobre las "
                    "versiones exactas de los dos `Cargo.lock` encontró, en cambio, cinco "
                    "crates vulnerables: `rustls` 0.23.41 (8 advisories, entre ellos secretos "
                    "TLS expuestos por los `impl Debug` de sesion), `h2` 0.4.15, "
                    "`rustls-webpki` 0.103.13 y `tokio` 1.52.3 en los dos casos.\n\n"
                    "**No estan corregidos.** El `Cargo.lock` lleva un checksum por crate y "
                    "la lista de dependencias de cada versión: editarlo a mano no es "
                    "verificable y romperia el build. La corrección correcta es "
                    "`cargo update -p <crate>` en una máquina con toolchain Rust, que aquí no "
                    "hay. Quedan declarados como `open_findings` en el `security.yml` de cada "
                    "caso, y el guardrail obliga a que lleven severidad y versión de "
                    "corrección. Dependabot (ecosistema `cargo`, que ahora **también** cubre "
                    "el caso 17) regenera el lock correctamente.\n\n"
                    "Es el espejo del caso de `rack`: alli OSV se quedó corto y "
                    "`bundler-audit` acertó; aquí `cargo audit` se quedó corto y acertó OSV."
                ),
            ),
        ],
    },
    "beam": {
        "languages": ["erlang", "elixir"],
        "title": "Erlang/OTP 27 → 28 · Elixir 1.17 → 1.18",
        "icon": "💜",
        "headline": "Sin urgencia en la máquina virtual, pero `cowboy` arrastraba tres "
        "advisories, uno de ellos HIGH.",
        "eol": [
            ("OTP 27", "2024-05-20", "2027-05-20", "con soporte"),
            ("OTP 28", "2025-05-20", "2028-05-20", "**adoptada**"),
            ("OTP 29", "2026-05-11", "2029-05-11", "última"),
        ],
        "why": [
            "OTP 27 aun tiene soporte hasta 2027: el salto a 28 es margen, no urgencia.",
            "Emisor y receptor se mueven juntos para que compartan la misma OTP: el "
            "emisor pasa a `elixir:1.18-otp-28-alpine`. El código usa el módulo `:json` "
            "de OTP, disponible desde la 27.",
            "Lo que si era urgente es `cowboy` 2.12.0 → 2.20.0, el servidor HTTP del "
            "receptor: acumulacion de buffer sin límite al parsear cabeceras multipart "
            "(`CVE-2026-8466`, HIGH), bypass de `max_headers` con nombres duplicados "
            "(`CVE-2026-65624`) y HTTP request/response splitting (`CVE-2026-43966`).",
        ],
        "risk": "Bajo. El receptor es Cowboy + Mnesia embebida; el emisor usa `:httpc`. "
        "Ninguno de los dos se compila en el pipeline: solo dentro de su imagen "
        "Docker, que **no se construyo** en este pase.",
        "sources": ["https://endoflife.date/erlang", "https://endoflife.date/elixir"],
    },
    "crystal": {
        "languages": ["crystal"],
        "title": "Crystal 1.14 → 1.22",
        "icon": "💠",
        "headline": "Ocho versiones menores de retraso. Sin CVE, pero con el framework "
        "web del caso anclado a una rama vieja.",
        "eol": [
            ("1.14", "2024-10-?", "sin EOL formal", "8 menores atrás"),
            ("1.22", "2026-10-30", "última estable", "**adoptada**"),
        ],
        "why": [
            "Crystal no publica ventanas de soporte: solo hay una última estable.",
            "El motor del cambio es `kemal`, el framework del receptor: la 1.15.0 exige "
            "`crystal >= 1.12.0`, así que el `shard.yml` sube de `~> 1.6.0` a "
            "`~> 1.15.0` y el requisito declarado de Crystal pasa de `>= 1.10.0` a "
            "`>= 1.12.0`.",
        ],
        "risk": "**El mas alto del pase.** Es un salto de ocho menores en un lenguaje "
        "pre-1.0 en lo que respecta a estabilidad de librerias, y no hay "
        "compilador Crystal en la máquina ni en el pipeline: el caso solo se "
        "compila dentro de su imagen Docker, que no se construyo. Es el primer "
        "sitio donde mirar si el build falla.",
        "sources": [
            "https://crystal-lang.org/releases/",
            "https://github.com/kemalcr/kemal",
        ],
    },
    "swift": {
        "languages": ["swift"],
        "title": "Swift 6.0 → 6.2",
        "icon": "🧡",
        "headline": "Mantenimiento: dos años de retraso en el emisor del caso 20.",
        "eol": [
            ("6.0", "2024-09-17", "sin EOL formal", "2 años atrás"),
            ("6.2", "2025-09-?", "rama soportada", "**adoptada**"),
            ("6.4", "2026-10-30", "última", "no adoptada"),
        ],
        "why": [
            "Swift no publica ventanas de soporte por rama; la corrección llega en la "
            "siguiente versión.",
            "Se va a 6.2 y no a 6.4 porque el `Package.swift` declara "
            "`swift-tools-versión:5.9` y 6.2 es la rama mas rodada que lo sigue "
            "aceptando sin cambios.",
        ],
        "risk": "Bajo. El emisor es un ejecutable con `URLSession` y `Codable`. No se "
        "compila en el pipeline.",
        "sources": ["https://www.swift.org/download/"],
    },
    "dart": {
        "languages": ["dart", "debian"],
        "title": "Dart y Debian: fuera los tags flotantes",
        "icon": "🎯",
        "headline": "`dart:stable` y `debian:stable-slim` no son versiones: son "
        "punteros moviles. El build no era reproducible.",
        "eol": [
            ("dart:stable", "—", "tag movil", "**eliminado**"),
            ("dart:3.10-sdk", "2026-?", "rama fijada", "**adoptada**"),
            ("debian:stable-slim", "—", "tag movil", "**eliminado**"),
            ("debian:13-slim", "2025-08-09", "trixie, estable", "**adoptada**"),
        ],
        "why": [
            "Un tag movil hace que **la misma linea de `Dockerfile` produzca imagenes "
            "distintas** según el día. Dos builds del mismo commit no son comparables, y "
            "un fallo nuevo no se puede atribuir a un cambio del repositorio.",
            "Ademas deja ciego al guardrail: `check_runtime_security.py` rechaza "
            "`:latest`, pero `stable` es exactamente el mismo problema con otro nombre, y "
            "no habia nada concreto que comprobar.",
            "El `pubspec.yaml` declara `sdk: >=3.5.0 <4.0.0`, que `dart:3.10-sdk` cumple. "
            "`debian:13-slim` es trixie, la estable actual.",
        ],
        "risk": "Bajo, y de hecho **reduce** riesgo: a partir de ahora el build es "
        "reproducible. No se compila en el pipeline.",
        "sources": [
            "https://hub.docker.com/_/dart",
            "https://www.debian.org/releases/",
        ],
    },
    "jvm": {
        "languages": ["java", "gradle"],
        "title": "JVM: Temurin 21 se queda, Gradle 8.11 → 8.14",
        "icon": "☕",
        "headline": "El único apartado donde la decision correcta fue **no** subir el "
        "runtime. Lo que si estaba vulnerable eran las librerias.",
        "eol": [
            ("Temurin 21 (LTS)", "2023-09-19", "2029-12-31", "**se mantiene**"),
            ("Temurin 25 (LTS)", "2025-09-16", "2031-09-30", "no adoptada"),
            ("Gradle 8.11", "2024-11-?", "—", "última 8.x: 8.14"),
            ("Gradle 8.14", "2025-?", "—", "**adoptada**"),
        ],
        "why": [
            "Java 21 es LTS con soporte hasta **2029-12-31** y el tag `21-jre-alpine` ya "
            "trae el último parche. Subir a 25 no cerraria ningun advisory y obligaria a "
            "Gradle 9 y a revisar el toolchain de Kotlin: coste sin beneficio de "
            "seguridad.",
            "Gradle sube al último parche de la linea 8.x, compatible con el plugin de "
            "Spring Boot 3.5.",
            "La imagen del emulador de Firestore (caso 20) pasa de "
            "`21-jdk-jammy` a `21-jdk-noble`: Ubuntu 22.04 → 24.04 LTS, mas margen de "
            "parches de OS.",
        ],
        "risk": "Bajo. Pero ver el apartado siguiente: aquí el riesgo no estaba en el "
        "runtime.",
        "sources": [
            "https://endoflife.date/eclipse-temurin",
            "https://gradle.org/releases/",
        ],
        "extra": [
            (
                "Dónde estaba el riesgo de verdad",
                (
                    "Tres cadenas de dependencias JVM arrastraban advisories abiertos, y "
                    "ninguna se arregla subiendo la JVM:\n\n"
                    "**Spring Boot 3.3.5 → 3.5.16** (caso 10, emisor). La rama 3.3 salió del "
                    "soporte OSS. Pero el problema de fondo es que **Spring Boot 3.5.16 "
                    "gestiona `jackson-bom` 2.21.4**, que arrastra `jackson-databind` con "
                    "**9 advisories abiertos**. Subir Boot no basta: hay que pisar la "
                    'propiedad del BOM con `ext["jackson-bom.versión"] = "2.21.8"`, que '
                    "reemplaza toda la familia Jackson de una vez.\n\n"
                    "**pgjdbc 42.7.4 → 42.7.12** (caso 10, receptor). Tres advisories HIGH de "
                    "autenticación: fallback a autenticación insegura **aunque se pida "
                    "`channelBinding=require`** (`CVE-2025-49146`), iteraciones PBKDF2 sin "
                    "límite en SCRAM (`CVE-2026-42198`) y downgrade silencioso del channel "
                    "binding (`CVE-2026-54291`).\n\n"
                    "**ring 1.12.2 → 1.15.6** (caso 19). `ring-jetty-adapter` 1.12.2 fija "
                    "**Jetty 11**, con tres advisories abiertos. La 1.15.6 pasa a Jetty "
                    "12.1.14, por encima del piso de los cinco. Y `cheshire` 6.2.0 fija "
                    "`jackson-core` 2.21.1, por debajo del piso 2.21.7: se añade "
                    "`jackson-core` 2.21.8 como **dependencia directa** del `project.clj` "
                    "para pisar la transitiva.\n\n"
                    "**Ktor 2.3.13 se mantiene**: no tiene advisory abierto, y Ktor 3.x "
                    "cambia la API (migracion a `kotlinx-io`). Subir de major sin un fallo "
                    "que lo justifique es cambio por el cambio."
                ),
            ),
        ],
    },
    "pnpm": {
        "languages": ["pnpm"],
        "title": "pnpm 10 → 11: npm fuera del laboratorio",
        "icon": "📦",
        "headline": "Y la trampa mas peligrosa del pase: pnpm 11 **ya no lee** el campo "
        "`pnpm` de `package.json`.",
        "eol": [
            ("pnpm 10", "2025-01-?", "—", "no lee Node >= 22.13"),
            ("pnpm 11.2.2", "2026-?", "—", "**adoptada**"),
            ("pnpm 12.16.1", "2026-10-?", "última", "no adoptada: ver abajo"),
        ],
        "why": [
            "pnpm 11 trae las dos defensas que importan contra campañas tipo "
            "**Shai-Hulud**: los scripts de instalacion estan **bloqueados por defecto** "
            "y hay **cuarentena** configurable sobre versiones recien publicadas. El "
            "vector de esas campañas es justo un `postinstall` en un paquete recien "
            "comprometido.",
            "Exige Node >= 22.13, así que no se podia activar mientras el laboratorio "
            "estaba en Node 20. Los dos cambios van juntos.",
            "Se fija **11.2.2 y no 12.16.1** a propósito: 11.2.2 es la versión con la que "
            "se regeneraron y auditaron los 9 lockfiles en esta máquina. Fijar lo "
            "verificado vale mas que fijar lo último.",
        ],
        "risk": "Bajo en ejecucion, **alto si no se hubiera detectado la trampa**. Los 9 "
        "paquetes cierran `pnpm audit` sin vulnerabilidades.",
        "sources": ["https://pnpm.io/settings", "https://pnpm.io/npmrc"],
        "extra": [
            (
                "La política que estuvo a punto de desactivarse en silencio",
                (
                    "El repositorio protegia sus transitivas con `pnpm.overrides` dentro de "
                    "`package.json`. **pnpm 11 ya no lee ese campo**: al actualizar, los "
                    "`overrides` de seguridad y el `onlyBuiltDependencies` habrían quedado "
                    "inertes sin un solo mensaje de error, y el lockfile se habría "
                    "regenerado sin ellos.\n\n"
                    'Se detectó porque pnpm emite un `[WARN] The "pnpm" field in '
                    "package.json is no longer read` — fácil de pasar por alto entre el ruido "
                    "de un install. La política se traslado a un `pnpm-workspace.yaml` por "
                    "paquete, y se **comprobó** que vuelve a aplicarse: el bloque "
                    "`overrides:` reaparece en el lockfile resuelto.\n\n"
                    "```yaml\n"
                    "onlyBuiltDependencies: []   # ningun paquete ejecuta postinstall\n"
                    "minimumReleaseAge: 1440     # cuarentena de 24 h\n"
                    "overrides: ...              # pisos de versión por CVE\n"
                    "```\n\n"
                    "La prueba de que funciona llego sola: al instalar el caso 16, pnpm "
                    "**bloqueó** el `postinstall` de `@apollo/protobufjs`."
                ),
            ),
            (
                "npm: cero invocaciones",
                (
                    "`npm` ya no se ejecuta en ninguna superficie del repositorio:\n\n"
                    "| Donde | Antes | Ahora |\n"
                    "| :--- | :--- | :--- |\n"
                    "| `.github/workflows/ci-cd.yml` | `npm install -g pnpm@10` | "
                    "`corepack enable && corepack prepare pnpm@11.2.2 --activate` |\n"
                    "| `.claude/settings.local.json` | `npx --yes pnpm@10 audit` | "
                    "`pnpm audit` |\n"
                    "| `.gitignore` | solo `cases/*/dest/package-lock.json` | "
                    "`package-lock.json`, `npm-shrinkwrap.json` y las tres rutas de casos |\n"
                    "| Dockerfiles Node | `pnpm install --prod` | "
                    "`pnpm install --prod --frozen-lockfile` |\n\n"
                    "El ecosistema de Dependabot sigue llamandose `npm` porque es el nombre "
                    "del **registro**, no del gestor: lee los `pnpm-lock.yaml` sin ejecutar "
                    "npm."
                ),
            ),
        ],
    },
    "zig": {
        "languages": ["zig"],
        "title": "Zig 0.13: por qué NO se subió",
        "icon": "⚡",
        "headline": "La decision de no tocar algo también es una decision, y merece "
        "quedar escrita.",
        "eol": [
            ("0.13.0", "2024-06-?", "sin EOL formal", "**se mantiene**"),
            ("0.17.0", "2026-?", "última", "no adoptada"),
        ],
        "why": [
            "Zig **no tiene ningun advisory** en OSV: no hay un fallo de seguridad que "
            "subir de versión cierre.",
            "La ruta 0.13 → 0.17 rompe el sistema de build. La 0.15 reescribió la API de "
            "`std.Io` (lo que la comunidad llamo *Writergate*), de modo que el "
            "`build.zig` y el código del emisor necesitarian reescritura.",
            "No hay toolchain Zig en esta máquina ni en el pipeline: el caso solo se "
            "compila dentro de su imagen Docker. Subir a ciegas una versión que rompe la "
            "API, sin poder compilar y sin un CVE que lo justifique, es cambiar por "
            "cambiar.",
            "Lo que **si** se parcheo es la capa que de verdad tenia riesgo: la Alpine "
            "sobre la que compila, de 3.20 (sin parches desde el 2026-04-01) a 3.23.7.",
        ],
        "risk": "Ninguno anadido. El riesgo que queda es la deuda tecnica de un "
        "toolchain de 2024, no una vulnerabilidad.",
        "sources": ["https://ziglang.org/download/", "https://osv.dev/"],
    },
}


def load_docs() -> list[dict]:
    out = []
    for p in sorted((ROOT / "cases").glob("*/security.yml")):
        d = yaml.safe_load(p.read_text(encoding="utf-8"))
        d["_slug"] = p.parent.name
        out.append(d)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    docs = load_docs()
    indice: list[tuple[str, str, str, str, str, int]] = []

    for slug, meta in LANGS.items():
        langs = set(meta["languages"])
        runtimes = [
            (d["case"], rt)
            for d in docs
            for rt in d["runtimes"]
            if rt["language"] in langs
        ]
        deps = [
            (d["case"], dep)
            for d in docs
            for dep in (d["dependencies"] or [])
            if dep["ecosystem"] in _ECOS.get(slug, set())
        ]
        advisories = sorted({a for _, dep in deps for a in (dep["advisories"] or [])})
        casos = sorted({c for c, _ in runtimes})

        L: list[str] = []
        A = L.append
        A(f"# {meta['icon']} {meta['title']}")
        A("")
        A(f"> {meta['headline']}")
        A("")
        A(
            "[← Volver al índice de actualizaciones](../VERSION_UPGRADES.md) · "
            "[README](../../README.md)"
        )
        A("")
        A("---")
        A("")
        A("## Resumen")
        A("")
        A("| | |")
        A("| :--- | :--- |")
        A(f"| **Casos afectados** | {len(casos)} ({', '.join(casos)}) |")
        A(f"| **Cambios de versión registrados** | {len(runtimes)} |")
        A(
            f"| **Advisories cerrados en dependencias de este stack** | {len(advisories)} |"
        )
        A(f"| **Riesgo de ruptura** | {meta['risk'].split('.')[0]} |")
        A("")
        A("## Ventanas de soporte")
        A("")
        A("| Versión | Publicada | Fin de soporte | Estado |")
        A("| :--- | :--- | :--- | :--- |")
        for v, rel, eol, estado in meta["eol"]:
            A(f"| `{v}` | {rel} | {eol} | {estado} |")
        A("")
        A("```mermaid")
        A("%%{init: {'theme':'neutral'}}%%")
        A("gantt")
        A("    title Soporte de seguridad por versión")
        A("    dateFormat YYYY-MM-DD")
        A("    axisFormat %Y")
        A("    todayMarker stroke-width:3px,stroke:#dc2626,opacity:0.9")
        A("    section Abandonadas")
        for v, rel, eol, estado in meta["eol"]:
            if "EOL" in estado and "inminente" not in estado:
                if _is_date(rel) and _is_date(eol):
                    A(f"    {v} :done, {rel}, {eol}")
        A("    section Vigentes")
        for v, rel, eol, estado in meta["eol"]:
            if "EOL" not in estado or "inminente" in estado:
                ini = rel if _is_date(rel) else "2024-01-01"
                fin = eol if _is_date(eol) else "2029-12-31"
                marca = (
                    "crit" if "adoptada" in estado or "mantiene" in estado else "active"
                )
                A(f"    {v} :{marca}, {ini}, {fin}")
        A("```")
        A("")
        A("## Por qué se cambió")
        A("")
        for w in meta["why"]:
            A(f"- {w}")
            A("")
        for titulo, cuerpo in meta.get("extra", []):
            A(f"## {titulo}")
            A("")
            A(cuerpo)
            A("")
        A("## Implementación — dónde quedó escrito cada cambio")
        A("")
        A(
            "Las rutas de esta tabla las verifica `scripts/validate_security_manifests.py` "
            "en CI: si alguna no existe, el pipeline falla."
        )
        A("")
        A("| Caso | Componente | De | A | Motivo | Fichero y mecanismo |")
        A("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for caso, rt in runtimes:
            A(
                f"| {caso} | {rt['component']} | `{rt['from']}` | `{rt['to']}` | "
                f"`{rt['reason']}` | {rt['applied_in']} |"
            )
        A("")
        if deps:
            A("## Dependencias de este stack")
            A("")
            A(
                "| Caso | Paquete | De | A | Severidad | Advisories | Fichero y mecanismo |"
            )
            A("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for caso, dep in deps:
                adv = ", ".join(dep["advisories"] or []) or "—"
                A(
                    f"| {caso} | `{dep['package']}` | `{dep['from']}` | `{dep['to']}` | "
                    f"{dep['severity']} | {adv} | {dep['applied_in']} |"
                )
            A("")
        A("## Riesgo y verificación")
        A("")
        A(meta["risk"])
        A("")
        A("## Fuentes")
        A("")
        for s in meta["sources"]:
            A(f"- <{s}>")
        A("")

        (OUT_DIR / f"{slug}.md").write_text("\n".join(L), encoding="utf-8")
        indice.append(
            (
                slug,
                meta["icon"],
                meta["title"],
                meta["headline"],
                ", ".join(casos),
                len(advisories),
            )
        )
        print(f"docs/upgrades/{slug}.md  ({len(runtimes)} runtimes, {len(deps)} deps)")

    escribir_indice(indice)
    escribir_readme(indice)
    return indice


_ECOS = {
    "go": {"Go"},
    "nodejs": {"npm"},
    "python": {"PyPI"},
    "php": set(),
    "ruby": {"RubyGems"},
    "dotnet": {"NuGet"},
    "alpine": set(),
    "rust": {"crates.io"},
    "beam": {"Hex"},
    "crystal": {"Crystal/shards"},
    "swift": set(),
    "dart": {"Pub"},
    "jvm": {"Maven"},
    "pnpm": set(),
    "zig": set(),
}


def _is_date(s: str) -> bool:
    import re as _re

    return bool(_re.match(r"^\d{4}-\d{2}-\d{2}$", s))


# ==================================================================================================
# Indice vivo (docs/VERSION_UPGRADES.md) y bloque del README
# ==================================================================================================

PROCESO = """## Cómo se hace una subida de versión en este repositorio

Este documento **no es el registro de un release concreto**: es el procedimiento, y se
amplía con cada pase. El de abajo es el orden que se siguió y el que hay que seguir.

### 1. Inventariar lo que hay, no lo que se recuerda

```bash
# Imágenes base de cada caso
grep -rn "^FROM" --include=Dockerfile cases/ Dockerfile
grep -n "image:" docker-compose.yml

# Manifiestos de dependencias por ecosistema
find cases -name "go.mod" -o -name "package.json" -o -name "requirements.in" \\
     -o -name "build.gradle.kts" -o -name "project.clj" -o -name "Cargo.toml" \\
     -o -name "Gemfile" -o -name "rebar.config" -o -name "shard.yml" \\
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
curl -s -o /dev/null -w "%{http_code}\\n" \\
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
uv pip compile --upgrade --universal --generate-hashes --python-version 3.13 \\
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
"""


def escribir_indice(indice):
    L = []
    A = L.append
    A("# 🔼 Mejoras de versión y remediación de CVE")
    A("")
    A(
        "> Documento **vivo**. El índice de abajo se regenera desde los 20 "
        "`cases/NN-*/security.yml` con `python scripts/build_upgrade_docs.py`."
    )
    A("")
    A(
        "Aquí está el detalle de cada cambio de versión del laboratorio: qué se movió, "
        "contra qué advisory, dónde quedó escrito y qué riesgo tiene. El README lleva el "
        "resumen; esto es el expediente."
    )
    A("")
    A("---")
    A("")
    A("## Índice de cambios")
    A("")
    A("| Stack | Cambio | Casos | Advisories | Detalle |")
    A("| :--- | :--- | :--- | ---: | :--- |")
    for slug, icon, title, _headline, casos, n_adv in indice:
        A(
            f"| {icon} | **{title}** | {casos or '—'} | {n_adv or '—'} | "
            f"[Ver documentación](upgrades/{slug}.md) |"
        )
    A("")
    A(
        "Cada página lleva: ventanas de soporte con gráfico, la justificación del cambio, "
        "la tabla de implementación fichero a fichero, las dependencias del stack con sus "
        "advisories, el riesgo de ruptura y las fuentes."
    )
    A("")
    A("---")
    A("")
    A(PROCESO)
    A("")
    A("---")
    A("")
    A("## Historial de pases")
    A("")
    A("### v4.11.0 — 2026-11-01")
    A("")
    A("Primer pase sistemático. Ningún runtime del laboratorio queda en EOL.")
    A("")
    A("| | |")
    A("| :--- | ---: |")
    A(f"| Casos revisados | {len(load_docs())} / 20 |")
    _d = load_docs()
    _rt = sum(len(x["runtimes"]) for x in _d)
    _dp = sum(len(x["dependencies"] or []) for x in _d)
    _adv = {
        a
        for x in _d
        for dep in (x["dependencies"] or [])
        for a in (dep["advisories"] or [])
    }
    _open = sum(len(x.get("open_findings") or []) for x in _d)
    A(f"| Cambios de runtime / imagen base | {_rt} |")
    A(f"| Entradas de dependencia revisadas | {_dp} |")
    A(f"| Advisories cerrados | {len(_adv)} |")
    A(
        f"| · de ellos con identificador CVE | {len([a for a in _adv if a.startswith('CVE-')])} |"
    )
    A(f"| Hallazgos declarados ABIERTOS | {_open} |")
    A("")
    A(
        "Detalle por stack en el índice de arriba. Entrada completa en "
        "[CHANGELOG.md](../CHANGELOG.md)."
    )
    A("")
    A("---")
    A("")
    A("## Hallazgos ABIERTOS")
    A("")
    A(
        "Un informe que solo lista lo cerrado no es un informe de seguridad. Esto sigue "
        "vulnerable y está declarado como `open_findings` en el `security.yml` de su caso, "
        "de modo que el guardrail no puede presentarlo como resuelto."
    )
    A("")
    A("| Caso | Paquete | Versión | Corrige en | Severidad | Advisories |")
    A("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for x in _d:
        for f in x.get("open_findings") or []:
            A(
                f"| {x['case']} | `{f['ecosystem']}/{f['package']}` | {f['version']} | "
                f"**{f['fix_version']}** | {f['severity']} | {', '.join(f['advisories'])} |"
            )
    A("")
    A(
        "Los cinco son transitivas de los `Cargo.lock` de los dos casos Rust y requieren "
        "`cargo update -p <crate>` en una máquina con toolchain Rust: el lock lleva un "
        "checksum por crate, así que editarlo a mano no es verificable. Contexto completo "
        "en [la página de Rust](upgrades/rust.md)."
    )
    A("")
    A("---")
    A("")
    A("## Lo que NO se subió, y por qué")
    A("")
    A("| Qué | Versión actual | Por qué se conserva |")
    A("| :--- | :--- | :--- |")
    A(
        "| **Zig** | 0.13.0 | Sin advisories. 0.13 → 0.17 rompe el sistema de build "
        "(*Writergate* en 0.15) y no hay toolchain para verificar. "
        "[Detalle](upgrades/zig.md) |"
    )
    A(
        "| **Ktor** | 2.3.13 | Sin advisory. Ktor 3.x migra a `kotlinx-io`. "
        "[Detalle](upgrades/jvm.md) |"
    )
    A("| **XTDB** | 1.24.3 | Sin advisory. La rama 2.x es una reescritura completa |")
    A(
        "| **Express** | 4.22.x | Express 5 es ruptura; los advisories de la 4 se cierran "
        "con 4.22.3 + `overrides`. [Detalle](upgrades/nodejs.md) |"
    )
    A(
        "| **Next.js** | 15.5.28 | Next 16 es ruptura; 15.5.28 está sobre el piso de los "
        "38 advisories. [Detalle](upgrades/nodejs.md) |"
    )
    A("| **Spring Boot** | 3.5.16 | Boot 4 es ruptura. [Detalle](upgrades/jvm.md) |")
    A(
        "| **Driver MongoDB** | 6.21.0 | El major 7 es ruptura y el 6 no tiene advisory |"
    )
    A(
        "| **`reqwest` / `rumqttc`** | 0.12 / 0.24 | Sin advisory en la crate directa. "
        "[Detalle](upgrades/rust.md) |"
    )
    A(
        "| **Java** | Temurin 21 LTS | Soporte hasta 2029-12-31. "
        "[Detalle](upgrades/jvm.md) |"
    )
    A(
        "| **pnpm** | 11.2.2 | Existe 12.16.1, pero 11.2.2 es la versión con la que se "
        "auditaron los 9 lockfiles. [Detalle](upgrades/pnpm.md) |"
    )
    A(
        "| **Imágenes de BD e infraestructura** | sin cambios | Este pase cubre "
        "**lenguajes**. `mongo:6.0` e `influxdb:1.8` son las más atrasadas y merecen un "
        "pase propio |"
    )
    A("")
    (ROOT / "docs" / "VERSION_UPGRADES.md").write_text(
        "\n".join(L) + "\n", encoding="utf-8"
    )
    print("docs/VERSION_UPGRADES.md")


INICIO = "<!-- UPGRADES:INICIO (generado por scripts/build_upgrade_docs.py) -->"
FIN = "<!-- UPGRADES:FIN -->"


def escribir_readme(indice):
    _d = load_docs()
    _rt = sum(len(x["runtimes"]) for x in _d)
    _dp = sum(len(x["dependencies"] or []) for x in _d)
    _adv = {
        a
        for x in _d
        for dep in (x["dependencies"] or [])
        for a in (dep["advisories"] or [])
    }
    _open = sum(len(x.get("open_findings") or []) for x in _d)

    L = []
    A = L.append
    A(INICIO)
    A("")
    A(
        "**Un runtime en fin de vida no arrastra «un CVE»: arrastra todos los publicados "
        "desde su último parche.** Por eso la revisión de la v4.11.0 recorrió los 20 "
        "casos lenguaje por lenguaje, hasta que ninguno quedara sobre una versión sin "
        "soporte."
    )
    A("")
    A(
        f"| Advisories cerrados | Cambios de runtime | Dependencias revisadas | "
        f"Runtimes en EOL | Hallazgos abiertos |"
    )
    A("| ---: | ---: | ---: | ---: | ---: |")
    A(
        f"| **{len(_adv)}** ({len([a for a in _adv if a.startswith('CVE-')])} con CVE) | "
        f"**{_rt}** | **{_dp}** | **0** | **{_open}** (declarados) |"
    )
    A("")
    A(
        "«Casos» es a cuántos de los 20 afecta el cambio; cada página lista cuáles. Ahí "
        "están también la ventana de soporte con su gráfico, la justificación, la tabla "
        "de implementación fichero a fichero y el riesgo de ruptura."
    )
    A("")
    A("| Cambio | Casos | Advisories | Por qué | Documentación |")
    A("| :--- | ---: | ---: | :--- | :--- |")
    MOTIVO = {
        "go": "EOL desde 2024-08-13; 72 advisories de stdlib",
        "nodejs": "EOL desde 2026-04-30",
        "python": "Solo-seguridad; base Debian 12 → 13",
        "php": "Soporte activo cerrado en 2024-12-31",
        "ruby": "EOL desde 2026-03-31",
        "dotnet": ".NET 6 llevaba 2 años sin parches",
        "alpine": "Sin parches desde 2026-04-01",
        "rust": "16 releases de retraso",
        "beam": "`cowboy` con 3 advisories, uno HIGH",
        "crystal": "`kemal` 1.15 exige Crystal ≥ 1.12",
        "swift": "2 años de retraso",
        "dart": "Tags flotantes: build irreproducible",
        "jvm": "Jackson, pgjdbc y Jetty vulnerables",
        "pnpm": "Mitigación Shai-Hulud + npm fuera",
        "zig": "**No se subió**: sin advisory y rompe el build",
    }
    for slug, icon, title, _h, casos, n_adv in indice:
        n_casos = len(casos.split(", ")) if casos else 0
        A(
            f"| {icon} **{title}** | {n_casos or '—'} | {n_adv or '—'} | "
            f"{MOTIVO.get(slug, '—')} | [Ver detalle](docs/upgrades/{slug}.md) |"
        )
    A("")
    A(
        "> 📘 **Procedimiento, historial y hallazgos abiertos**: "
        "[docs/VERSION_UPGRADES.md](docs/VERSION_UPGRADES.md) — el documento vivo que "
        "explica cómo se hace una subida de versión aquí, para este pase y los siguientes."
    )
    A("")
    A(FIN)

    readme = ROOT / "README.md"
    t = readme.read_text(encoding="utf-8")
    bloque = "\n".join(L)
    if INICIO in t and FIN in t:
        ini = t.index(INICIO)
        fin = t.index(FIN) + len(FIN)
        t = t[:ini] + bloque + t[fin:]
        readme.write_text(t, encoding="utf-8")
        print("README.md: bloque de upgrades actualizado")
    else:
        (ROOT / "docs" / "_readme_block.md").write_text(bloque + "\n", encoding="utf-8")
        print("README.md: sin marcadores; bloque escrito en docs/_readme_block.md")


if __name__ == "__main__":
    main()
