// ================================================================================================
// EMISOR NEXT.JS — Route Handler (Case 14: Next.js -> n8n -> Supabase)
// ================================================================================================
// Un Route Handler de Next.js (App Router) que, al llamarse (GET /api/emit), lee la cola de posts
// y reenvía los vencidos al webhook de n8n. Representa el "frontend/edge" del stack Supabase.
// La lógica de red se comparte con el emisor CLI (emit.mjs).

import { readFileSync } from "node:fs";
import { join } from "node:path";

export async function GET() {
  const webhook = process.env.WEBHOOK_URL;
  const posts = JSON.parse(readFileSync(join(process.cwd(), "posts.json"), "utf-8"));
  const results = [];

  for (const post of posts.filter((p) => !p.published)) {
    const payload = {
      id: post.id,
      text: post.text,
      channel: post.channel ?? "default",
      scheduled_at: post.scheduled_at ?? "",
    };
    if (!webhook) {
      results.push({ id: post.id, status: "dry-run" });
      continue;
    }
    try {
      const r = await fetch(webhook, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      results.push({ id: post.id, status: r.status });
    } catch (e) {
      results.push({ id: post.id, status: "error", error: e.message });
    }
  }

  return Response.json({ emitted: results });
}
