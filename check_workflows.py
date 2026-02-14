"""Script para verificar el estado de workflows en n8n y activarlos si es necesario"""
import requests
import json
import time

N8N_URL = "http://localhost:5678"
CREDENTIALS = {
    "email": "admin@social-bot.local",
    "password": "SocialBot2026!"
}

def setup_owner():
    """Crear el owner si no existe"""
    try:
        response = requests.post(
            f"{N8N_URL}/api/v1/owner/setup",
            json={
                "email": CREDENTIALS["email"],
                "firstName": "Admin",
                "lastName": "SocialBot",
                "password": CREDENTIALS["password"]
            },
            timeout=5
        )
        if response.status_code == 200:
            print("[+] Owner creado exitosamente")
            return True
        else:
            print(f"[!] Setup owner: {response.status_code}")
            return False
    except Exception as e:
        print(f"[!] Error en setup: {e}")
        return False

def login():
    """Login a n8n y obtener sesión"""
    session = requests.Session()
    try:
        response = session.post(
            f"{N8N_URL}/api/v1/login",
            json=CREDENTIALS,
            timeout=5
        )
        if response.status_code == 200:
            print("[+] Login exitoso")
            return session
        elif response.status_code == 401:
            print("[!] Login falló, intentando crear owner...")
            setup_owner()
            time.sleep(2)
            response = session.post(
                f"{N8N_URL}/api/v1/login",
                json=CREDENTIALS,
                timeout=5
            )
            if response.status_code == 200:
                print("[+] Login exitoso después de crear owner")
                return session
        print(f"[ERROR] Login falló: {response.status_code}")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def check_workflows(session):
    """Verificar workflows y activarlos si es necesario"""
    try:
        response = session.get(f"{N8N_URL}/api/v1/workflows", timeout=5)
        if response.status_code != 200:
            print(f"[ERROR] No se pudo obtener workflows: {response.status_code}")
            return
        
        workflows = response.json().get('data', [])
        print(f"\n[+] Workflows encontrados: {len(workflows)}")
        
        for wf in workflows:
            name = wf.get('name', 'Unknown')
            active = wf.get('active', False)
            wf_id = wf.get('id')
            
            status = "[ACTIVO]" if active else "[INACTIVO]"
            print(f"   {status} {name} (ID: {wf_id})")
            
            # Activar si está inactivo
            if not active:
                print(f"      -> Activando workflow {wf_id}...")
                activate_response = session.patch(
                    f"{N8N_URL}/api/v1/workflows/{wf_id}",
                    json={"active": True},
                    timeout=5
                )
                if activate_response.status_code == 200:
                    print(f"      -> [OK] Activado!")
                else:
                    print(f"      -> [ERROR] No se pudo activar: {activate_response.status_code}")
        
        print(f"\n[SUCCESS] Verificación completada")
        
    except Exception as e:
        print(f"[ERROR] {e}")

def main():
    print("[*] Verificador de Workflows n8n")
    print("=" * 60)
    
    # Login
    session = login()
    if not session:
        print("[ERROR] No se pudo iniciar sesión en n8n")
        return 1
    
    # Verificar workflows
    check_workflows(session)
    
    return 0

if __name__ == "__main__":
    exit(main())
