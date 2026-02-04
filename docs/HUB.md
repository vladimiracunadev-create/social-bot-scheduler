# 🚀 Guía de Uso del HUB (Capa de Orquestación)

El **Social Bot Scheduler** incluye una capa de orquestación llamada **HUB** que permite gestionar todos los casos de integración de forma centralizada y segura.

## 🛠️ Herramientas Disponibles

Puedes interactuar con el HUB de tres maneras:
- **Linux/Mac**: `./hub.sh`
- **Windows**: `.\hub.ps1`
- **Makefile**: `make hub-listar`, `make hub-ejecutar`, `make hub-doctor`

---

## 📋 Comandos del CLI

### 1. Listar Casos
Enumera todos los casos de integración registrados mediante archivos `app.manifest.yml`.
```bash
python hub.py listar-casos
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
