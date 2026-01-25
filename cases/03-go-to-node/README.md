# Caso 03: 🐹 Go -> 🔗 n8n -> 🍏 Node.js

Este eje tecnológico muestra la potencia de un emisor de alto rendimiento escrito en Go comunicándose con un ecosistema flexible basado en Node.js.

## 🏗️ Arquitectura del Flujo
1.  **Origen (Emisor)**: `main.go` (Go 1.21) - Scheduler de alta concurrencia.
2.  **Puente (Orquestador)**: n8n (Nodo Webhook -> Nodo HTTP Request)
3.  **Destino (Receptor)**: `index.js` (Node.js 20 - Express)

## 🐹 Funcionamiento: Origen (Go)
El emisor en Go está diseñado para ser ligero y rápido:
- **Lógica**: Lee un archivo `posts.json`, parsea las fechas y despacha los posts al webhook de n8n cuando llega el momento.
- **Tecnologías**: 
    - `net/http`: Cliente HTTP estándar.
    - `encoding/json`: Para el manejo nativo de datos estructurados.
- **Ejecución**: Se compila y ejecuta automáticamente, o manualmente con `go run main.go` desde `origin/`.

## 🍏 Funcionamiento: Destino (Node.js)
El receptor utiliza Express para gestionar las peticiones entrantes:
- **Tecnología**: Servidor Express con middleware `json` y `urlencoded`.
- **Log**: Los posts se añaden a `social_bot_node.log` en formato legible.
- **Dashboard**: Sirve una interfaz moderna en el puerto `3000` que permite "refrescar" y ver los posts recibidos en tiempo real.

## 🚦 Verificación
- **URL Dashboard**: [http://localhost:8083](http://localhost:8083)
- **Endpoint Webhook**: `POST /webhook` (Interno: 3000)
