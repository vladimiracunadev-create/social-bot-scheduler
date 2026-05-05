# 📖 Manual de Usuario

El **Social Bot Scheduler** lee las publicaciones desde un archivo JSON local. Esta guía explica cómo gestionar ese contenido.

## Estructura de `posts.json`
El archivo debe contener una lista de objetos con el siguiente formato:

```json
[
  {
    "id": "p001",
    "text": "Este es mi primer mensaje programado",
    "channels": ["twitter", "linkedin"],
    "scheduled_at": "2026-01-25T18:00:00",
    "published": false
  }
]
```

### Campos:
- **id**: Identificador único para el post.
- **text**: El contenido del mensaje.
- **channels**: Un array de redes sociales o canales donde n8n enviará el post.
- **scheduled_at**: Fecha y hora en formato ISO 8601. Solo se enviarán los posts cuya fecha sea igual o anterior a la hora actual de ejecución del bot.
- **published**: (Booleano) El bot cambia automáticamente este valor a `true` una vez enviado el post exitosamente, evitando duplicados.

## Modo de Operación
El bot funciona en modo "batch":
1. Lee `posts.json`.
2. Filtra los posts pendientes (no publicados y con fecha vencida).
3. Envía cada post al webhook configurado.
4. Actualiza el archivo `posts.json` marcando los posts como `published: true`.
5. Finaliza su ejecución.

Para un funcionamiento continuo, se recomienda programar su ejecución mediante un **CronJob** de Kubernetes (incluido en `k8s/cronjob.yaml`) o un cron local.

## Integración con n8n
El payload enviado al webhook tiene la misma estructura que el objeto del JSON. En n8n, registra un nodo "Webhook" de tipo POST y usa los datos para distribuirlos a tus nodos sociales.

## 🎛️ Master Dashboard (v4.3.0)

`http://localhost:8080` es la entrada visual al laboratorio. A partir de v4.3.0:

- Cada caso muestra **estado en vivo** (`READY` / `OFFLINE`) detectado por el navegador cada 20 s.
- Si un caso está apagado, el botón **"Probar Integración"** se transforma en **"⚙️ Mostrar comando para levantarlo"** y abre un modal con:
  - El comando exacto: `docker-compose --profile caseXX up -d`
  - La **RAM estimada** que consumirá (núcleo + caso)
  - Un botón **📋 Copiar** al portapapeles
- La **barra Docker** en la cabecera resume cuántos casos están READY/OFFLINE/PLANNED y el `Última comprobación: HH:MM:SS`.
- El botón **🔄 Re-comprobar** permite forzar un ciclo manual sin esperar al intervalo.

> El dashboard nunca ejecuta `docker` por ti — sólo te muestra el comando exacto. Mantiene la postura "Hardened" (sin backend privilegiado).
