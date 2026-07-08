/**
 * ==================================================================================================
 * RECEIVER SUPABASE (Case 14: Next.js -> n8n -> Supabase (Postgres + RLS) via PostgREST)
 * ==================================================================================================
 * Supabase = Postgres + PostgREST + RLS + Auth. Este receiver representa la capa de acceso a datos
 * de Supabase: traduce el contrato REST del laboratorio a llamadas contra **PostgREST**, el servicio
 * que expone la tabla como API REST. Las **políticas RLS** (Row Level Security) del rol `web_anon`
 * gobiernan qué puede leer/escribir cada request.
 *
 * Endpoints del laboratorio: /webhook, /errors, /logs, /health, /.
 */

import express from "express";
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 3000);
const PGRST = process.env.POSTGREST_URL || "http://postgrest-14:3000";

const app = express();
app.use(express.json());

app.get("/health", (_req, res) => res.json({ ok: true, engine: "supabase-postgrest" }));

app.post("/webhook", async (req, res) => {
  const { id, text, channel = "default" } = req.body || {};
  if (!id || !text) {
    return res.status(422).json({ ok: false, error: "id y text son obligatorios" });
  }
  try {
    // Prefer: resolution=merge-duplicates => upsert sobre la PK (idempotente).
    const r = await fetch(`${PGRST}/social_posts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Prefer: "resolution=merge-duplicates",
      },
      body: JSON.stringify({ id, text, channel }),
      signal: AbortSignal.timeout(8000),
    });
    if (r.ok) {
      return res.json({
        ok: true,
        message: "Post persistido en Supabase (Postgres + RLS via PostgREST)",
        case: "14-nextjs-to-supabase",
      });
    }
    return res.status(502).json({ ok: false, error: await r.text() });
  } catch (e) {
    return res.status(502).json({ ok: false, error: e.message });
  }
});

app.post("/errors", (req, res) => {
  console.log("Error en DLQ:", JSON.stringify(req.body).slice(0, 200));
  res.json({ ok: true, message: "Error registrado en DLQ" });
});

app.get("/logs", async (_req, res) => {
  try {
    const r = await fetch(
      `${PGRST}/social_posts?select=id,channel,text,created_at&order=created_at.desc&limit=20`,
      { signal: AbortSignal.timeout(8000) }
    );
    const rows = await r.json();
    const logs = (Array.isArray(rows) ? rows : []).map(
      (x) => `[${x.created_at}] SUPABASE | id=${x.id} | channel=${x.channel} | text=${x.text}`
    );
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
  console.log(`Receiver Case 14 escuchando en :${PORT} (motor: Supabase / PostgREST).`);
});
