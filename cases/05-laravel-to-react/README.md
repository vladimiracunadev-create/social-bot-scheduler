# Caso 05: 🐘 Laravel -> 🔗 n8n -> ⚛️ React

Este eje tecnológico demuestra la convergencia entre el backend empresarial tradicional (Laravel) y el desarrollo de interfaces modernas de usuario (React).

## 🏗️ Arquitectura del Flujo
1.  **Origen (Emisor)**: `ArtisanPost.php` (PHP 8.2 / Simulación Artisan)
2.  **Puente (Orquestador)**: n8n (Nodo Webhook -> Nodo HTTP Request)
3.  **Destino (Receptor)**: `server.js` (Node.js) + `App.jsx` (React)

## 🐘 Funcionamiento: Origen (Laravel)
El origen simula cómo un framework de gran escala como Laravel gestionaría publicaciones:
- **Lógica**: Utiliza una clase que imita un `Console Command`. Recorre un archivo `posts.json`, extrae los pendientes y los despacha.
- **Tecnologías**: 
    - `PHP Streams`: Envío HTTP nativo sin dependencias externas pesadas.
    - `JSON Formatting`: Preservación de la estructura del post original.
- **Ejecución**: Se corre con `php ArtisanPost.php` desde la carpeta `origin/`.

## ⚛️ Funcionamiento: Destino (React)
El receptor es un entorno fullstack de JavaScript:
- **Backend (Node/Express)**: Recibe el post en `/webhook`, lo valida y lo persiste en `posts_react.log`.
- **Frontend (React)**: Una Single Page Application (SPA) que consulta periódicamente los logs al backend y los muestra con una estética moderna.
- **Interoperabilidad**: Demuestra cómo n8n puede alimentar directamente interfaces interactivas de usuario.

## 🚦 Verificación
- **URL Dashboard**: [http://localhost:8085](http://localhost:8085)
- **Endpoint Webhook**: `POST /webhook` (Interno: 4000)
