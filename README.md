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

## ⚡ Inicio Inmediato con Makefile
Este proyecto incluye un `Makefile` para simplificar todas las operaciones comunes.

### 🐳 Con Docker (Recomendado)
Levanta el bot en segundos:

```bash
# Construir y levantar
make build
make up
```

### 🐍 Ejecución Local
```bash
# Instalar dependencias
make install
# Renombrar .env.example a .env y configurar
# Ejecutar bot
python bot.py
```

---

## 🚀 Características Principales
- **🧩 Modularidad**: Fácil integración con webhooks externos (n8n, Make/Integromat).
- **🐳 Container Ready**: Configuraciones listas para Docker y Docker Compose.
- **☸️ Enterprise Grade**: Manifiestos de Kubernetes (CronJob) para despliegues a escala.
- **🛠️ Automatización**: Makefile intuitivo y **GitHub Actions** para CI/CD continuo.
- **🛡️ Calidad**: Linters (`flake8`, `black`) y Hooks de `pre-commit` integrados.

---

## 📖 Documentación Avanzada
Explora nuestras guías detalladas para maximizar el uso del bot:
- 📖 [Guía de Instalación](docs/INSTALL.md): Despliegue en Docker, K8s y servidores locales.
- 📖 [Manual de Usuario](docs/USER_MANUAL.md): Cómo estructurar tus posts y canales.
- 🏗️ [Arquitectura](docs/ARCHITECTURE.md): Diagramas Mermaid y flujo de datos.
- 🔌 [Referencia de API](docs/API.md): Contrato del webhook y payloads JSON.
- 📜 [Catálogo de Funcionalidades](docs/SYSTEMS_CATALOG.md): Detalle técnico de capacidades.
- 🛡️ [Seguridad](docs/SECURITY.md): Políticas de protección y manejo de secretos.
- 🧑‍💻 [Guía de Mantenedores](docs/MAINTAINERS.md): Estándares de código y flujos de trabajo.
- 🕒 [Historial de Cambios](CHANGELOG.md): Registro detallado de versiones y mejoras.

---

## 🤝 Comunidad y Colaboración
¡Este proyecto está abierto a contribuciones! Si deseas ayudar a mejorar el scheduler:
1. Haz un **Fork** del proyecto.
2. Crea una **Rama** para tu funcionalidad (`git checkout -b feature/nueva-mejora`).
3. Envía un **Pull Request**.

---
*Desarrollado con ❤️ para la comunidad de automatizadores.*
