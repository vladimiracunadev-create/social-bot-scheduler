# Social Bot Scheduler - HUB Wrapper (PowerShell)

$PythonCmd = "python"
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
}

& $PythonCmd hub.py $args
