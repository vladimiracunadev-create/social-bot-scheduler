# Social Bot Scheduler – Automatización Inteligente de Redes Sociales

**Social Bot Scheduler** es una solución profesional de orquestación para la publicación programada en múltiples canales. Diseñada para integrarse perfectamente con flujos de trabajo en **n8n**, permite gestionar el contenido de redes sociales de manera eficiente y escalable.

---

## 🛠️ Stack Tecnológico
Para que el ecosistema funcione correctamente, el sistema utiliza las siguientes tecnologías:

| Componente | Tecnología | Rol |
| :--- | :--- | :--- |
| **Core** | `Python 3.11+` | Lógica de scheduling y procesamiento de datos. |
| **Automation** | `n8n` | Orquestador de flujos y conexión con APIs externas. |
| **API Receiver** | `PHP 8.2` | Receptor de eventos y logging de publicaciones. |
| **Infraestructura** | `Docker / Compose` | Contenerización y despliegue universal. |
| **Orquestación** | `Kubernetes` | (Opcional) Despliegue en clusters escalables. |
| **Calidad** | `Pytest / Mypy` | Pruebas unitarias y tipado estático. |

---

## 🖥️ Requerimientos de Hardware
Dependiendo de la escala de tu automatización, estos son los recursos necesarios:

| Recurso | Mínimo (Home Bot) | Recomendado (Pro) | Enterprise (Cluster) |
| :--- | :--- | :--- | :--- |
| **CPU** | 1 Core (vCPU) | 2 Cores | 4+ Cores |
| **RAM** | 2 GB* | 4 GB | 8 GB+ |
| **Disco** | 5 GB (SSD) | 20 GB | 100 GB+ |
| **Red** | 10 Mbps | 100 Mbps | 1 Gbps+ |

> [!NOTE]
> *n8n es el componente más demandante en RAM. Si solo usas el bot de Python sin n8n, podrías funcionar con 512MB de RAM.

---

## ⚡ Inicio Inmediato (Instalación Universal)
Para que todo funcione a la primera en cualquier sistema (Windows, Mac, Linux), recomendamos el uso de Docker:

1. **Configura tu entorno**:
   ```bash
   python setup.py
   ```
   *Este script verificará tus requisitos y configurará los archivos necesarios.*

2. **Levanta todo el ecosistema**:
   ```bash
   docker-compose up -d
   ```
   *Esto iniciará automáticamente Python, n8n y el receptor PHP.*

---

## 📖 Documentación para Todos
- 📘 [**Guía para Principiantes**](docs/BEGINNERS_GUIDE.md): ¿No sabes por dónde empezar? Lee esto primero para entender la lógica del proyecto.
- 📖 [Manual de Usuario](docs/USER_MANUAL.md): Aprende a gestionar tus posts y canales.

### 🛡️ Para Desarrolladores y DevOps
- 🚀 [Guía de Instalación Avanzada](docs/INSTALL.md): Docker, Kubernetes y entornos locales.
- 🏗️ [Arquitectura](docs/ARCHITECTURE.md): Detalle técnico, diagramas Mermaid y flujos.
- 🔌 [Referencia de API](docs/API.md): Contrato del webhook y payloads JSON.
- 🧑‍💻 [Guía de Mantenedores](docs/MAINTAINERS.md): Estándares, Linting y CI/CD.

### 📋 Referencia Técnica
- 📜 [Catálogo de Funcionalidades](docs/SYSTEMS_CATALOG.md): Capacidades actuales.
- 🛡️ [Seguridad](docs/SECURITY.md): Manejo de secretos y riesgos.
- 🕒 [Historial de Cambios](CHANGELOG.md): Registro de versiones (SemVer).

---

## 🤝 Comunidad y Colaboración
¡Este proyecto está abierto a contribuciones! Si deseas ayudar a mejorar el scheduler:
1. Haz un **Fork** del proyecto.
2. Crea una **Rama** para tu funcionalidad (`git checkout -b feature/nueva-mejora`).
3. Envía un **Pull Request**.

---
*Desarrollado con ❤️ para la comunidad de automatizadores.*
