#!/usr/bin/env python3
"""
Script compartido para gestionar Circuit Breaker.
Usado por todos los workflows de n8n (casos 01-08).
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuración
SCRIPT_DIR = Path(__file__).parent
STATE_FILE = SCRIPT_DIR / "shared" / "circuit_state.json"
FAILURE_THRESHOLD = 5  # Fallos consecutivos para abrir el circuito
TIMEOUT_MINUTES = 5  # Tiempo en OPEN antes de pasar a HALF_OPEN


def load_state():
    """Carga el estado del circuit breaker."""
    if not STATE_FILE.exists():
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        return {}

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    """Guarda el estado del circuit breaker."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_case_state(case_id):
    """Obtiene el estado de un caso específico."""
    state = load_state()

    if case_id not in state:
        state[case_id] = {
            "state": "CLOSED",
            "failures": 0,
            "opened_at": None,
            "last_check": None,
        }
        save_state(state)

    return state[case_id]


def check_circuit(case_id):
    """Verifica el estado del circuit breaker y actualiza si es necesario."""
    state = load_state()
    case_state = get_case_state(case_id)

    current_state = case_state["state"]

    # Si está OPEN, verificar si debe pasar a HALF_OPEN
    if current_state == "OPEN":
        opened_at = datetime.fromisoformat(case_state["opened_at"])
        elapsed = datetime.now() - opened_at

        if elapsed >= timedelta(minutes=TIMEOUT_MINUTES):
            case_state["state"] = "HALF_OPEN"
            case_state["last_check"] = datetime.now().isoformat()
            state[case_id] = case_state
            save_state(state)
            current_state = "HALF_OPEN"

    return {
        "state": current_state,
        "failures": case_state["failures"],
        "can_proceed": current_state in ["CLOSED", "HALF_OPEN"],
    }


def record_success(case_id):
    """Registra un éxito (resetea contador y cierra circuito)."""
    state = load_state()
    case_state = get_case_state(case_id)

    case_state["state"] = "CLOSED"
    case_state["failures"] = 0
    case_state["opened_at"] = None
    case_state["last_check"] = datetime.now().isoformat()

    state[case_id] = case_state
    save_state(state)

    return {"state": "CLOSED", "failures": 0}


def record_failure(case_id):
    """Registra un fallo (incrementa contador y abre circuito si es necesario)."""
    state = load_state()
    case_state = get_case_state(case_id)

    case_state["failures"] += 1
    case_state["last_check"] = datetime.now().isoformat()

    # Si alcanzamos el threshold, abrir el circuito
    if case_state["failures"] >= FAILURE_THRESHOLD:
        case_state["state"] = "OPEN"
        case_state["opened_at"] = datetime.now().isoformat()

    state[case_id] = case_state
    save_state(state)

    return {
        "state": case_state["state"],
        "failures": case_state["failures"],
        "threshold_reached": case_state["failures"] >= FAILURE_THRESHOLD,
    }


def reset_circuit(case_id):
    """Resetea manualmente el circuit breaker."""
    state = load_state()

    state[case_id] = {
        "state": "CLOSED",
        "failures": 0,
        "opened_at": None,
        "last_check": datetime.now().isoformat(),
    }

    save_state(state)
    return {"state": "CLOSED", "reset": True}


def get_all_states():
    """Obtiene el estado de todos los circuitos."""
    return load_state()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: circuit_breaker.py <action> <case_id>"}))
        sys.exit(1)

    action = sys.argv[1]

    if action == "check" and len(sys.argv) == 3:
        case_id = sys.argv[2]
        result = check_circuit(case_id)
        print(json.dumps(result))

    elif action == "record_success" and len(sys.argv) == 3:
        case_id = sys.argv[2]
        result = record_success(case_id)
        print(json.dumps(result))

    elif action == "record_failure" and len(sys.argv) == 3:
        case_id = sys.argv[2]
        result = record_failure(case_id)
        print(json.dumps(result))

    elif action == "reset" and len(sys.argv) == 3:
        case_id = sys.argv[2]
        result = reset_circuit(case_id)
        print(json.dumps(result))

    elif action == "status":
        result = get_all_states()
        print(json.dumps(result, indent=2))

    else:
        print(
            json.dumps(
                {
                    "error": f"Invalid action '{action}'. Use: check, record_success, record_failure, reset, status"
                }
            )
        )
        sys.exit(1)
