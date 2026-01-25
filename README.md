# 🤖 Social Bot Scheduler: Matriz de Integración Multi-Eje
### *Automatización avanzada: Orquestación de Python, Go, Node.js y PHP mediante n8n.*

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![Ecosystem](https://img.shields.io/badge/Matriz-6_Ejes-blueviolet.svg)]()
[![Documentation](https://img.shields.io/badge/docs-completo-green.svg)]()

---

## 💡 Sobre el Proyecto
**Social Bot Scheduler** no es solo un bot; es un **laboratorio de ingeniería de software unificado**. Su propósito es demostrar cómo sistemas independientes (Python, Go, Node, etc.) pueden orquestarse en una matriz coherente. A través de flujos de trabajo en **n8n**, el sistema actúa como un despachador universal de contenido para redes sociales, garantizando que cada pieza tecnológica haga lo que mejor sabe hacer.

## 🏗️ La Gran Matriz de Integración
Este repositorio es un laboratorio de ingeniería que demuestra cómo diferentes tecnologías pueden orquestarse para automatizar redes sociales. Cada **Caso** es un eje completo de comunicación.

| ID | Eje Tecnológico (Origen -> Puente -> Destino) | Dashboard | Estado |
| :--- | :--- | :--- | :--- |
| **01** | 🐍 **Python** -> 🔗 n8n -> 🐘 **PHP** | `localhost:8081` | ✅ |
| **02** | 🐍 **Python** -> 🔗 n8n -> 🐹 **Go** | `localhost:8082` | ✅ |
| **03** | 🐹 **Go** -> 🔗 n8n -> 🍏 **Node.js** | `localhost:8083` | ✅ |
| **04** | 🍏 **Node.js** -> 🔗 n8n -> 🐍 **FastAPI** | `localhost:8084` | ✅ |
| **05** | 🐘 **Laravel** -> 🔗 n8n -> ⚛️ **React** | `localhost:8085` | ✅ |
| **06** | 🐹 **Go** -> 🔗 n8n -> 🐘 **Symfony** | `localhost:8086` | ✅ |
| **07** | 🦀 **Rust** -> 🔗 n8n -> 💎 **Ruby** | `localhost:8087` | ✅ |
| **08** | ❄️ **C#** -> 🔗 n8n -> 🌶️ **Flask** | `localhost:8088` | ✅ |

---

## 🎮 Panel de Control Maestro (`index.html`)
Ahora puedes probar todos los casos desde una interfaz unificada. Simplemente abre `index.html` en tu navegador para enviar peticiones de prueba y ver los resultados en tiempo real.

---

## 🚀 Inicio Inteligente con Master Launcher
Hemos simplificado la complejidad. No necesitas configurar cada caso a mano.

1.  **Ejecuta el asistente maestro**:
    ```bash
    python setup.py
    ```
2.  **Elige tu Eje**: Selecciona del 1 al 6. El script configurará archivos `.env`, instalará dependencias y preparará el terreno para ese caso específico.
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
- 📔 [Arquitectura Profunda](docs/ARCHITECTURE.md): Diagramas de flujo de los 8 ejes.
- 📘 [Guía de Principiantes](docs/BEGINNERS_GUIDE.md): Conceptos básicos y uso de Makefile.
- 🔧 [Solución de Problemas](docs/TROUBLESHOOTING.md): Guía de errores comunes.
- 💡 [Visión del Proyecto](docs/INSIGHTS.md): Desafíos, alcance y ventajas.
- 📜 [Historial de Cambios](CHANGELOG.md): Registro de actualizaciones.

---

## 🤝 Comunidad y Contribución
- 🚀 [**Guía de Contribución**](CONTRIBUTING.md): ¿Quieres añadir un eje? ¡Mira cómo!
- ⚖️ [**Código de Conducta**](CODE_OF_CONDUCT.md): Mantengamos la comunidad saludable.

---
*Desarrollado para la comunidad de automatizadores – © 2026*
