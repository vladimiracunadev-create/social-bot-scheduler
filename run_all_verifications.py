import requests
import json

CASES = [
    {"id": "01", "path": "social-bot-scheduler-php", "port": 5678},
    {"id": "02", "path": "social-bot-scheduler-case-02", "port": 5678},
    {"id": "03", "path": "social-bot-scheduler-case-03", "port": 5678},
    {"id": "04", "path": "social-bot-scheduler-case-04", "port": 5678},
    {"id": "05", "path": "social-bot-scheduler-case-05", "port": 5678},
    {"id": "06", "path": "social-bot-scheduler-case-06", "port": 5678},
    {"id": "07", "path": "social-bot-scheduler-case-07", "port": 5678},
    {"id": "08", "path": "social-bot-scheduler-case-08", "port": 5678},
]


def trigger_case(case):
    url = f"http://localhost:{case['port']}/webhook/{case['path']}"
    payload = {
        "id": f"verify-case-{case['id']}",
        "text": f"End-to-end verification for Case {case['id']}",
        "channel": "automated-verification-script",
        "scheduled_at": "2026-02-13T19:10:00",
    }
    headers = {"Content-Type": "application/json"}
    try:
        print(f"Triggering Case {case['id']} at {url}...")
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Response Case {case['id']}: {resp.status_code}")
        if not resp.ok:
            print(f"Error: {resp.text}")
        return resp.ok
    except Exception as e:
        print(f"Exception Case {case['id']}: {e}")
        return False


results = {}
for case in CASES:
    results[case["id"]] = trigger_case(case)

print("\n--- Summary ---")
for cid, success in results.items():
    status = "SUCCESS" if success else "FAILED"
    print(f"Case {cid}: {status}")
