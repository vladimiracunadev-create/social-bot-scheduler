# 🤖 Social Bot Scheduler: Matriz de Integración Multi-Eje

### *Automatización avanzada: Orquestación de Python, Go, Node.js y PHP mediante n8n.*

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![Ecosystem](https://img.shields.io/badge/Matriz-8_Ejes-blueviolet.svg)]()
[![Security](https://img.shields.io/badge/Security-Hardened-success.svg)]()
[![Latest Release](https://img.shields.io/badge/release-v2.2.0-blue.svg)]()

---

## 💡 Sobre el Proyecto
**Social Bot Scheduler** es un laboratorio de ingeniería de software diseñado para demostrar la interoperabilidad entre múltiples lenguajes de programación. Utiliza **n8n** como bus de orquestación central para comunicar emisores (bots) escritos en diversos lenguajes con receptores (dashboards) también agnósticos.

### 🛡️ Hardening de Producción
Este repositorio ha sido auditado y robustecido siguiendo estándares de seguridad industrial:
- **Seguridad en Contenedores**: Ejecución forzada como usuario no-root y sistema de archivos de solo lectura.
- **Validación de Entradas**: El HUB CLI protege contra Path Traversal y ejecución remota de código (RCE).
- **Orquestación Segura**: Manifiestos de Kubernetes con `SecurityContext` restrictivo y `NetworkPolicy` de denegación por defecto.
- **Escaneo Automático**: Integración de `Gitleaks`, `Trivy` y `pip-audit` en el pipeline de CI/CD.
- **Capa HUB**: Orquestador centralizado con manifiestos YAML, auditoría y diagnósticos integrados.

---

## 🚀 Guía de Inicio Rápido

### Prerrequisitos
Antes de comenzar, asegúrate de tener instalado:
1.  **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**: Para ejecutar la infraestructura (n8n, bases de datos y receptores).
2.  **[Python 3.10+](https://www.python.org/downloads/)**: Para ejecutar el asistente de configuración `setup.py` y los bots emisores.
3.  **[Git](https://git-scm.com/downloads)**: Para clonar este repositorio.

### Paso 1: Instalación
Clona el repositorio en tu máquina local:
```bash
git clone https://github.com/vladimiracunadev-create/social-bot-scheduler.git
cd social-bot-scheduler
```

### Paso 2: Configuración (Elige tu camino)

#### Opción A: Orquestador HUB (Recomendado)
Usa el nuevo HUB para listar y diagnosticar:
```bash
# Windows
.\hub.ps1 listar-casos
.\hub.ps1 doctor

# Linux
./hub.sh listar-casos
```

#### Opción B: Asistente Legacy
Sigue el flujo tradicional con nuestro asistente interactivo:
```bash
python setup.py
```
1.  Selecciona el **Caso 01 (Python -> PHP)**.
2.  El script generará los archivos `.env` y preparará el entorno.

### Paso 3: Levantar Infraestructura
El asistente te dará el comando exacto al finalizar. Generalmente será:
```bash
docker-compose up -d n8n dest-php
```
*Nota: Esto descargará las imágenes y levantará los servicios en segundo plano.*

### Paso 4: Conectar n8n (El Cerebro)
Esta es la única parte manual e importante:
1.  Abre [http://localhost:5678](http://localhost:5678).
2.  Configura tu usuario admin (si es la primera vez).
3.  Importa el flujo (Workflow) desde el archivo JSON ubicado en `cases/0X-.../n8n/workflow.json`.
4.  **ACTIVA** el workflow (switch arriba a la derecha).

### Paso 5: ¡Disparar y Monitorear!
Ejecuta el bot emisor desde su carpeta `origin`:
```bash
cd cases/01-python-to-php/origin
python bot.py
```

### 📊 ¿Dónde están mis Logs?
Si los logs aparecen vacíos, sigue estos pasos:
1.  **Dashboard Maestro (Global)**: Entra en [http://localhost:8080](http://localhost:8080) para ver el estado de todos los casos.
2.  **Logs en Tiempo Real**: Ejecuta `make logs` en la raíz para ver la actividad de todos los contenedores Docker.
3.  **Logs de n8n**: Ejecuta `make logs-n8n` para ver si el puente está recibiendo datos.
4.  **Logs persistentes (Archivos)**: Revisa carpetas como `cases/01-python-to-php/dest/logs/`. Estos archivos solo se crean si el `WEBHOOK_URL` en tu `.env` es correcto y el post llega al destino.

Verifica el Dashboard del Caso 01: [http://localhost:8081](http://localhost:8081)



---

## 🏗️ La Gran Matriz de Integración
Tabla de estado actual de los 8 ejes de integración:

| ID | Eje Tecnológico (Origen -> Puente -> Destino) | Dashboard | Estado |
| :--- | :--- | :--- | :--- |
| [**01**](cases/01-python-to-php/README.md) | 🐍 **Python** -> 🔗 n8n -> 🐘 **PHP** | `localhost:8081` | ✅ Operativo |
| [**02**](cases/02-python-to-go/README.md) | 🐍 **Python** -> 🔗 n8n -> 🐹 **Go** | `localhost:8082` | ✅ Operativo |
| [**03**](cases/03-go-to-node/README.md) | 🐹 **Go** -> 🔗 n8n -> 🍏 **Node.js** | `localhost:8083` | ✅ Operativo |
| [**04**](cases/04-node-to-fastapi/README.md) | 🍏 **Node.js** -> 🔗 n8n -> 🐍 **FastAPI** | `localhost:8084` | ✅ Operativo |
| [**05**](cases/05-laravel-to-react/README.md) | 🐘 **Laravel** -> 🔗 n8n -> ⚛️ **React** | `localhost:8085` | ✅ Operativo |
| [**06**](cases/06-go-to-symfony/README.md) | 🐹 **Go** -> 🔗 n8n -> 🐘 **Symfony** | `localhost:8086` | ✅ Operativo |
| [**07**](cases/07-rust-to-ruby/README.md) | 🦀 **Rust** -> 🔗 n8n -> 💎 **Ruby** | `localhost:8087` | ✅ Operativo |
| [**08**](cases/08-csharp-to-flask/README.md) | ❄️ **C#** -> 🔗 n8n -> 🌶️ **Flask** | `localhost:8088` | ✅ Operativo |

---

## 📖 Documentación Detallada
- 🎓 **[Guía Paso a Paso para Principiantes](docs/BEGINNERS_GUIDE.md)**: Manual detallado desde cero.
- 🔧 **[Solución de Problemas](docs/TROUBLESHOOTING.md)**: Cómo arreglar errores comunes (Docker, n8n, dependencias).
- 📊 **[Índice de Casos](docs/CASES_INDEX.md)**: Explicación técnica de cada combinación.
- 🏗️ **[Arquitectura](docs/ARCHITECTURE.md)**: Diagramas del sistema.

---

## 🤝 Contribución
Las Pull Requests son bienvenidas. Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles sobre nuestro código de conducta y el proceso para enviarnos pull requests.

---
*© 2026 Social Bot Scheduler - Laboratorio de Integración*
