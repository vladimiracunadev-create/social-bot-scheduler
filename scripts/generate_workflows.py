#!/usr/bin/env python3
"""
Script para generar workflows de n8n con resiliencia completa para todos los casos.
"""

import json
from pathlib import Path

# Configuración de casos
CASES = {
    "02": {
        "name": "Python to Go",
        "dest_url": "http://dest-go:8080/webhook",
        "error_url": "http://dest-go:8080/errors",
    },
    "03": {
        "name": "Go to Node",
        "dest_url": "http://dest-node:3000/webhook",
        "error_url": "http://dest-node:3000/errors",
    },
    "04": {
        "name": "Node to FastAPI",
        "dest_url": "http://dest-fastapi:8000/webhook",
        "error_url": "http://dest-fastapi:8000/errors",
    },
    "05": {
        "name": "Laravel to React",
        "dest_url": "http://dest-react:4000/webhook",
        "error_url": "http://dest-react:4000/errors",
    },
    "06": {
        "name": "Go to Symfony",
        "dest_url": "http://dest-symfony:80/index.php",
        "error_url": "http://dest-symfony:80/errors",
    },
    "07": {
        "name": "Rust to Ruby",
        "dest_url": "http://dest-ruby:4567/webhook",
        "error_url": "http://dest-ruby:4567/errors",
    },
    "08": {
        "name": "C# to Flask",
        "dest_url": "http://dest-flask:5000/webhook",
        "error_url": "http://dest-flask:5000/errors",
    },
}


def generate_workflow(case_id, case_name, dest_url, error_url):
    """Genera un workflow completo con resiliencia para un caso específico."""
    return {
        "name": f"Case {case_id} - {case_name} (Complete Resilience)",
        "nodes": [
            {
                "parameters": {
                    "path": f"social-bot-scheduler-case-{case_id}",
                    "responseMode": "lastNode",
                },
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [250, 400],
            },
            {
                "parameters": {
                    "values": {
                        "string": [
                            {
                                "name": "fingerprint",
                                "value": "={{$json.body.id}}_{{$json.body.channel}}",
                            },
                            {"name": "case_id", "value": case_id},
                        ]
                    }
                },
                "name": "Set Fingerprint",
                "type": "n8n-nodes-base.set",
                "typeVersion": 1,
                "position": [450, 400],
            },
            {
                "parameters": {
                    "command": "=python3 /data/scripts/circuit_breaker.py check {{$json.case_id}}"
                },
                "name": "Check Circuit Breaker",
                "type": "n8n-nodes-base.executeCommand",
                "typeVersion": 1,
                "position": [650, 400],
            },
            {
                "parameters": {
                    "conditions": {
                        "boolean": [
                            {
                                "value1": "={{JSON.parse($json.stdout).can_proceed}}",
                                "value2": True,
                            }
                        ]
                    }
                },
                "name": "Can Proceed?",
                "type": "n8n-nodes-base.if",
                "typeVersion": 1,
                "position": [850, 400],
            },
            {
                "parameters": {
                    "command": "=python3 /data/scripts/check_idempotency.py check {{$node['Set Fingerprint'].json.fingerprint}} {{$node['Set Fingerprint'].json.case_id}}"
                },
                "name": "Check Idempotency",
                "type": "n8n-nodes-base.executeCommand",
                "typeVersion": 1,
                "position": [1050, 300],
            },
            {
                "parameters": {
                    "conditions": {
                        "boolean": [
                            {
                                "value1": "={{JSON.parse($json.stdout).exists}}",
                                "value2": False,
                            }
                        ]
                    }
                },
                "name": "Is New Post?",
                "type": "n8n-nodes-base.if",
                "typeVersion": 1,
                "position": [1250, 300],
            },
            {
                "parameters": {
                    "command": "=python3 /data/scripts/check_idempotency.py add {{$node['Set Fingerprint'].json.fingerprint}} {{$node['Set Fingerprint'].json.case_id}}"
                },
                "name": "Add Fingerprint",
                "type": "n8n-nodes-base.executeCommand",
                "typeVersion": 1,
                "position": [1450, 200],
            },
            {
                "parameters": {
                    "requestMethod": "POST",
                    "url": dest_url,
                    "jsonParameters": True,
                    "options": {
                        "retryOnFail": True,
                        "maxRetries": 3,
                        "waitBetweenRetries": 1000,
                    },
                    "bodyParametersJson": "={{JSON.stringify($node['Set Fingerprint'].json.body)}}",
                },
                "name": "HTTP Request",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [1650, 200],
                "onError": "continueErrorOutput",
            },
            {
                "parameters": {
                    "command": "=python3 /data/scripts/circuit_breaker.py record_success {{$node['Set Fingerprint'].json.case_id}}"
                },
                "name": "Record Success",
                "type": "n8n-nodes-base.executeCommand",
                "typeVersion": 1,
                "position": [1850, 200],
            },
            {
                "parameters": {
                    "command": "=python3 /data/scripts/circuit_breaker.py record_failure {{$node['Set Fingerprint'].json.case_id}}"
                },
                "name": "Record Failure",
                "type": "n8n-nodes-base.executeCommand",
                "typeVersion": 1,
                "position": [1850, 400],
            },
            {
                "parameters": {
                    "requestMethod": "POST",
                    "url": error_url,
                    "jsonParameters": True,
                    "bodyParametersJson": f"={{{{JSON.stringify({{ error: $json.error, payload: $node['Set Fingerprint'].json.body, case: '{case_id}', fingerprint: $node['Set Fingerprint'].json.fingerprint }})}}}}",
                },
                "name": "Dead Letter Queue (DLQ)",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [2050, 400],
            },
        ],
        "connections": {
            "Webhook": {
                "main": [[{"node": "Set Fingerprint", "type": "main", "index": 0}]]
            },
            "Set Fingerprint": {
                "main": [
                    [{"node": "Check Circuit Breaker", "type": "main", "index": 0}]
                ]
            },
            "Check Circuit Breaker": {
                "main": [[{"node": "Can Proceed?", "type": "main", "index": 0}]]
            },
            "Can Proceed?": {
                "main": [
                    [{"node": "Check Idempotency", "type": "main", "index": 0}],
                    [],
                ]
            },
            "Check Idempotency": {
                "main": [[{"node": "Is New Post?", "type": "main", "index": 0}]]
            },
            "Is New Post?": {
                "main": [[{"node": "Add Fingerprint", "type": "main", "index": 0}], []]
            },
            "Add Fingerprint": {
                "main": [[{"node": "HTTP Request", "type": "main", "index": 0}]]
            },
            "HTTP Request": {
                "main": [
                    [{"node": "Record Success", "type": "main", "index": 0}],
                    [{"node": "Record Failure", "type": "main", "index": 0}],
                ]
            },
            "Record Failure": {
                "main": [
                    [{"node": "Dead Letter Queue (DLQ)", "type": "main", "index": 0}]
                ]
            },
        },
    }


def main():
    base_path = Path("cases")

    for case_id, config in CASES.items():
        case_dir = base_path / f"{case_id}-*"
        # Buscar directorio que coincida con el patrón
        matching_dirs = list(base_path.glob(f"*{case_id}*"))

        if not matching_dirs:
            print(f"[ERROR] No se encontro directorio para caso {case_id}")
            continue

        case_dir = matching_dirs[0]
        workflow_file = case_dir / "n8n" / "workflow.json"

        # Generar workflow
        workflow = generate_workflow(
            case_id, config["name"], config["dest_url"], config["error_url"]
        )

        # Guardar
        workflow_file.parent.mkdir(parents=True, exist_ok=True)
        with open(workflow_file, "w") as f:
            json.dump(workflow, f, indent=2)

        print(f"[OK] Caso {case_id}: {workflow_file}")

    print("\n[OK] Todos los workflows generados exitosamente!")


if __name__ == "__main__":
    main()
