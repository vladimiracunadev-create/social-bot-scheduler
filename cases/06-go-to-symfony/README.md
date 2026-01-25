# Caso 06: 🐹 Go -> 🔗 n8n -> 🐘 Symfony

Este eje tecnológico muestra la integración entre un emisor de alta velocidad en Go y un potente backend empresarial basado en Symfony.

## 🏗️ Arquitectura del Flujo
1.  **Origen (Emisor)**: `main.go` (Go 1.21)
2.  **Puente (Orquestador)**: n8n (Nodo Webhook -> Nodo HTTP Request)
3.  **Destino (Receptor)**: `webhook.php` (Symfony 7 / PHP 8.2)

## 🐹 Funcionamiento: Origen (Go)
El emisor en Go gestiona el ciclo de vida de los posts:
- **Lógica**: Carga un `posts.json`, calcula los tiempos de envío y dispara las peticiones HTTP concurrentemente.
- **Eficiencia**: Diseñado para consumir menos de 20MB de RAM durante la ejecución.

## 🐘 Funcionamiento: Destino (Symfony)
El receptor utiliza un controlador estandarizado de Symfony:
- **Tecnología**: Symfony Lite (simulación de controlador productivo).
- **Procesamiento**: Recibe el POST en `/webhook.php`, parsea el JSON y añade la entrada a `symfony.log`.
- **Dashboard**: El mismo controlador sirve una interfaz de administración empresarial para monitorizar el estado de los posts recibidos.

## 🚦 Verificación
- **URL Dashboard**: [http://localhost:8086](http://localhost:8086)
- **Endpoint Webhook**: `POST /webhook.php` (Interno: 80)
