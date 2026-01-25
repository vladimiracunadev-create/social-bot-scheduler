# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

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
