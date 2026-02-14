"""Script para importar workflows a n8n manualmente via API"""

import requests
import json
import glob
import time
from pathlib import Path

N8N_URL = "http://localhost:5678"
CREDENTIALS = {"email": "admin@social-bot.local", "password": "SocialBot2026!"}


def setup_owner():
    """Crear owner si no existe"""
    try:
        print("[*] Intentando crear owner...")
        r = requests.post(
            f"{N8N_URL}/api/v1/owner/setup",
            json={
                "email": CREDENTIALS["email"],
                "firstName": "Admin",
                "lastName": "SocialBot",
                "password": CREDENTIALS["password"],
            },
            timeout=5,
        )
        if r.status_code in [200, 201]:
            print("[+] Owner creado exitosamente")
            time.sleep(2)  # Esperar a que se configure
            return True
        elif r.status_code == 400:
            print("[+] Owner ya existe")
            return True
        else:
            print(f"[!] Setup owner: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False


def login():
    """Login y obtener sesión"""
    session = requests.Session()
    try:
        print("[*] Intentando login...")
        r = session.post(f"{N8N_URL}/api/v1/login", json=CREDENTIALS, timeout=5)
        if r.status_code == 200:
            print("[+] Login exitoso")
            return session
        else:
            print(f"[!] Login falló: {r.status_code} - {r.text}")
            return None
    except Exception as e:
        print(f"[!] Error en login: {e}")
        return None


def import_workflows(session):
    """Importar todos los workflows"""
    workflows_dir = Path("n8n/workflows")
    workflow_files = list(workflows_dir.glob("*.json"))

    if not workflow_files:
        print("[!] No se encontraron workflows en n8n/workflows/")
        return 0

    print(f"\n[*] Encontrados {len(workflow_files)} workflows para importar")
    imported = 0

    for workflow_file in sorted(workflow_files):
        try:
            # Leer workflow
            with open(workflow_file, "r", encoding="utf-8") as f:
                workflow_data = json.load(f)

            workflow_name = workflow_data.get("name", workflow_file.stem)
            print(f"\n[*] Importando: {workflow_name}...")

            # Importar workflow
            r = session.post(
                f"{N8N_URL}/api/v1/workflows", json=workflow_data, timeout=10
            )

            if r.status_code in [200, 201]:
                workflow_id = r.json().get("id")
                print(f"    [+] Importado (ID: {workflow_id})")

                # Activar workflow
                time.sleep(0.5)
                activate_r = session.patch(
                    f"{N8N_URL}/api/v1/workflows/{workflow_id}",
                    json={"active": True},
                    timeout=5,
                )

                if activate_r.status_code == 200:
                    print(f"    [+] ACTIVADO")
                    imported += 1
                else:
                    print(f"    [!] No se pudo activar: {activate_r.status_code}")
            else:
                print(f"    [!] Error importando: {r.status_code} - {r.text[:100]}")

        except Exception as e:
            print(f"    [!] Error: {e}")

    return imported


def main():
    print("=" * 60)
    print("[*] Importador Manual de Workflows n8n")
    print("=" * 60)

    # Verificar health
    try:
        r = requests.get(f"{N8N_URL}/healthz", timeout=3)
        if r.status_code != 200:
            print("[!] n8n no está respondiendo")
            return 1
        print("[+] n8n está saludable")
    except:
        print("[!] No se puede conectar a n8n")
        return 1

    # Setup owner
    if not setup_owner():
        print("[!] No se pudo configurar owner")
        return 1

    # Login
    session = login()
    if not session:
        print("\n[ERROR] No se pudo hacer login")
        print("[INFO] Accede manualmente a http://localhost:5678 y crea la cuenta")
        return 1

    # Importar workflows
    print("\n" + "=" * 60)
    imported = import_workflows(session)
    print("\n" + "=" * 60)

    if imported > 0:
        print(f"[SUCCESS] {imported}/8 workflows importados y activados!")
        print(f"\n[NEXT] Verifica en: http://localhost:5678")
        print(
            f"[NEXT] Prueba el bot: cd cases/01-python-to-php/origin && python bot.py"
        )
        return 0
    else:
        print("[!] No se importó ningún workflow")
        return 1


if __name__ == "__main__":
    exit(main())
