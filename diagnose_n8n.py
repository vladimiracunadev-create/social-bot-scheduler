"""Verificador avanzado de n8n que muestra el estado completo"""

import requests
import json

N8N_URL = "http://localhost:5678"


def check_health():
    try:
        r = requests.get(f"{N8N_URL}/healthz", timeout=3)
        print(f"[+] Health: {r.status_code}")
        return r.status_code == 200
    except:
        print("[!] n8n no está respondiendo")
        return False


def check_setup():
    """Verificar si n8n necesita setup inicial"""
    try:
        r = requests.get(f"{N8N_URL}/api/v1/owner", timeout=3)
        if r.status_code == 200:
            print("[+] Owner configurado")
            return True
        elif r.status_code == 404:
            print("[!] n8n necesita setup de owner")
            return False
    except:
        return None


def do_setup():
    """Configurar owner via API"""
    try:
        r = requests.post(
            f"{N8N_URL}/api/v1/owner/setup",
            json={
                "email": "admin@social-bot.local",
                "firstName": "Admin",
                "lastName": "SocialBot",
                "password": "SocialBot2026!",
            },
            timeout=5,
        )
        if r.status_code in [200, 201]:
            print("[+] Owner creado via API")
            return True
        else:
            print(f"[!] Setup failed: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False


def main():
    print("=" * 60)
    print("[*] Diagnostico de n8n")
    print("=" * 60)

    if not check_health():
        return

    setup_status = check_setup()
    if setup_status is False:
        print("[*] Configurando owner...")
        do_setup()

    print("\n[INFO] Accede a http://localhost:5678 manualmente")
    print("[INFO] Credenciales: admin@social-bot.local / SocialBot2026!")


if __name__ == "__main__":
    main()
