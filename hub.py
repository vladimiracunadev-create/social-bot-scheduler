import os
import sys
import argparse
import subprocess
import re
import datetime
import yaml
from pathlib import Path

# Configuración de Rutas
CASES_DIR = Path("cases").resolve()
AUDIT_LOG = Path("hub.audit.log").resolve()

def safe_print(text):
    """Imprime texto manejando errores de codificación en Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def log_audit(comando, estado, detalles=""):
    """Registra una acción en el log de auditoría."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usuario = os.getlogin() if hasattr(os, 'getlogin') else "desconocido"
    entrada = f"[{timestamp}] USUARIO:{usuario} CMD:{comando} ESTADO:{estado} {detalles}\n"
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(entrada)

def obtener_manifiesto(ruta_caso):
    """Carga el manifiesto app.manifest.yml de un caso."""
    ruta_manifiesto = ruta_caso / "app.manifest.yml"
    if not ruta_manifiesto.exists():
        return None
    try:
        with open(ruta_manifiesto, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        safe_print(f"Error cargando manifiesto en {ruta_caso}: {e}")
        return None

def listar_casos():
    """Enumera todos los casos disponibles basados en sus manifiestos."""
    if not CASES_DIR.exists():
        safe_print(f"Error: Directorio de casos {CASES_DIR} no encontrado.")
        log_audit("listar-casos", "FALLO", "Directorio no encontrado")
        return

    safe_print("Casos Disponibles (Matriz de Integración):")
    encontrados = 0
    for d in sorted(CASES_DIR.iterdir()):
        if d.is_dir():
            manifiesto = obtener_manifiesto(d)
            if manifiesto:
                encontrados += 1
                safe_print(f" - [{manifiesto.get('id', '??')}] {manifiesto.get('name', d.name)}")
                safe_print(f"   Tech: {', '.join(manifiesto.get('stack', []))}")
    
    if encontrados == 0:
        safe_print("No se encontraron casos con app.manifest.yml válido.")
    
    log_audit("listar-casos", "EXITO", f"Casos encontrados: {encontrados}")

def ejecutar_caso(nombre_caso, dry_run=True):
    """Lanza la ejecución de un caso específico."""
    # Validación de Seguridad: Formato de nombre
    if not re.match(r"^[a-zA-Z0-9_\-]+$", nombre_caso):
        safe_print(f"Error: Nombre de caso '{nombre_caso}' no válido.")
        log_audit(f"ejecutar {nombre_caso}", "FALLO", "Formato inválido")
        return

    ruta_caso = (CASES_DIR / nombre_caso).resolve()
    
    # Validación de Seguridad: Prevent Path Traversal
    if not str(ruta_caso).startswith(str(CASES_DIR)):
        safe_print("Error: Intento de acceso no autorizado detectado.")
        log_audit(f"ejecutar {nombre_caso}", "FALLO", "Path traversal detectado")
        return

    manifiesto = obtener_manifiesto(ruta_caso)
    if not manifiesto:
        safe_print(f"Error: El caso '{nombre_caso}' no tiene un app.manifest.yml válido.")
        log_audit(f"ejecutar {nombre_caso}", "FALLO", "Sin manifiesto")
        return

    safe_print(f"Ejecutando caso: {manifiesto.get('name')}")
    if dry_run:
        safe_print("[MODO SIMULACIÓN] No se realizarán publicaciones reales.")

    origin_info = manifiesto.get("origin", {})
    entrypoint = ruta_caso / origin_info.get("entrypoint", "bot.py")
    
    if entrypoint.exists():
        lenguaje = origin_info.get("language", "python").lower()
        cmd = []
        
        if lenguaje == "python":
            cmd = [sys.executable, entrypoint.name]
        elif lenguaje == "nodejs":
            cmd = ["node", entrypoint.name]
        elif lenguaje == "go":
            cmd = ["go", "run", entrypoint.name]
        else:
            safe_print(f"Error: Lenguaje '{lenguaje}' no soportado automáticamente.")
            log_audit(f"ejecutar {nombre_caso}", "FALLO", f"Lenguaje no soportado: {lenguaje}")
            return

        env = os.environ.copy()
        if dry_run:
            env["DRY_RUN"] = "True"
            env["NO_PUBLIC_POSTING"] = "True"

        safe_print(f"Ejecutando: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, cwd=entrypoint.parent, env=env, check=True)
            log_audit(f"ejecutar {nombre_caso}", "EXITO", f"Simulación: {dry_run}")
        except subprocess.CalledProcessError as e:
            safe_print(f"Error ejecutando el bot: {e}")
            log_audit(f"ejecutar {nombre_caso}", "FALLO", f"Error de proceso: {e}")
    else:
        safe_print(f"Error: No se encontró el punto de entrada '{entrypoint}'.")
        log_audit(f"ejecutar {nombre_caso}", "FALLO", "Punto de entrada no encontrado")

def ejecutar_doctor():
    """Realiza un diagnóstico del sistema de orquestación."""
    safe_print("=== HUB DOCTOR: Informe de Diagnóstico ===")
    
    # 1. Verificar Docker
    try:
        docker_check = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if docker_check.returncode == 0:
            safe_print(f"[OK] Docker: {docker_check.stdout.strip()}")
        else:
            safe_print("[ERROR] Docker: Instalado pero no responde.")
    except FileNotFoundError:
        safe_print("[ERROR] Docker: No encontrado en el PATH.")

    # 2. Verificar Docker Compose
    try:
        dc_check = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
        if dc_check.returncode == 0:
            safe_print(f"[OK] Docker Compose: {dc_check.stdout.strip()}")
        else:
            safe_print("[ERROR] Docker Compose: No responde.")
    except FileNotFoundError:
        safe_print("[ERROR] Docker Compose: No encontrado.")

    # 3. Integridad de Manifiestos
    encontrados = 0
    validos = 0
    for d in CASES_DIR.iterdir():
        if d.is_dir():
            encontrados += 1
            if (d / "app.manifest.yml").exists():
                validos += 1
    
    if encontrados > 0:
        safe_print(f"[OK] Casos: {validos}/{encontrados} tienen manifiesto YAML.")
    else:
        safe_print("[ERROR] Directorio 'cases/' vacío o no encontrado.")

    # 4. Log de Auditoría
    if AUDIT_LOG.exists():
        safe_print(f"[OK] Log de Auditoría: Activo ({AUDIT_LOG.stat().st_size} bytes)")
    else:
        safe_print("[AVISO] Log de Auditoría: Aún no creado.")

    log_audit("doctor", "EXITO")

def gestionar_stack(accion):
    """Inicia o detiene los servicios definidos en docker-compose."""
    cmd = ["docker-compose", accion]
    safe_print(f"Ejecutando: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        log_audit(f"stack {accion}", "EXITO")
    except subprocess.CalledProcessError as e:
        safe_print(f"Error gestionando el stack: {e}")
        log_audit(f"stack {accion}", "FALLO", str(e))

def main():
    parser = argparse.ArgumentParser(description="HUB CLI para Social Bot Scheduler")
    subparsers = parser.add_subparsers(dest="command")

    # listar-casos
    subparsers.add_parser("listar-casos", help="Enumera los casos de la matriz")

    # ejecutar
    run_parser = subparsers.add_parser("ejecutar", help="Lanza un caso de integración")
    run_parser.add_argument("caso", help="Nombre de la carpeta del caso (ej: 01-python-to-php)")
    run_parser.add_argument("--real", action="store_false", dest="dry_run", help="Desactivar modo simulación")
    run_parser.set_defaults(dry_run=True)

    # doctor
    subparsers.add_parser("doctor", help="Ejecuta diagnósticos del sistema")

    # up / down
    subparsers.add_parser("up", help="Levanta la infraestructura Docker")
    subparsers.add_parser("down", help="Detiene la infraestructura Docker")

    args = parser.parse_args()

    if args.command == "listar-casos":
        listar_casos()
    elif args.command == "ejecutar":
        ejecutar_caso(args.caso, args.dry_run)
    elif args.command == "doctor":
        ejecutar_doctor()
    elif args.command == "up":
        gestionar_stack("up")
    elif args.command == "down":
        gestionar_stack("down")
    else:
        parser.print_help()

if __name__ == "__main__":
    # Asegurar soporte para caracteres en consola Windows
    if os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    
    main()
