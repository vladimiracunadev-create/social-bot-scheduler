#!/usr/bin/env python3
"""
==================================================================================================
VALIDADOR DE PUERTOS — la garantía "ningún caso se puede romper". (Sin dependencias externas.)
==================================================================================================
Regla canónica y única del laboratorio:

        puerto_host(caso) = PORT_BASE + numero_de_caso        (PORT_BASE = 8080)

    caso 01 -> 8081, ..., caso 09 -> 8089, caso 10 -> 8090, ..., caso 20 -> 8100,
    caso 30 -> 8110, ... (escala hasta ~caso 1000 antes de tocar Prometheus:9090).

Se ejecuta en CI (y localmente) y FALLA si:
  1. El `port` del `app.manifest.yml` de algún caso no cumple la fórmula.
  2. Dos servicios publican el mismo puerto host (misma pareja puerto/protocolo) en compose.
  3. Un caso implementado (status != planned) no publica su puerto de fórmula en compose.
  4. Un puerto de infraestructura reservado colisiona con la banda de un caso implementado.

Así, cualquier colisión o desvío se detecta ANTES de levantar nada.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "cases"
COMPOSE = ROOT / "docker-compose.yml"

PORT_BASE = 8080

RESERVED_INFRA = {
    3000: "grafana",
    5678: "n8n",
    8080: "master-dashboard",
    9090: "prometheus",
    9091: "cadvisor",
}

# host:container(/proto) al final de una entrada de puertos de compose.
COMPOSE_PORT_RE = re.compile(r"(\d+):\d+(?:/(tcp|udp))?\"")
ID_RE = re.compile(r'^id:\s*"?(\d+)"?', re.M)
PORT_RE = re.compile(r"^\s*port:\s*(\d+)", re.M)
STATUS_RE = re.compile(r'^status:\s*"?(\w+)"?', re.M)


def expected_port(case_id: str) -> int:
    return PORT_BASE + int(case_id)


def load_manifests() -> list[dict]:
    cases = []
    for manifest in sorted(CASES_DIR.glob("*/app.manifest.yml")):
        text = manifest.read_text(encoding="utf-8-sig")
        cid = ID_RE.search(text)
        port = PORT_RE.search(text)
        status = STATUS_RE.search(text)
        cases.append(
            {
                "id": cid.group(1) if cid else None,
                "port": int(port.group(1)) if port else None,
                "status": status.group(1) if status else "ready",
                "path": manifest.parent.name,
            }
        )
    return cases


def collect_compose_ports() -> list[tuple[int, str]]:
    text = COMPOSE.read_text(encoding="utf-8")
    out = []
    for m in COMPOSE_PORT_RE.finditer(text):
        out.append((int(m.group(1)), m.group(2) or "tcp"))
    return out


def main() -> int:
    errors: list[str] = []
    cases = load_manifests()

    # (1) Fórmula en cada manifest.
    for c in cases:
        if c["id"] is None:
            errors.append(f"[manifest] {c['path']}: sin campo id")
            continue
        exp = expected_port(c["id"])
        if c["port"] != exp:
            errors.append(
                f"[formula] caso {c['id']} ({c['path']}): port={c['port']}, "
                f"esperado {exp} (= {PORT_BASE} + {int(c['id'])})"
            )

    # (2) Unicidad global de puertos host (por puerto/protocolo).
    seen: dict[tuple[int, str], bool] = {}
    for host_port, proto in collect_compose_ports():
        key = (host_port, proto)
        if key in seen:
            errors.append(f"[colision] puerto {host_port}/{proto} publicado por 2+ servicios")
        seen[key] = True

    published = {p for p, _ in seen}

    # (3) Cada caso implementado publica su puerto de fórmula.
    for c in cases:
        if c["status"] == "planned" or c["id"] is None:
            continue
        exp = expected_port(c["id"])
        if exp not in published:
            errors.append(
                f"[cableado] caso {c['id']} (implementado) no publica su puerto "
                f"de fórmula {exp} en docker-compose.yml"
            )

    # (4) Infra reservada no colisiona con la banda de casos implementados.
    case_ports = {expected_port(c["id"]) for c in cases if c["status"] != "planned" and c["id"]}
    for port, name in RESERVED_INFRA.items():
        if port in case_ports:
            errors.append(f"[infra] '{name}' usa {port}, puerto de fórmula de un caso")

    if errors:
        print("Validacion de puertos FALLIDA:")
        for e in errors:
            print(f" - {e}")
        return 1

    ready = sorted((c for c in cases if c["status"] != "planned" and c["id"]), key=lambda x: x["id"])
    print(f"Validacion de puertos OK - {len(ready)} casos implementados, formula 8080+id.")
    print("  " + ", ".join(f"{c['id']}:{expected_port(c['id'])}" for c in ready))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
