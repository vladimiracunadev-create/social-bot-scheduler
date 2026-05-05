# 🧩 Caso 14: ⚫ Next.js (App Router) -> 🌉 n8n -> 🟢 Supabase (BaaS)

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Framework: Next.js](https://img.shields.io/badge/Framework-Next.js%2015-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![BaaS: Supabase](https://img.shields.io/badge/BaaS-Supabase-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![Database: Postgres + RLS](https://img.shields.io/badge/Database-Postgres%20%2B%20RLS-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño.

Primer caso **BaaS (Backend-as-a-Service)** de la matriz. Demuestra cómo n8n se integra con plataformas opinadas que ya traen Auth + Storage + Realtime + Postgres + Edge Functions. El "anti-microservicio" controlado.

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: Next.js 15 App Router con Server Actions — formulario que envía a n8n.
2. **🌉 Puente**: **n8n** — valida, transforma, reenvía a Supabase Edge Function.
3. **📥 Destino**: **Supabase Edge Function** (Deno runtime) — escribe en tabla `posts` con **Row Level Security**.
4. **📁 Persistencia**: **PostgreSQL** gestionada por Supabase + **Realtime** broadcast a clientes WS.

> [!NOTE]
> Se usa la **CLI local de Supabase** (`supabase start`) para mantener el laboratorio 100% offline. No se conecta a la nube de Supabase.

---

## 🎯 Objetivos didácticos

- Contrastar microservicios DIY (cases 01-13) vs BaaS integrado.
- **Row Level Security (RLS)**: políticas a nivel de fila como mecanismo de autorización declarativo.
- **Realtime subscriptions**: WebSockets sobre cambios en Postgres vía replicación lógica.
- **Edge Functions** Deno: cómputo cerca del cliente, sin contenedor adicional propio.
- Trade-off: velocidad de desarrollo vs lock-in del proveedor.

---

## ⚠️ Consideraciones de seguridad

- **NUNCA** exponer la `service_role` key al frontend; solo `anon` key.
- RLS habilitado por defecto en todas las tablas — caso contrario, filtración total.
- Validar JWT de Supabase en n8n antes de procesar webhooks.

---

## 📋 TODO de implementación

- [ ] Stack `supabase/cli` local (Postgres + Auth + Storage + Studio + Edge Runtime).
- [ ] Migraciones SQL con RLS policies en `dest/supabase/migrations/`.
- [ ] Edge Function en `dest/supabase/functions/ingest/`.
- [ ] Frontend Next.js 15 con Server Actions y `@supabase/ssr`.
- [ ] Workflow n8n `case14-supabase.json` con auth header.
- [ ] Demo de Realtime subscription en el dashboard.
- [ ] Perfil `case14` en `docker-compose.yml`.

---

*Pendiente — parte del roadmap v5.0. Caso solicitado explícitamente: cubre el hueco BaaS.*
