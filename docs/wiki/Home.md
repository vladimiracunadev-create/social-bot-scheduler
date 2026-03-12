# 🤖 Social Bot Scheduler: Wiki

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![Ecosystem](https://img.shields.io/badge/Matriz-9_Ejes-blueviolet.svg)]()
[![Security](https://img.shields.io/badge/Security-Hardened-success.svg)]()
[![Latest Release](https://img.shields.io/badge/release-v3.0.0-blue.svg)]()

Bienvenido a la Wiki oficial de **Social Bot Scheduler**. Este es un laboratorio de ingeniería diseñado para demostrar la interoperabilidad entre múltiples lenguajes de programación mediante un bus de orquestación central (**n8n**).

---

## 🧭 Mapa de Navegación

### 🚀 Primeros Pasos
- **[Inicio Rápido](Usage-Guide)**: Cómo instalar y ejecutar el proyecto.
- **[Guía de Uso Detallada](Usage-Guide)**: Comandos del HUB y configuración.

### 🛡️ Seguridad y Resiliencia
- **[Hardening de Seguridad](Security-Hardening)**: Estrategia de contenedores y escaneo.
- **[Resiliencia y Guardrails](Resilience)**: Circuit Breakers, Idempotencia y DLQ.

### 🏗️ Arquitectura y Casos
- **[?ndice de Casos](Cases-Index)**: Detalle de los 9 casos de integraci?n.
- **[Arquitectura](https://github.com/vladimiracunadev-create/social-bot-scheduler/blob/main/docs/ARCHITECTURE.md)**: Diagramas y flujos de datos.

---

## 📊 Matriz de Integración (Estado Actual)

| ID | Eje Tecnológico (Origen -> Puente -> Destino) | Estado |
| :--- | :--- | :--- |
| **01** | 🐍 **Python** -> 🔗 n8n -> 🐘 **PHP** | ✅ Operativo |
| **02** | 🐍 **Python** -> 🔗 n8n -> 🐹 **Go** | ✅ Operativo |
| **03** | 🐹 **Go** -> 🔗 n8n -> 🍏 **Node.js** | ✅ Operativo |
| **04** | 🍏 **Node.js** -> 🔗 n8n -> 🐍 **FastAPI** | ✅ Operativo |
| **05** | 🐘 **Laravel** -> 🔗 n8n -> ⚛️ **React** | ✅ Operativo |
| **06** | 🐹 **Go** -> 🔗 n8n -> 🐘 **Symfony** | ✅ Operativo |
| **07** | 🦀 **Rust** -> 🔗 n8n -> 💎 **Ruby** | ✅ Operativo |
| **08** | ❄️ **C#** -> 🔗 n8n -> 🌶️ **Flask** | ✅ Operativo |

---

## ❓ Ayuda
Si encuentras problemas, consulta la [Guía de Solución de Problemas](https://github.com/vladimiracunadev-create/social-bot-scheduler/blob/main/docs/TROUBLESHOOTING.md).
