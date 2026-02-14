#!/usr/bin/env python3
"""
Generador Único y Definitivo de Workflows n8n
Genera workflows simples y confiables para los 8 casos de integración.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

# Configuración de los 8 casos
CASES = [
    ("01", "PYTHON TO PHP", "php", "social-bot-dest-php", 80, "/index.php"),
    ("02", "PYTHON TO GO", "go", "social-bot-dest-go", 8080, "/webhook"),
    ("03", "GO TO NODE", "node", "social-bot-dest-node", 3000, "/webhook"),
    ("04", "NODE TO FASTAPI", "fastapi", "social-bot-dest-fastapi", 8000, "/webhook"),
    ("05", "LARAVEL TO REACT", "react", "social-bot-dest-react", 4000, "/webhook"),
    ("06", "GO TO SYMFONY", "symfony", "social-bot-dest-symfony", 80, "/"),
    ("07", "RUST TO RUBY", "ruby", "social-bot-dest-ruby", 4567, "/webhook"),
    ("08", "CSHARP TO FLASK", "flask", "social-bot-dest-flask", 5000, "/webhook")
]


def generate_workflow(case_id: str, name: str, path_suffix: str, 
                      dest_host: str, dest_port: int, dest_path: str) -> Dict[str, Any]:
    """
    Genera un workflow simple y confiable para n8n.
    
    Arquitectura:
    1. Webhook - Recibe POST desde los bots
    2. Prepare Payload - Normaliza datos
    3. HTTP Request - Envía a servicio destino
    
    Esta estructura es aceptada por n8n sin necesidad de configuración adicional.
    """
    workflow = {
        "name": f"CASE {case_id} {name}",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": f"social-bot-scheduler-{path_suffix}",
                    "responseMode": "lastNode"
                },
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [250, 400]
            },
            {
                "parameters": {
                    "values": {
                        "string": [
                            {
                                "name": "channel",
                                "value": "={{$json.body.channels ? $json.body.channels[0] : ($json.body.channel || 'default')}}"
                            },
                            {
                                "name": "id",
                                "value": "={{$json.body.id}}"
                            },
                            {
                                "name": "text",
                                "value": "={{$json.body.text}}"
                            },
                            {
                                "name": "case_id",
                                "value": case_id
                            }
                        ]
                    }
                },
                "name": "Prepare Payload",
                "type": "n8n-nodes-base.set",
                "typeVersion": 1,
                "position": [450, 400]
            },
            {
                "parameters": {
                    "requestMethod": "POST",
                    "url": f"http://{dest_host}:{dest_port}{dest_path}",
                    "jsonParameters": True,
                    "bodyParametersJson": "={{JSON.stringify($node['Prepare Payload'].json)}}"
                },
                "name": "HTTP Request",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 1,
                "position": [650, 400]
            }
        ],
        "connections": {
            "Webhook": {
                "main": [
                    [
                        {
                            "node": "Prepare Payload",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Prepare Payload": {
                "main": [
                    [
                        {
                            "node": "HTTP Request",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {},
        "staticData": None,
        "pinData": {},
        "versionId": None
    }
    return workflow


def validate_workflow(workflow: Dict[str, Any]) -> tuple[bool, str]:
    """
    Valida que el workflow tenga la estructura correcta para n8n.
    
    Returns:
        (is_valid, error_message)
    """
    # Validar campos requeridos
    required_fields = ["name", "nodes", "connections", "active"]
    for field in required_fields:
        if field not in workflow:
            return False, f"Falta campo requerido: {field}"
    
    # Validar que hay nodos
    if not workflow["nodes"]:
        return False, "El workflow debe tener al menos un nodo"
    
    # Validar tipos de nodos
    valid_node_types = [
        "n8n-nodes-base.webhook",
        "n8n-nodes-base.set",
        "n8n-nodes-base.httpRequest"
    ]
    
    for node in workflow["nodes"]:
        if "type" not in node:
            return False, f"Nodo sin tipo: {node.get('name', 'Unknown')}"
        
        if node["type"] not in valid_node_types:
            return False, f"Tipo de nodo inválido: {node['type']}"
        
        if "name" not in node:
            return False, f"Nodo sin nombre"
        
        if "parameters" not in node:
            return False, f"Nodo {node['name']} sin parámetros"
    
    return True, ""


def main():
    """Genera todos los workflows y los guarda en n8n/workflows/"""
    output_dir = Path('n8n/workflows')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("[*] Generador de Workflows n8n v3.0")
    print("=" * 60)
    
    generated_count = 0
    errors = []
    
    for case_id, name, suffix, host, port, path in CASES:
        try:
            # Generar workflow
            workflow = generate_workflow(case_id, name, suffix, host, port, path)
            
            # Validar
            is_valid, error = validate_workflow(workflow)
            if not is_valid:
                errors.append(f"Caso {case_id}: {error}")
                continue
            
            # Guardar
            filename = output_dir / f"case-{case_id}-{name.lower().replace(' ', '-')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2)
            
            print(f"[OK] Caso {case_id}: {filename.name}")
            generated_count += 1
            
        except Exception as e:
            errors.append(f"Caso {case_id}: {str(e)}")
    
    print("=" * 60)
    print(f"[+] Generados: {generated_count}/8 workflows")
    
    if errors:
        print("\n[!] Errores:")
        for error in errors:
            print(f"   - {error}")
        return 1
    
    print("\n[SUCCESS] Todos los workflows generados exitosamente!")
    print("[INFO] Ubicacion: n8n/workflows/")
    print("\n[NEXT] Proximo paso: docker-compose restart n8n")
    return 0

    return 0


if __name__ == "__main__":
    exit(main())
