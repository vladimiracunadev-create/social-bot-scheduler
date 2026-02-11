# Caso 02: 🐍 Python -> 🔗 n8n -> 🐹 Go

Este eje tecnológico integra la facilidad de scripting de Python con la eficiencia de un binario compilado en Go.

## 🏗️ Arquitectura del Flujo
1.  **Origen (Emisor)**: `bot.py` (Python 3.11) - Utiliza el bus de eventos común de Python.
2.  **Puente (Orquestador)**: n8n (Nodo Webhook -> Nodo HTTP Request)
3.  **Destino (Receptor)**: `main.go` (Compilado en imagen Alpine)

## 🐍 Funcionamiento: Origen (Python)
El bot comparte la lógica base del Caso 01:
- **Lógica**: Detecta posts programados en su `posts.json` local.
- **Envío**: Despacha a n8n vía el webhook específico para Go.

## 🐹 Funcionamiento: Destino (Go)
El receptor Go destaca por su baja latencia y huella de memoria:
- **Tecnología**: Servidor HTTP nativo de Go (`net/http`).
- **Concurrent-Safe**: Utiliza `sync.Mutex` para garantizar que las escrituras en el log sean seguras entre múltiples hilos.
- **Log**: Almacena en `social_bot_go.log` dentro del contenedor.
- **Dashboard**: Un servidor simple sirve el archivo `index.html` estático que visualiza los posts recibidos.

## 🛡️ Guardrails Implementados

Este caso incluye mecanismos de resiliencia en la capa de n8n:

### Reintentos Automáticos
- El nodo HTTP Request está configurado con **3 reintentos** (backoff de 1 segundo).
- Si el servicio Go está caído, n8n intentará 3 veces antes de marcar el envío como fallido.

### Dead Letter Queue (DLQ)
- Si todos los reintentos fallan, el payload se envía a un endpoint `/errors` del servicio Go.
- Los errores se registran con timestamp, caso, error y payload completo.

Para más detalles, consulta la guía de [Guardrails](../../docs/GUARDRAILS.md).

## 🚦 Verificación
- **URL Dashboard**: [http://localhost:8082](http://localhost:8082)
- **Endpoint Webhook**: `POST /webhook` (Interno: 8080)
