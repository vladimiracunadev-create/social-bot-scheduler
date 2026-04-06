# 🧩 Caso 01: 🐍 Python -> 🌉 n8n -> 🐘 PHP

[![Language: Python](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Language: PHP](https://img.shields.io/badge/Language-PHP-777BB4?logo=php&logoColor=white)](https://www.php.net/)
[![Database: MySQL](https://img.shields.io/badge/Database-MySQL-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)

Este eje tecnológico demuestra la integración fluida entre un script de automatización moderno en **Python** y un receptor web tradicional en **PHP**, orquestados por la potencia de **n8n**.

---

## 🏗️ Arquitectura del Flujo

1.  **📤 Origen**: `bot.py` (Python 3.11 + Pydantic)
2.  **🌉 Puente**: **n8n** (Webhook e Inyección HTTP)
3.  **📥 Destino**: `index.php` (Apache 2.4 + PHP 8.2)
4.  **📁 Persistencia**: **MySQL 8.0**

---

## 🐍 Origen: Python Local Bot

El bot de Python actúa como el cerebro programador del flujo:
- **Lógica**: Lee `posts.json`, valida la estructura con **Pydantic** y dispara hacia n8n.
- **Resiliencia**: Manejo de errores en el envío y logs locales de ejecución.

> [!TIP]
> Para ejecutar este caso de forma aislada:
> ```bash
> docker-compose --profile case01 up -d
> ```

---

## 🐘 Destino: PHP Collector

Un script PHP optimizado para recibir y persistir datos de auditoría:
- **Lógica**: Valida los campos `id`, `text` y `channel`.
- **Motor**: Almacena los resultados en una base de datos **MySQL**.
- **Visualización**: El Dashboard maestro (`:8081`) consulta esta persistencia en tiempo real.

---

## 🛡️ Guardrails (Resiliencia)

Este caso implementa patrones robustos para evitar la pérdida de datos:

- **🔄 Reintentos**: n8n realiza hasta 3 reintentos automáticos con backoff exponencial.
- **📥 DLQ (Dead Letter Queue)**: Si el destino falla tras los reintentos, el mensaje se deriva a una tabla de errores para inspección.
- **✅ Idempotencia**: El sistema verifica el `post_hash` para evitar publicaciones duplicadas.

---

## 🚦 Verificación y Acceso

- **🌐 Dashboard**: [http://localhost:8081](http://localhost:8081)
- **⚙️ API Endpoint**: `POST /index.php`
- **📂 Logs**: Mapeados en el volumen `dest/logs/`

---

*Desarrollado como parte del Social Bot Scheduler v4.0*

