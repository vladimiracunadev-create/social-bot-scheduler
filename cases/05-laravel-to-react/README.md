# 🧩 Caso 05: 🐘 Laravel -> 🌉 n8n -> ⚛️ React

[![Language: PHP/Laravel](https://img.shields.io/badge/Language-Laravel-FF2D20?logo=laravel&logoColor=white)](https://laravel.com/)
[![Language: React](https://img.shields.io/badge/Language-React-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![Database: MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)

Este eje tecnológico demuestra la convergencia entre el backend empresarial tradicional (**Laravel**) y el desarrollo de interfaces de usuario modernas y reactivas (**React**).

---

## 🏗️ Arquitectura del Flujo

1.  **📤 Origen**: `ArtisanPost.php` (PHP 8.2 / Simulación Artisan)
2.  **🌉 Puente**: **n8n** (Webhook e Inyección HTTP)
3.  **📥 Destino**: `server.js` (Node.js) + **React SPA**
4.  **📁 Persistencia**: **MongoDB 6.0**

---

## 🐘 Origen: Laravel Artisan Simulator

El origen simula cómo un framework de gran escala gestionaría tareas programadas:
- **Lógica**: Utiliza una clase que imita un `Console Command`. Extrae publicaciones pendientes de `posts.json` y las despacha.
- **Tecnología**: Implementación de **PHP Streams** para envíos HTTP eficientes y ligeros.

> [!TIP]
> Para activar este entorno en el laboratorio:
> ```bash
> docker-compose --profile case05 up -d
> ```

---

## ⚛️ Destino: React & Node Fullstack Receptor

El receptor es un entorno de JavaScript moderno diseñado para la interacción en tiempo real:
- **Backend (Node/Express)**: Recibe el post, lo valida y lo persiste en **MongoDB**.
- **Frontend (React)**: Una **Single Page Application (SPA)** que visualiza los posts con una estética profesional y actualizaciones periódicas.
- **Interoperabilidad**: Muestra cómo n8n puede alimentar directamente flujos de datos hacia interfaces dinámicas.

---

## 🛡️ Guardrails (Resiliencia)

Este caso implementa protecciones para asegurar la disponibilidad de la interfaz:

- **🔄 Reintentos Automáticos**: n8n reintenta el envío hasta 3 veces con backoff exponencial ante fallos del servidor Node.
- **📥 Dead Letter Queue (DLQ)**: Los fallos críticos de entrega se registran para auditoría, permitiendo la recuperación de datos no visualizados.
- **🔍 Integridad Documental**: MongoDB asegura que la estructura semi-estructurada de los posts se preserve correctamente.

---

## 🚦 Verificación y Acceso

- **🌐 Dashboard**: [http://localhost:8085](http://localhost:8085)
- **⚙️ API Endpoint**: `POST /webhook`
- **📁 Datos**: Visibles a través de la interfaz SPA de React.

---

*Desarrollado como parte del Social Bot Scheduler v4.0*
