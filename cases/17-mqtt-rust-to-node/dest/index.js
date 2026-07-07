/**
 * ==================================================================================================
 * SUBSCRIBER MQTT + RECEIVER REST (Case 17: Rust MQTT -> n8n -> Node -> InfluxDB)
 * ==================================================================================================
 * Este servicio Node cumple un doble rol sobre un único bus MQTT (Mosquitto):
 *
 *   1. SUBSCRIBER: se suscribe al topic `social/posts` y persiste cada mensaje en InfluxDB
 *      (BD de series temporales) vía line protocol sobre HTTP. Aquí llegan tanto los mensajes
 *      publicados directamente por el emisor Rust como los reinyectados por el propio receiver.
 *
 *   2. RECEIVER REST: expone el contrato homogéneo del laboratorio (`/webhook`, `/errors`, `/logs`,
 *      `/health`, `/`). En `/webhook` PUBLICA el post en `social/posts`, de modo que la entrega
 *      HTTP de n8n se reinyecta en el mismo pipeline MQTT -> InfluxDB. Un único sink, dos entradas.
 *
 * Por qué InfluxDB 1.8: line protocol + InfluxQL vía HTTP puro (fetch nativo), sin cliente pesado.
 */

import express from "express";
import mqtt from "mqtt";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));

// 12-Factor config.
const PORT = Number(process.env.PORT || 3000);
const MQTT_URL = process.env.MQTT_URL || "mqtt://mosquitto-17:1883";
const MQTT_TOPIC = process.env.MQTT_TOPIC || "social/posts";
const INFLUX_URL = process.env.INFLUX_URL || "http://influxdb-17:8086";
const INFLUX_DB = process.env.INFLUX_DB || "social";

// ==================================================================================================
// INFLUXDB (line protocol 1.8 vía HTTP)
// ==================================================================================================
function escapeTag(v) {
  return String(v).replace(/([,= ])/g, "\\$1");
}
function escapeField(v) {
  return String(v).replace(/(["\\])/g, "\\$1");
}

async function writeInflux({ id, text, channel }) {
  // measurement,tag=... field="..." timestamp(ms)
  const line = `social_posts,channel=${escapeTag(channel)} id="${escapeField(id)}",text="${escapeField(text)}" ${Date.now()}`;
  const resp = await fetch(`${INFLUX_URL}/write?db=${INFLUX_DB}&precision=ms`, {
    method: "POST",
    body: line,
    signal: AbortSignal.timeout(8000),
  });
  if (!resp.ok && resp.status !== 204) {
    throw new Error(`InfluxDB write HTTP ${resp.status}: ${await resp.text()}`);
  }
}

async function queryRecent() {
  const q = encodeURIComponent(
    "SELECT id, channel, text FROM social_posts ORDER BY time DESC LIMIT 20"
  );
  const resp = await fetch(`${INFLUX_URL}/query?db=${INFLUX_DB}&q=${q}`, {
    signal: AbortSignal.timeout(8000),
  });
  const data = await resp.json();
  const series = data?.results?.[0]?.series?.[0];
  if (!series) return [];
  const cols = series.columns;
  const idx = (name) => cols.indexOf(name);
  return series.values.map((row) => {
    const time = row[idx("time")];
    const id = row[idx("id")];
    const channel = row[idx("channel")];
    const text = row[idx("text")];
    return `[${time}] INFLUX | id=${id} | channel=${channel} | text=${text}`;
  });
}

// ==================================================================================================
// MQTT (subscriber + publisher sobre el mismo cliente)
// ==================================================================================================
const client = mqtt.connect(MQTT_URL, {
  reconnectPeriod: 2000,
  connectTimeout: 10000,
});

client.on("connect", () => {
  console.log(`[mqtt] Conectado a ${MQTT_URL}`);
  client.subscribe(MQTT_TOPIC, (err) => {
    if (err) console.error("[mqtt] Error al suscribir:", err.message);
    else console.log(`[mqtt] Suscrito a '${MQTT_TOPIC}'`);
  });
});

client.on("error", (e) => console.error("[mqtt] Error:", e.message));

client.on("message", async (_topic, payload) => {
  try {
    const post = JSON.parse(payload.toString());
    await writeInflux({
      id: post.id,
      text: post.text,
      channel: post.channel || "default",
    });
    console.log(`[sink] Post persistido en InfluxDB: ${post.id}`);
  } catch (e) {
    console.error("[sink] Error persistiendo mensaje MQTT:", e.message);
  }
});

// ==================================================================================================
// SERVIDOR HTTP (contrato REST del laboratorio)
// ==================================================================================================
const app = express();
app.use(express.json());

app.get("/health", (_req, res) =>
  res.json({ ok: true, engine: "mqtt+influxdb", mqtt: client.connected })
);

// n8n entrega aquí; reinyectamos el post en el bus MQTT.
app.post("/webhook", (req, res) => {
  const { id, text, channel = "default" } = req.body || {};
  if (!id || !text) {
    return res.status(422).json({ ok: false, error: "id y text son obligatorios" });
  }
  client.publish(MQTT_TOPIC, JSON.stringify({ id, text, channel }), { qos: 1 }, (err) => {
    if (err) {
      return res.status(502).json({ ok: false, error: err.message });
    }
    res.json({ ok: true, message: "Post publicado en MQTT (sink -> InfluxDB)", case: "17-mqtt-rust-to-node" });
  });
});

app.post("/errors", (req, res) => {
  console.log("Error en DLQ:", JSON.stringify(req.body).slice(0, 200));
  res.json({ ok: true, message: "Error registrado en DLQ" });
});

app.get("/logs", async (_req, res) => {
  try {
    const logs = await queryRecent();
    res.json({ ok: true, logs });
  } catch (e) {
    res.status(502).json({ ok: false, error: e.message, logs: [] });
  }
});

app.get("/", (_req, res) => {
  const file = join(__dirname, "index.html");
  if (existsSync(file)) res.type("html").send(readFileSync(file, "utf-8"));
  else res.send("<h1>Dashboard no encontrado</h1>");
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Receiver Case 17 escuchando en :${PORT} (motor: MQTT + InfluxDB).`);
});
