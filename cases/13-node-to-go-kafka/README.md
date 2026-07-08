# 🧩 Caso 13: 🟢 Node.js + Kafka → 🌉 n8n → 🐹 Go consumer → 📊 ClickHouse

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Language: Node](https://img.shields.io/badge/Origen-Node%2FKafka-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![Broker: Kafka](https://img.shields.io/badge/Broker-Kafka%20(KRaft)-231F20?logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Database: ClickHouse](https://img.shields.io/badge/Database-ClickHouse-FAFF69?logo=clickhouse&logoColor=black)](https://clickhouse.com/)

**Event streaming** real con **Kafka** (modo KRaft, sin Zookeeper) y sink columnar **ClickHouse**. Patrón **CQRS**: los posts entran como eventos a un topic y un consumer Go los proyecta en ClickHouse para consultas analíticas.

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/producer.js`: productor **Node/kafkajs** que publica los posts en el topic `social-posts` y los reenvía a n8n.
2. **🌉 Puente** — **n8n**: guardrails canónicos (fingerprint → circuit breaker → idempotencia → HTTP con reintentos → DLQ).
3. **📥 Destino** — `dest/main.go`: servicio **Go** con doble rol sobre el mismo topic:
   - **Producer**: en `/webhook` publica el post en Kafka.
   - **Consumer**: una goroutine lee del topic y hace INSERT en ClickHouse (interfaz HTTP).
4. **📁 Persistencia** — **ClickHouse 24**: tabla `social_posts` (`ReplacingMergeTree ORDER BY id`, idempotente).

> [!NOTE]
> Kafka (KRaft) y el emisor Node producen al mismo topic; el consumer Go es el único **sink** hacia ClickHouse. Dos entradas, un pipeline (CQRS).

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case13 up -d      # Kafka + ClickHouse + consumer Go
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `kafka-13` | Broker Kafka (KRaft) | interno |
| `clickhouse-13` | ClickHouse (OLAP columnar) | interno |
| `dest-go-13` | Producer + consumer + dashboard | **8093** |

- **Dashboard del caso**: <http://localhost:8093>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-13**.

---

## 🎯 Objetivos didácticos

- **Event streaming**: Kafka como log distribuido; producer/consumer desacoplados.
- **CQRS**: escritura como evento, lectura proyectada en un store analítico.
- **ClickHouse**: OLAP columnar para agregaciones a gran escala.

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Puerto `8093` = `8080 + 13` (regla canónica, ver [docs/PORTS.md](../../docs/PORTS.md)).
- ClickHouse expone un usuario `sbuser` accesible desde la red del lab (el `default` solo permite localhost).
- El receiver valida `id`/`text` (→ HTTP 422). Kafka es el servicio pesado (~1 GB).

---

## ✅ Estado

Implementado y verificado (build + boot + health). Parte del **Lote 4** del roadmap v5.0 → v4.8.
