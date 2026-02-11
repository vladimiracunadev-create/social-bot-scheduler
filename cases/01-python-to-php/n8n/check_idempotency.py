#!/usr/bin/env python3
"""
Script de ayuda para verificar idempotencia en n8n.
Lee fingerprints procesados de un archivo JSON y verifica si un nuevo fingerprint ya existe.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

FINGERPRINTS_FILE = Path(__file__).parent / "processed_fingerprints.json"
TTL_HOURS = 24


def load_fingerprints():
    """Carga fingerprints del archivo JSON, limpiando los expirados."""
    if not FINGERPRINTS_FILE.exists():
        return {}

    with open(FINGERPRINTS_FILE, "r") as f:
        data = json.load(f)

    # Limpiar fingerprints expirados (> 24 horas)
    now = datetime.now()
    cleaned = {}
    for fp, timestamp_str in data.items():
        timestamp = datetime.fromisoformat(timestamp_str)
        if now - timestamp < timedelta(hours=TTL_HOURS):
            cleaned[fp] = timestamp_str

    return cleaned


def save_fingerprints(fingerprints):
    """Guarda fingerprints en el archivo JSON."""
    with open(FINGERPRINTS_FILE, "w") as f:
        json.dump(fingerprints, f, indent=2)


def check_fingerprint(fingerprint):
    """Verifica si un fingerprint ya fue procesado."""
    fingerprints = load_fingerprints()
    return fingerprint in fingerprints


def add_fingerprint(fingerprint):
    """Agrega un nuevo fingerprint al registro."""
    fingerprints = load_fingerprints()
    fingerprints[fingerprint] = datetime.now().isoformat()
    save_fingerprints(fingerprints)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: check_idempotency.py <fingerprint>"}))
        sys.exit(1)

    action = sys.argv[1]

    if action == "check" and len(sys.argv) == 3:
        fingerprint = sys.argv[2]
        exists = check_fingerprint(fingerprint)
        print(json.dumps({"exists": exists, "fingerprint": fingerprint}))

    elif action == "add" and len(sys.argv) == 3:
        fingerprint = sys.argv[2]
        add_fingerprint(fingerprint)
        print(json.dumps({"added": True, "fingerprint": fingerprint}))

    else:
        print(json.dumps({"error": "Invalid action. Use 'check <fp>' or 'add <fp>'"}))
        sys.exit(1)
