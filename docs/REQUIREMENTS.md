# 💻 Requisitos del Sistema

Para ejecutar **Social Bot Scheduler** y toda su matriz de integración (Hub + n8n + 8 casos), tu equipo debe cumplir con los siguientes requisitos.

## hardware Mínimo y Recomendado

| Componente | Mínimo (Pruebas básicas) | Recomendado (Matriz completa) | Razón |
|------------|--------------------------|-------------------------------|-------|
| **RAM** | 4 GB | **8 GB+** | n8n consume ~500MB + cada contenedor destino (x8). |
| **CPU** | 2 Cores | **4 Cores+** | La orquestación y el levantamiento simultáneo de contenedores requiere potencia. |
| **Espacio** | 10 GB | **20 GB** | Imágenes Docker de múltiples lenguajes (PHP, Go, Rust, etc.). |

## Software Necesario

### Obligatorio
1.  **Docker Desktop (o Engine + Compose)**
    -   Versión: 24.0+
    -   *Nota*: En Windows, se recomienda usar WSL 2 backend para mejor rendimiento.
2.  **Python 3.10+**
    -   Necesario para el CLI `hub.py` y los scripts de los bots.
3.  **Git**
    -   Para clonar el repositorio.

### Opcional (Pero útil)
-   **Make**: Si deseas usar el `Makefile` en lugar de los scripts directos.
-   **VS Code**: Con extensiones recomendadas (Docker, Python).

## ⚙️ Configuración Automática

**n8n se auto-configura al arrancar** con Docker Compose:
-   Los 8 workflows se importan y activan automáticamente
-   Se crea un usuario admin de laboratorio: `admin@social-bot.local` / `SocialBot2026!`
-   No se requiere configuración manual en la UI de n8n

## Notas de Rendimiento
-   Si tienes poca RAM, intenta levantar solo los casos que necesitas (ej. `docker-compose up -d n8n dest-php` en lugar de todo).
-   El primer despliegue ("pull" de imágenes) puede tardar 10-20 minutos dependiendo de tu internet.
-   La primera vez que arranca n8n, la auto-configuración tarda ~30 segundos adicionales.

