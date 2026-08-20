#!/usr/bin/env python3
"""Verifica el sitio generado ANTES de publicarlo.

Por que existe: GitHub Pages despliega un 404 con el mismo exito que una pagina
buena. Un enlace roto no rompe el build, no aparece en ningun log y solo lo
descubre la persona a la que le pasaste el enlace. Por eso la comprobacion
ocurre antes del deploy y falla el workflow.

Que exige:

1. Todo destino interno (`href`/`src`) existe como archivo del sitio.
2. Todo anchor apunta a un `id` que existe en la pagina de destino.
3. Ningun enlace del sitio apunta a un `.md`: la web se navega en HTML.
4. La portada no carga scripts ni hojas de estilo de otro host.
5. Existen las paginas obligatorias y la portada muestra exactamente los casos
   que declaran los manifiestos, cada uno con su ficha publicada.

Con `--external` ademas comprueba por red los destinos http(s). No corre en CI:
depende de terceros y convertiria una caida ajena en un despliegue bloqueado.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "cases"

REQUIRED_PAGES = (
    "index.html",
    "casos.html",
    "documentacion.html",
    "404.html",
    "README.html",
    "SECURITY.html",
    "CHANGELOG.html",
    "docs/ARCHITECTURE.html",
    "docs/INSTALL.html",
    "assets/site.css",
    "assets/favicon.svg",
    "sitemap.xml",
    "robots.txt",
    ".nojekyll",
)

_ATTR_RE = re.compile(r"""\b(href|src)\s*=\s*["']([^"']*)["']""", re.I)
_ID_RE = re.compile(r"""\bid\s*=\s*["']([^"']+)["']""")
# `<link rel="canonical">` apunta al sitio publicado por diseno: lo que importa
# es que no se cargue codigo ni estilos desde otro host.
_EXTERNAL_ASSET_RES = (
    re.compile(r"""<script\b[^>]*\bsrc\s*=\s*["']https?://""", re.I),
    re.compile(
        r"""<link\b[^>]*\brel\s*=\s*["'](?:stylesheet|preload|modulepreload)["']"""
        r"""[^>]*\bhref\s*=\s*["']https?://""",
        re.I,
    ),
)
_LOCAL_SCHEMES = ("mailto:", "tel:", "data:", "javascript:")


def collect_ids(text: str) -> set[str]:
    return set(_ID_RE.findall(text))


def expected_cases() -> list[str]:
    return sorted(path.parent.name for path in CASES_DIR.glob("*/app.manifest.yml"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site", default=str(ROOT / "site"), help="directorio generado"
    )
    parser.add_argument(
        "--external",
        action="store_true",
        help="ademas comprueba por red los enlaces http(s) (lento, depende de terceros)",
    )
    args = parser.parse_args()

    site = Path(args.site).resolve()
    if not site.is_dir():
        print(f"ERROR: no existe el sitio en {site}", file=sys.stderr)
        return 1

    pages = sorted(site.rglob("*.html"))
    if not pages:
        print("ERROR: el sitio no tiene ni una pagina HTML", file=sys.stderr)
        return 1

    contents = {page: page.read_text(encoding="utf-8") for page in pages}
    ids = {
        page.relative_to(site).as_posix(): collect_ids(text)
        for page, text in contents.items()
    }

    errors: list[str] = []
    external: dict[str, list[str]] = defaultdict(list)
    internal_checked = 0

    for page, text in contents.items():
        rel_page = page.relative_to(site).as_posix()
        for _attribute, raw in _ATTR_RE.findall(text):
            value = raw.strip()
            if not value:
                continue
            if value.startswith("#"):
                anchor = unquote(value[1:])
                if anchor and anchor not in ids[rel_page]:
                    errors.append(f"{rel_page}: anchor propio inexistente '{value}'")
                continue
            if value.startswith(_LOCAL_SCHEMES):
                continue
            if value.startswith(("http://", "https://", "//")):
                if urlsplit(value).path.endswith(".md"):
                    errors.append(f"{rel_page}: enlace a Markdown '{value}'")
                external[value].append(rel_page)
                continue

            split = urlsplit(value)
            target_path = unquote(split.path)
            if target_path.endswith(".md"):
                errors.append(f"{rel_page}: enlace a Markdown '{value}'")
                continue
            if target_path.startswith("/"):
                errors.append(
                    f"{rel_page}: ruta absoluta '{value}' (el sitio usa rutas relativas)"
                )
                continue

            resolved = (page.parent / target_path).resolve()
            internal_checked += 1
            if resolved.is_dir():
                resolved = resolved / "index.html"
            if not resolved.exists():
                errors.append(f"{rel_page}: destino inexistente '{value}'")
                continue
            try:
                resolved_rel = resolved.relative_to(site).as_posix()
            except ValueError:
                errors.append(f"{rel_page}: destino fuera del sitio '{value}'")
                continue
            if split.fragment and resolved_rel.endswith(".html"):
                anchor = unquote(split.fragment)
                if anchor not in ids.get(resolved_rel, set()):
                    errors.append(
                        f"{rel_page}: anchor inexistente en destino '{value}'"
                    )

    for required in REQUIRED_PAGES:
        target = site / required
        if not target.is_file():
            errors.append(f"falta la pagina obligatoria: {required}")
        elif target.stat().st_size == 0 and required != ".nojekyll":
            errors.append(f"pagina vacia: {required}")

    index_text = contents.get(site / "index.html", "")
    if any(pattern.search(index_text) for pattern in _EXTERNAL_ASSET_RES):
        errors.append("index.html carga scripts o estilos de un host externo")

    slugs = expected_cases()
    shown = index_text.count('class="case-card"')
    if shown != len(slugs):
        errors.append(
            f"index.html muestra {shown} casos y los manifiestos declaran {len(slugs)}"
        )
    for slug in slugs:
        for doc in ("README.html", "ARCHITECTURE.html"):
            if not (site / "cases" / slug / doc).is_file():
                errors.append(f"falta cases/{slug}/{doc}")

    if args.external:
        errors.extend(check_external(external))

    print(f"paginas revisadas   : {len(pages)}")
    print(f"enlaces internos    : {internal_checked}")
    print(f"enlaces externos    : {len(external)} destinos unicos")
    print(f"casos en la portada : {shown}/{len(slugs)}")

    if errors:
        print(f"\nERRORES ({len(errors)}):", file=sys.stderr)
        for error in errors[:80]:
            print(f"  x {error}", file=sys.stderr)
        if len(errors) > 80:
            print(f"  ... y {len(errors) - 80} mas", file=sys.stderr)
        return 1

    print("\nOK: sin enlaces rotos, sin anchors muertos y sin destinos Markdown.")
    return 0


def check_external(external: dict[str, list[str]]) -> list[str]:
    """Comprobacion opcional por red. Solo se llama con `--external`."""
    problems: list[str] = []
    for url in sorted(external):
        request = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "social-bot-scheduler-linkcheck"}
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status >= 400:
                    problems.append(f"{url} -> HTTP {response.status}")
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 405, 429):
                continue  # el host rechaza HEAD o limita: no es un enlace roto
            problems.append(f"{url} -> HTTP {exc.code}")
        except (
            Exception
        ) as exc:  # noqa: BLE001 - cualquier fallo de red se reporta igual
            problems.append(f"{url} -> {type(exc).__name__}: {exc}")
    return problems


if __name__ == "__main__":
    raise SystemExit(main())
