"""Guardrails to keep compose/runtime hardening from regressing."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - defensive UX for clean machines
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILES = [ROOT / "docker-compose.yml", ROOT / "docker-compose.dev.yml"]
DOCKERFILES = list(ROOT.rglob("Dockerfile"))
SENSITIVE_ENV_KEYS = {
    "CASE01_DB_PASSWORD",
    "CASE02_DB_PASSWORD",
    "CASE03_DB_PASSWORD",
    "CASE08_DB_PASSWORD",
    "GF_SECURITY_ADMIN_PASSWORD",
    "INTEGRATION_API_KEY",
    "MARIADB_ROOT_PASSWORD",
    "MSSQL_SA_PASSWORD",
    "MYSQL_ROOT_PASSWORD",
    "N8N_ENCRYPTION_KEY",
    "N8N_OWNER_PASSWORD",
    "POSTGRES_PASSWORD",
    "EDGE_BASIC_AUTH_HASH",
}
PROFILE_REQUIREMENTS = {
    "prometheus": {"observability", "full"},
    "grafana": {"observability", "full"},
    "cadvisor": {"observability", "full"},
    "edge-proxy": {"edge"},
}
ALLOWED_PORT_PREFIXES = (
    "${HOST_BIND_IP:-127.0.0.1}",
    "${EDGE_BIND_IP:-127.0.0.1}",
)


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def env_items(service: dict[str, Any]) -> dict[str, str]:
    environment = service.get("environment", {})
    parsed: dict[str, str] = {}

    if isinstance(environment, list):
        for item in environment:
            if isinstance(item, str) and "=" in item:
                key, value = item.split("=", 1)
                parsed[key] = value
    elif isinstance(environment, dict):
        for key, value in environment.items():
            parsed[str(key)] = "" if value is None else str(value)

    return parsed


def validate_compose(compose_file: Path) -> list[str]:
    issues: list[str] = []
    data = load_yaml(compose_file)

    for service_name, service in (data.get("services") or {}).items():
        image = service.get("image")
        if isinstance(image, str) and ":latest" in image:
            issues.append(
                f"{compose_file.name}:{service_name} uses a mutable image tag: {image}"
            )

        for port in service.get("ports", []) or []:
            if isinstance(port, str):
                if "0.0.0.0" in port:
                    issues.append(
                        f"{compose_file.name}:{service_name} publishes on 0.0.0.0: {port}"
                    )
                if not port.startswith(ALLOWED_PORT_PREFIXES):
                    issues.append(
                        f"{compose_file.name}:{service_name} does not pin the host bind IP to loopback/env: {port}"
                    )

        env_map = env_items(service)
        for key, value in env_map.items():
            if key in SENSITIVE_ENV_KEYS and "${" not in value:
                issues.append(
                    f"{compose_file.name}:{service_name} hardcodes sensitive env {key}"
                )

        if service_name in PROFILE_REQUIREMENTS:
            profiles = set(service.get("profiles", []) or [])
            required = PROFILE_REQUIREMENTS[service_name]
            if not profiles or not required.issubset(profiles):
                issues.append(
                    f"{compose_file.name}:{service_name} must declare profiles {sorted(required)}"
                )

    return issues


def validate_dockerfile(path: Path) -> list[str]:
    issues: list[str] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if re.search(r"^\s*FROM\s+\S+:latest\b", line, flags=re.IGNORECASE):
            issues.append(f"{path.relative_to(ROOT)}:{lineno} uses a mutable Docker base tag")
    return issues


def main() -> int:
    if yaml is None:
        print("[runtime-security] PyYAML is required. Install dependencies from requirements.txt first.")
        return 2

    issues: list[str] = []

    for compose_file in COMPOSE_FILES:
        issues.extend(validate_compose(compose_file))

    for dockerfile in DOCKERFILES:
        issues.extend(validate_dockerfile(dockerfile))

    if issues:
        print("[runtime-security] FAIL")
        for issue in issues:
            print(f" - {issue}")
        return 1

    print("[runtime-security] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
