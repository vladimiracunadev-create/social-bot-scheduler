# Caso 01: 🐍 Python -> 🔗 n8n -> 🐘 PHP

Este eje tecnológico demuestra la integración entre un script de automatización en Python y un servidor web tradicional en PHP, orquestados por n8n.

## 🏗️ Arquitectura del Flujo
1.  **Origen (Emisor)**: `bot.py` (Python 3.11)
2.  **Puente (Orquestador)**: n8n (Nodo Webhook -> Nodo HTTP Request)
3.  **Destino (Receptor)**: `webhook.php` (Apache/PHP 8.2)

## 🐍 Funcionamiento: Origen (Python)
El bot de Python actúa como un scheduler local:
- **Lógica**: Carga posts desde `posts.json`, verifica si es el momento de publicarlos y los envía al webhook de n8n.
- **Tecnologías**: 
    - `pydantic`: Para validación de datos.
    - `requests`: Para el envío HTTP POST.
    - `dotenv`: Gestión de variables de entorno (URL del webhook).
- **Ejecución**: Se corre con `python bot.py` desde la carpeta `origin/`.

## 🐘 Funcionamiento: Destino (PHP)
El receptor es un script PHP ligero que actúa como verificador:
- **Lógica**: Recibe el POST de n8n, valida que los campos `id`, `text` y `channel` existan, y los guarda en un archivo de texto plano.
- **Log**: Los posts se almacenan en `dest/logs/social_bot.log`.
- **Dashboard**: `index.html` lee los logs vía AJAX para mostrarlos visualmente.

## 🚦 Verificación
- **URL Dashboard**: [http://localhost:8081](http://localhost:8081)
- **Endpoint Webhook**: `POST /webhook.php`
