# Social Bot Scheduler – Automatización Inteligente de Redes Sociales

**Social Bot Scheduler** es una solución profesional de orquestación para la publicación programada en múltiples canales. Diseñada para integrarse perfectamente con flujos de trabajo en **n8n**, permite gestionar el contenido de redes sociales de manera eficiente y escalable.

---

## 📋 Requisitos del Sistema
Para asegurar un funcionamiento óptimo, se recomienda:
- **Python**: 3.11+
- **Docker**: Engine 20.10+ y Compose v2
- **Kubernetes** (Opcional): kubectl configurado para despliegue en cluster.
- **n8n**: Una instancia con un webhook configurado para recibir los posts.

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
