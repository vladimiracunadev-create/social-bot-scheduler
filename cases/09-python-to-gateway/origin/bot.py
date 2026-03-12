import json
import os
from pathlib import Path

import requests

DEFAULT_WEBHOOK = "http://localhost:5678/webhook/social-bot-scheduler-gateway"
PAYLOAD_FILE = Path(__file__).with_name("payload.example.json")


def load_payload() -> dict:
    with PAYLOAD_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    webhook_url = os.getenv("WEBHOOK_URL", DEFAULT_WEBHOOK)
    payload = load_payload()

    response = requests.post(webhook_url, json=payload, timeout=20)
    print(f"POST {webhook_url}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except ValueError:
        print(response.text)

    response.raise_for_status()


if __name__ == "__main__":
    main()
