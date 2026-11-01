#!/usr/bin/env python3
"""Guardrail de los manifiestos de seguridad por caso (`cases/NN-*/security.yml`).

Por que existe
--------------
Un fichero de seguridad que nadie valida se convierte en documentacion muerta: dice
que un runtime esta en una version y el Dockerfile dice otra. Este script cruza las
tres fuentes y falla en CI si se separan:

  1. Que los 20 casos tengan `security.yml` y que `app.manifest.yml` lo apunte.
  2. Que la estructura sea la esperada y que `lab_version` coincida con la version
     declarada en el badge del README (la unica fuente de verdad de version del repo).
  3. Que toda version `to` de un runtime que nombre una imagen aparezca de verdad en
     algun Dockerfile o en docker-compose.yml. Si alguien baja una imagen y se olvida
     del manifiesto (o al contrario), el conteo no cuadra y el job se cae.
  4. Que ningun `FROM` ni `image:` del repositorio siga usando una version que algun
     `security.yml` declara como ya abandonada (`from`), que es el fallo clasico:
     se parchea un caso y queda otro con la imagen vieja.

No comprueba si existen CVE nuevos: eso es trabajo de `pip-audit`, `pnpm audit`,
`govulncheck`, `cargo audit`, `bundler-audit` y Dependabot. Aqui solo se verifica
que lo que el repositorio AFIRMA sobre sus versiones sea cierto.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - UX en maquinas limpias
    print("Falta pyyaml: pip install pyyaml", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = ROOT / "cases"
README = ROOT / "README.md"
COMPOSE = ROOT / "docker-compose.yml"

EXPECTED_CASES = 20
VALID_REASONS = {
    "eol",
    "fin-de-soporte",
    "fin-de-soporte-activo",
    "mantenimiento",
    "endurecimiento",
    "sin-cambio",
}
# "SIN-CLASIFICAR" existe porque no todo advisory publica una severidad textual:
# muchos RUSTSEC solo traen el vector CVSS. Traducirlo a una etiqueta seria una
# interpretacion nuestra, no un dato de la fuente, asi que se declara como lo que es.
VALID_SEVERITIES = {"CRITICAL", "HIGH", "MODERATE", "LOW", "SIN-CLASIFICAR", "-"}
ADVISORY_RE = re.compile(
    r"^(CVE-\d{4}-\d{4,}|GHSA-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}|"
    r"PYSEC-\d{4}-\d+|RUSTSEC-\d{4}-\d{4}|GO-\d{4}-\d+|EEF-CVE-\d{4}-\d+)$"
)

# Una version `to`/`from` solo se cruza contra los Dockerfiles cuando nombra una
# imagen de verdad. Entradas como "sin cambio", "toolchain stable en CI" o versiones
# de paquete (no de imagen) se saltan: no hay nada que cruzar.
NOT_AN_IMAGE = re.compile(
    r"sin cambio|toolchain|go\.mod|override|con hash|sin pin|pins", re.I
)


def read_version_from_readme() -> str:
    m = re.search(
        r"img\.shields\.io/badge/version-([0-9]+\.[0-9]+\.[0-9]+)-",
        README.read_text(encoding="utf-8"),
    )
    if not m:
        raise SystemExit("No se encontro el badge de version en README.md")
    return m.group(1)


MANIFEST_GLOBS = (
    "cases/*/*/*.csproj",
    "cases/*/*/*.fsproj",
    "cases/*/*/build.gradle.kts",
    "cases/*/*/go.mod",
    "cases/*/*/rebar.config",
    "cases/*/*/mix.exs",
    "cases/*/*/shard.yml",
    "cases/*/*/pubspec.yaml",
    "cases/*/*/project.clj",
    "cases/*/*/Package.swift",
)


def version_references() -> str:
    """Todo el texto donde puede aparecer la version declarada de un runtime.

    No solo los Dockerfiles: el target framework de .NET vive en el `.csproj` y la
    version de Go en el `go.mod`, asi que los casos sin imagen propia tambien se
    pueden cruzar.
    """
    chunks = []
    for dockerfile in sorted(ROOT.rglob("Dockerfile")):
        if ".claude" in dockerfile.parts or "node_modules" in dockerfile.parts:
            continue
        chunks.append(dockerfile.read_text(encoding="utf-8"))
    for compose in (COMPOSE, ROOT / "docker-compose.dev.yml"):
        if compose.is_file():
            chunks.append(compose.read_text(encoding="utf-8"))
    for pattern in MANIFEST_GLOBS:
        for manifest in sorted(ROOT.glob(pattern)):
            chunks.append(manifest.read_text(encoding="utf-8"))
    return "\n".join(chunks)


IMAGE_REF_RE = re.compile(r"^\s*(?:FROM\s+|image:\s*)([^\s#]+)", re.M | re.I)

# Que nombres de imagen corresponden a cada `language` del manifiesto. Hace falta
# porque los valores `from`/`to` son solo fragmentos de tag: sin esto, el "6.0" de
# swift colisionaria con `mongo:6.0`, que es otra cosa por completo. Un lenguaje que
# no aparece aqui (pnpm, zig) no se distribuye como imagen y no se cruza por tag.
LANGUAGE_IMAGES: dict[str, tuple[str, ...]] = {
    "python": ("python",),
    "nodejs": ("node",),
    "go": ("golang",),
    "php": ("php",),
    "ruby": ("ruby",),
    "rust": ("rust",),
    "erlang": ("erlang",),
    "elixir": ("elixir",),
    "alpine": ("alpine",),
    "crystal": ("crystallang/crystal",),
    "dotnet": ("mcr.microsoft.com/dotnet/sdk", "mcr.microsoft.com/dotnet/runtime"),
    "java": ("eclipse-temurin", "gradle", "clojure"),
    "gradle": ("gradle",),
    "swift": ("swift",),
    "dart": ("dart",),
    "debian": ("debian",),
}


def image_refs_in_use(text: str) -> set[str]:
    """Referencias de imagen realmente usadas, con su tag y sin variables de compose."""
    refs: set[str] = set()
    for raw in IMAGE_REF_RE.findall(text):
        # `image: ${N8N_IMAGE:-n8nio/n8n:2.7.5}` -> se queda el valor por defecto.
        m = re.match(r"^\$\{[A-Z0-9_]+:-(.+)\}$", raw)
        if m:
            raw = m.group(1)
        if raw.startswith("$"):
            continue
        refs.add(raw)
    return refs


def check_structure(path: Path, doc: Any, lab_version: str) -> list[str]:
    issues: list[str] = []
    rel = path.relative_to(ROOT)

    for key in (
        "case",
        "name",
        "lab_version",
        "reviewed",
        "sources",
        "runtimes",
        "dependencies",
    ):
        if key not in doc:
            issues.append(f"{rel}: falta la clave '{key}'")
    if issues:
        return issues

    if doc["lab_version"] != lab_version:
        issues.append(
            f"{rel}: lab_version={doc['lab_version']!r} pero el README declara {lab_version!r}"
        )

    if doc["case"] != path.parent.name.split("-")[0]:
        issues.append(f"{rel}: case={doc['case']!r} no coincide con el directorio")

    if not doc["runtimes"]:
        issues.append(f"{rel}: 'runtimes' no puede estar vacio")

    for i, rt in enumerate(doc["runtimes"] or []):
        for key in (
            "component",
            "language",
            "from",
            "to",
            "reason",
            "detail",
            "applied_in",
        ):
            if key not in rt:
                issues.append(f"{rel}: runtimes[{i}] sin '{key}'")
        if rt.get("reason") not in VALID_REASONS:
            issues.append(
                f"{rel}: runtimes[{i}] reason={rt.get('reason')!r} no es valido "
                f"(validos: {sorted(VALID_REASONS)})"
            )
        if (
            rt.get("reason") == "sin-cambio"
            and rt.get("from") != rt.get("to")
            and "sin cambio" not in str(rt.get("to", ""))
        ):
            issues.append(f"{rel}: runtimes[{i}] dice 'sin-cambio' pero from != to")

    for i, dep in enumerate(doc["dependencies"] or []):
        for key in (
            "ecosystem",
            "package",
            "from",
            "to",
            "advisories",
            "severity",
            "note",
            "applied_in",
        ):
            if key not in dep:
                issues.append(f"{rel}: dependencies[{i}] sin '{key}'")
        if dep.get("severity") not in VALID_SEVERITIES:
            issues.append(
                f"{rel}: dependencies[{i}] severity={dep.get('severity')!r} no es valido"
            )
        advisories = dep.get("advisories") or []
        for a in advisories:
            if not ADVISORY_RE.match(a):
                issues.append(
                    f"{rel}: dependencies[{i}] advisory con formato raro: {a!r}"
                )
        if advisories and dep.get("severity") == "-":
            issues.append(
                f"{rel}: dependencies[{i}] lista advisories pero severity='-'"
            )
        if not advisories and dep.get("severity") != "-":
            issues.append(
                f"{rel}: dependencies[{i}] sin advisories pero severity="
                f"{dep.get('severity')!r}"
            )

    # `applied_in` dice DONDE quedo escrito el cambio. Si cita un fichero que no
    # existe, la documentacion esta mintiendo sobre su propia implementacion, asi que
    # se comprueba ruta por ruta. Las rutas van entre acentos graves.
    for scope in ("runtimes", "dependencies"):
        for i, entry in enumerate(doc.get(scope) or []):
            applied = str(entry.get("applied_in") or "")
            if "(sin cambio" in applied or "(no localizado" in applied:
                if "(no localizado" in applied:
                    issues.append(f"{rel}: {scope}[{i}] tiene applied_in sin resolver")
                continue
            rutas = re.findall(r"`([^`]+)`", applied)
            if not rutas:
                issues.append(
                    f"{rel}: {scope}[{i}] applied_in no cita ninguna ruta entre "
                    f"acentos graves: {applied[:60]!r}"
                )
            for ruta in rutas:
                limpia = ruta.split()[0].strip("`")
                if limpia.startswith("<") or "/" not in limpia:
                    continue  # descripcion, no ruta (p. ej. una propiedad de Gradle)
                if not (ROOT / limpia).is_file():
                    issues.append(
                        f"{rel}: {scope}[{i}] applied_in cita '{limpia}', que no existe"
                    )

    # `open_findings` es opcional y describe lo contrario que `dependencies`: un
    # advisory CONOCIDO y NO remediado. Existe para que el informe no pueda
    # presentar como cerrado algo que sigue abierto. Exige decir que lo bloquea.
    for i, finding in enumerate(doc.get("open_findings") or []):
        for key in (
            "ecosystem",
            "package",
            "version",
            "advisories",
            "severity",
            "fix_version",
            "blocked_by",
            "note",
        ):
            if key not in finding:
                issues.append(f"{rel}: open_findings[{i}] sin '{key}'")
        if finding.get("severity") not in VALID_SEVERITIES - {"-"}:
            issues.append(
                f"{rel}: open_findings[{i}] severity={finding.get('severity')!r} no es "
                f"valido (un hallazgo abierto no puede tener severity '-')"
            )
        if not (finding.get("advisories") or []):
            issues.append(f"{rel}: open_findings[{i}] no lista ningun advisory")
        for a in finding.get("advisories") or []:
            if not ADVISORY_RE.match(a):
                issues.append(
                    f"{rel}: open_findings[{i}] advisory con formato raro: {a!r}"
                )
    return issues


# Una linea que cita un release anterior describe lo que era cierto ENTONCES:
# corregirle la cifra seria reescribir la historia, asi que se excluye.
HISTORICO_RE = re.compile(r"v4\.(?:[0-9]|10)\b")


def texto_actual(doc: Path) -> str:
    """El documento sin su registro historico.

    No basta con filtrar linea a linea: una fila de tabla no repite la version, la
    lleva su ENCABEZADO ("### Resueltos en v4.4.1"). Al entrar en la seccion de un
    release anterior se salta entera, hasta el siguiente encabezado.
    """
    fuera: list[str] = []
    en_historico = False
    for linea in doc.read_text(encoding="utf-8").splitlines():
        if linea.startswith("#"):
            en_historico = bool(HISTORICO_RE.search(linea))
        if en_historico or HISTORICO_RE.search(linea):
            continue
        fuera.append(linea)
    return "\n".join(fuera)


def check_doc_claims() -> list[str]:
    """Comprueba las cifras que los documentos afirman sobre el propio repositorio."""
    issues: list[str] = []

    # Dependabot: cuantas entradas y cuantos ecosistemas hay de verdad.
    dependabot = ROOT / ".github" / "dependabot.yml"
    if dependabot.is_file():
        cfg = yaml.safe_load(dependabot.read_text(encoding="utf-8")) or {}
        updates = cfg.get("updates") or []
        n_entradas = len(updates)
        n_ecos = len({u.get("package-ecosystem") for u in updates})

        # ROADMAP y CHANGELOG son registros historicos: sus cifras describen el
        # estado de un release pasado y no deben "corregirse". Solo se comprueban
        # los documentos de ESTADO ACTUAL.
        for rel in ("SECURITY.md", "README.md"):
            doc = ROOT / rel
            if not doc.is_file():
                continue
            texto = texto_actual(doc)
            for m in re.finditer(
                r"\*?\*?(\d+) entradas\*?\*?[^.\n]{0,40}(?:que cubren|cubriendo)", texto
            ):
                if int(m.group(1)) != n_entradas:
                    issues.append(
                        f"{rel}: afirma {m.group(1)} entradas de Dependabot, "
                        f"pero .github/dependabot.yml tiene {n_entradas}"
                    )
            for m in re.finditer(r"(\d+) ecosistemas", texto):
                if int(m.group(1)) != n_ecos:
                    issues.append(
                        f"{rel}: afirma {m.group(1)} ecosistemas de Dependabot, "
                        f"pero hay {n_ecos}"
                    )
            # Cada directorio citado tiene que existir.
        for u in updates:
            d = str(u.get("directory", "")).lstrip("/")
            if d and not (ROOT / d).is_dir():
                issues.append(
                    f".github/dependabot.yml: la entrada {u.get('package-ecosystem')} "
                    f"apunta a '/{d}', que no existe"
                )

    # Locks con hash de Python y lockfiles de Node, contados de verdad.
    n_py = len(
        [
            q
            for q in ROOT.rglob("requirements.txt")
            if "venv" not in q.parts
            and ".claude" not in q.parts
            and "node_modules" not in q.parts
        ]
    )
    n_node = len(
        [
            q
            for q in (ROOT / "cases").rglob("pnpm-lock.yaml")
            if "node_modules" not in q.parts
        ]
    )
    for rel in ("SECURITY.md", "README.md"):
        doc = ROOT / rel
        if not doc.is_file():
            continue
        texto = texto_actual(doc)
        for m in re.finditer(r"los (\d+) `requirements\.txt`", texto):
            if int(m.group(1)) != n_py:
                issues.append(
                    f"{rel}: afirma {m.group(1)} requirements.txt, pero hay {n_py}"
                )
        for m in re.finditer(r"los (\d+) paquetes Node", texto):
            if int(m.group(1)) != n_node:
                issues.append(
                    f"{rel}: afirma {m.group(1)} paquetes Node, pero hay {n_node} "
                    f"con pnpm-lock.yaml"
                )

    # GitHub Actions: ninguna referencia `uses:` puede quedar sin SHA-pinnear, y la
    # cifra que afirme la documentacion tiene que ser la real. Un tag movil deja la
    # puerta abierta a que lo reescriban; es el riesgo que P-07 cerro.
    wf_dir = ROOT / ".github" / "workflows"
    if wf_dir.is_dir():
        total_uses = 0
        sin_pin: list[str] = []
        versiones: dict[str, set[str]] = {}
        for wf in sorted(wf_dir.glob("*.yml")):
            for linea in wf.read_text(encoding="utf-8").splitlines():
                s = linea.strip()
                if not s.startswith("- uses:") and not s.startswith("uses:"):
                    continue
                total_uses += 1
                ref = s.split("uses:", 1)[1].strip()
                # Lo que importa es el SHA de 40, no que el comentario sea una
                # version: `dtolnay/rust-toolchain@<sha> # stable` esta pinneada
                # igual de bien, y esa action no publica tags de version.
                if not re.match(r"^[^@]+@[0-9a-f]{40}(\s|$)", ref):
                    sin_pin.append(f"{wf.name}: {ref[:60]}")
                else:
                    nombre, resto = ref.split("@", 1)
                    if "#" in resto:
                        etiqueta = resto.split("#", 1)[1].strip()
                        if re.match(r"^v?[0-9]", etiqueta):
                            versiones.setdefault(nombre, set()).add(etiqueta)

        for s in sin_pin:
            issues.append(
                f".github/workflows/{s} no esta pinneada a SHA de 40 caracteres"
            )

        # La misma action con dos versiones distintas entre workflows es deriva.
        for nombre, vs in sorted(versiones.items()):
            if len(vs) > 1:
                issues.append(
                    f".github/workflows: {nombre} aparece con versiones distintas "
                    f"({', '.join(sorted(vs))})"
                )

        for rel in ("SECURITY.md", "README.md"):
            doc = ROOT / rel
            if not doc.is_file():
                continue
            for m in re.finditer(
                r"[Ll]as (\d+) referencias `uses:`", texto_actual(doc)
            ):
                if int(m.group(1)) != total_uses:
                    issues.append(
                        f"{rel}: afirma {m.group(1)} referencias `uses:`, "
                        f"pero los workflows tienen {total_uses}"
                    )

    return issues


def main() -> int:
    issues: list[str] = []
    lab_version = read_version_from_readme()
    declared = version_references()

    manifests = sorted(CASES_DIR.glob("*/security.yml"))
    if len(manifests) != EXPECTED_CASES:
        issues.append(
            f"Se esperaban {EXPECTED_CASES} security.yml y hay {len(manifests)}"
        )

    stale_versions: dict[str, str] = {}
    applied = 0

    for path in manifests:
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            issues.append(f"{path.relative_to(ROOT)}: YAML invalido ({exc})")
            continue

        issues.extend(check_structure(path, doc, lab_version))

        app_manifest = path.parent / "app.manifest.yml"
        if not app_manifest.is_file():
            issues.append(f"{path.parent.name}: falta app.manifest.yml")
        else:
            app = yaml.safe_load(app_manifest.read_text(encoding="utf-8")) or {}
            if app.get("security_manifest") != "security.yml":
                issues.append(
                    f"{path.parent.name}/app.manifest.yml: no apunta a security.yml "
                    f"(security_manifest={app.get('security_manifest')!r})"
                )

        for rt in doc.get("runtimes") or []:
            to, frm = str(rt.get("to", "")), str(rt.get("from", ""))
            if rt.get("reason") == "sin-cambio" or NOT_AN_IMAGE.search(to):
                continue
            # La version destino tiene que estar realmente escrita en algun Dockerfile
            # o en el compose; si no, el manifiesto va por delante del codigo.
            if to.split()[0] not in declared:
                issues.append(
                    f"{path.parent.name}: security.yml dice que "
                    f"{rt['language']} esta en '{to}' pero esa version no aparece "
                    f"en ningun Dockerfile, compose ni manifiesto de proyecto"
                )
            else:
                applied += 1
            if frm and not NOT_AN_IMAGE.search(frm) and frm.split()[0] != to.split()[0]:
                stale_versions.setdefault(
                    (rt["language"], frm.split()[0]), path.parent.name
                )

    # Ninguna version abandonada puede seguir viva en el repositorio. Los valores
    # `from` del manifiesto son fragmentos de tag ("20-alpine", "8.2-apache"), no
    # referencias completas, asi que hay que comparar contra el tag de cada imagen
    # y no contra el texto crudo.
    used = image_refs_in_use(declared)
    checked_stale = 0
    for (language, stale), case_name in sorted(stale_versions.items()):
        names = LANGUAGE_IMAGES.get(language)
        if not names:
            continue
        checked_stale += 1
        for ref in sorted(used):
            name, _, tag = ref.partition(":")
            if name not in names:
                continue
            if tag == stale or ref == stale:
                issues.append(
                    f"La version '{stale}' de {language}, que {case_name} declara "
                    f"abandonada en su security.yml, sigue usandose: {ref}"
                )
                break

    # ------------------------------------------------------------------------------
    # Afirmaciones numericas de la documentacion contra la realidad del repositorio.
    # Una cifra escrita a mano en un .md envejece en cuanto alguien toca un fichero,
    # y entonces la documentacion miente sin que nadie se entere.
    # ------------------------------------------------------------------------------
    issues.extend(check_doc_claims())

    if issues:
        print("Guardrail de manifiestos de seguridad: FALLA\n")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    print("Guardrail de manifiestos de seguridad: OK")
    print(f"  - {len(manifests)} casos con security.yml, lab_version {lab_version}")
    print(
        f"  - {applied} versiones de runtime verificadas contra Dockerfiles, compose y manifiestos"
    )
    print(f"  - {checked_stale} versiones abandonadas comprobadas como ausentes")
    abiertos = sum(
        len(yaml.safe_load(m.read_text(encoding="utf-8")).get("open_findings") or [])
        for m in manifests
    )
    if abiertos:
        print(f"  - {abiertos} hallazgos ABIERTOS declarados (ver open_findings)")
    else:
        print("  - 0 hallazgos abiertos declarados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
