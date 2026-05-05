# 🚀 HUB Maestro de Orquestación

El **Social Bot Scheduler** incluye dos capas de control complementarias:

1. **HUB CLI** (`hub.py` / `hub.sh` / `hub.ps1`) — la herramienta para gestionar la matriz de **9 casos implementados** (+ [11 planificados](PLANNED_CASES.md)) desde terminal de forma centralizada, segura y estandarizada.
2. **Master Dashboard** (`http://localhost:8080`, v4.3.0+) — interfaz web read-only con **detección automática del estado de Docker por caso**, contadores live, indicador de última comprobación y modal con el comando `docker-compose --profile caseXX up -d` listo para copiar cuando un caso está caído. Ver [HEALTH_CHECK.md](HEALTH_CHECK.md#diagnóstico-desde-el-master-dashboard-v430).

---

## 🛠️ Modos de Interacción

Dependiendo de tu sistema operativo, puedes invocar al orquestador mediante los siguientes wrappers:

| Entorno | Comando | Descripción |
| :--- | :--- | :--- |
| **Linux / macOS** | `./hub.sh` | Wrapper en Bash con auto-detección de Python. |
| **Windows** | `.\hub.ps1` | Script en PowerShell optimizado para el entorno local. |
| **Universal** | `make hub-*` | Comandos integrados en el `Makefile` para CI/CD. |

---

## 🏗️ Funcionalidades del HUB

### 1. Diagnóstico de Salud (Doctor)
Verifica que el daemon de Docker esté activo y que todos los servicios necesarios (incluyendo las 8 DBs) estén configurados.
```bash
python hub.py doctor
```

### 2. Ejecución Controlada
Lanza el bot de origen de un caso específico. Por defecto, el sistema opera en modo `dry-run` para evitar efectos secundarios.
```bash
# Modo Simulación (Seguro)
python hub.py ejecutar 01-python-to-php

# Ejecución Real (Producción/Integración)
python hub.py ejecutar 01-python-to-php --real
```

### 3. Inventario de Casos
Escanea el sistema en busca de archivos `app.manifest.yml` y genera la matriz de integración actual.
```bash
python hub.py listar-casos
```

---

## 🔐 Seguridad y Auditoría

> [!IMPORTANT]
> **Audit Trail**: Cada comando ejecutado a través del HUB queda registrado en `hub.audit.log`, permitiendo la trazabilidad de operaciones en el laboratorio.

El HUB implementa **Validación de Entradas** estricta para prevenir ataques de inyección de comandos o Path Traversal durante la ejecución de los entrypoints de los bots.

---

## 📁 El Manifiesto de Aplicación

Cada caso dentro del directorio `cases/` debe contar con un archivo `app.manifest.yml` para ser reconocido por el HUB:

```yaml
id: "01"
name: "Python to PHP Integration"
origin:
  language: "python"
  entrypoint: "origin/bot.py" # Relativo a la carpeta del caso
destination:
  port: 8081
  database: "mysql"
```

---
*Documentación técnica del orquestador v4.0 — Social Bot Scheduler*
