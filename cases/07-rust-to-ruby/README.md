# Caso 07: 🦀 Rust -> 🔗 n8n -> 💎 Ruby

Este eje tecnológico combina la robustez y rendimiento de Rust con la elegancia sintáctica de Ruby a través del orquestador n8n.

## 🏗️ Arquitectura del Flujo
1.  **Origen (Emisor)**: `main.rs` (Rust 1.7x) - Utiliza serialización fuertemente tipada.
2.  **Puente (Orquestador)**: n8n (Nodo Webhook -> Nodo HTTP Request)
3.  **Destino (Receptor)**: `app.rb` (Ruby 3.2 / Sinatra)

## 🦀 Funcionamiento: Origen (Rust)
El emisor en Rust garantiza la integridad de los datos antes del envío:
- **Lógica**: Utiliza estructuras (`structs`) para definir el esquema del post. Un bucle infinito envía datos de prueba simulando un flujo de producción.
- **Tecnologías**: 
    - `serde`: Serialización/Deserialización ultra rápida de JSON.
    - `reqwest`: Cliente HTTP asíncrono/bloqueante para Rust.
- **Ejecución**: Se corre con `cargo run` desde la carpeta `origin/`.

## 💎 Funcionamiento: Destino (Ruby)
El receptor utiliza Sinatra, un micro-framework web DSL para Ruby:
- **Tecnología**: Sinatra + Puma (servidor web).
- **Almacenamiento**: Mantiene una lista circular de los últimos 20 posts en una variable global de memoria.
- **Dashboard**: Utiliza plantillas ERB para generar el dashboard visual en el puerto `4567`.


## 🛡️ Guardrails Implementados

Este caso incluye mecanismos de resiliencia en la capa de n8n:

### Reintentos Automáticos
- El nodo HTTP Request está configurado con **3 reintentos** (backoff de 1 segundo).
- Si el servicio de destino está caído, n8n intentará 3 veces antes de marcar el envío como fallido.

### Dead Letter Queue (DLQ)
- Si todos los reintentos fallan, el payload se envía a un endpoint `/errors` del servicio de destino.
- Los errores se registran con timestamp, caso, error y payload completo.

Para más detalles, consulta la guía de [Guardrails](../../docs/GUARDRAILS.md).

## 🚦 Verificación
- **URL Dashboard**: [http://localhost:8087](http://localhost:8087)
- **Endpoint Webhook**: `POST /webhook` (Interno: 4567)
