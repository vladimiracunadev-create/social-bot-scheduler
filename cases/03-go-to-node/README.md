# 🧩 Caso 03: 🐹 Go -> 🌉 n8n -> 🟢 Node.js

[![Language: Go](https://img.shields.io/badge/Language-Go-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Language: Node.js](https://img.shields.io/badge/Language-Node.js-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Database: PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

Este eje tecnológico muestra la potencia de un emisor concurrente escrito en **Go** comunicándose con un ecosistema flexible y asíncrono basado en **Node.js (Express)**.

---

## 🏗️ Arquitectura del Flujo

1.  **📤 Origen**: `main.go` (Go 1.21) - Scheduler de alta concurrencia.
2.  **🌉 Puente**: **n8n** (Webhook e Inyección HTTP)
3.  **📥 Destino**: `index.js` (Node.js 20 + Express)
4.  **📁 Persistencia**: **PostgreSQL 15**

---

## 🐹 Origen: Go Concurrent Scheduler

El emisor en Go está diseñado para la máxima eficiencia y velocidad:
- **Lógica**: Utiliza goroutines para el escaneo de `posts.json` y despacho inmediato.
- **Tecnologías**: Cliente HTTP nativo de Go sin dependencias externas pesadas.

> [!TIP]
> Para activar este flujo en el laboratorio:
> ```bash
> docker-compose --profile case03 up -d
> ```

---

## 🟢 Destino: Node.js Express Receptor

El receptor utiliza Express para gestionar eventos con la flexibilidad característica de Node:
- **Tecnología**: Servidor Express con optimización de JSON parsing.
- **Base de Datos**: Persistencia relacional avanzada en **PostgreSQL**.
- **Dashboard**: Interfaz dinámica en el puerto `:8083` con recarga automática de datos.

---

## 🛡️ Guardrails (Resiliencia)

Este caso implementa defensas contra fallos en cascada:

- **🔄 Reintentos Automáticos**: n8n aplica una política de 3 reintentos con intervalo de 1s.
- **📥 Dead Letter Queue (DLQ)**: Los eventos que fallan tras los reintentos se registran en una tabla de auditoría para recuperación manual.
- **🔍 Validación de Schema**: El receptor Node valida rigurosamente el payload antes de la inserción en el PGSQL.

---

## 🚦 Verificación y Acceso

- **🌐 Dashboard**: [http://localhost:8083](http://localhost:8083)
- **⚙️ API Endpoint**: `POST /webhook`
- **📂 Persistencia**: Accesible vía herramientas estándar de PostgreSQL.

---

*Desarrollado como parte del Social Bot Scheduler v4.0*

