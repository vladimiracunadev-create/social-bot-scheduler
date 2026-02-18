Todos los cambios notables en este proyecto serán documentados en este archivo.

## [4.1.0] - 2026-02-18
### Añadido
- **Verificación de Recursos**: Nuevo script `check_resources.py` para monitorear CPU, RAM y Disco del host.
- **Indicador de Disponibilidad**: Dashboard visual que muestra la salud del sistema y preparación del entorno.
- **Limpieza Profunda**: Comandos `make clean` y `hub clean` para purgar contenedores, volúmenes e imágenes.
- **Perfiles de Docker**: Carga selectiva de servicios mediante `--profile` (ej: `case01`, `full`).
- **Requisitos del Sistema**: Nueva guía detallada en `docs/REQUIREMENTS.md`.

### Cambiado
- **Optimización de Rendimiento**: Límites de CPU/RAM para los 20 contenedores.
- **Migración a Alpine**: Servicios de destino migrados a imágenes ligeras basadas en Alpine.
- **Hub CLI mejorado**: Integración de diagnóstico de recursos en los comandos `doctor` y `up`.

## [4.0.0] - 2026-02-18
### Añadido
- **Persistencia Multi-Motor (Políglota)**: Integración de 8 bases de datos distintas (MySQL, MariaDB, PostgreSQL, SQLite, MongoDB, Redis, Cassandra y SQL Server) en los 8 casos de integración.
- **Dashboard Dinámico v2**: El Dashboard Maestro ahora visualiza el estado de la base de datos y previsualiza los últimos registros persistidos en tiempo real.
- **Auto-Provisionamiento de Datos**: Lógica de creación automática de bases de datos, colecciones y tablas en todos los servicios receptores.
- **Nuevas Dependencias**: Soporte para `pyodbc` (Python), `cassandra-driver` (Ruby), `pg` (Node), `mongodb` (Node) y extensiones de Redis en PHP.
- **Infraestructura Expandida**: Nueve servicios de bases de datos añadidos al orquestador `docker-compose`.

## [3.0.0] - 2026-02-11
### Añadido
- **Resiliencia Global (100%)**: Implementación de **Idempotencia (SQLite)** y **Circuit Breaker** en los 8 casos de integración.
- **Dead Letter Queue (DLQ)**: Sistema de captura de errores irrecuperables en todos los receptores.
- **Scripts Compartidos**: Nueva librería en `scripts/` para lógica reutilizable de resiliencia.
- **Generador de Workflows**: Script `generate_workflows.py` para estandarizar flujos de n8n.
- **Documentación Técnica**: Nuevas guías `GUARDRAILS.md` y `RESILIENCE_GUIDE.md`.

## [2.2.0] - 2026-01-25
### Añadido
- **Empaquetado**: Generación de archivo ZIP distribuible para despliegue rápido.
- **Estabilización**: Revisión de metadatos y documentación para el lanzamiento oficial.

## [2.1.0] - 2026-01-25
### Corregido
- **Estandarización Sistémica**: Todos los receptores internos (Go, Node, FastAPI, React, Sinatra, Flask) ahora escuchan en `/webhook` (o `/webhook.php`), eliminando errores 404 en n8n.
- **Normalización de Datos**: Unificados los campos de envío de posts a `id`, `text` y `channel` en toda la matriz.
- **Formateado de Código**: Aplicado `black` a todos los archivos Python para asegurar cumplimiento con el CI.
- **Construcción de Imágenes**: Añadidas dependencias de compilación (`build-base`) en el Dockerfile de Ruby para evitar fallos de gemas nativas.

### Añadido
- **Manual de Usuario**: Nueva `Guía Paso a Paso` detallada para principiantes en la carpeta `docs/`.
- **Dashboard Maestro Funcional**: Los botones de "Probar Integración" ahora abren los verificadores reales de cada caso.


## [2.0.0] - 2026-01-25
### Añadido
- **Caso 07**: Integración completa Rust (Origen) -> n8n -> Ruby Sinatra (Destino).
- **Caso 08**: Integración completa C# .NET (Origen) -> n8n -> Flask (Destino).
- **Makefile**: Soporte para comandos rápidos (`make up-case-01`, `make help`, etc.).
- **Documentación**: `README.md` estandarizado en cada carpeta de `cases/`.
- **Dashboard**: `index.html` actualizado con botones para los 8 casos.
- **Docs**: Guía de solución de problemas (`TROUBLESHOOTING.md`) y visión del proyecto (`INSIGHTS.md`).

### Cambiado
- **Arquitectura**: Actualizada la matriz de integración para soportar 8 ejes.
- **Setup**: `setup.py` mejorado para detectar entornos de Rust y .NET.
- **Guía de Principiantes**: Expandida para incluir las nuevas tecnologías.

## [1.0.0] - 2026-01-20
### Añadido
- Estructura base del proyecto con 6 casos iniciales.
- Orquestación con docker-compose.
- Dashboard unificado en `index.html`.
