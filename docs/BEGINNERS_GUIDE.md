# 🌟 Guía para Principiantes: El Universo Social Bot

¡Bienvenido! Estás ante un proyecto único. A diferencia de otros bots, este es un **laboratorio de automatización**. Aquí aprenderás cómo diferentes lenguajes de programación pueden hablar entre sí usando un "puente" llamado **n8n**.

---

## 👋 ¿Qué es un "Caso Technològico"?

Hemos creado **6 formas diferentes** de hacer lo mismo. Imagina que quieres ir de un punto A a un punto B. Puedes ir en coche, en bici o en avión. 

En este proyecto:
- **Punto A (Origen)**: El programa que envía tus mensajes.
- **n8n (El Puente)**: El cartero que reparte tus mensajes a las redes sociales.
- **Punto B (Destino)**: La pantalla donde ves que el mensaje llegó bien.

Cada "Caso" usa un vehículo diferente (Python, Go, Node, etc.). ¡Tú eliges cuál quieres probar!

---

## 🛠️ ¿Cómo empiezo? (Sin miedo)

No necesitas ser un experto. Sigue estos 3 pasos:

1.  **Ejecuta el Asistente**: Abre tu terminal y escribe:
    ```bash
    python setup.py
    ```
    Elige el número del caso que te dé curiosidad (recomendamos el 1 para empezar).

2.  **Levanta la Infraestructura**: El asistente te dirá un comando de Docker. Escríbelo. Por ejemplo:
    ```bash
    docker-compose up -d n8n dest-php
    ```

3.  **Mira la Magia**: Abre tu navegador en la dirección que el asistente te dio (ej. `http://localhost:8081`). Verás un tablero vacío esperando tus mensajes.

---

## 🧩 ¿Por qué tantos lenguajes?

¡Para que aprendas! 
- **Python** es genial por su sencillez.
- **Go** es ultra-rápido.
- **Node.js** es lo que usa la mayoría de la web actual.
- **Laravel/Symfony** son como los "tanques" blindados de las empresas.

¡Diviértete explorando la interacción entre todos ellos! 🚀
