# 🧩 Caso 17: 🦀 Rust (MQTT publisher) -> 🌉 n8n -> 🟢 Node (subscriber) -> 📊 InfluxDB

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Protocol: MQTT](https://img.shields.io/badge/Protocol-MQTT%205.0-660066?logo=mqtt&logoColor=white)](https://mqtt.org/)
[![Database: InfluxDB](https://img.shields.io/badge/Database-InfluxDB-22ADF6?logo=influxdb&logoColor=white)](https://www.influxdata.com/)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño.

Caso **IoT/telemetría**: el patrón clásico de dispositivos restringidos publicando vía **MQTT** sobre un broker (Mosquitto/EMQX), con n8n actuando de bridge MQTT↔HTTP y persistencia en una time-series DB optimizada.

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `publisher.rs` (Rust + `rumqttc`) — simula sensores publicando al broker.
2. **📡 Broker**: **Mosquitto 2.x** o **EMQX** con QoS 1.
3. **🌉 Puente**: **n8n** — nodo MQTT trigger; transforma payload binario y reenvía.
4. **📥 Destino**: `subscriber.js` (Node + `@influxdata/influxdb-client`) — escribe métricas en InfluxDB.
5. **📁 Persistencia**: **InfluxDB 2.x** con buckets y retention policies.

---

## 🎯 Objetivos didácticos

- MQTT: QoS levels (0/1/2), retained messages, last-will-and-testament.
- Patrón pub/sub asíncrono vs request/response síncrono (resto de casos).
- InfluxDB Flux query language vs InfluxQL.
- Backpressure: qué pasa cuando el subscriber no puede consumir al ritmo del publisher.

---

## ⚠️ Consideraciones de seguridad

- MQTT sin TLS expone payloads en claro → en lab usar `mqtts://` con cert auto-firmado.
- Mosquitto debe configurarse con `allow_anonymous false` y ACL.
- Retained messages pueden filtrar estado histórico → revisar política.

---

## 📋 TODO de implementación

- [ ] Broker Mosquitto en `docker-compose.yml` con `mosquitto.conf` hardenizado.
- [ ] Publisher Rust con `tokio` + `rumqttc`.
- [ ] Subscriber Node con reconexión automática.
- [ ] Schema InfluxDB con measurements + tags + fields.
- [ ] Workflow n8n `case17-mqtt.json`.
- [ ] Dashboard Grafana con panel time-series.
- [ ] Perfil `case17` en `docker-compose.yml`.

---

*Pendiente — parte del backlog exploratorio v5.0+.*
