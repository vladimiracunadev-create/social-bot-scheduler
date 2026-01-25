# 🧑‍💻 Guía de Mantenedores

Información crítica para el mantenimiento y evolución del **Social Bot Scheduler**.

## Estándares de Código
- **Lenguaje**: Python 3.11+.
- **Estilo**: Seguir PEP 8.
- **Tipado**: Usar `dataclasses` y annotations cuando sea posible para mejorar la legibilidad.

## Flujo de Trabajo (Git)
1. Las nuevas funcionalidades se desarrollan en ramas `feature/`.
2. Las correcciones de errores en ramas `fix/`.
3. Todas las PR deben ser revisadas por al menos un mantenedor.

## Pruebas
Antes de proponer un cambio, asegúrate de:
- Verificar el build de Docker: `make build`.
- Probar el bot en modo "Dry-run" (sin `WEBHOOK_URL` en el `.env`) para asegurar que la lógica de carga de posts sigue funcionando.

## Versionado
Seguimos [SemVer](https://semver.org/lang/es/).
- **Major**: Cambios en el contrato de API o ruptura de compatibilidad.
- **Minor**: Nuevas funcionalidades (ej: soporte para nuevos canales JSON).
- **Patch**: Corrección de bugs.
