/**
 * ==================================================================================================
 * PRODUCTOR NODE/KAFKA (Case 13: Node+Kafka -> n8n -> Go consumer -> ClickHouse)
 * ==================================================================================================
 * El emisor Node produce eventos a un topic Kafka con kafkajs (event-streaming). Además, reenvía
 * cada post vencido al webhook de n8n (contrato del laboratorio), de modo que ambos caminos —
 * Kafka directo y n8n->receiver->Kafka— convergen en el mismo pipeline hacia ClickHouse.
 *
 * Modo dry-run: sin WEBHOOK_URL sólo se produce a Kafka (o se simula si tampoco hay broker).
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { Kafka } from "kafkajs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const POSTS_FILE = join(__dirname, "posts.json");

const WEBHOOK_URL = process.env.WEBHOOK_URL || "";
const KAFKA_BROKER = process.env.KAFKA_BROKER || "localhost:9092";
const TOPIC = process.env.KAFKA_TOPIC || "social-posts";

async function main() {
  const posts = JSON.parse(readFileSync(POSTS_FILE, "utf-8"));
  const due = posts.filter((p) => !p.published);

  const kafka = new Kafka({ clientId: "case13-producer", brokers: [KAFKA_BROKER] });
  const producer = kafka.producer({ allowAutoTopicCreation: true });

  try {
    await producer.connect();
    for (const post of due) {
      const payload = {
        id: post.id,
        text: post.text,
        channel: post.channel ?? "default",
        scheduled_at: post.scheduled_at ?? "",
      };
      await producer.send({ topic: TOPIC, messages: [{ key: post.id, value: JSON.stringify(payload) }] });
      console.log(`[kafka] Post ${post.id} producido en '${TOPIC}'.`);

      if (WEBHOOK_URL) {
        try {
          const resp = await fetch(WEBHOOK_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          console.log(`[n8n] Post ${post.id} -> n8n (${resp.status}).`);
        } catch (e) {
          console.error(`[n8n] Fallo reenviando ${post.id}: ${e.message}`);
        }
      }
    }
    await producer.disconnect();
  } catch (e) {
    console.error(`[ERROR] Kafka no disponible (${e.message}). Modo dry-run.`);
    for (const post of due) console.log(`[DRY-RUN] Post ${post.id}.`);
  }
}

main();
