# 🌟 Guía para Principiantes: Social Bot Scheduler

¡Bienvenido! Si eres nuevo en este repositorio, no te preocupes. Esta guía está diseñada para explicarte **qué está pasando aquí**, por qué usamos tantos lenguajes diferentes y cómo este sistema te ayuda a ser un maestro de la automatización.

---

## 🤔 ¿Qué es esto y para qué sirve?

El **Social Bot Scheduler** es como un "director de orquesta" para tus redes sociales. Su trabajo es tomar mensajes que tú has escrito, esperar al momento exacto en que deben publicarse, y enviarlos a través de internet para que aparezcan en tus canales favoritos.

### ¿A qué ayuda?
1.  **Ahorro de tiempo**: Escribe todos tus posts una vez al mes y deja que el bot trabaje por ti.
2.  **Organización**: Mantén un registro claro de qué has publicado y qué falta por salir.
3.  **Flexibilidad**: Puedes enviar un mismo mensaje a Twitter, Telegram o Slack al mismo tiempo.

---

## 🏗️ La "Triada" Tecnológica (Python, n8n y PHP)

En este proyecto verás tres piezas moviéndose juntas. Puede parecer complicado, pero cada una tiene un "superpoder" específico:

### 1. 🐍 Python (El Cerebro Programador)
- **¿Qué es?**: Es el lenguaje que maneja la lógica.
- **¿Qué hace aquí?**: Lee el archivo `posts.json` (donde están tus mensajes), revisa el reloj y decide: *"¡Oye, ya es hora de enviar este post!"*.
- **¿Por qué Python?**: Porque es excelente manejando calendarios, datos y procesos en segundo plano.

### 2. 🔗 n8n (El Puente de Automatización)
- **¿Qué es?**: Es una herramienta visual de automatización (como un LEGO para internet).
- **¿Qué hace aquí?**: Recibe el mensaje que le envía Python y lo "reparte". Si Python dice "Publica esto", n8n se encarga de hablar con las APIs de Facebook, Instagram o X.
- **¿Por qué n8n?**: Porque conectar una red social a mano es difícil. n8n lo hace fácil con sus "nodos" visuales.

### 3. 🐘 PHP (El Receptor / API)
- **¿Qué es?**: Un lenguaje clásico de la web.
- **¿Qué hace aquí?**: Actúa como un "buzón de entrada". En este proyecto, tenemos un script PHP que recibe los datos finales, los guarda en un log y confirma que todo llegó bien.
- **¿Por qué PHP?**: Muchos servidores web ya tienen PHP instalado. Es la forma más rápida y universal de crear un "punto de recepción" (API) que cualquier servidor pueda entender.

---

## 🔄 El Flujo de Trabajo (Paso a Paso)

1.  **Tú escribes**: Pones tus posts en el archivo `posts.json`.
2.  **Python detecta**: El script de Python ve que ya es la hora señalada.
3.  **Envío al Puente**: Python le "lanza" el mensaje a **n8n**.
4.  **n8n procesa**: n8n decide a qué canales enviarlo (vía el flujo de trabajo en `n8n/social-bot.json`).
5.  **PHP confirma**: Al final del camino, el receptor en **PHP** guarda el registro de que el post fue enviado con éxito.

---

## 🚀 ¿Cómo lo hago funcionar?

Para que no tengas que instalar cada cosa por separado, usamos **Docker**. Imagina que Docker es una caja donde ya viene todo instalado y configurado.

1.  Asegúrate de tener **Docker Desktop** instalado.
2.  Ejecuta el comando mágico:
    ```bash
    docker-compose up -d
    ```
3.  ¡Listo! El cerebro (Python), el puente (n8n) y el receptor (PHP) estarán hablando entre ellos automáticamente.

---
> [!TIP]
> Si quieres ver qué está haciendo el bot en tiempo real, usa el comando `make logs`.
