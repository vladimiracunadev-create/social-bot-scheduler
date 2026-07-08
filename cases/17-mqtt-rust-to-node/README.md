# 🧩 Caso 17: 🦀 Rust (MQTT) → 🌉 n8n → 🟢 Node (subscriber) → 📊 InfluxDB

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Language: Rust](https://img.shields.io/badge/Language-Rust-000000?logo=rust&logoColor=white)](https://www.rust-lang.org/)
[![Protocol: MQTT](https://img.shields.io/badge/Protocol-MQTT-660066?logo=mqtt&logoColor=white)](https://mqtt.org/)
[![Database: InfluxDB](https://img.shields.io/badge/Database-InfluxDB-22ADF6?logo=influxdb&logoColor=white)](https://www.influxdata.com/)

Patrón **pub/sub IoT**: un emisor **Rust** publica en un broker **Mosquitto** (MQTT) y un **subscriber Node** persiste en **InfluxDB** (series temporales). Mosquitto actúa como bus interno y InfluxDB como sink.

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/src/main.rs`: publisher Rust (`rumqttc`, API síncrona, binario release pequeño) que publica los posts en el topic `social/posts`.
2. **🌉 Puente** — **n8n**: guardrails canónicos; entrega vía HTTP al receiver.
3. **📥 Destino** — `dest/index.js`: servicio Node con **doble rol** sobre el mismo bus MQTT:
   - **Subscriber**: consume `social/posts` y escribe cada mensaje en InfluxDB (line protocol).
   - **Receiver REST** (`/webhook`): reinyecta la entrega de n8n en el bus MQTT, unificando ambas entradas en un único sink.
4. **📁 Persistencia** — **InfluxDB 1.8**: measurement `social_posts`, consultado con InfluxQL para el dashboard.

> [!NOTE]
> Dos caminos de entrada, un solo sink: el emisor Rust (MQTT directo) y n8n (HTTP → receiver → MQTT) convergen en el mismo pipeline `MQTT → InfluxDB`.

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case17 up -d      # Mosquitto + InfluxDB + receiver Node
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `mosquitto-17` | Broker MQTT | interno |
| `influxdb-17` | InfluxDB 1.8 (series temporales) | interno |
| `dest-mqtt-17` | Subscriber + receiver REST + dashboard | **8097** |

- **Dashboard del caso**: <http://localhost:8097>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-17**.

### Probar el emisor Rust (opcional)

```bash
cd cases/17-mqtt-rust-to-node/origin
docker build -t case17-origin . && docker run --rm --network social-bot-scheduler_bot-network \
  -e MQTT_HOST=mosquitto-17 case17-origin
```

---

## 🎯 Objetivos didácticos

- **MQTT pub/sub**: desacople total entre emisor y consumidor vía broker.
- **Rust para IoT**: publisher de baja latencia, binario mínimo (LTO + strip).
- **InfluxDB**: modelo de series temporales (measurement, tags, fields) e InfluxQL.

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Broker con acceso anónimo — aceptable en el modelo local-only (todo en `127.0.0.1`).
- El receiver valida el payload (`id` y `text` → HTTP 422) antes de publicar en el bus.
- InfluxDB sin auth para simplificar el lab; en producción se activaría `INFLUXDB_HTTP_AUTH_ENABLED`.

---

## ✅ Estado

Implementado y verificado (build + boot + health). Parte del **Lote 1** del roadmap v5.0 → v4.5.
