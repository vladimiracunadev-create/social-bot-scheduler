# 📖 Guía de Operación y Uso — Social Bot Scheduler

Esta guía proporciona las instrucciones operativas para interactuar con el laboratorio de ingeniería, desde la ejecución de bots individuales hasta la orquestación masiva.

---

## 🚦 Primeros Pasos (Bootstrap)

Asegúrate de haber configurado tu entorno siguiendo la [Guía de Instalación](../../docs/INSTALL.md).

### 🖥️ Interacción con el HUB (CLI)
El **HUB** es la herramienta maestra para gestionar la matriz de 9 casos:
- **Windows**: `.\hub.ps1 doctor`
- **Linux / macOS**: `./hub.sh doctor`

---

## 🧩 Ejecución de Casos de Integración

Existen dos modalidades principales para poner a prueba el ecosistema:

### 🚀 Modo A: Ejecución Unificada (HUB)
Utiliza el HUB para automatizar el lanzamiento de bots sin navegar por carpetas:
```bash
# Listar todos los ejes disponibles
python hub.py listar-casos

# Ejecutar el bot del Caso 01 (Simulación)
python hub.py ejecutar 01-python-to-php

# Ejecutar el bot real (Envío HTTP activo)
python hub.py ejecutar 01-python-to-php --real
```

### 🛠️ Modo B: Ejecución Manual (Directa)
Para desarrolladores que deseen depurar el código de los emisores:
1. Accede a la carpeta del caso: `cd cases/01-python-to-php/origin`.
2. Ejecuta el emisor nativo: `python bot.py`.

---

## 🏗️ Gestión de Infraestructura Docker

Operar 20+ contenedores requiere comandos precisos:
- **🎛️ Activar Todo (`full`)**: `make up` o `python hub.py up`.
- **🛡️ Núcleo Seguro**: `make up-secure` (n8n + Dashboard).
- **📊 Monitoreo**: `make up-observability` (Prometheus/Grafana).
- **🧹 Purga Total**: `make clean` (Elimina volúmenes y estados).

---

## 🛡️ Diagnóstico y Salud

> [!TIP]
> **Diagnostic Trail**: Utiliza `make doctor` frecuentemente para verificar la conectividad de los puertos y la presencia de variables de entorno críticas.

- **Check n8n**: `python verify_n8n.py`
- **Check Security**: `python scripts/check_runtime_security.py`

---
*Manual de operaciones v4.0 — Social Bot Scheduler*
