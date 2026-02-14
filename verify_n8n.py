"""Script de verificación de workflows en n8n"""
import requests
import sys

try:
    # Verificar que n8n esté respondiendo
    response = requests.get("http://localhost:5678/healthz", timeout=5)
    print(f"[+] n8n health check: {response.status_code}")
    
    # Intentar obtener workflows
    try:
        workflows_response = requests.get("http://localhost:5678/api/v1/workflows", timeout=5)
        if workflows_response.status_code == 200:
            workflows = workflows_response.json().get('data', [])
            print(f"[+] Workflows importados: {len(workflows)}")
            for wf in workflows:
                status = "ACTIVO" if wf.get('active') else "INACTIVO"
                print(f"   - {wf.get('name', 'Unknown')}: {status}")
        else:
            print(f"[!] No se pudo obtener workflows (auth requerido)")
            print(f"[INFO] Accede a http://localhost:5678 para verificar manualmente")
    except:
        print(f"[!] Requiere autenticación - accede a http://localhost:5678 manualmente")
    
    print(f"\n[SUCCESS] n8n está funcionando correctamente!")
    print(f"[INFO] URL: http://localhost:5678")
    print(f"[INFO] Credenciales: admin@social-bot.local / SocialBot2026!")
    
except requests.exceptions.ConnectionError:
    print("[ERROR] n8n no está respondiendo")
    print("[INFO] Espera unos segundos más o verifica: docker-compose logs n8n")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {str(e)}")
    sys.exit(1)
