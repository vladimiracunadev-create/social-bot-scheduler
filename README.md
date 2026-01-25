# 🤖 Social Bot Scheduler: El Hub de Integración
### *Explora el poder de la automatización Multi-Eje: Origen -> n8n -> Destino*

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![Ecosystem](https://img.shields.io/badge/Matriz-4_Ejes-blueviolet.svg)]()
[![Docker Stack](https://img.shields.io/badge/stack-Python--Go--Node--PHP--FastAPI-blue.svg)]()

---

## 🏗️ La Gran Matriz de Integración
Este repositorio es un laboratorio de ingeniería que demuestra cómo diferentes tecnologías pueden orquestarse para automatizar redes sociales. Cada **Caso** es un eje completo de comunicación.

| ID | Eje Tecnológico (Origen -> Puente -> Destino) | Dashboard | Estado |
| :--- | :--- | :--- | :--- |
| **01** | 🐍 **Python** -> 🔗 n8n -> 🐘 **PHP** | `localhost:8081` | ✅ |
| **02** | 🐍 **Python** -> 🔗 n8n -> 🐹 **Go** | `localhost:8082` | ✅ |
| **03** | 🐹 **Go** -> 🔗 n8n -> 🍏 **Node.js** | `localhost:8083` | 🚀 |
| **04** | 🍏 **Node.js** -> 🔗 n8n -> 🐍 **FastAPI** | `localhost:8084` | 🚀 |

---

## 🚀 Inicio Inteligente con Master Launcher
Hemos simplificado la complejidad. No necesitas configurar cada caso a mano.

1.  **Ejecuta el asistente maestro**:
    ```bash
    python setup.py
    ```
2.  **Elige tu Eje**: Selecciona del 1 al 4. El script configurará archivos `.env`, instalará dependencias y preparará el terreno para ese caso específico.
3.  **Lanza el Destino**:
    ```bash
    docker-compose up -d n8n [servicio-elegido]
    ```
4.  **Lanza el Emisor**: Sigue las instrucciones del script para ejecutar el bot emisor correspondiente en su carpeta `origin/`.

---

## 🖥️ Requerimientos de Hardware
| Perfil | CPU | RAM | Disco |
| :--- | :--- | :--- | :--- |
| **🏠 Personal** | 1 Core | 2 GB | 5 GB SSD |
| **🏢 Business** | 2 Cores | 4 GB | 20 GB SSD |

---

## 📖 Documentación por Niveles
- 📗 [**Comparativa de Ejes**](docs/CASES_INDEX.md): ¿Cuál elegir y por qué?
- 📔 [Arquitectura Profunda](docs/ARCHITECTURE.md): Diagramas de flujo de los 3 ejes.
- 📘 [Guía de Principiantes](docs/BEGINNERS_GUIDE.md): Conceptos básicos de automatización.

---
*Desarrollado para la comunidad de automatizadores – © 2026*
