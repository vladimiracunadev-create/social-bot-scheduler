# 🧩 Caso 06: 🐹 Go -> 🌉 n8n -> 🎼 Symfony

[![Language: Go](https://img.shields.io/badge/Language-Go-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Language: PHP/Symfony](https://img.shields.io/badge/Language-Symfony-000000?logo=symfony&logoColor=white)](https://symfony.com/)
[![Database: Redis](https://img.shields.io/badge/Database-Redis-DC382D?logo=redis&logoColor=white)](https://redis.io/)

Este eje tecnológico muestra la integración entre un emisor de alta velocidad en **Go** y un potente backend empresarial basado en **Symfony**, utilizando **Redis** como motor de persistencia ultra-rápido.

---

## 🏗️ Arquitectura del Flujo

1.  **📤 Origen**: `main.go` (Go 1.21) - Emisor concurrente.
2.  **🌉 Puente**: **n8n** (Webhook e Inyección HTTP)
3.  **📥 Destino**: `index.php` (Symfony 7 / PHP 8.2)
4.  **📁 Persistencia**: **Redis 7** (In-Memory Key-Value)

---

## 🐹 Origen: Go Concurrent Dispatcher

El emisor en Go está diseñado para un rendimiento óptimo con mínima carga:
- **Lógica**: Carga `posts.json`, calcula los tiempos de envío y dispara las peticiones HTTP de forma concurrente.
- **Eficiencia**: Optimizado para un consumo de memoria inferior a los 20MB durante ráfagas de tráfico.

> [!TIP]
> Para desplegar este entorno de prueba:
> ```bash
> docker-compose --profile case06 up -d
> ```

---

## 🎼 Destino: Symfony Business Receptor

El receptor utiliza un controlador estandarizado de Symfony para procesar eventos industriales:
- **Tecnología**: **Symfony Lite** ejecutándose sobre Apache 2.4.
- **Procesamiento**: Parsea el JSON entrante y persiste el estado en una base de datos **Redis** para acceso instantáneo.
- **Dashboard**: Interfaz de administración integrada para monitorizar flujos de datos.

---

## 🛡️ Guardrails (Resiliencia)

Este caso implementa protecciones de nivel corporativo:

- **🔄 Reintentos Automáticos**: n8n aplica una política de 3 reintentos con intervalo de 1s ante latencias de red.
- **📥 Dead Letter Queue (DLQ)**: Los eventos que no pueden ser procesados por Symfony se derivan a un log de errores estructurado.
- **⚡ Fast-Path Persistence**: El uso de Redis garantiza que la persistencia no sea el cuello de botella del sistema.

---

## 🚦 Verificación y Acceso

- **🌐 Dashboard**: [http://localhost:8086](http://localhost:8086)
- **⚙️ API Endpoint**: `POST /index.php`
- **📂 Memoria**: El estado actual puede inspeccionarse directamente en Redis.

---

*Desarrollado como parte del Social Bot Scheduler v4.0*
