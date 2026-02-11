import json
import os
import sys


def validate_workflow(file_path):
    required_nodes = ["Set Fingerprint", "HTTP Request", "Dead Letter Queue (DLQ)"]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        nodes = [node.get("name") for node in data.get("nodes", [])]
        missing = [req for req in required_nodes if req not in nodes]

        if missing:
            print(f"[ERROR] {file_path}: Faltan nodos: {', '.join(missing)}")
            return False

        # Verificar configuración de reintentos en HTTP Request
        http_node = next(
            (n for n in data["nodes"] if n["name"] == "HTTP Request"), None
        )
        if http_node:
            options = http_node.get("parameters", {}).get("options", {})
            if not options.get("retryOnFail"):
                print(
                    f"[WARNING] {file_path}: 'HTTP Request' no tiene habilitado 'retryOnFail'"
                )
                return False

        print(f"[OK] {file_path}: Estructura de Guardrails correcta.")
        return True
    except Exception as e:
        print(f"[FAIL] Error procesando {file_path}: {e}")
        return False


def main():
    cases_dir = "cases"
    all_valid = True
    print("Iniciando validación estructural de flujos n8n...\n")

    for i in range(1, 9):
        case_num = str(i).zfill(2)
        # Buscar el nombre exacto de la carpeta del caso
        case_folder = next(
            (f for f in os.listdir(cases_dir) if f.startswith(case_num)), None
        )
        if not case_folder:
            continue

        workflow_path = os.path.join(cases_dir, case_folder, "n8n", "workflow.json")
        if os.path.exists(workflow_path):
            if not validate_workflow(workflow_path):
                all_valid = False
        else:
            print(f"❓ {workflow_path} no encontrado.")

    if not all_valid:
        sys.exit(1)
    print("\n[FIN] Todos los flujos cumplen con los estandares de Guardrails.")


if __name__ == "__main__":
    main()
