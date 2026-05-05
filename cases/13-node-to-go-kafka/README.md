# 🧩 Caso 13: 🟢 Node.js -> 🌉 n8n + 📨 Kafka -> 🐹 Go Consumer -> 🟡 ClickHouse

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Language: Node.js](https://img.shields.io/badge/Language-Node.js-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Language: Go](https://img.shields.io/badge/Language-Go-00ADD8?logo=go&logoColor=white)](https://go.dev/)
[![Broker: Kafka](https://img.shields.io/badge/Broker-Kafka-231F20?logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Database: ClickHouse](https://img.shields.io/badge/Database-ClickHouse-FFCC01?logo=clickhouse&logoColor=black)](https://clickhouse.com/)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño.

Primer caso de la matriz que introduce **event streaming real** (no solo webhooks puntuales). Demuestra el patrón **CQRS + analytical store** con ClickHouse como sink columnar.

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `producer.js` (Node + `kafkajs`) — emite eventos a topic `events.raw`.
2. **🌉 Puente**: **n8n** — consume `events.raw`, enriquece, republica a `events.enriched`.
3. **📥 Destino**: `consumer.go` — consume `events.enriched`, batch-inserta en ClickHouse.
4. **📁 Persistencia**: **ClickHouse** (tablas con engine `MergeTree`, partitioning por día).

---

## 🎯 Objetivos didácticos

- Diferencia entre **mensajería transaccional** (RabbitMQ) y **streaming** (Kafka).
- **Consumer groups**, offsets, replay y at-least-once delivery.
- Por qué ClickHouse no es Postgres: storage columnar, compresión, queries OLAP a billones de filas.
- n8n como **stream processor** ligero (no como reemplazo de Flink/Spark).

---

## ⚠️ Consideraciones operacionales

- Kafka exige Zookeeper o KRaft → +2-3 contenedores. Documentar el coste de RAM.
- Topics deben tener `replication.factor` apropiado incluso en single-broker dev.
- ClickHouse insert batching crítico: insertar fila-a-fila destruye el rendimiento.

---

## 📋 TODO de implementación

- [ ] Bitnami Kafka (KRaft mode) en `docker-compose.yml`.
- [ ] Productor Node con `kafkajs` y schema validation (Zod).
- [ ] Consumer Go con `confluent-kafka-go` o `segmentio/kafka-go`.
- [ ] Schema ClickHouse con `MergeTree` particionado.
- [ ] Workflow n8n `case13-stream.json`.
- [ ] Dashboard Grafana con métricas de lag.
- [ ] Perfil `case13` en `docker-compose.yml`.

---

*Pendiente — parte del roadmap v5.0. Caso de mayor coste operacional (~5 contenedores extra).*
