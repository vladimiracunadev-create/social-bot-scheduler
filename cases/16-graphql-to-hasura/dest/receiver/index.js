/**
 * ==================================================================================================
 * MICRO-RECEIVER REST ↔ HASURA GRAPHQL (Case 16: Apollo GraphQL -> n8n -> Hasura + TimescaleDB)
 * ==================================================================================================
 * ¿Por qué un receiver delgado delante de Hasura?
 * El puente n8n del laboratorio habla un contrato REST homogéneo (`POST /webhook`, `POST /errors`,
 * `GET /logs`) idéntico en los 20 casos, de modo que los guardrails (idempotencia, circuit breaker,
 * DLQ) y el dashboard maestro funcionan sin ramificaciones por caso. Este receiver traduce ese
 * contrato REST a **GraphQL real contra Hasura**: cada post se persiste con una `mutation` y el
 * dashboard se alimenta de una `query`. Así el "motor destino" es genuinamente Hasura/TimescaleDB,
 * no una simulación.
 *
 * Arranque auto-reparable:
 *   1. Espera a que Hasura responda /healthz (Hasura a su vez espera a TimescaleDB).
 *   2. Registra ("trackea") la tabla `social_posts` vía Metadata API — idempotente: si ya está
 *      trackeada, se ignora el error.
 *   3. Levanta el servidor HTTP.
 */

import express from "express";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));

// 12-Factor config.
const PORT = Number(process.env.PORT || 3000);
const HASURA_URL = process.env.HASURA_URL || "http://hasura-16:8080";
const ADMIN_SECRET = process.env.HASURA_ADMIN_SECRET || "";
const GRAPHQL_ENDPOINT = `${HASURA_URL}/v1/graphql`;
const METADATA_ENDPOINT = `${HASURA_URL}/v1/metadata`;

const adminHeaders = {
  "Content-Type": "application/json",
  ...(ADMIN_SECRET ? { "x-hasura-admin-secret": ADMIN_SECRET } : {}),
};

// In-memory DLQ (los errores también quedan en el log de stdout del contenedor).
const deadLetters = [];

// ==================================================================================================
// CLIENTE GRAPHQL (fetch nativo de Node 20)
// ==================================================================================================
async function gql(query, variables) {
  const resp = await fetch(GRAPHQL_ENDPOINT, {
    method: "POST",
    headers: adminHeaders,
    body: JSON.stringify({ query, variables }),
    signal: AbortSignal.timeout(10000),
  });
  const data = await resp.json();
  if (data.errors) {
    throw new Error(data.errors.map((e) => e.message).join("; "));
  }
  return data.data;
}

const INSERT_MUTATION = `
  mutation InsertPost($obj: social_posts_insert_input!) {
    insert_social_posts_one(object: $obj) { id }
  }
`;

const RECENT_QUERY = `
  query RecentPosts {
    social_posts(order_by: { created_at: desc }, limit: 20) {
      id
      text
      channel
      created_at
    }
  }
`;

// ==================================================================================================
// BOOTSTRAP: esperar a Hasura y trackear la tabla
// ==================================================================================================
async function waitForHasura(retries = 60) {
  for (let i = 0; i < retries; i++) {
    try {
      const resp = await fetch(`${HASURA_URL}/healthz`, {
        signal: AbortSignal.timeout(3000),
      });
      if (resp.ok) return true;
    } catch {
      /* aún no está listo */
    }
    await new Promise((r) => setTimeout(r, 2000));
  }
  throw new Error("Hasura no respondió /healthz a tiempo.");
}

async function trackTable() {
  const resp = await fetch(METADATA_ENDPOINT, {
    method: "POST",
    headers: adminHeaders,
    body: JSON.stringify({
      type: "pg_track_table",
      args: {
        source: "default",
        table: { schema: "public", name: "social_posts" },
      },
    }),
    signal: AbortSignal.timeout(8000),
  });
  if (resp.ok) {
    console.log("[bootstrap] Tabla social_posts trackeada en Hasura.");
    return;
  }
  const body = await resp.json().catch(() => ({}));
  // "already-tracked" es esperado en reinicios: lo tratamos como éxito.
  if (JSON.stringify(body).includes("already-tracked")) {
    console.log("[bootstrap] Tabla social_posts ya estaba trackeada.");
    return;
  }
  console.warn("[bootstrap] Aviso al trackear tabla:", JSON.stringify(body));
}

// ==================================================================================================
// SERVIDOR HTTP (contrato REST del laboratorio)
// ==================================================================================================
const app = express();
app.use(express.json());

// Health simple para el dashboard maestro y para depends_on/healthcheck.
app.get("/health", (_req, res) => res.json({ ok: true, engine: "hasura+timescaledb" }));

// Webhook principal: n8n entrega aquí el post ya validado por los guardrails.
app.post("/webhook", async (req, res) => {
  const { id, text, channel = "default", scheduled_at = null } = req.body || {};
  if (!id || !text) {
    return res.status(422).json({ ok: false, error: "id y text son obligatorios" });
  }
  try {
    await gql(INSERT_MUTATION, {
      obj: { id, text, channel, scheduled_at },
    });
    console.log(`Post persistido vía Hasura: ${id}`);
    return res.json({ ok: true, message: "Post persistido en Hasura/TimescaleDB", case: "16-graphql-to-hasura" });
  } catch (e) {
    console.error(`Error persistiendo ${id}:`, e.message);
    return res.status(502).json({ ok: false, error: e.message });
  }
});

// Dead Letter Queue: n8n reporta aquí los fallos tras agotar reintentos.
app.post("/errors", (req, res) => {
  const entry = { ...req.body, received_at: new Date().toISOString() };
  deadLetters.push(entry);
  console.log("Error en DLQ:", JSON.stringify(entry).slice(0, 200));
  res.json({ ok: true, message: "Error registrado en DLQ" });
});

// Consulta para el dashboard: últimos registros, formateados como strings.
app.get("/logs", async (_req, res) => {
  try {
    const data = await gql(RECENT_QUERY);
    const logs = (data.social_posts || []).map(
      (p) => `[${p.created_at}] HASURA | id=${p.id} | channel=${p.channel} | text=${p.text}`
    );
    res.json({ ok: true, logs });
  } catch (e) {
    res.status(502).json({ ok: false, error: e.message, logs: [] });
  }
});

// Dashboard estático.
app.get("/", (_req, res) => {
  const file = join(__dirname, "index.html");
  if (existsSync(file)) {
    res.type("html").send(readFileSync(file, "utf-8"));
  } else {
    res.send("<h1>Dashboard no encontrado</h1>");
  }
});

// ==================================================================================================
// ARRANQUE
// ==================================================================================================
async function main() {
  console.log(`[bootstrap] Esperando a Hasura en ${HASURA_URL}...`);
  await waitForHasura();
  await trackTable();
  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Receiver Case 16 escuchando en :${PORT} (motor: Hasura + TimescaleDB).`);
  });
}

main().catch((e) => {
  console.error("Fallo fatal en el receiver:", e);
  process.exit(1);
});
