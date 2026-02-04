import os
import sys
import argparse
import subprocess
import re
from pathlib import Path

CASES_DIR = Path("cases").resolve()

def list_cases():
    if not CASES_DIR.exists():
        print(f"Error: {CASES_DIR} directory not found.")
        return

    cases = sorted([d.name for d in CASES_DIR.iterdir() if d.is_dir()])
    print("Available Cases:")
    for case in cases:
        print(f" - {case}")

def run_case(case_name, dry_run=True):
    # Security Check: Validate case_name format
    if not re.match(r"^[a-zA-Z0-9_\-]+$", case_name):
        print(f"Error: Invalid case name '{case_name}'. Only alphanumeric, hyphens, and underscores are allowed.")
        return

    # Security Check: Prevent Path Traversal
    try:
        case_path = (CASES_DIR / case_name).resolve()
        if not str(case_path).startswith(str(CASES_DIR)):
            print(f"Error: Potential path traversal detected for case '{case_name}'.")
            return
    except (ValueError, RuntimeError) as e:
        print(f"Error resolving path: {e}")
        return

    if not case_path.exists():
        print(f"Error: Case '{case_name}' not found in {CASES_DIR}.")
        return

    print(f"Running case: {case_name}")
    if dry_run:
        print("[DRY-RUN MODE] Execution simulated. No posts will be made.")
    
    # Logic to execute the case (simplified for now as per specific case launchers)
    # Most cases have an 'origin/bot.py' or similar
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
        except subprocess.CalledProcessError as e:
            print(f"Error executing case: {e}")
    else:
        print(f"Warning: No bot.py found in {origin_path}. Manual execution might be required.")

def manage_stack(action, case_name=None):
    cmd = ["docker-compose"]
    if case_name:
        # In this repo, cases often share a global docker-compose or have specific services
        # For now, we'll use the main docker-compose and target services if we can map them
        pass
    
    cmd.append(action)
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description="HUB CLI for Social Bot Scheduler")
    subparsers = parser.add_subparsers(dest="command")

    # list-cases
    subparsers.add_parser("list-cases", help="List all available cases")

    # run
    run_parser = subparsers.add_parser("run", help="Run a specific case")
    run_parser.add_argument("case", help="Case name (e.g., 01-python-to-php)")
    run_parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Disable dry-run mode")
    run_parser.set_defaults(dry_run=True)

    # up / down
    subparsers.add_parser("up", help="Bring up the stack")
    subparsers.add_parser("down", help="Bring down the stack")

    args = parser.parse_args()

    if args.command == "list-cases":
        list_cases()
    elif args.command == "run":
        run_case(args.case, args.dry_run)
    elif args.command == "up":
        manage_stack("up")
    elif args.command == "down":
        manage_stack("down")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
