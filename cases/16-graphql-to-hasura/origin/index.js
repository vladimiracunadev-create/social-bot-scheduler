/**
 * ==================================================================================================
 * EMISOR GRAPHQL-FIRST (Case 16: Apollo GraphQL -> n8n -> Hasura + TimescaleDB)
 * ==================================================================================================
 * ¿Por qué Apollo Server en el emisor?
 * A diferencia de los emisores REST de los casos 01-09, aquí la fuente de verdad de los posts
 * programados se expone como un **API GraphQL fuertemente tipado** (Apollo Server 4 standalone).
 * Esto demuestra el patrón "schema-first" del lado del origen, en contraste con el enfoque
 * "database-first" de Hasura en el destino.
 *
 * Doble rol del proceso:
 *   1. Servidor GraphQL (puerto 4016): permite inspeccionar/consultar la cola de posts vía queries
 *      `scheduledPosts` y `duePosts`, útil para debugging y para clientes GraphQL externos.
 *   2. Daemon de polling: cada POLL_INTERVAL_MS reevalúa qué posts están vencidos y los reenvía al
 *      webhook de n8n, que aplica los guardrails (idempotencia + circuit breaker) y persiste en
 *      Hasura. El estado `published` se mantiene en memoria + posts.json (persistencia ligera).
 *
 * Modo dry-run: si WEBHOOK_URL no está definido, los envíos se simulan (log) para pruebas locales
 * sin dependencia de la infraestructura Docker.
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { ApolloServer } from "@apollo/server";
import { startStandaloneServer } from "@apollo/server/standalone";

const __dirname = dirname(fileURLToPath(import.meta.url));
const POSTS_FILE = join(__dirname, "posts.json");

// 12-Factor: toda la configuración entra por entorno con defaults seguros para local.
const WEBHOOK_URL = process.env.WEBHOOK_URL || "";
const POLL_INTERVAL_MS = Number(process.env.POLL_INTERVAL_MS || 30000);
const GRAPHQL_PORT = Number(process.env.GRAPHQL_PORT || 4016);

// ==================================================================================================
// ESTADO (persistencia ligera en JSON, igual que los otros emisores del laboratorio)
// ==================================================================================================
function loadPosts() {
  if (!existsSync(POSTS_FILE)) return [];
  return JSON.parse(readFileSync(POSTS_FILE, "utf-8"));
}

function savePosts(posts) {
  writeFileSync(POSTS_FILE, JSON.stringify(posts, null, 2), "utf-8");
}

// ==================================================================================================
// ESQUEMA GRAPHQL (schema-first)
// ==================================================================================================
const typeDefs = `#graphql
  "Un post social programado, tal como lo maneja el emisor."
  type ScheduledPost {
    id: ID!
    text: String!
    channel: String!
    scheduledAt: String!
    published: Boolean!
  }

  type Query {
    "Todos los posts conocidos por el emisor."
    scheduledPosts: [ScheduledPost!]!
    "Sólo los posts vencidos y aún no publicados (los que se reenviarían a n8n)."
    duePosts: [ScheduledPost!]!
  }
`;

const resolvers = {
  Query: {
    scheduledPosts: () =>
      loadPosts().map((p) => ({
        id: p.id,
        text: p.text,
        channel: p.channel ?? "default",
        scheduledAt: p.scheduled_at,
        published: Boolean(p.published),
      })),
    duePosts: () =>
      loadPosts()
        .filter((p) => !p.published && new Date(p.scheduled_at) <= new Date())
        .map((p) => ({
          id: p.id,
          text: p.text,
          channel: p.channel ?? "default",
          scheduledAt: p.scheduled_at,
          published: false,
        })),
  },
};

// ==================================================================================================
// DAEMON DE POLLING -> n8n
// ==================================================================================================
async function forwardPost(post) {
  // Dry-run: sin webhook configurado, simulamos el envío.
  if (!WEBHOOK_URL) {
    console.log(`[DRY-RUN] Post ${post.id} (canal ${post.channel}) reenviado.`);
    return true;
  }
  try {
    const resp = await fetch(WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: post.id,
        text: post.text,
        channel: post.channel ?? "default",
        scheduled_at: post.scheduled_at,
      }),
      signal: AbortSignal.timeout(15000),
    });
    if (resp.ok) {
      console.log(`[OK] Post ${post.id} aceptado por n8n (${resp.status}).`);
      return true;
    }
    console.error(`[ERROR] n8n respondió ${resp.status} para ${post.id}.`);
  } catch (e) {
    console.error(`[ERROR] Fallo reenviando ${post.id}: ${e.message}`);
  }
  return false;
}

async function pollOnce() {
  const posts = loadPosts();
  let changed = false;
  const now = new Date();
  for (const post of posts) {
    if (!post.published && new Date(post.scheduled_at) <= now) {
      console.log(`Procesando post ${post.id}...`);
      const ok = await forwardPost(post);
      if (ok) {
        post.published = true;
        changed = true;
      }
    }
  }
  if (changed) {
    savePosts(posts);
    console.log("Estado de posts actualizado.");
  }
}

// ==================================================================================================
// BOOTSTRAP
// ==================================================================================================
async function main() {
  const server = new ApolloServer({ typeDefs, resolvers });
  const { url } = await startStandaloneServer(server, {
    listen: { port: GRAPHQL_PORT, host: "0.0.0.0" },
  });
  console.log(`Emisor Apollo GraphQL escuchando en ${url}`);
  console.log(
    WEBHOOK_URL
      ? `Reenviando posts vencidos a ${WEBHOOK_URL} cada ${POLL_INTERVAL_MS}ms.`
      : "WEBHOOK_URL no definido: modo DRY-RUN."
  );

  await pollOnce();
  setInterval(pollOnce, POLL_INTERVAL_MS);
}

main().catch((e) => {
  console.error("Fallo fatal en el emisor:", e);
  process.exit(1);
});
