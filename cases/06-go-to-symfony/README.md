# Caso 06: 🐹 Go -> 🔗 n8n -> 🐘 Symfony

Este eje tecnológico muestra la integración entre un emisor de alta velocidad en Go y un potente backend empresarial basado en Symfony.

## 🏗️ Arquitectura del Flujo
1.  **Origen (Emisor)**: `main.go` (Go 1.21)
2.  **Puente (Orquestador)**: n8n (Nodo Webhook -> Nodo HTTP Request)
3.  **Destino (Receptor)**: `index.php` (Symfony 7 / PHP 8.2)

## 🐹 Funcionamiento: Origen (Go)
El emisor en Go gestiona el ciclo de vida de los posts:
- **Lógica**: Carga un `posts.json`, calcula los tiempos de envío y dispara las peticiones HTTP concurrentemente.
- **Eficiencia**: Diseñado para consumir menos de 20MB de RAM durante la ejecución.

## 🐘 Funcionamiento: Destino (Symfony)
El receptor utiliza un controlador estandarizado de Symfony:
- **Tecnología**: Symfony Lite (simulación de controlador productivo).
- **Procesamiento**: Recibe el POST en `/index.php`, parsea el JSON y añade la entrada a `symfony.log`.

- **Dashboard**: El mismo controlador sirve una interfaz de administración empresarial para monitorizar el estado de los posts recibidos.


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
- **URL Dashboard**: [http://localhost:8086](http://localhost:8086)
- **Endpoint Webhook**: `POST /index.php` (Interno: 80)
