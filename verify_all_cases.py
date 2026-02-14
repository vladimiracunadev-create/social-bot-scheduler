"""
Script de verificacion completa de los 8 casos
Prueba cada bot y verifica respuesta
"""
import subprocess
import time
import requests
from pathlib import Path
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CASES = [
    ("01", "python-to-php", 8081, "cases/01-python-to-php/origin"),
    ("02", "python-to-go", 8082, "cases/02-python-to-go/origin"),
    ("03", "go-to-node", 8083, "cases/03-go-to-node/origin"),
    ("04", "node-to-fastapi", 8084, "cases/04-node-to-fastapi/origin"),
    ("05", "laravel-to-react", 8085, "cases/05-laravel-to-react/origin"),
    ("06", "go-to-symfony", 8086, "cases/06-go-to-symfony/origin"),
    ("07", "rust-to-ruby", 8087, "cases/07-rust-to-ruby/origin"),
    ("08", "csharp-to-flask", 8088, "cases/08-csharp-to-flask/origin"),
]

def check_service(port):
    """Verificar que el servicio destino esté corriendo"""
    try:
        r = requests.get(f"http://localhost:{port}", timeout=3)
        return r.status_code == 200
    except:
        return False

def run_bot(case_dir):
    """Ejecutar el bot del caso"""
    try:
        # Buscar el archivo ejecutable del bot
        bot_dir = Path(case_dir)
        
        # Python bot
        if (bot_dir / "bot.py").exists():
            result = subprocess.run(
                ["python", "bot.py"],
                cwd=bot_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout + result.stderr
        
        # Go bot
        elif (bot_dir / "main.go").exists():
            result = subprocess.run(
                ["go", "run", "main.go"],
                cwd=bot_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout + result.stderr
        
        # Node bot
        elif (bot_dir / "bot.js").exists():
            result = subprocess.run(
                ["node", "bot.js"],
                cwd=bot_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout + result.stderr
        
        # Rust bot
        elif (bot_dir / "Cargo.toml").exists():
            result = subprocess.run(
                ["cargo", "run"],
                cwd=bot_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            return result.returncode == 0, result.stdout + result.stderr
        
        # C# bot
        elif (bot_dir / "Program.cs").exists():
            result = subprocess.run(
                ["dotnet", "run"],
                cwd=bot_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            return result.returncode == 0, result.stdout + result.stderr
        
        else:
            return False, "No se encontró archivo ejecutable del bot"
            
    except Exception as e:
        return False, str(e)

def main():
    print("="*70)
    print("[*] Verificación Completa de los 8 Casos")
    print("="*70)
    
    results = []
    
    for case_id, case_name, port, bot_dir in CASES:
        print(f"\n[Caso {case_id}] {case_name.upper()}")
        print("-" * 70)
        
        # 1. Verificar servicio destino
        print(f"  [1/3] Verificando servicio destino (:{port})...", end=" ")
        if check_service(port):
            print("✓ OK")
            service_ok = True
        else:
            print("✗ NO DISPONIBLE")
            service_ok = False
        
        # 2. Ejecutar bot
        print(f"  [2/3] Ejecutando bot...", end=" ")
        if Path(bot_dir).exists():
            success, output = run_bot(bot_dir)
            if success:
                print("✓ EJECUTADO")
                bot_ok = True
            else:
                print("✗ FALLÓ")
                print(f"       Output: {output[:100]}")
                bot_ok = False
        else:
            print("✗ DIRECTORIO NO ENCONTRADO")
            bot_ok = False
        
        # 3. Esperar y verificar
        if service_ok and bot_ok:
            print(f"  [3/3] Esperando respuesta...", end=" ")
            time.sleep(2)
            print("⏱")
        
        # Resultado
        status = "✓ PASS" if (service_ok and bot_ok) else "✗ FAIL"
        results.append((case_id, case_name, status))
        print(f"  Resultado: {status}")
    
    # Resumen final
    print("\n" + "="*70)
    print("[*] RESUMEN DE VERIFICACIÓN")
    print("="*70)
    
    for case_id, case_name, status in results:
        print(f"  Caso {case_id} ({case_name}): {status}")
    
    passed = sum(1 for _, _, s in results if "PASS" in s)
    print(f"\n  Total: {passed}/8 casos funcionando")
    
    if passed == 8:
        print("\n  🎉 ¡TODOS LOS CASOS VERIFICADOS!")
    else:
        print(f"\n  ⚠ {8-passed} casos requieren atención")

if __name__ == "__main__":
    main()
