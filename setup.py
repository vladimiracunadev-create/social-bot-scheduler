import os
import subprocess
import venv
from pathlib import Path


def run_cmd(cmd, cwd=None):
    print(f"Executing: {cmd}")
    try:
        subprocess.check_call(cmd, shell=True, cwd=cwd)
        return True
    except:
        return False


def configure_env(case_id, webhook_suffix):
    webhook = f"http://localhost:5678/webhook/social-bot-scheduler{webhook_suffix}"
    env_content = f"WEBHOOK_URL={webhook}\nLOG_LEVEL=INFO\nPOSTS_FILE=posts.json\n"
    # Escribir en la carpeta del origen del caso
    case_folders = [f for f in os.listdir("cases") if f.startswith(case_id)]
    if case_folders:
        origin_path = Path("cases") / case_folders[0] / "origin"
        (origin_path / ".env").write_text(env_content)
        print(f"✅ .env configurado en {origin_path}")
        return case_folders[0]
    return None


def setup():
    print("=== SOCIAL BOT SCHEDULER: MASTER LAUNCHER ===")

    cases = {
        "1": {"name": "Python -> n8n -> PHP", "suffix": "-php"},
        "2": {"name": "Python -> n8n -> Go", "suffix": "-go"},
        "3": {"name": "Go -> n8n -> Node.js", "suffix": "-node-dest"},
        "4": {"name": "Node.js -> n8n -> FastAPI", "suffix": "-fastapi"},
        "5": {"name": "Laravel -> n8n -> React", "suffix": "-react"},
        "6": {"name": "Go -> n8n -> Symfony", "suffix": "-symfony"},
        "7": {"name": "Rust -> n8n -> Ruby (Sinatra)", "suffix": "-ruby"},
        "8": {"name": "C# (.NET) -> n8n -> Flask", "suffix": "-flask"},
    }

    print("\nSelecciona el Eje Tecnológico a activar:")
    for k, v in cases.items():
        print(f"{k}) {v['name']}")

    choice = input("\nOpción: ").strip()
    if choice not in cases:
        choice = "1"

    case_folder = configure_env(f"0{choice}", cases[choice]["suffix"])

    print("\nInstalando requisitos del emisor...")
    origin_path = Path("cases") / case_folder / "origin"

    # Manejar instalaciones según lenguaje
    if choice in ["1", "2"]:  # Python
        v_dir = origin_path / "venv"
        if not v_dir.exists():
            venv.create(v_dir, with_pip=True)
        pip = v_dir / ("Scripts" if os.name == "nt" else "bin") / "pip"
        run_cmd(f"{pip} install -r requirements.txt", cwd=origin_path)
    elif choice in ["3", "6"]:  # Go
        print("Asegúrate de tener Go instalado para ejecutar el emisor.")
    elif choice == "4":  # Node
        run_cmd("npm install axios", cwd=origin_path)
    elif choice == "5":  # Laravel (PHP)
        print("Asegúrate de tener PHP instalado para ejecutar el comando Artisan.")
    elif choice == "7":  # Rust
        print("Asegúrate de tener Rust (cargo) instalado para ejecutar: cargo run")
    elif choice == "8":  # C#
        print("Asegúrate de tener .NET SDK instalado para ejecutar: dotnet run")

    print("\n" + "=" * 50)
    print("SISTEMA CONFIGURADO EXITOSAMENTE")
    print("=" * 50)
    print(f"\n1. Inicia el puente y el destino:")
    dest_services = [
        "dest-php",
        "dest-go",
        "dest-node",
        "dest-fastapi",
        "dest-react",
        "dest-symfony",
        "dest-ruby",
        "dest-flask",
    ]
    dest_svc = dest_services[int(choice) - 1]
    print(f"   docker-compose up -d n8n {dest_svc}")
    
    workflow_path = Path("cases") / case_folder / "n8n" / "workflow.json"
    print(f"\n2. IMPORTANTE: Configura n8n:")
    print(f"   - Abre http://localhost:5678")
    print(f"   - Configura tu cuenta de propietario (si es la primera vez)")
    print(f"   - Importa el workflow desde: {workflow_path.absolute()}")
    print(f"   - ACTIVA el workflow switch (arriba a la derecha)")

    print(f"\n3. Lanza el emisor ({cases[choice]['name'].split(' -> ')[0]}):")
    print(f"   cd cases/{case_folder}/origin")
    if choice in ["1", "2"]:
        print(f"   ..\\..\\..\\venv\\Scripts\\activate (Windows) o source ../../../venv/bin/activate (Linux/Mac)")
        print(f"   python bot.py")
    elif choice == "4":
        print(f"   node emisor.js (o el archivo principal)")
    else:
        print(f"   Ejecuta el comando correspondiente al lenguaje.")

    print(f"\n4. Dashboard disponible en:")
    print(f"   http://localhost:{8080+int(choice)}")


if __name__ == "__main__":
    setup()
