# 🚀 Guía de Uso del HUB (Capa de Orquestación)

El **Social Bot Scheduler** incluye una capa de orquestación llamada **HUB** que permite gestionar todos los casos de integración de forma centralizada y segura.

## 🛠️ Herramientas Disponibles

Puedes interactuar con el HUB de tres maneras:
- **Linux/Mac**: `./hub.sh`
- **Windows**: `.\hub.ps1`
- **Makefile**: `make hub-listar`, `make hub-ejecutar`, `make hub-doctor`

---

## ⚖️ Decisión de Runtime (Obligatoria)

Este repositorio utiliza **Python** como lenguaje principal para el HUB siguiendo estas reglas:
1. **Detección**: Se detectó `pyproject.toml` / `requirements.txt` en la raíz.
2. **Prioridad**: Al ser un repositorio Python-first, el HUB se implementa en Python (`hub.py`).
3. **Alternativas**: Si el repo fuera Node.js, se usaría TS. Si no tuviera runtime claro, se usaría Bash/BS1.
4. **Opcionalidad**: El HUB es una capa de conveniencia. El "legacy quickstart" (`docker-compose up`) sigue funcionando sin cambios.

---

## 🛠️ Herramientas de Acceso (Detección de Sistema)

El HUB detecta automáticamente tu entorno a través de estos puntos de entrada:
- **Linux/bash**: `./hub.sh` (Auto-detecta `python3` o `python`).
- **Windows/powershell**: `.\hub.ps1` (Auto-detecta `python`).
- **Universal/Makefile**: `make hub-listar`, etc.

---

### 1. Listar Casos
Enumera todos los casos de integración registrados mediante archivos `app.manifest.yml`.
```bash
# Recomendado usar los wrappers:
./hub.sh listar-casos
# o
make hub-listar
```

### 2. Ejecutar un Bot
Lanza el emisor de un caso específico. Por defecto funciona en modo simulación (dry-run).
```bash
# Modo simulación
python hub.py ejecutar 01-python-to-php

# Ejecución real (si el bot lo soporta)
python hub.py ejecutar 01-python-to-php --real
```

### 3. Diagnóstico (Doctor)
Verifica que tu entorno (Docker, casos, logs) esté correctamente configurado.
```bash
python hub.py doctor
```

### 4. Gestión de Infraestructura
Levanta o detiene los servicios de Docker Compose.
```bash
python hub.py up
python hub.py down
```

> **Soporte Multi-DB**: El HUB heredará la orquestación de las 8 bases de datos definidas en `docker-compose.yml`, asegurando que la infraestructura de persistencia esté lista antes de ejecutar los bots.

---

## 📄 Archivos de Configuración

### Manifiesto de Aplicación (`app.manifest.yml`)
Cada caso debe incluir este archivo para ser reconocido por el HUB.
```yaml
id: "01"
name: "Nombre del Caso"
origin:
  language: "python"
  entrypoint: "origin/bot.py"
destination:
  port: 8081
```

### Log de Auditoría (`hub.audit.log`)
Registra cada acción realizada a través del CLI para fines de seguridad y monitoreo.

---

> [!NOTE]
> El HUB es una herramienta opcional diseñada para facilitar el desarrollo. El flujo tradicional de configuración manual (`setup.py` y `docker-compose`) sigue estando disponible.
