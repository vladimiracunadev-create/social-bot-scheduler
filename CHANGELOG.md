Todos los cambios notables en este proyecto serán documentados en este archivo.

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
