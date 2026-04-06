# 🧩 Caso 04: 🟢 Node.js -> 🌉 n8n -> ⚡ FastAPI

[![Language: Node.js](https://img.shields.io/badge/Language-Node.js-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Language: Python](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Database: SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)

Este eje tecnológico muestra la integración entre un ecosistema de **JavaScript asíncrono** y un servidor de alto rendimiento en **Python** utilizando **FastAPI**.

---

## 🏗️ Arquitectura del Flujo

1.  **📤 Origen**: `index.js` (Node.js 20) - Utiliza promesas para el envío asíncrono.
2.  **🌉 Puente**: **n8n** (Webhook e Inyección HTTP)
3.  **📥 Destino**: `main.py` (FastAPI + Uvicorn)
4.  **📁 Persistencia**: **SQLite** (Embebido)

---

## 🟢 Origen: Node.js Async Dispatcher

El emisor en Node.js está optimizado para operaciones de E/S no bloqueantes:
- **Lógica**: Carga `posts.json`, itera sobre las publicaciones pendientes y las envía usando **Axios**.
- **Tecnología**: Cliente HTTP basado en promesas para gestión eficiente de flujos.

> [!TIP]
> Para ejecutar este caso en el entorno local:
> ```bash
> docker-compose --profile case04 up -d
> ```

---

## ⚡ Destino: FastAPI High-Performance Receptor

El receptor aprovecha las ventajas de los tipos de Python modernos y la validación automática:
- **Tecnología**: Framework **FastAPI** con servidor ASGI (**Uvicorn**).
- **Validación**: Utiliza modelos de **Pydantic** para asegurar la integridad de los datos recibidos.
- **Base de Datos**: Persistencia ágil en un archivo **SQLite** local.

---

## 🛡️ Guardrails (Resiliencia)

Este caso implementa defensas contra fallos en la comunicación:

- **🔄 Reintentos Automáticos**: n8n aplica una política de 3 reintentos con intervalo de 1s ante errores temporales.
- **📥 Dead Letter Queue (DLQ)**: Los eventos fallidos se registran en un endpoint de auditoría de errores para su posterior análisis.
- **🔍 Tipado Estricto**: FastAPI garantiza que solo los datos con el formato correcto lleguen a la base de datos.

---

## 🚦 Verificación y Acceso

- **🌐 Dashboard**: [http://localhost:8084](http://localhost:8084)
- **⚙️ API Endpoint**: `POST /webhook`
- **📂 Datos**: Almacenados en `social_bot.db` dentro del volumen del caso.

---

*Desarrollado como parte del Social Bot Scheduler v4.0*
