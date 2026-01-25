# 🤖 Social Bot Scheduler: Matriz de Integración Multi-Eje

### *Automatización avanzada: Orquestación de Python, Go, Node.js y PHP mediante n8n.*

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![Ecosystem](https://img.shields.io/badge/Matriz-8_Ejes-blueviolet.svg)]()
[![Documentation](https://img.shields.io/badge/docs-completo-green.svg)]()

---

## 💡 Sobre el Proyecto
**Social Bot Scheduler** es un laboratorio de ingeniería de software diseñado para demostrar la interoperabilidad entre múltiples lenguajes de programación. Utiliza **n8n** como bus de orquestación central para comunicar emisores (bots) escritos en diversos lenguajes con receptores (dashboards) también agnósticos.

El objetivo es demostrar que la arquitectura modular puede superar las barreras del lenguaje.

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

### Paso 2: Configuración Automática
Hemos creado un asistente maestro que configura todo por ti. Ejecútalo:
```bash
python setup.py
```
Sigue las instrucciones en pantalla:
1.  Selecciona el **Caso 01 (Python -> PHP)** para tu primera prueba.
2.  El script generará los archivos `.env` y configurará los entornos virtuales necesarios.

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

### Paso 5: ¡Disparar!
Ejecuta el bot emisor desde su carpeta `origin`:
```bash
cd cases/01-python-to-php/origin
python bot.py
```
Verifica el resultado en el Dashboard: [http://localhost:8081](http://localhost:8081)

---

## 🏗️ La Gran Matriz de Integración
Tabla de estado actual de los 8 ejes de integración:

| ID | Eje Tecnológico (Origen -> Puente -> Destino) | Dashboard | Estado |
| :--- | :--- | :--- | :--- |
| **01** | 🐍 **Python** -> 🔗 n8n -> 🐘 **PHP** | `localhost:8081` | ✅ Operativo |
| **02** | 🐍 **Python** -> 🔗 n8n -> 🐹 **Go** | `localhost:8082` | ✅ Operativo |
| **03** | 🐹 **Go** -> 🔗 n8n -> 🍏 **Node.js** | `localhost:8083` | ✅ Operativo |
| **04** | 🍏 **Node.js** -> 🔗 n8n -> 🐍 **FastAPI** | `localhost:8084` | ✅ Operativo |
| **05** | 🐘 **Laravel** -> 🔗 n8n -> ⚛️ **React** | `localhost:8085` | ✅ Operativo |
| **06** | 🐹 **Go** -> 🔗 n8n -> 🐘 **Symfony** | `localhost:8086` | ✅ Operativo |
| **07** | 🦀 **Rust** -> 🔗 n8n -> 💎 **Ruby** | `localhost:8087` | ✅ Operativo |
| **08** | ❄️ **C#** -> 🔗 n8n -> 🌶️ **Flask** | `localhost:8088` | ✅ Operativo |

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
