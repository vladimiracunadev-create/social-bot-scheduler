# 🧩 Caso 07: 🦀 Rust -> 🌉 n8n -> 💎 Ruby

[![Language: Rust](https://img.shields.io/badge/Language-Rust-000000?logo=rust&logoColor=white)](https://www.rust-lang.org/)
[![Language: Ruby](https://img.shields.io/badge/Language-Ruby-CC342D?logo=ruby&logoColor=white)](https://www.ruby-lang.org/)
[![Database: Cassandra](https://img.shields.io/badge/Database-Cassandra-1287B1?logo=apache-cassandra&logoColor=white)](https://cassandra.apache.org/)

Este eje tecnológico combina la robustez y el rendimiento de **Rust** con la elegancia sintáctica de **Ruby**, integrando un emisor fuertemente tipado con un receptor ágil basado en **Sinatra**.

---

## 🏗️ Arquitectura del Flujo

1.  **📤 Origen**: `main.rs` (Rust 1.7x) - Emisor asíncrono de alto rendimiento.
2.  **🌉 Puente**: **n8n** (Webhook e Inyección HTTP)
3.  **📥 Destino**: `app.rb` (Ruby 3.2 / Sinatra)
4.  **📁 Persistencia**: **Cassandra 4.1** (Columnar Distribuido)

---

## 🦀 Origen: Rust Safety Dispatcher

El emisor en Rust garantiza la integridad de los datos antes del envío mediante su sistema de tipos:
- **Lógica**: Utiliza estructuras (`structs`) y **Serde** para una serialización ultra rápida de los posts.
- **Tecnología**: Cliente **Reqwest** asíncrono para despachos masivos sin bloqueo.

> [!TIP]
> Para poner en marcha este caso:
> ```bash
> docker-compose --profile case07 up -d
> ```

---

## 💎 Destino: Ruby Sinatra Receptor

El receptor utiliza Sinatra para gestionar los eventos con una sintaxis limpia y minimalista:
- **Tecnología**: **Sinatra DSL** ejecutándose sobre el servidor **Puma**.
- **Persistencia**: Almacenamiento distribuido en **Cassandra**, ideal para flujos de datos de alta escritura.
- **Dashboard**: Interfaz dinámica generada con plantillas **ERB**.

---

## 🛡️ Guardrails (Resiliencia)

Este caso implementa defensas para garantizar entregas seguras en flujos de datos intensos:

- **🔄 Reintentos Automáticos**: n8n reintenta el envío hasta 3 veces con backoff si el receptor Ruby no responde a tiempo.
- **📥 Dead Letter Queue (DLQ)**: Los mensajes fallidos se registran en una cola persistente para evitar la pérdida de eventos críticos.
- **⚡ Escrituras Masivas**: Cassandra permite absorber ráfagas de datos sin degradar la respuesta del receptor Ruby.

---

## 🚦 Verificación y Acceso

- **🌐 Dashboard**: [http://localhost:8087](http://localhost:8087)
- **⚙️ API Endpoint**: `POST /webhook`
- **📂 Cluster**: El estado del anillo puede inspeccionarse con herramientas nativas de Cassandra.

---

*Desarrollado como parte del Social Bot Scheduler v4.0*

