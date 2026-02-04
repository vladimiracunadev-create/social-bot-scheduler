# Social Bot Scheduler - HUB Wrapper (PowerShell)
# DECISIÓN DE RUNTIME: Este repo es "Python-first" (tiene pyproject.toml/requirements.txt).
# Se usa hub.py como motor principal.

$PythonCmd = "python"
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
}

if (-not (Get-Command $PythonCmd -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python no está instalado. El HUB requiere Python en este repositorio." -ForegroundColor Red
    exit 1
}

& $PythonCmd hub.py $args
