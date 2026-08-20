#!/usr/bin/env python3
"""Genera en `site/` el sitio publico del laboratorio (GitHub Pages).

Por que el sitio no se versiona: se reconstruye en cada despliegue desde el
propio repositorio -- los manifiestos `cases/*/app.manifest.yml` y los 85
documentos Markdown. Un HTML escrito a mano permitiria que la web afirmara algo
distinto de lo que dice el repo, que es exactamente como envejecen las landings.

Que produce:

* `index.html`         portada con la matriz de casos leida de los manifiestos.
* `casos.html`         tabla completa: puerto, perfil de compose y documentos.
* `documentacion.html` indice de toda la documentacion publicada.
* `<ruta>.html`        cada `.md` del repo renderizado como pagina propia.
* `404.html`, `sitemap.xml`, `robots.txt`, `.nojekyll` y los assets.

Regla que manda sobre todo lo demas: **ningun enlace del sitio apunta a un
`.md`**. Un `.md` en Pages es una descarga o un 404, no una pagina. Cada enlace
relativo entre documentos se reescribe al `.html` equivalente; lo que no es
Markdown (compose, scripts, workflows) se manda al blob de GitHub. Si un destino
no existe ni como documento ni como archivo del repo, el build falla aqui, antes
de publicar nada. `check_site_links.py` lo vuelve a comprobar sobre el HTML ya
generado.

Sin dependencias externas: stdlib y `site_markdown.py`.
"""

from __future__ import annotations

import html
import posixpath
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))

from site_markdown import MarkdownDocument, render_markdown  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SITE_SRC = ROOT / "site-src"
CASES_DIR = ROOT / "cases"

REPO_URL = "https://github.com/vladimiracunadev-create/social-bot-scheduler"
BLOB = REPO_URL + "/blob/main/"
TREE = REPO_URL + "/tree/main/"
SITE_URL = "https://vladimiracunadev-create.github.io/social-bot-scheduler/"
AUTHOR = "Vladimir Acuna"

# Directorios que no forman parte de la documentacion publicable.
SKIP_DIRS = {
    ".git",
    ".github",
    ".agent",
    ".claude",
    ".mypy_cache",
    ".pytest_cache",
    "venv",
    "node_modules",
    "__pycache__",
    "site",
    "site-src",
}

# -- catalogo ---------------------------------------------------------------

LANGUAGES = {
    "python": "Python",
    "php": "PHP",
    "go": "Go",
    "node": "Node.js",
    "nodejs": "Node.js",
    "react": "React",
    "ruby": "Ruby",
    "rust": "Rust",
    "csharp": "C#",
    "java": "Java",
    "kotlin": "Kotlin",
    "elixir": "Elixir",
    "erlang": "Erlang",
    "zig": "Zig",
    "crystal": "Crystal",
    "swift": "Swift",
    "dart": "Dart",
    "fsharp": "F#",
    "clojure": "Clojure",
}

ENGINES = {
    "mysql": "MySQL",
    "mariadb": "MariaDB",
    "postgresql": "PostgreSQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "sqlserver": "SQL Server",
    "duckdb": "DuckDB",
    "pgvector": "pgvector",
    "clickhouse": "ClickHouse",
    "cockroachdb": "CockroachDB",
    "timescaledb": "TimescaleDB",
    "influxdb": "InfluxDB",
    "neo4j": "Neo4j",
    "mnesia": "Mnesia",
    "xtdb": "XTDB",
    "firestore": "Firestore",
}

FRAMEWORKS = {
    "spring-boot": "Spring Boot",
    "ktor": "Ktor",
    "cowboy": "Cowboy",
    "kemal": "Kemal",
    "shelf": "Shelf",
    "fastapi": "FastAPI",
    "apollo-server": "Apollo",
    "hasura": "Hasura",
    "nextjs-15-app-router": "Next.js 15",
    "supabase-postgrest": "PostgREST",
    "kafkajs": "Kafka",
    "kafka-go": "Kafka",
    "ring": "Ring",
    "mix": "Mix",
    "urllib": "",
    "foundation": "",
    "fastapi+grpcio": "FastAPI + gRPC",
}

_SCALAR = re.compile(r"^(\s*)([A-Za-z_][\w-]*):\s*(.*?)\s*$")


def _scalar(raw: str) -> object:
    """Valor YAML del subconjunto que usan los manifiestos."""
    if raw.startswith("[") and raw.endswith("]"):
        body = raw[1:-1].strip()
        if not body:
            return []
        return [item.strip().strip('"').strip("'") for item in body.split(",")]
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    if raw.isdigit():
        return int(raw)
    return raw


def parse_manifest(path: Path) -> dict:
    """Lee un `app.manifest.yml`.

    Se parsea a mano por la misma razon que `validate_ports.py`: los manifiestos
    son planos (escalares y un nivel de anidamiento) y el sitio no deberia
    necesitar PyYAML instalado para poder publicarse.
    """
    data: dict = {}
    current: dict | None = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = _SCALAR.match(line)
        if not match:
            continue
        indent, key, raw = match.group(1), match.group(2), match.group(3)
        if indent:
            if current is not None:
                current[key] = _scalar(raw)
            continue
        if raw:
            data[key] = _scalar(raw)
            current = None
        else:
            current = {}
            data[key] = current
    return data


def label(table: dict[str, str], value: object, fallback: str = "") -> str:
    key = str(value or "").strip().lower()
    if not key:
        return fallback
    return table.get(key, key.replace("-", " ").title())


def load_cases() -> list[dict]:
    cases: list[dict] = []
    for manifest in sorted(CASES_DIR.glob("*/app.manifest.yml")):
        data = parse_manifest(manifest)
        origin = data.get("origin") or {}
        dest = data.get("destination") or {}
        database = data.get("database") or {}
        broker = data.get("broker") or {}
        slug = manifest.parent.name
        case = {
            "id": str(data.get("id") or slug[:2]),
            "slug": slug,
            "name": str(data.get("name") or slug).replace("->", "→"),
            "status": str(data.get("status") or "ready"),
            "description": str(data.get("description") or ""),
            "origin": label(LANGUAGES, origin.get("language")),
            "origin_framework": label(FRAMEWORKS, origin.get("framework")),
            "origin_key": str(origin.get("language") or "").lower(),
            "dest": label(LANGUAGES, dest.get("language")),
            "dest_framework": label(FRAMEWORKS, dest.get("framework")),
            "dest_key": str(dest.get("language") or "").lower(),
            "engine": label(ENGINES, database.get("engine"), "—"),
            "engine_key": str(database.get("engine") or "").lower(),
            "engine_version": str(database.get("version") or ""),
            "broker": label(ENGINES, broker.get("engine"), ""),
            "port": int(dest.get("port") or 0),
            "stack": list(data.get("stack") or []),
            "docs": sorted(
                doc.relative_to(ROOT).as_posix() for doc in manifest.parent.glob("*.md")
            ),
        }
        case["profile"] = "case" + case["id"]
        cases.append(case)
    cases.sort(key=lambda item: item["id"])
    return cases


def repo_version() -> str:
    """Version declarada por el CHANGELOG (la fuente que se actualiza primero)."""
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r"^##\s*\S*\s*\[?v?(\d+\.\d+\.\d+)\]?", changelog, re.M)
    return match.group(1) if match else "0.0.0"


# -- documentos -------------------------------------------------------------


def markdown_files() -> list[Path]:
    found: list[Path] = []
    for path in sorted(ROOT.rglob("*.md")):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts[:-1]):
            continue
        found.append(rel)
    return found


def summary(text: str) -> str:
    """Primer parrafo util del documento, para el indice."""
    for block in re.split(r"\n\s*\n", text):
        line = block.strip()
        if not line or line.startswith(("#", ">", "|", "```", "---", "<")):
            continue
        if line.startswith("[!["):
            continue
        line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"[*`_#]+", "", line).replace("\n", " ").strip()
        if len(line) < 12:
            continue
        return line[:157] + "…" if len(line) > 158 else line
    return ""


def doc_title(document: MarkdownDocument, rel: Path) -> str:
    if document.title:
        return document.title
    return rel.stem.replace("_", " ").replace("-", " ").title()


# -- plantilla --------------------------------------------------------------

NAV = (
    ("index.html", "Inicio"),
    ("casos.html", "Casos"),
    ("documentacion.html", "Documentación"),
    ("docs/ARCHITECTURE.html", "Arquitectura"),
    ("SECURITY.html", "Seguridad"),
)


def rel_href(from_rel: str, to_rel: str) -> str:
    base = posixpath.dirname(from_rel) or "."
    return posixpath.relpath(to_rel, base)


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def shell(
    out_rel: str, title: str, description: str, body: str, active: str = ""
) -> str:
    href = lambda target: esc(rel_href(out_rel, target))  # noqa: E731
    canonical = SITE_URL + ("" if out_rel == "index.html" else out_rel)
    nav = "\n".join(
        f'        <a href="{href(target)}"'
        + (' aria-current="page"' if target == active else "")
        + f">{esc(text)}</a>"
        for target, text in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="author" content="{esc(AUTHOR)}">
<meta name="theme-color" content="#0b1120">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Social Bot Scheduler">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{href('assets/favicon.svg')}" type="image/svg+xml">
<link rel="stylesheet" href="{href('assets/site.css')}">
</head>
<body>
<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="topbar">
    <div class="shell">
        <a class="brand" href="{href('index.html')}"><span class="dot"></span>Social Bot Scheduler</a>
        <nav class="nav">
{nav}
        <a href="{esc(REPO_URL)}" target="_blank" rel="noopener noreferrer">GitHub</a>
        </nav>
    </div>
</header>
<main id="contenido">
{body}
</main>
<footer>
    <div class="shell">
        <div>
            <strong>Social Bot Scheduler</strong> · laboratorio local de integración políglota con n8n.<br>
            Sitio generado desde el repositorio en cada despliegue · licencia MIT · {esc(AUTHOR)}.
        </div>
        <nav>
            <a href="{href('documentacion.html')}">Documentación</a>
            <a href="{href('CHANGELOG.html')}">Changelog</a>
            <a href="{href('SECURITY.html')}">Seguridad</a>
            <a href="{esc(REPO_URL)}" target="_blank" rel="noopener noreferrer">Repositorio</a>
        </nav>
    </div>
</footer>
</body>
</html>
"""


# -- resolucion de enlaces --------------------------------------------------


class Resolver:
    """Reescribe los destinos de un documento Markdown a destinos del sitio."""

    def __init__(self, doc_rel: Path, out_rel: str, pages: dict[str, str]) -> None:
        self.doc_rel = doc_rel
        self.out_rel = out_rel
        self.pages = pages
        self.broken: list[str] = []
        self.assets: set[str] = set()

    def __call__(self, target: str, is_image: bool) -> str:
        raw = target.strip()
        if not raw:
            return "#"
        low = raw.lower()
        if low.startswith(
            ("http://", "https://", "//", "mailto:", "tel:", "data:", "#")
        ):
            return raw
        match = re.match(r"^([^#?]*)([?#].*)?$", raw)
        path_part = match.group(1) if match else raw
        suffix = (match.group(2) or "") if match else ""
        if not path_part:
            return raw
        base = self.doc_rel.parent.as_posix()
        base = "" if base == "." else base
        repo_rel = posixpath.normpath(posixpath.join(base, unquote(path_part)))
        if repo_rel.startswith(".."):
            self.broken.append(
                f"{self.doc_rel.as_posix()}: destino fuera del repo '{raw}'"
            )
            return "#"

        page = self.pages.get(repo_rel)
        if page:
            return rel_href(self.out_rel, page) + suffix

        absolute = ROOT / repo_rel
        if absolute.is_dir():
            return TREE + repo_rel + suffix
        if absolute.is_file():
            if is_image:
                self.assets.add(repo_rel)
                return rel_href(self.out_rel, "assets/repo/" + repo_rel)
            return BLOB + repo_rel + suffix

        self.broken.append(f"{self.doc_rel.as_posix()}: destino inexistente '{raw}'")
        return "#"


# -- paginas de documentacion ----------------------------------------------


def toc_html(headings: list[tuple[int, str, str]]) -> str:
    items = [
        f'<a class="lvl{level}" href="#{esc(anchor)}">{esc(text)}</a>'
        for level, anchor, text in headings
        if 2 <= level <= 3 and text
    ]
    if len(items) < 3:
        return ""
    return '<aside class="toc"><b>En esta página</b>' + "\n".join(items) + "</aside>"


def breadcrumb(rel: Path, out_rel: str) -> str:
    trail = [f'<a href="{esc(rel_href(out_rel, "index.html"))}">Inicio</a>']
    if rel.parts[0] == "cases":
        trail.append(f'<a href="{esc(rel_href(out_rel, "casos.html"))}">Casos</a>')
    else:
        trail.append(
            f'<a href="{esc(rel_href(out_rel, "documentacion.html"))}">Documentación</a>'
        )
    trail.append(f"<span>{esc(rel.as_posix())}</span>")
    return '<p class="breadcrumb">' + " / ".join(trail) + "</p>"


def render_doc_page(
    rel: Path, out_rel: str, pages: dict[str, str]
) -> tuple[str, Resolver, str]:
    text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
    folder = rel.parent.as_posix()
    source_url = REPO_URL if folder == "." else TREE + folder
    resolver = Resolver(rel, out_rel, pages)
    document = render_markdown(text, resolver)
    title = doc_title(document, rel)
    description = summary(text) or f"Documentación del laboratorio: {rel.as_posix()}"
    body = f"""<div class="shell doc-layout">
    <article class="doc">
{breadcrumb(rel, out_rel)}
{document.html}
        <div class="doc-nav">
            <a href="{esc(rel_href(out_rel, 'documentacion.html'))}">← Toda la documentación</a>
            <a href="{esc(rel_href(out_rel, 'index.html'))}">Portada</a>
            <a href="{esc(source_url)}" target="_blank" rel="noopener noreferrer">Esta carpeta en GitHub</a>
        </div>
    </article>
{toc_html(document.headings)}
</div>"""
    suffix = "" if "Social Bot Scheduler" in title else " · Social Bot Scheduler"
    return shell(out_rel, title + suffix, description, body), resolver, title


# -- portada ----------------------------------------------------------------


def flow_chips(case: dict) -> str:
    chips = [f'<span class="chip">{esc(case["origin"])}</span>']
    chips.append('<span class="arrow">→</span>')
    chips.append('<span class="chip bridge">n8n</span>')
    chips.append('<span class="arrow">→</span>')
    chips.append(f'<span class="chip">{esc(case["dest"])}</span>')
    if case["engine"] and case["engine"] != "—":
        chips.append('<span class="arrow">→</span>')
        chips.append(f'<span class="chip db">{esc(case["engine"])}</span>')
    return '<div class="case-flow">' + "".join(chips) + "</div>"


def case_card(case: dict, from_rel: str, pages: dict[str, str]) -> str:
    ready = case["status"] != "planned"
    pill = (
        '<span class="pill ready">operativo</span>'
        if ready
        else '<span class="pill planned">pendiente</span>'
    )
    links = []
    for name, doc in (("Guía", "README.md"), ("Arquitectura", "ARCHITECTURE.md")):
        page = pages.get(f"cases/{case['slug']}/{doc}")
        if page:
            links.append(f'<a href="{esc(rel_href(from_rel, page))}">{name}</a>')
    return f"""<article class="case-card" id="caso-{esc(case['id'])}">
    <div class="top">
        <span class="case-id">{esc(case['id'])}</span>
        {pill}
        <span class="case-meta">:{case['port']} · --profile {esc(case['profile'])}</span>
    </div>
    <h3>{esc(case['name'])}</h3>
    {flow_chips(case)}
    <p class="desc">{esc(case['description'])}</p>
    <div class="case-links">{''.join(links)}</div>
</article>"""


DIAGRAM = """<div class="diagram">
<svg viewBox="0 0 900 240" role="img" aria-label="Emisor politglota, n8n como puente, receptor HTTP y motor de datos">
    <defs>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#6366f1"/><stop offset="100%" stop-color="#c084fc"/>
        </linearGradient>
        <marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M0 0L10 5L0 10z" fill="#64748b"/>
        </marker>
    </defs>
    <g font-family="ui-monospace, monospace" font-size="14">
        <rect x="10" y="60" width="180" height="80" rx="12" fill="#131c31" stroke="#334155"/>
        <text x="100" y="92" fill="#e8edf7" text-anchor="middle" font-size="15">Emisor</text>
        <text x="100" y="114" fill="#94a3b8" text-anchor="middle" font-size="12">Python, Go, Rust, Zig,</text>
        <text x="100" y="130" fill="#94a3b8" text-anchor="middle" font-size="12">Swift, F#, Elixir, Java...</text>

        <rect x="250" y="45" width="180" height="110" rx="12" fill="#1a2540" stroke="url(#g)" stroke-width="2"/>
        <text x="340" y="78" fill="#c7d2fe" text-anchor="middle" font-size="15">n8n</text>
        <text x="340" y="100" fill="#94a3b8" text-anchor="middle" font-size="12">webhook + workflow</text>
        <text x="340" y="118" fill="#94a3b8" text-anchor="middle" font-size="12">idempotencia, reintentos,</text>
        <text x="340" y="134" fill="#94a3b8" text-anchor="middle" font-size="12">circuit breaker, DLQ</text>

        <rect x="490" y="60" width="180" height="80" rx="12" fill="#131c31" stroke="#334155"/>
        <text x="580" y="92" fill="#e8edf7" text-anchor="middle" font-size="15">Receptor HTTP</text>
        <text x="580" y="114" fill="#94a3b8" text-anchor="middle" font-size="12">POST /webhook</text>
        <text x="580" y="130" fill="#94a3b8" text-anchor="middle" font-size="12">puerto 8080 + id</text>

        <rect x="730" y="60" width="160" height="80" rx="12" fill="#131c31" stroke="#14532d"/>
        <text x="810" y="92" fill="#34d399" text-anchor="middle" font-size="15">Motor de datos</text>
        <text x="810" y="114" fill="#94a3b8" text-anchor="middle" font-size="12">SQL, NoSQL, grafo,</text>
        <text x="810" y="130" fill="#94a3b8" text-anchor="middle" font-size="12">vectorial, columnar...</text>

        <line x1="192" y1="100" x2="246" y2="100" stroke="#64748b" stroke-width="2" marker-end="url(#a)"/>
        <line x1="432" y1="100" x2="486" y2="100" stroke="#64748b" stroke-width="2" marker-end="url(#a)"/>
        <line x1="672" y1="100" x2="726" y2="100" stroke="#64748b" stroke-width="2" marker-end="url(#a)"/>
        <text x="450" y="200" fill="#64748b" text-anchor="middle" font-size="12">
            Mismo contrato JSON en los 19 casos: cambia el lenguaje y el motor, no la interfaz.
        </text>
    </g>
</svg>
</div>"""


def build_index(cases: list[dict], pages: dict[str, str], version: str) -> str:
    out_rel = "index.html"
    ready = [case for case in cases if case["status"] != "planned"]
    engines = sorted({case["engine_key"] for case in cases if case["engine_key"]})
    languages = sorted(
        {case["origin_key"] for case in cases if case["origin_key"]}
        | {case["dest_key"] for case in cases if case["dest_key"]} - {""}
    )
    language_names = sorted({label(LANGUAGES, key) for key in languages})

    cards = "\n".join(case_card(case, out_rel, pages) for case in cases)
    stats = [
        (str(len(cases)), "casos definidos"),
        (str(len(ready)), "operativos con Docker"),
        (str(len(engines)), "motores de datos"),
        (str(len(language_names)), "lenguajes y frameworks"),
        ("8080+id", "fórmula de puertos"),
    ]
    stats_html = "\n".join(
        f'<div class="stat"><b>{esc(value)}</b><span>{esc(text)}</span></div>'
        for value, text in stats
    )

    doc_cards = [
        (
            "docs/INSTALL.md",
            "Instalación",
            "Requisitos, primer arranque y verificación.",
        ),
        (
            "docs/ARCHITECTURE.md",
            "Arquitectura",
            "Cómo se conectan emisor, n8n, receptor y motor.",
        ),
        (
            "docs/API.md",
            "Contrato de API",
            "El JSON que viaja y las respuestas de cada receptor.",
        ),
        (
            "docs/GUARDRAILS.md",
            "Guardrails",
            "Idempotencia, reintentos, circuit breaker y DLQ.",
        ),
        (
            "docs/RUNTIME_SECURITY.md",
            "Seguridad runtime",
            "Aislamiento en localhost y política de puertos.",
        ),
        (
            "docs/TROUBLESHOOTING.md",
            "Troubleshooting",
            "Qué mirar cuando un caso no levanta.",
        ),
    ]
    doc_html = "\n".join(
        f"""<a class="card" href="{esc(rel_href(out_rel, pages[src]))}">
    <h3>{esc(name)}</h3><p>{esc(text)}</p></a>"""
        for src, name, text in doc_cards
        if src in pages
    )

    body = f"""<div class="shell">
<section class="hero">
    <span class="eyebrow">v{esc(version)} · laboratorio 100% local</span>
    <h1>Un contrato, {len(ready)} integraciones, {len(engines)} motores de datos</h1>
    <p class="lead">
        <strong>Social Bot Scheduler</strong> es una matriz tecnológica: en cada caso un emisor
        publica un post, <strong>n8n</strong> hace de puente y un receptor escrito en otro lenguaje
        lo persiste en un motor de datos distinto. Mismo JSON, mismos guardrails, {len(cases)} combinaciones
        que se levantan una a una con un solo comando.
    </p>
    <div class="badges">
        <span class="badge ok">{len(ready)}/{len(cases)} casos operativos</span>
        <span class="badge">{len(engines)} motores de datos</span>
        <span class="badge">{len(language_names)} lenguajes y frameworks</span>
        <span class="badge">Docker Compose por perfiles</span>
        <span class="badge ok">MIT</span>
    </div>
    <div class="cta">
        <a class="btn primary" href="#quickstart">Levantarlo en 2 comandos</a>
        <a class="btn" href="casos.html">Ver los {len(cases)} casos</a>
        <a class="btn" href="{esc(REPO_URL)}" target="_blank" rel="noopener noreferrer">Repositorio</a>
    </div>
    <div class="stats">
{stats_html}
    </div>
</section>

<section id="como-funciona">
    <div class="section-head">
        <h2>Cómo funciona</h2>
        <p>
            El emisor no sabe nada del receptor: publica contra un webhook de n8n y ahí termina su
            responsabilidad. El workflow aplica los guardrails y entrega al receptor, que persiste en
            su propio motor. Cambiar de lenguaje o de base de datos no cambia el contrato.
        </p>
    </div>
    {DIAGRAM}
</section>

<section id="que-demuestra">
    <div class="section-head">
        <h2>Qué demuestra</h2>
        <p>Tres cosas que suelen quedarse en la teoría y aquí se ejecutan.</p>
    </div>
    <div class="grid c3">
        <div class="card">
            <h3>Integración políglota real</h3>
            <p>
                {len(language_names)} lenguajes y frameworks conviviendo con {len(engines)} motores bajo el mismo contrato JSON:
                relacional, documental, clave-valor, columnar, grafo, vectorial, series temporales,
                bitemporal y streaming.
            </p>
        </div>
        <div class="card">
            <h3>Guardrails de resiliencia</h3>
            <p>No es un &laquo;hola mundo&raquo; con webhook: cada caso comparte las mismas defensas.</p>
            <ul>
                <li>Idempotencia por clave de evento</li>
                <li>Reintentos con backoff</li>
                <li>Circuit breaker en el emisor</li>
                <li>Dead letter queue para lo que no entra</li>
            </ul>
        </div>
        <div class="card">
            <h3>Seguridad runtime</h3>
            <p>
                Todo escucha en <code>127.0.0.1</code>, sin secretos en el repositorio, imágenes fijadas
                por versión y escaneo de contenedor y dependencias en cada push.
            </p>
        </div>
    </div>
</section>

<section id="casos">
    <div class="section-head">
        <h2>La matriz de casos</h2>
        <p>
            Cada tarjeta es una carpeta autocontenida en <code>cases/</code> con emisor, receptor,
            workflow de n8n y su documentación. El puerto sale siempre de la fórmula
            <code>8080 + id</code>, así que nunca colisionan.
        </p>
    </div>
    <div class="grid cases">
{cards}
    </div>
</section>

<section id="quickstart">
    <div class="section-head">
        <h2>Quickstart</h2>
        <p>Diseñado para ejecutarse solo en local. El modo por defecto no expone nada fuera de <code>localhost</code>.</p>
    </div>
    <div class="grid c2">
        <div class="card">
            <h3>1 · Núcleo seguro</h3>
            <div class="codeblock"><span class="code-lang">bash</span><pre><code>cp .env.example .env
docker compose up -d</code></pre></div>
            <p>Levanta n8n en <code>:5678</code> y el Master Dashboard en <code>:8080</code>.</p>
        </div>
        <div class="card">
            <h3>2 · Un caso concreto</h3>
            <div class="codeblock"><span class="code-lang">bash</span><pre><code>docker compose --profile case12 up -d
curl http://localhost:8092/health</code></pre></div>
            <p>Cada perfil arrastra su receptor y su motor de datos, y nada más.</p>
        </div>
    </div>
</section>

<section id="documentacion">
    <div class="section-head">
        <h2>Documentación</h2>
        <p>Todo el material del repositorio, publicado como páginas HTML navegables.</p>
    </div>
    <div class="grid c3">
{doc_html}
    </div>
    <p style="margin-top:1.2rem"><a class="btn" href="documentacion.html">Índice completo de documentación</a></p>
</section>
</div>"""
    description = (
        f"Laboratorio local de integración políglota con n8n y Docker: {len(cases)} casos "
        f"emisor → n8n → receptor sobre {len(engines)} motores de datos, con guardrails de "
        "resiliencia y aislamiento en localhost."
    )
    return shell(
        out_rel,
        "Social Bot Scheduler · laboratorio políglota con n8n",
        description,
        body,
        active="index.html",
    )


def build_cases_page(cases: list[dict], pages: dict[str, str]) -> str:
    out_rel = "casos.html"
    rows = []
    for case in cases:
        docs = []
        for doc in case["docs"]:
            page = pages.get(doc)
            if page:
                stem = Path(doc).stem
                name = CASE_DOC_NAMES.get(stem, stem.replace("_", " ").capitalize())
                docs.append(f'<a href="{esc(rel_href(out_rel, page))}">{esc(name)}</a>')
        state = (
            '<span class="pill ready">operativo</span>'
            if case["status"] != "planned"
            else '<span class="pill planned">pendiente</span>'
        )
        engine = case["engine"]
        if case["engine_version"]:
            engine += f" {case['engine_version']}"
        rows.append(
            "<tr>"
            f'<td><code>{esc(case["id"])}</code></td>'
            f"<td>{esc(case['origin'])}"
            + (
                f" <small>({esc(case['origin_framework'])})</small>"
                if case["origin_framework"]
                else ""
            )
            + "</td>"
            f"<td>{esc(case['dest'])}"
            + (
                f" <small>({esc(case['dest_framework'])})</small>"
                if case["dest_framework"]
                else ""
            )
            + "</td>"
            f"<td>{esc(engine)}</td>"
            f'<td><code>{case["port"]}</code></td>'
            f'<td><code>--profile {esc(case["profile"])}</code></td>'
            f"<td>{state}</td>"
            f'<td>{" · ".join(docs)}</td>'
            "</tr>"
        )
    ready = sum(1 for case in cases if case["status"] != "planned")
    body = f"""<div class="shell">
<section>
    <div class="section-head">
        <h1>Los {len(cases)} casos de integración</h1>
        <p>
            {ready} verificados end-to-end con Docker (cada uno con persistencia real en su motor).
            El puerto de cada receptor sale de la fórmula <code>8080 + id</code> y su perfil de
            Compose se llama <code>caseNN</code>.
        </p>
    </div>
    <div class="tablewrap">
    <table>
        <thead><tr>
            <th>ID</th><th>Emisor</th><th>Receptor</th><th>Motor de datos</th>
            <th>Puerto</th><th>Perfil</th><th>Estado</th><th>Documentos</th>
        </tr></thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
    </table>
    </div>
    <p>
        ¿Prefieres el formato tarjeta? La <a href="index.html#casos">portada</a> muestra la misma
        matriz con el flujo completo de cada caso.
    </p>
</section>
</div>"""
    return shell(
        out_rel,
        f"Los {len(cases)} casos · Social Bot Scheduler",
        f"Matriz completa de los {len(cases)} casos de integración: emisor, receptor, motor de "
        "datos, puerto y perfil de Docker Compose.",
        body,
        active="casos.html",
    )


CASE_DOC_NAMES = {
    "README": "Guía",
    "ARCHITECTURE": "Arquitectura",
    "IDEMPOTENCY_TEST": "Prueba de idempotencia",
}

DOC_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "Empezar",
        "Del clon al primer caso levantado.",
        (
            "README.md",
            "docs/INSTALL.md",
            "docs/REQUIREMENTS.md",
            "docs/BEGINNERS_GUIDE.md",
            "docs/USER_MANUAL.md",
            "docs/HUB.md",
            "docs/TROUBLESHOOTING.md",
        ),
    ),
    (
        "Arquitectura y contratos",
        "Cómo está hecho y qué promete cada pieza.",
        (
            "docs/ARCHITECTURE.md",
            "docs/API.md",
            "docs/CASES_INDEX.md",
            "docs/SYSTEMS_CATALOG.md",
            "docs/PORTS.md",
            "docs/FILE_MAP.md",
            "docs/AWS_MIGRATION.md",
        ),
    ),
    (
        "Resiliencia y verificación",
        "Lo que evita que un caso se rompa en silencio.",
        (
            "docs/GUARDRAILS.md",
            "docs/RESILIENCE_GUIDE.md",
            "docs/VERIFICATION_GUIDE.md",
            "docs/HEALTH_CHECK.md",
            "docs/AUDIT_v4.9.0.md",
            "docs/DOCKER_REPORT.md",
            "docs/DOCKER_RESOURCES.md",
            "docs/LIMITATIONS.md",
        ),
    ),
    (
        "Seguridad y cumplimiento",
        "Modelo de amenaza, aislamiento y límites de uso.",
        (
            "SECURITY.md",
            "docs/RUNTIME_SECURITY.md",
            "docs/COMPLIANCE.md",
            "killed.md",
        ),
    ),
    (
        "Proyecto",
        "Historia, plan y cómo participar.",
        (
            "CHANGELOG.md",
            "ROADMAP.md",
            "docs/PLANNED_CASES.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "docs/MAINTAINERS.md",
            "docs/INSIGHTS.md",
            "docs/RECRUITER.md",
            "articulo/LINKEDIN_ARTICLE.md",
        ),
    ),
    (
        "Workflows de n8n",
        "Importar, activar y mantener los workflows del puente.",
        (
            "n8n/README.md",
            "IMPORT_WORKFLOWS.md",
            "COMO_ACTIVAR_WORKFLOWS.md",
            "docs/templates/guardrails_section.md",
        ),
    ),
    (
        "Wiki",
        "Las páginas que se sincronizan con la wiki de GitHub.",
        (
            "docs/wiki/Home.md",
            "docs/wiki/Cases-Index.md",
            "docs/wiki/Usage-Guide.md",
            "docs/wiki/Resilience.md",
            "docs/wiki/Security-Hardening.md",
        ),
    ),
)


def build_docs_index(
    pages: dict[str, str], summaries: dict[str, str], titles: dict[str, str]
) -> str:
    out_rel = "documentacion.html"
    grouped: set[str] = set()
    blocks: list[str] = []

    def entry(src: str) -> str:
        page = pages[src]
        about = summaries.get(src, "")
        return (
            "<li>"
            f'<a class="name" href="{esc(rel_href(out_rel, page))}">{esc(titles.get(src, src))}</a>'
            f"<code>{esc(src)}</code>"
            + (f'<span class="about">{esc(about)}</span>' if about else "")
            + "</li>"
        )

    for name, intro, sources in DOC_GROUPS:
        items = [entry(src) for src in sources if src in pages]
        grouped.update(src for src in sources if src in pages)
        if not items:
            continue
        blocks.append(f"""<section>
    <div class="section-head"><h2>{esc(name)}</h2><p>{esc(intro)}</p></div>
    <ul class="doc-list">
{chr(10).join(items)}
    </ul>
</section>""")

    case_docs = sorted(src for src in pages if src.startswith("cases/"))
    if case_docs:
        blocks.append(f"""<section>
    <div class="section-head">
        <h2>Documentación por caso</h2>
        <p>{len(case_docs)} documentos, entre guías y fichas de arquitectura, uno por carpeta de caso.</p>
    </div>
    <ul class="doc-list">
{chr(10).join(entry(src) for src in case_docs)}
    </ul>
</section>""")
        grouped.update(case_docs)

    rest = sorted(set(pages) - grouped)
    if rest:
        blocks.append(f"""<section>
    <div class="section-head"><h2>Otros documentos</h2><p>Material suelto del repositorio.</p></div>
    <ul class="doc-list">
{chr(10).join(entry(src) for src in rest)}
    </ul>
</section>""")

    body = f"""<div class="shell">
<section>
    <div class="section-head">
        <h1>Documentación</h1>
        <p>
            Los {len(pages)} documentos Markdown del repositorio, publicados como páginas HTML.
            Ningún enlace de este sitio devuelve un <code>.md</code>: cada referencia entre
            documentos se reescribe a su página equivalente al generar el sitio.
        </p>
    </div>
</section>
{chr(10).join(blocks)}
</div>"""
    return shell(
        out_rel,
        "Documentación · Social Bot Scheduler",
        f"Índice de los {len(pages)} documentos del laboratorio: instalación, arquitectura, "
        "contratos, guardrails, seguridad y una ficha por caso.",
        body,
        active="documentacion.html",
    )


def build_404() -> str:
    body = """<div class="shell notfound">
    <h1>404</h1>
    <p class="lead">Esa página no existe en el sitio del laboratorio.</p>
    <div class="cta">
        <a class="btn primary" href="index.html">Volver a la portada</a>
        <a class="btn" href="casos.html">Ver los casos</a>
        <a class="btn" href="documentacion.html">Documentación</a>
    </div>
</div>"""
    return shell(
        "404.html", "404 · Social Bot Scheduler", "Página no encontrada.", body
    )


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#818cf8"/><stop offset="1" stop-color="#c084fc"/>
</linearGradient></defs>
<rect width="64" height="64" rx="14" fill="#0b1120"/>
<circle cx="16" cy="32" r="6" fill="url(#g)"/>
<circle cx="32" cy="32" r="9" fill="none" stroke="url(#g)" stroke-width="4"/>
<circle cx="48" cy="32" r="6" fill="url(#g)"/>
<path d="M22 32h3M39 32h3" stroke="#818cf8" stroke-width="3" stroke-linecap="round"/>
</svg>
"""


# -- orquestacion -----------------------------------------------------------


def write(rel: str, content: str) -> None:
    target = SITE / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main() -> int:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    cases = load_cases()
    version = repo_version()
    sources = markdown_files()
    pages = {rel.as_posix(): rel.with_suffix(".html").as_posix() for rel in sources}

    broken: list[str] = []
    assets: set[str] = set()
    summaries: dict[str, str] = {}
    titles: dict[str, str] = {}

    for rel in sources:
        src = rel.as_posix()
        out_rel = pages[src]
        page, resolver, title = render_doc_page(rel, out_rel, pages)
        write(out_rel, page)
        broken.extend(resolver.broken)
        assets |= resolver.assets
        titles[src] = title
        summaries[src] = summary(
            (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        )

    write("index.html", build_index(cases, pages, version))
    write("casos.html", build_cases_page(cases, pages))
    write("documentacion.html", build_docs_index(pages, summaries, titles))
    write("404.html", build_404())

    shutil.copytree(SITE_SRC / "assets", SITE / "assets", dirs_exist_ok=True)
    write("assets/favicon.svg", FAVICON)
    for asset in sorted(assets):
        target = SITE / "assets" / "repo" / asset
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / asset, target)

    urls = ["", "casos.html", "documentacion.html"] + sorted(pages.values())
    sitemap = "\n".join(
        f"  <url><loc>{esc(SITE_URL + url)}</loc></url>" for url in dict.fromkeys(urls)
    )
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap}\n</urlset>\n",
    )
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n")
    # GitHub Pages pasa el artefacto por Jekyll salvo que exista este fichero;
    # sin el, cualquier ruta que empiece por `_` desaparece del sitio publicado.
    write(".nojekyll", "")

    if broken:
        print(
            f"ERROR: {len(broken)} enlaces rotos en la documentacion:", file=sys.stderr
        )
        for item in sorted(set(broken)):
            print(f"  x {item}", file=sys.stderr)
        return 1

    html_pages = len(list(SITE.rglob("*.html")))
    print(
        f"casos en el catalogo : {len(cases)} ({sum(1 for c in cases if c['status'] != 'planned')} operativos)"
    )
    print(f"documentos renderizados: {len(sources)}")
    print(f"paginas HTML generadas : {html_pages}")
    print(f"version del repositorio: {version}")
    print(f"sitio en              : {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
