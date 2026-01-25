# Caso 04: 🍏 Node.js -> 🔗 n8n -> 🐍 FastAPI

Este eje tecnológico muestra la integración entre un ecosistema de JavaScript asíncrono y un servidor de alto rendimiento en Python utilizando FastAPI.

## 🏗️ Arquitectura del Flujo
1.  **Origen (Emisor)**: `index.js` (Node.js 20) - Utiliza promesas para el envío asíncrono.
2.  **Puente (Orquestador)**: n8n (Nodo Webhook -> Nodo HTTP Request)
3.  **Destino (Receptor)**: `main.py` (FastAPI / Uvicorn)

## 🍏 Funcionamiento: Origen (Node.js)
El emisor en Node.js está optimizado para operaciones de E/S no bloqueantes:
- **Lógica**: Carga un `posts.json`, itera sobre las publicaciones pendientes y las envía usando un cliente HTTP moderno.
- **Tecnologías**: 
    - `axios`: Cliente HTTP basado en promesas.
    - `promise-based logic`: Gestión eficiente de flujos de envío.
- **Ejecución**: Se corre con `node index.js` desde la carpeta `origin/`.

## 🐍 Funcionamiento: Destino (FastAPI)
El receptor aprovecha las ventajas de los tipos de Python modernos:
- **Tecnología**: Framework FastAPI con servidor ASGI (Uvicorn).
- **Validación**: Utiliza modelos de `pydantic` para asegurar que el contenido recibido cumpla con el esquema `id`, `text` y `channel`.
- **Log**: Almacena en `social_bot_fastapi.log`.
- **Dashboard**: Sirve el dashboard vía `HTMLResponse` en el puerto `8000`.

## 🚦 Verificación
- **URL Dashboard**: [http://localhost:8084](http://localhost:8084)
- **Endpoint Webhook**: `POST /webhook` (Interno: 8000)
