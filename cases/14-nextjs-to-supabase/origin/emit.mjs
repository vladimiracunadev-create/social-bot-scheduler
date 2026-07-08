// Emisor CLI (Case 14) — reenvía los posts vencidos a n8n. Comparte lógica con el Route Handler.
import { readFileSync } from "node:fs";

const webhook = process.env.WEBHOOK_URL;
const posts = JSON.parse(readFileSync(new URL("./posts.json", import.meta.url), "utf-8"));

for (const post of posts.filter((p) => !p.published)) {
  const payload = {
    id: post.id,
    text: post.text,
    channel: post.channel ?? "default",
    scheduled_at: post.scheduled_at ?? "",
  };
  if (!webhook) {
    console.log(`[DRY-RUN] Post ${post.id} reenviado.`);
    continue;
  }
  try {
    const r = await fetch(webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    console.log(`[OK] Post ${post.id} -> n8n (${r.status}).`);
  } catch (e) {
    console.error(`[ERROR] Fallo reenviando ${post.id}: ${e.message}`);
  }
}
