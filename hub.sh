#!/bin/bash
# Social Bot Scheduler - HUB Wrapper (Shell)

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

$PYTHON_CMD hub.py "$@"
