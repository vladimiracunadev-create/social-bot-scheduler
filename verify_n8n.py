"""Utility script to verify n8n health and imported workflows."""

from __future__ import annotations

import sys
from pathlib import Path

import requests


def load_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def looks_like_placeholder(value: str) -> bool:
    lowered = value.lower()
    return "change-me" in lowered or "local.invalid" in lowered


def main() -> int:
    env = load_env_file(Path(".env"))

    base_url = (
        env.get("N8N_EDITOR_BASE_URL")
        or env.get("N8N_WEBHOOK_URL", "http://localhost:5678/")
    ).rstrip("/")
    owner_email = env.get("N8N_OWNER_EMAIL", "change-me@local.invalid")
    owner_password = env.get("N8N_OWNER_PASSWORD", "ChangeMe-Local-Only!")

    try:
        response = requests.get(f"{base_url}/healthz", timeout=5)
        print(f"[+] n8n health check: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERROR] n8n is not responding")
        print("[INFO] Wait a few seconds or inspect: docker-compose logs n8n")
        return 1
    except Exception as exc:  # pragma: no cover - defensive utility script
        print(f"[ERROR] {exc}")
        return 1

    session = requests.Session()
    if not looks_like_placeholder(owner_email) and not looks_like_placeholder(
        owner_password
    ):
        login_response = session.post(
            f"{base_url}/api/v1/login",
            json={"email": owner_email, "password": owner_password},
            timeout=5,
        )
        if login_response.status_code == 200:
            print(f"[+] Authenticated as {owner_email}")
        else:
            print(
                f"[!] Login failed with status {login_response.status_code}; "
                "continuing with unauthenticated checks."
            )
    else:
        print(
            "[!] Placeholder credentials detected in .env; skipping authenticated API checks."
        )

    workflows_response = session.get(f"{base_url}/api/v1/workflows", timeout=5)
    if workflows_response.status_code == 200:
        workflows = workflows_response.json().get("data", [])
        print(f"[+] Imported workflows: {len(workflows)}")
        for workflow in workflows:
            status = "ACTIVE" if workflow.get("active") else "INACTIVE"
            print(f"   - {workflow.get('name', 'Unknown')}: {status}")
    else:
        print(f"[!] Workflows endpoint returned {workflows_response.status_code}")
        print("[INFO] Verify credentials in .env or inspect the n8n UI manually.")

    print(f"\n[SUCCESS] n8n is reachable at {base_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
