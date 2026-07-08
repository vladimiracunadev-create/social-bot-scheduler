# 🧩 Caso 14: ▲ Next.js 15 → 🌉 n8n → ⚡ Supabase (Postgres + RLS)

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Origen: Next.js](https://img.shields.io/badge/Origen-Next.js%2015-000000?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![BaaS: Supabase](https://img.shields.io/badge/BaaS-Supabase-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![Security: RLS](https://img.shields.io/badge/Security-Row%20Level%20Security-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

Primer caso **BaaS** de la matriz. Reproduce el **núcleo de Supabase** — **Postgres + PostgREST + Row Level Security (RLS)** — sin la suite completa: **Next.js** emite y el receiver persiste vía **PostgREST**, gobernado por las políticas RLS del rol `web_anon`.

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/app/api/emit/route.js`: Route Handler de **Next.js 15** (App Router) que reenvía los posts a n8n (también hay un emisor CLI en `origin/emit.mjs`).
2. **🌉 Puente** — **n8n**: guardrails canónicos (fingerprint → circuit breaker → idempotencia → HTTP con reintentos → DLQ).
3. **📥 Destino** — `dest/index.js`: receiver que traduce el contrato REST del laboratorio a llamadas contra **PostgREST** (upsert vía `Prefer: resolution=merge-duplicates`).
4. **📁 Persistencia** — **Postgres 16** con **RLS**: la tabla `social_posts` está protegida y una política permite acceso al rol `web_anon` que PostgREST asume.

> [!NOTE]
> **Supabase-lite**: Postgres + PostgREST + RLS son el corazón de Supabase (la suite completa añade GoTrue, Realtime, Storage, Kong…). Aquí se demuestran el patrón BaaS y las políticas RLS sin ~6 contenedores extra.

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case14 up -d      # Postgres (RLS) + PostgREST + receiver
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `db-postgres-14` | Postgres 16 + RLS | interno |
| `postgrest-14` | PostgREST (API REST sobre Postgres) | interno (`:3000`) |
| `dest-supabase-14` | Receiver + dashboard | **8094** |

- **Dashboard del caso**: <http://localhost:8094>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-14**.

---

## 🎯 Objetivos didácticos

- **BaaS**: exponer una tabla como API REST sin escribir backend (PostgREST).
- **Row Level Security**: políticas declarativas que gobiernan el acceso por rol.
- **Next.js App Router**: Route Handlers como capa de emisión.

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Puerto `8094` = `8080 + 14` (regla canónica, ver [docs/PORTS.md](../../docs/PORTS.md)).
- La política RLS del lab es permisiva (`web_anon` full); en producción se restringiría por usuario/tenant vía JWT.
- El receiver valida `id`/`text` (→ HTTP 422).

---

## ✅ Estado

Implementado y verificado (build + boot + health). Parte del **Lote 4** del roadmap v5.0 → v4.8.
