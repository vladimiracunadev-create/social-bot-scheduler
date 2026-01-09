# Social Bot Scheduler (Python + n8n + PHP)

Proyecto de ejemplo/portafolio que muestra un flujo completo de automatización:

- **Python** decide qué publicaciones están listas para salir (scheduler).
- **n8n** recibe las publicaciones por Webhook y las separa según el canal.
- **PHP** actúa como API interna que recibe cada publicación y la registra en un log (o en el futuro, en base de datos, correo, etc.).

El objetivo es tener un **bot de publicaciones** modular, donde la lógica de “cuándo y qué publicar” esté separada de la lógica de “qué hacer con la publicación” (guardar, enviar a redes, etc.).

---

## Arquitectura general

Flujo básico:

1. **Archivo `posts.json`** contiene una lista de publicaciones planificadas:
   - `id`
   - `text`
   - `channels` (ej. `["linkedin", "twitter"]`)
   - `scheduled_at` (fecha/hora programada)

2. **Script Python `bot.py`**:
   - Carga `posts.json`.
   - Compara la fecha/hora de cada post con la hora actual.
   - Para cada publicación “vencida” (que ya debería publicarse) envía un JSON a un **Webhook de n8n** (`/webhook/social-bot`).

3. **Workflow en n8n**:
   - Recibe el JSON en un nodo **Webhook**.
   - Lo pasa por un nodo **Function** que genera un item por cada canal (linkedin, twitter, etc.).
   - Para cada canal, hace un `POST` hacia la API PHP.

4. **API PHP `social_bot_receiver.php`**:
   - Recibe `id`, `text`, `channel`, `scheduled_at`.
   - Valida los datos.
   - Registra cada publicación en un archivo de log (`logs/social_bot.log`).
   - Devuelve una respuesta JSON simple (`ok: true/false`).

De esta forma, el sistema es fácilmente extensible:
- Se puede reemplazar la parte PHP por inserción en MySQL.
- Se pueden agregar nodos en n8n para publicar en redes sociales reales.
- Se pueden agregar reglas más complejas en el scheduler Python.

---

## Requisitos

- **Python 3.x** instalado (con `pip`).
- **PHP** 5.4 o superior (por ejemplo XAMPP, WAMP o un Apache+PHP ya configurado).
- **Servidor web local** accesible en algo como `http://localhost/...` para servir `social_bot_receiver.php`.
- **n8n** funcionando (local o en servidor).  
  Ejemplo: `http://localhost:5678/`
- **Git** (opcional, pero recomendado para versionado del proyecto).

---

## Estructura de archivos recomendada

```

---

## Documentación del proyecto

- `LICENSE` — Licencia MIT (2026) — **maintainer@example.com**
- `NOTICE` — Información de créditos y avisos
- `CONTRIBUTING.md` — Guía para contribuir y normas
- `SECURITY.md` — Cómo reportar vulnerabilidades
- `ROADMAP.md` — Hoja de ruta del proyecto

> Si prefieres otra licencia o quieres que use un contacto distinto, indícalo y lo actualizo.
text
social-bot-scheduler/
├─ bot.py
├─ posts.json
├─ requirements.txt
├─ .env.example
├─ README.md
├─ social_bot_receiver.php
├─ n8n_workflow_social_bot_php.json   (opcional, export del workflow)
├─ .gitignore
└─ logs/                              (se crea automáticamente al recibir posts)
