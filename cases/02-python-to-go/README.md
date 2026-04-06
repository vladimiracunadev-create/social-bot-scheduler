# 🧩 Caso 02: 🐍 Python -> 🌉 n8n -> 🐹 Go

[![Language: Python](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Language: Go](https://img.shields.io/badge/Language-Go-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Database: MariaDB](https://img.shields.io/badge/Database-MariaDB-003545?logo=mariadb&logoColor=white)](https://mariadb.org/)

Este eje tecnológico integra la versatilidad de **Python** para el scripting de automatización con la extrema eficiencia de un receptor compilado en **Go**, enfocado en baja latencia.

---

## 🏗️ Arquitectura del Flujo

1.  **📤 Origen**: `bot.py` (Python 3.11 + Pydantic)
2.  **🌉 Puente**: **n8n** (Orquestación de Eventos)
3.  **📥 Destino**: `main.go` (Compilado en Go 1.21 / Alpine 3.20)
4.  **📁 Persistencia**: **MariaDB 10.11**

---

## 🐍 Origen: Python Event Bus

El bot utiliza el motor de eventos común para detectar y despachar publicaciones programadas:
- **Lógica**: Carga `posts.json` y valida cada entrada antes del envío.
- **Webhook**: Dirigido específicamente al flujo de n8n para receptores Go.

> [!TIP]
> Para levantar este entorno de prueba:
> ```bash
> docker-compose --profile case02 up -d
> ```

---

## 🐹 Destino: Go High-Performance Receptor

El receptor Go destaca por su concurrencia segura y mínima huella de memoria:
- **Tecnología**: Servidor HTTP nativo de Go optimizado.
- **Seguridad de Hilo**: Implementa `sync.Mutex` para garantizar integridad en escrituras concurrentes.
- **Base de Datos**: Persistencia robusta en **MariaDB**.

---

## 🛡️ Guardrails (Resiliencia)

Este caso aprovecha los patrones de n8n para asegurar la entrega:

- **🔄 Reintentos Automáticos**: Hasta 3 intentos ante fallos de red o saturación del servicio Go.
- **📥 Dead Letter Queue (DLQ)**: Si el binario Go no responde, el mensaje se guarda en una cola de errores con el payload original.
- **⚡ Baja Latencia**: Diseñado para procesar ráfagas de eventos sin degradación del servicio.

---

## 🚦 Verificación y Acceso

- **🌐 Dashboard**: [http://localhost:8082](http://localhost:8082)
- **⚙️ API Endpoint**: `POST /webhook`
- **📁 Salud del Binario**: Verificable vía logs internos de Docker.

---

*Desarrollado como parte del Social Bot Scheduler v4.0*

