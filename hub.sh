#!/bin/bash
# Social Bot Scheduler - HUB Wrapper (Shell)
# DECISIÓN DE RUNTIME: Este repo es "Python-first" (tiene pyproject.toml/requirements.txt).
# Se usa hub.py como motor principal.

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Error: Python no está instalado. El HUB requiere Python en este repositorio."
    exit 1
fi

$PYTHON_CMD hub.py "$@"
