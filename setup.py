import os
import subprocess
import sys
import venv
from pathlib import Path


def run_command(command, cwd=None):
    """Ejecuta un comando y muestra la salida en tiempo real."""
    print(f"Executing: {command}")
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar: {command}\n{e}")
        return False


def setup_case(case_num):
    print(f"\n--- Configurando Caso 0{case_num} ---")
    env_file = Path(".env")
    if case_num == "1":
        webhook = "http://n8n:5678/webhook/social-bot-scheduler"
        case_name = "Python + n8n + PHP"
    else:
        webhook = "http://n8n:5678/webhook/social-bot-scheduler-go"
        case_name = "Python + n8n + Go"

    env_content = f"# Configuración para {case_name}\nWEBHOOK_URL={webhook}\nLOG_LEVEL=INFO\nPOSTS_FILE=posts.json\n"
    env_file.write_text(env_content)
    print(f"✅ Archivo .env configurado para {case_name}")


def setup():
    print("=== Social Bot Scheduler - Selector de Casos ===")

    # 0. Verificar Docker
    print("\n[INFO] Verificando requisitos de sistema...")
    run_command("docker --version")

    # 1. Menú de Selección
    print("\nSelecciona el caso tecnológico que deseas activar:")
    print("1) Caso 01: Python + n8n + PHP (Receptor Web Clásico)")
    print("2) Caso 02: Python + n8n + Go  (Receptor de Alto Rendimiento)")

    choice = input("\nElige una opción (1 o 2): ").strip()
    if choice not in ["1", "2"]:
        print("Opción inválida. Usando Caso 01 por defecto.")
        choice = "1"

    setup_case(choice)

    # 2. Crear Entorno Virtual e instalar
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print("Creando entorno virtual...")
        venv.create(venv_dir, with_pip=True)

    pip_exe = (
        venv_dir / "Scripts" / "pip.exe"
        if os.name == "nt"
        else venv_dir / "bin" / "pip"
    )
    run_command(f"{pip_exe} install -r requirements.txt")

    print("\n" + "=" * 50)
    print("INSTALACION COMPLETADA EXITOSAMENTE!")
    print("=" * 50)
    print(f"\n1. Levanta el stack del Caso {choice}:")
    if choice == "1":
        print("   Ejecuta: docker-compose up -d n8n api-php")
    else:
        print("   Ejecuta: docker-compose up -d n8n api-go")
    print(f"\n2. Activa tu venv y lanza el bot:")
    print("   venv\\Scripts\\activate (Windows) o source venv/bin/activate (Unix)")
    print("   python bot.py")
    print("\n¡Todo listo para automatizar tus redes sociales!")


if __name__ == "__main__":
    setup()
