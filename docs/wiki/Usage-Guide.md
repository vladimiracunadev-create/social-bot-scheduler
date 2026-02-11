# 📖 Guía de Uso Detallada

[![CI/CD Pipeline](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/vladimiracunadev-create/social-bot-scheduler/actions/workflows/ci-cd.yml)
[![Ecosystem](https://img.shields.io/badge/Matriz-8_Ejes-blueviolet.svg)]()

[← Volver al Inicio](Home)

---


El proyecto se puede utilizar a través de tres capas principales:

## 1. HUB CLI (Recomendado)
El HUB centraliza todas las operaciones. Puedes usarlo mediante los wrappers `hub.sh` (Linux) o `hub.ps1` (Windows).

### Comandos Principales:
- `listar-casos`: Muestra todos los escenarios disponibles.
- `doctor`: Diagnostica el estado de Docker, archivos y logs.
- `up` / `down`: Gestiona la infraestructura de contenedores.
- `ejecutar <id>`: Lanza un bot emisor específico.

## 2. Gestión de Contenido (`posts.json`)
Cada bot de origen lee las tareas pendientes desde un archivo JSON.
- **Formato**:
```json
{
  "id": "p001",
  "text": "Mensaje...",
  "channels": ["twitter"],
  "scheduled_at": "2026-02-04T12:00:00",
  "published": false
}
```
- **Lógica**: El bot solo procesará posts donde `published` sea `false` y la fecha haya pasado.

## 3. Orquestador n8n
1. Accede a `http://localhost:5678`.
2. Importa el archivo `workflow.json` del caso que estés probando.
3. El bot emisor enviará el JSON al webhook de n8n, y n8n se encargará de distribuirlo al destino.

## 4. Recuperación de Fallos

Si algo sale mal, el sistema tiene mecanismos de auto-protección.
- Si un servicio destino falla, se reintentará 3 veces.
- Si persiste, se enviará al **DLQ** (`errors.log` en el destino).
- Para más detalles, ver [Resiliencia](Resilience.md).
