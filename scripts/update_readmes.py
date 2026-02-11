import os
import re

# Template de la sección de Guardrails
guardrails_template = """
## 🛡️ Guardrails Implementados

Este caso incluye mecanismos de resiliencia en la capa de n8n:

### Reintentos Automáticos
- El nodo HTTP Request está configurado con **3 reintentos** (backoff de 1 segundo).
- Si el servicio de destino está caído, n8n intentará 3 veces antes de marcar el envío como fallido.

### Dead Letter Queue (DLQ)
- Si todos los reintentos fallan, el payload se envía a un endpoint `/errors` del servicio de destino.
- Los errores se registran con timestamp, caso, error y payload completo.

Para más detalles, consulta la guía de [Guardrails](../../docs/GUARDRAILS.md).

"""

# Casos a actualizar (03-08)
cases = [
    "03-go-to-node",
    "04-node-to-fastapi",
    "05-laravel-to-react",
    "06-go-to-symfony",
    "07-rust-to-ruby",
    "08-csharp-to-flask"
]

for case in cases:
    readme_path = f"cases/{case}/README.md"
    
    if not os.path.exists(readme_path):
        print(f"[SKIP] {readme_path} no encontrado")
        continue
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la sección de Verificación
    if "## 🚦 Verificación" in content:
        # Insertar la sección de Guardrails antes de Verificación
        updated_content = content.replace(
            "## 🚦 Verificación",
            guardrails_template + "## 🚦 Verificación"
        )
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"[OK] {readme_path} actualizado")
    else:
        print(f"[WARNING] {readme_path} no tiene sección de Verificación")

print("\n[FIN] Actualización de READMEs completada")
