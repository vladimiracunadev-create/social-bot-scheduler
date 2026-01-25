# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-25

### Added
- **Refactorización Profesional**: El código ahora se organiza como un paquete Python en `src/social_bot/`.
- **Estructura Enterprise**: Implementación de `BotService` para separar la lógica de negocio.
- **Validación de Configuración**: Uso de `pydantic-settings` para validar variables de entorno y tipos de datos (URLs, Paths).
- **Suite de Tests**: Integración de `pytest` y `pytest-cov` para pruebas unitarias y reportes de cobertura.
- **Tipado Estático**: Configuración de `mypy` para asegurar la integridad del código.
- **CI/CD Avanzado**: 
    - Pipeline de GitHub Actions que publica automáticamente la imagen en **GitHub Container Registry (GHCR)**.
    - Chequeo automático de tipos, estilo y ejecución de tests en cada push.
- **Manuales Actualizados**: Reflejan la nueva arquitectura de paquetes.

### Changed
- Migración de `bot.py` a punto de entrada delgado que delega al paquete interno.
- Configuración de Kubernetes actualizada a `CronJob` para mayor eficiencia.

## [1.1.0] - 2026-01-25

### Added
- Soporte para **Docker** y **Docker Compose**.
- Manifiestos de **Kubernetes** (inicialmente como Deployment).
- **Makefile** para automatización de tareas comunes.
- **Gestión de Estado**: El bot marca posts como publicados en el JSON.
- **Documentación Pro**: Suite completa de documentos en `docs/` inspirada en `microsistemas`.

## [1.0.0] - 2026-01-24

### Added
- Versión inicial del bot scheduler.
- Soporte para lectura de JSON y envío a webhooks de n8n.
