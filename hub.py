import os
import sys
import argparse
import subprocess
import re
import datetime
import yaml
import json
from pathlib import Path

# ==================================================================================================
# CONFIGURACIÓN DE RUTAS
# ==================================================================================================
# Se utilizan rutas absolutas resueltas para evitar ambigüedades al ejecutar desde diferentes directorios.
# `Path.resolve()` convierte rutas relativas en rutas absolutas del sistema operativo.
CASES_DIR = Path(
    "cases"
).resolve()  # Directorio donde se almacenan los casos de migración/integración
AUDIT_LOG = Path(
    "hub.audit.log"
).resolve()  # Archivo de registro para auditoría de acciones

# ==================================================================================================
# UTILIDADES DEL SISTEMA
# ==================================================================================================


def safe_print(text):
    """
    Imprime texto en la consola manejando posibles errores de codificación en Windows.

    Contexto:
        En entornos Windows heredados (cmd.exe, PowerShell antiguo), la salida estándar puede no
        soportar caracteres Unicode (como tildes o emojis), lanzando `UnicodeEncodeError`.

    Mecanismo:
        Intenta imprimir normalmente. Si falla por codificación, codifica el texto a ASCII
        reemplazando los caracteres problemáticos co '?' (modo "replace") y luego lo decodifica
        para imprimirlo sin causar un crash.

    Args:
        text (str): El texto que se desea imprimir.
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback para consolas que no soportan UTF-8 completo
        print(text.encode("ascii", "replace").decode("ascii"))


def log_audit(comando, estado, detalles=""):
    """
    Registra una acción operativa en el archivo de log de auditoría.

    Contexto:
        Es crucial mantener un rastro de auditoría (audit trail) de quién ejecutó qué comando,
        cuándo y cuál fue el resultado, para propósitos de seguridad y depuración.

    Mecanismo:
        1. Obtiene el timestamp actual y el usuario del sistema operativo.
        2. Formatea una entrada de log estructurada.
        3. Añade (append) la entrada al archivo `hub.audit.log`.

    Args:
        comando (str): El nombre del comando ejecutado (ej: "ejecutar 01-python-to-php").
        estado (str): El resultado de la operación ("EXITO" o "FALLO").
        detalles (str, optional): Información adicional sobre el error o el resultado. Defaults to "".
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # `os.getlogin()` puede fallar en ciertos entornos no interactivos (ej: CI/CD, cron),
    # por lo que se comprueba su existencia.
    usuario = os.getlogin() if hasattr(os, "getlogin") else "desconocido"
    entrada = (
        f"[{timestamp}] USUARIO:{usuario} CMD:{comando} ESTADO:{estado} {detalles}\n"
    )
    # Se utiliza codificación utf-8 explícita para evitar problemas al leer el log en otros sistemas
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(entrada)


def obtener_manifiesto(ruta_caso):
    """
    Carga y parsea el archivo de configuración `app.manifest.yml` de un directorio de caso dado.

    Contexto:
        Cada "caso" es una aplicación autocontenida descrita por un manifiesto YAML. Este manifiesto
        contiene metadatos vitales como el nombre, lenguaje, stack tecnológico y puntos de entrada.

    Args:
        ruta_caso (Path): Objeto Path apuntando al directorio raíz del caso.

    Returns:
        dict | None: Diccionario con los datos del manifiesto si la carga es exitosa,
                     o None si el archivo no existe o es inválido.
    """
    ruta_manifiesto = ruta_caso / "app.manifest.yml"
    if not ruta_manifiesto.exists():
        return None
    try:
        with open(ruta_manifiesto, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        safe_print(f"Error cargando manifiesto en {ruta_caso}: {e}")
        return None


# ==================================================================================================
# COMANDOS CLI
# ==================================================================================================


def listar_casos():
    """
    Enumera y muestra en consola todos los casos registrados en el directorio `cases/`.

    Mecanismo:
        1. Valida la existencia del directorio `cases/`.
        2. Itera sobre cada subdirectorio.
        3. Intenta cargar el `app.manifest.yml` de cada uno.
        4. Si el manifiesto es válido, imprime la información formateada (ID, nombre, tecnologías).
    """
    if not CASES_DIR.exists():
        safe_print(f"Error: Directorio de casos {CASES_DIR} no encontrado.")
        log_audit("listar-casos", "FALLO", "Directorio no encontrado")
        return

    safe_print("Casos Disponibles (Matriz de Integración):")
    encontrados = 0
    # Se ordena la lista para mantener una salida determinista y ordenada alfabéticamente
    for d in sorted(CASES_DIR.iterdir()):
        if d.is_dir():
            manifiesto = obtener_manifiesto(d)
            if manifiesto:
                encontrados += 1
                safe_print(
                    f" - [{manifiesto.get('id', '??')}] {manifiesto.get('name', d.name)}"
                )
                safe_print(f"   Tech: {', '.join(manifiesto.get('stack', []))}")

    if encontrados == 0:
        safe_print("No se encontraron casos con app.manifest.yml válido.")

    log_audit("listar-casos", "EXITO", f"Casos encontrados: {encontrados}")


def ejecutar_caso(nombre_caso, dry_run=True):
    """
    Orquesta la ejecución de un caso de integración específico.

    Contexto:
        El objetivo principal del Hub es ejecutar bots/workers en diferentes lenguajes de forma unificada.
        Esta función actúa como un despachador políglota, preparando el entorno y lanzando el proceso adecuado.

    Mecanismo:
        1. **Validación de Seguridad**: Verifica que el nombre del caso sea seguro y previene ataques de
           Path Traversal (intentar salir del directorio `cases/`).
        2. **Carga de Configuración**: Lee el manifiesto para saber qué ejecutar.
        3. **Resolución del Runtime**: Determina si usar `python`, `node`, `go`, etc., basándose en el manifiesto.
        4. **Inyección de Entorno**: Prepara variables de entorno (como `DRY_RUN`) para controlar el comportamiento del bot.
        5. **Ejecución**: Lanza el subproceso y espera su terminación.

    Args:
        nombre_caso (str): Nombre del directorio del caso a ejecutar (ej: "01-python-to-php").
        dry_run (bool): Si es True (por defecto), indica al bot que NO realice acciones persistentes (ej: postear en redes).
    """
    # Validación de Seguridad: Whitelist de caracteres permitidos para evitar inyección de comandos
    if not re.match(r"^[a-zA-Z0-9_\-]+$", nombre_caso):
        safe_print(f"Error: Nombre de caso '{nombre_caso}' no válido.")
        log_audit(f"ejecutar {nombre_caso}", "FALLO", "Formato inválido")
        return

    ruta_caso = (CASES_DIR / nombre_caso).resolve()

    # Validación de Seguridad: Prevent Path Traversal
    # Asegura que la ruta resuelta siga estando dentro de CASES_DIR
    if not str(ruta_caso).startswith(str(CASES_DIR)):
        safe_print("Error: Intento de acceso no autorizado detectado.")
        log_audit(f"ejecutar {nombre_caso}", "FALLO", "Path traversal detectado")
        return

    manifiesto = obtener_manifiesto(ruta_caso)
    if not manifiesto:
        safe_print(
            f"Error: El caso '{nombre_caso}' no tiene un app.manifest.yml válido."
        )
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

        # Despachador de Runtimes: Construye el comando según el lenguaje
        if lenguaje == "python":
            cmd = [sys.executable, entrypoint.name]
        elif lenguaje == "nodejs":
            cmd = ["node", entrypoint.name]
        elif lenguaje == "go":
            cmd = ["go", "run", entrypoint.name]
        else:
            safe_print(f"Error: Lenguaje '{lenguaje}' no soportado automáticamente.")
            log_audit(
                f"ejecutar {nombre_caso}", "FALLO", f"Lenguaje no soportado: {lenguaje}"
            )
            return

        # Preparación del entorno de simulación
        env = os.environ.copy()
        if dry_run:
            env["DRY_RUN"] = "True"
            env["NO_PUBLIC_POSTING"] = "True"

        safe_print(f"Ejecutando: {' '.join(cmd)}")
        try:
            # `cwd=entrypoint.parent` es crítico: el bot se ejecuta "dentro" de su propia carpeta
            # para que pueda encontrar sus propios archivos locales (configs, assets, etc.)
            subprocess.run(cmd, cwd=entrypoint.parent, env=env, check=True)
            log_audit(f"ejecutar {nombre_caso}", "EXITO", f"Simulación: {dry_run}")
        except subprocess.CalledProcessError as e:
            safe_print(f"Error ejecutando el bot: {e}")
            log_audit(f"ejecutar {nombre_caso}", "FALLO", f"Error de proceso: {e}")
    else:
        safe_print(f"Error: No se encontró el punto de entrada '{entrypoint}'.")
        log_audit(f"ejecutar {nombre_caso}", "FALLO", "Punto de entrada no encontrado")


def ejecutar_doctor():
    """
    Realiza un diagnóstico de salud (Health Check) del entorno de ejecución.

    Contexto:
        Ayuda a los usuarios a depurar problemas comunes de configuración verificando
        que las dependencias externas (Docker) y la estructura interna (manifiestos) estén correctas.
    """
    safe_print("=== HUB DOCTOR: Informe de Diagnóstico ===")

    # 1. Verificar Docker
    try:
        docker_check = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True
        )
        if docker_check.returncode == 0:
            safe_print(f"[OK] Docker: {docker_check.stdout.strip()}")
        else:
            safe_print("[ERROR] Docker: Instalado pero no responde (¿Daemon apagado?).")
    except FileNotFoundError:
        safe_print("[ERROR] Docker: No encontrado en el PATH.")

    # 2. Verificar Docker Compose
    try:
        dc_check = subprocess.run(
            ["docker-compose", "--version"], capture_output=True, text=True
        )
        if dc_check.returncode == 0:
            safe_print(f"[OK] Docker Compose: {dc_check.stdout.strip()}")
        else:
            safe_print("[ERROR] Docker Compose: El comando falló.")
    except FileNotFoundError:
        safe_print("[ERROR] Docker Compose: No encontrado en el PATH.")

    # 3. Integridad de Manifiestos
    encontrados = 0
    validos = 0
    if CASES_DIR.exists():
        for d in CASES_DIR.iterdir():
            if d.is_dir():
                encontrados += 1
                if (d / "app.manifest.yml").exists():
                    validos += 1

        if encontrados > 0:
            safe_print(
                f"[OK] Casos: {validos}/{encontrados} tienen manifiesto YAML válido."
            )
        else:
            safe_print("[AVISO] No se encontraron subdirectorios en 'cases/'.")
    else:
        safe_print("[ERROR] Directorio 'cases/' no encontrado.")

    # 4. Log de Auditoría
    if AUDIT_LOG.exists():
        safe_print(f"[OK] Log de Auditoría: Activo ({AUDIT_LOG.stat().st_size} bytes)")
    else:
        safe_print(
            "[AVISO] Log de Auditoría: Aún no creado (se creará con la primera acción)."
        )

    # 5. Host Resources
    safe_print("\n--- Recursos del Sistema ---")
    try:
        subprocess.run([sys.executable, "check_resources.py"], check=True)
        if os.path.exists("resources.json"):
            with open("resources.json", "r") as f:
                res = json.load(f)
                safe_print(f"CPU: {res['cpu_cores']} cores")
                safe_print(f"RAM: {res['ram']['free_gb']}GB libres de {res['ram']['total_gb']}GB")
                safe_print(f"Disk: {res['disk']['free_gb']}GB libres")
                safe_print(f"Estado de Lanzamiento: {res['status']}")
    except:
        safe_print("[AVISO] No se pudo verificar recursos del sistema.")

    log_audit("doctor", "EXITO")


def limpiar_todo():
    """
    Realiza una limpieza profunda del entorno Docker para garantizar el uso óptimo.
    """
    safe_print("🧹 Iniciando limpieza profunda del entorno Docker...")
    try:
        # 1. Detener y eliminar contenedores, redes y volúmenes
        subprocess.run(["docker-compose", "down", "-v", "--rmi", "all"], check=True)
        # 2. Prune total (imágenes huérfanas, caches, etc.)
        subprocess.run(["docker", "system", "prune", "-f"], check=True)
        safe_print("✅ Limpieza completada exitosamente.")
        log_audit("limpiar-todo", "EXITO")
    except subprocess.CalledProcessError as e:
        safe_print(f"❌ Error durante la limpieza: {e}")
        log_audit("limpiar-todo", "FALLO", str(e))


def gestionar_stack(accion):
    """
    Wrapper para controlar `docker-compose` desde el Hub.

    Args:
        accion (str): "up" para levantar servicios, "down" para detenerlos.
    """
    if accion == "up":
        # Ejecutar verificación de recursos antes de subir
        safe_print("🔍 Verificando recursos antes de subir el stack...")
        try:
            subprocess.run([sys.executable, "check_resources.py"], check=True)
        except:
            pass

    cmd = ["docker-compose", accion]
    if accion == "up":
        cmd.append("-d")

    safe_print(f"Ejecutando infraestructura: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        log_audit(f"stack {accion}", "EXITO")
    except subprocess.CalledProcessError as e:
        safe_print(f"Error gestionando el stack: {e}")
        log_audit(f"stack {accion}", "FALLO", str(e))


def main():
    """
    Punto de entrada principal del CLI.
    Configura el parser de argumentos y despacha el comando correspondiente.
    """
    parser = argparse.ArgumentParser(description="HUB CLI para Social Bot Scheduler")
    subparsers = parser.add_subparsers(dest="command")

    # Comando: listar-casos
    subparsers.add_parser(
        "listar-casos", help="Enumera los casos de la matriz de integración disponibles"
    )

    # Comando: ejecutar
    run_parser = subparsers.add_parser(
        "ejecutar", help="Lanza un caso de integración específico"
    )
    run_parser.add_argument(
        "caso", help="Nombre de la carpeta del caso a ejecutar (ej: 01-python-to-php)"
    )
    run_parser.add_argument(
        "--real",
        action="store_false",
        dest="dry_run",
        help="Ejecuta en modo real (permitiendo efectos secundarios como posts reales). Por defecto es simulación.",
    )
    # Por seguridad, el valor por defecto es dry_run=True (Simulación activada)
    run_parser.set_defaults(dry_run=True)

    # Comando: doctor
    subparsers.add_parser(
        "doctor", help="Ejecuta diagnósticos del sistema y verifica dependencias"
    )

    # Comandos: Infraestructura (up / down)
    subparsers.add_parser(
        "up", help="Levanta la infraestructura Docker (docker-compose up)"
    )
    subparsers.add_parser(
        "down", help="Detiene y mantiene los contenedores (docker-compose down)"
    )
    subparsers.add_parser(
        "clean", help="Limpieza total: elimina contenedores, volúmenes e imágenes (PRUNE)"
    )

    args = parser.parse_args()

    # Despacho de comandos
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
    elif args.command == "clean":
        limpiar_todo()
    else:
        # Si no se pasa comando, mostrar ayuda
        parser.print_help()


if __name__ == "__main__":
    # Configuración específica para Windows:
    # Fuerza la página de códigos de la consola a UTF-8 (CP 65001) para soportar emojis y tildes correctamente.
    if os.name == "nt":
        import ctypes

        try:
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except Exception:
            pass  # Ignoramos errores si no se puede establecer (ej: entornos restringidos)

    main()
