#!/usr/bin/env python3
"""
Script para generar workflows de n8n con resiliencia completa para todos los casos.
"""

import json
from pathlib import Path

# Configuración de casos
CASES = {
    "01": {
        "name": "Python to PHP",
        "webhook_path": "social-bot-scheduler-php",
        "dest_url": "http://dest-php:80/index.php",
        "error_url": "http://dest-php:80/errors.php",
    },
    "02": {
        "name": "Python to Go",
        "webhook_path": "social-bot-scheduler-go",
        "dest_url": "http://dest-go:8080/webhook",
        "error_url": "http://dest-go:8080/errors",
    },
    "03": {
        "name": "Go to Node",
        "webhook_path": "social-bot-scheduler-node",
        "dest_url": "http://dest-node:3000/webhook",
        "error_url": "http://dest-node:3000/errors",
    },
    "04": {
        "name": "Node to FastAPI",
        "webhook_path": "social-bot-scheduler-fastapi",
        "dest_url": "http://dest-fastapi:8000/webhook",
        "error_url": "http://dest-fastapi:8000/errors",
    },
    "05": {
        "name": "Laravel to React",
        "webhook_path": "social-bot-scheduler-react",
        "dest_url": "http://dest-react:4000/webhook",
        "error_url": "http://dest-react:4000/errors",
    },
    "06": {
        "name": "Go to Symfony",
        "webhook_path": "social-bot-scheduler-symfony",
        "dest_url": "http://dest-symfony:80/index.php",
        "error_url": "http://dest-symfony:80/errors",
    },
    "07": {
        "name": "Rust to Ruby",
        "webhook_path": "social-bot-scheduler-ruby",
        "dest_url": "http://dest-ruby:4567/webhook",
        "error_url": "http://dest-ruby:4567/errors",
    },
    "08": {
        "name": "C# to Flask",
        "webhook_path": "social-bot-scheduler-flask",
        "dest_url": "http://dest-flask:5000/webhook",
        "error_url": "http://dest-flask:5000/errors",
    },
}


def generate_workflow(case_id, case_name, webhook_path, dest_url, error_url):
    """Genera un workflow completo con resiliencia para un caso específico."""
    return {
        "name": f"Case {case_id} - {case_name} (Resilience v3.0)",
        "nodes": [
            {
                "parameters": {
                    "path": webhook_path,
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
                            {
                                "name": "body",
                                "value": "={{JSON.stringify($json.body)}}",
                            },
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
                    "bodyParametersJson": "={{$node['Set Fingerprint'].json.body}}",
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
                    "bodyParametersJson": f"={{{{JSON.stringify({{ error: $json.error, payload: JSON.parse($node['Set Fingerprint'].json.body), case: '{case_id}', fingerprint: $node['Set Fingerprint'].json.fingerprint }})}}}}",
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
    output_base = Path("n8n/workflows")
    output_base.mkdir(parents=True, exist_ok=True)

    # Mapeo de nombres de archivos existentes para mantener consistencia
    FILE_NAMES = {
        "01": "case-01-python-to-php.json",
        "02": "case-02-python-to-go.json",
        "03": "case-03-go-to-node.json",
        "04": "case-04-node-to-fastapi.json",
        "05": "case-05-laravel-to-react.json",
        "06": "case-06-go-to-symfony.json",
        "07": "case-07-rust-to-ruby.json",
        "08": "case-08-csharp-to-flask.json",
    }

    for case_id, config in CASES.items():
        workflow_file = output_base / FILE_NAMES[case_id]

        # Generar workflow
        workflow = generate_workflow(
            case_id,
            config["name"],
            config["webhook_path"],
            config["dest_url"],
            config["error_url"],
        )

        # Guardar
        with open(workflow_file, "w") as f:
            json.dump(workflow, f, indent=2)

        print(f"[OK] Generado: {workflow_file}")

    print("\n[OK] Todos los workflows regenerados exitosamente en n8n/workflows/")


if __name__ == "__main__":
    main()
