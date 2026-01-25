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
