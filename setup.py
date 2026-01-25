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

def setup():
    print("=== Social Bot Scheduler - Instalación Infalible ===")
    
    # 0. Verificar Docker (Recomendado para instalación universal)
    print("\n[INFO] Verificando requisitos de sistema...")
    has_docker = run_command("docker --version")
    has_compose = run_command("docker-compose --version") or run_command("docker compose version")
    
    if not has_docker:
        print("WARN: Docker no detectado. Requerido para el stack completo (n8n/PHP).")
    if not has_compose:
        print("WARN: Docker Compose no detectado. Requerido para levantar el sistema.")
    
    if has_docker and has_compose:
        print("OK: Docker y Compose detectados. ¡Podrás usar la instalación universal!")

    # 1. Crear Entorno Virtual
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print("Creando entorno virtual...")
        venv.create(venv_dir, with_pip=True)
    
    # Determinar el ejecutable de python en venv
    if os.name == "nt":  # Windows
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:  # Unix
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"

    # 2. Instalar dependencias
    print("Instalando dependencias...")
    if not run_command(f"{pip_exe} install -r requirements.txt"):
        print("Fallo en la instalación de dependencias.")
        return

    # 3. Configurar .env
    env_file = Path(".env")
    if not env_file.exists():
        print("Creando archivo .env desde .env.example...")
        example = Path(".env.example")
        if example.exists():
            content = example.read_text()
            env_file.write_text(content)
        else:
            env_file.write_text("WEBHOOK_URL=http://localhost:5678/webhook-test\nLOG_LEVEL=INFO")
    
    # 4. Configurar posts.json inicial
    posts_file = Path("posts.json")
    if not posts_file.exists():
        print("Creando posts.json inicial...")
        initial_posts = """[
  {
    "id": "welcome",
    "text": "¡Instalación exitosa! El bot está listo.",
    "channels": ["system"],
    "scheduled_at": "2020-01-01T00:00:00",
    "published": false
  }
]"""
        posts_file.write_text(initial_posts, encoding="utf-8")

    # 5. Ejecutar Pruebas de Calidad
    print("Verificando instalación con tests...")
    if not run_command(f"{python_exe} -m pytest"):
        print("Atención: Los tests fallaron. Revisa el entorno.")
    else:
        print("\n" + "="*50)
        print("INSTALACION COMPLETADA EXITOSAMENTE!")
        print("="*50)
        print(f"\n1. Activa tu entorno virtual:")
        print(f"   - Windows: venv\\Scripts\\activate")
        print(f"   - Unix:    source venv/bin/activate")
        print(f"\n2. Levanta el stack completo (Universal):")
        print(f"   - Ejecuta: docker-compose up -d")
        print(f"\n3. Una vez arriba, puedes ver los logs:")
        print(f"   - Ejecuta: make logs")
        print("\n¡Todo listo para automatizar tus redes sociales!")

if __name__ == "__main__":
    setup()
