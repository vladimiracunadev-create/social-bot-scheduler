import os
import sys
import argparse
import subprocess
import re
import datetime
from pathlib import Path

CASES_DIR = Path("cases").resolve()
AUDIT_LOG = Path("hub.audit.log").resolve()

def log_audit(command, status, details=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = os.getlogin() if hasattr(os, 'getlogin') else "unknown"
    log_entry = f"[{timestamp}] USER:{user} CMD:{command} STATUS:{status} {details}\n"
    with open(AUDIT_LOG, "a") as f:
        f.write(log_entry)

def get_allowlist():
    if not CASES_DIR.exists():
        return []
    return sorted([d.name for d in CASES_DIR.iterdir() if d.is_dir()])

def list_cases():
    cases = get_allowlist()
    if not cases:
        print(f"Error: No cases found in {CASES_DIR}.")
        log_audit("list-cases", "FAILED", "No cases directory")
        return

    print("Available Cases (Allowlist):")
    for case in cases:
        print(f" - {case}")
    log_audit("list-cases", "SUCCESS")

def run_case(case_name, dry_run=True):
    # Security Check: Validate case_name format
    if not re.match(r"^[a-zA-Z0-9_\-]+$", case_name):
        print(f"Error: Invalid case name '{case_name}'.")
        log_audit(f"run {case_name}", "FAILED", "Invalid format")
        return

    # Security Check: Allowlist validation
    allowlist = get_allowlist()
    if case_name not in allowlist:
        print(f"Error: Case '{case_name}' is not in the allowlist.")
        log_audit(f"run {case_name}", "FAILED", "Not in allowlist")
        return

    # Security Check: Prevent Path Traversal
    try:
        case_path = (CASES_DIR / case_name).resolve()
        if not str(case_path).startswith(str(CASES_DIR)):
            print(f"Error: Potential path traversal detected.")
            log_audit(f"run {case_name}", "FAILED", "Path traversal attempt")
            return
    except (ValueError, RuntimeError) as e:
        print(f"Error resolving path: {e}")
        log_audit(f"run {case_name}", "FAILED", str(e))
        return

    print(f"Running case: {case_name}")
    if dry_run:
        print("[DRY-RUN MODE] Execution simulated.")
    
    origin_path = case_path / "origin"
    bot_script = origin_path / "bot.py"
    
    if bot_script.exists():
        cmd = [sys.executable, "bot.py"]
        env = os.environ.copy()
        if dry_run:
            env["DRY_RUN"] = "True"
            env["NO_PUBLIC_POSTING"] = "True"
        
        print(f"Executing: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, cwd=origin_path, env=env, check=True)
            log_audit(f"run {case_name}", "SUCCESS", f"Dry-run: {dry_run}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing case: {e}")
            log_audit(f"run {case_name}", "FAILED", f"Execution error: {e}")
    else:
        # Fallback for other languages if index.js exists
        if (origin_path / "index.js").exists():
             cmd = ["node", "index.js"]
             print(f"Executing: {' '.join(cmd)}")
             try:
                 subprocess.run(cmd, cwd=origin_path, check=True)
                 log_audit(f"run {case_name}", "SUCCESS", "Node execution")
             except subprocess.CalledProcessError as e:
                 print(f"Error: {e}")
                 log_audit(f"run {case_name}", "FAILED", f"Node error: {e}")
        else:
            print(f"Warning: No valid entry point found in {origin_path}.")
            log_audit(f"run {case_name}", "FAILED", "No entry point")

def run_doctor():
    print("=== HUB DOCTOR: Diagnostic Report ===")
    
    # 1. Check Docker
    docker_check = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    if docker_check.returncode == 0:
        print(f"[OK] Docker: {docker_check.stdout.strip()}")
    else:
        print("[ERROR] Docker: Not found or not running.")

    # 2. Check Docker Compose
    dc_check = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
    if dc_check.returncode == 0:
        print(f"[OK] Docker Compose: {dc_check.stdout.strip()}")
    else:
        print("[ERROR] Docker Compose: Not found.")

    # 3. Check Cases Integrity
    cases = get_allowlist()
    if cases:
        print(f"[OK] Cases Directory: Found {len(cases)} cases.")
    else:
        print("[ERROR] Cases Directory: Empty or not found.")

    # 4. Check Audit Log
    if AUDIT_LOG.exists():
        print(f"[OK] Audit Log: Active ({AUDIT_LOG.stat().st_size} bytes)")
    else:
        print("[WARN] Audit Log: Not yet created.")

    log_audit("doctor", "SUCCESS")

def manage_stack(action):
    cmd = ["docker-compose", action]
    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        log_audit(f"stack {action}", "SUCCESS")
    except subprocess.CalledProcessError as e:
        print(f"Error managing stack: {e}")
        log_audit(f"stack {action}", "FAILED", str(e))

def main():
    parser = argparse.ArgumentParser(description="HUB CLI for Social Bot Scheduler")
    subparsers = parser.add_subparsers(dest="command")

    # list-cases
    subparsers.add_parser("list-cases", help="List all available cases (Allowlist)")

    # run
    run_parser = subparsers.add_parser("run", help="Run a specific case")
    run_parser.add_argument("case", help="Case name (e.g., 01-python-to-php)")
    run_parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Disable dry-run mode")
    run_parser.set_defaults(dry_run=True)

    # doctor
    subparsers.add_parser("doctor", help="Run system diagnostics")

    # up / down
    subparsers.add_parser("up", help="Bring up the stack")
    subparsers.add_parser("down", help="Bring down the stack")

    args = parser.parse_args()

    if args.command == "list-cases":
        list_cases()
    elif args.command == "run":
        run_case(args.case, args.dry_run)
    elif args.command == "doctor":
        run_doctor()
    elif args.command == "up":
        manage_stack("up")
    elif args.command == "down":
        manage_stack("down")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
