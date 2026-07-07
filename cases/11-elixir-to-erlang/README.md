# 🧩 Caso 11: 💧 Elixir → 🌉 n8n → 🔴 Erlang (Cowboy) + Mnesia

[![Status: Ready](https://img.shields.io/badge/Status-Ready-brightgreen.svg)]()
[![Language: Elixir](https://img.shields.io/badge/Language-Elixir-4B275F?logo=elixir&logoColor=white)](https://elixir-lang.org/)
[![Language: Erlang](https://img.shields.io/badge/Language-Erlang-A90533?logo=erlang&logoColor=white)](https://www.erlang.org/)
[![Runtime: BEAM](https://img.shields.io/badge/Runtime-BEAM-purple.svg)]()

Demuestra el modelo de **concurrencia por actores** sobre la **BEAM VM** — un paradigma que ningún caso 01–09 cubre. Emisor **Elixir** y receptor **Erlang/Cowboy** con persistencia en **Mnesia**, la única BD de la matriz que vive *dentro* del runtime de la aplicación (sin contenedor de base de datos separado).

---

## 🏗️ Arquitectura del Flujo

1. **📤 Origen** — `origin/lib/publisher.ex`: emisor Elixir que lee `posts.json` y reenvía los posts vencidos al webhook de n8n (HTTP vía `:httpc`, JSON vía el módulo `:json` de OTP 27, sin dependencias externas).
2. **🌉 Puente** — **n8n**: guardrails canónicos (fingerprint → circuit breaker → idempotencia → HTTP con reintentos → DLQ).
3. **📥 Destino** — `dest/src/*.erl`: aplicación **Erlang/Cowboy 2.12** con árbol de supervisión OTP. Expone el contrato REST (`/webhook`, `/errors`, `/logs`, `/health`, `/`).
4. **📁 Persistencia** — **Mnesia** (`ram_copies`): tabla `social_post` como `ordered_set`, embebida en el nodo BEAM.

> [!NOTE]
> El destino se empaqueta como un **release OTP** con ERTS embebido (`rebar3 as prod release`), el formato de despliegue idiomático de Erlang.

---

## 🚀 Cómo levantarlo

```bash
docker-compose --profile case11 up -d      # sólo el receptor BEAM; no hay contenedor de BD
```

| Servicio | Rol | Puerto host |
| :--- | :--- | :---: |
| `dest-erlang-11` | Erlang/Cowboy + Mnesia + dashboard | **8092** |

- **Dashboard del caso**: <http://localhost:8092>
- **Probar desde el dashboard maestro**: <http://localhost:8080> → tarjeta **CASE-11**.

### Probar el emisor Elixir (opcional)

```bash
cd cases/11-elixir-to-erlang/origin
WEBHOOK_URL=http://localhost:5678/webhook/social-bot-scheduler-beam mix run -e "Case11.Publisher.main()"
```

---

## 🎯 Objetivos didácticos

- **Modelo de actores**: cada request = un proceso BEAM ligero (~2 KB), aislado.
- **"Let it crash" + supervisión OTP**: el árbol de supervisión mantiene la app viva.
- **Mnesia**: la única BD de la matriz embebida en el runtime; transacciones ACID sin servidor externo.

---

## ⚠️ Consideraciones (modelo del laboratorio)

- Puerto bindeado a `127.0.0.1` (aislamiento runtime).
- El receptor valida el payload (`id` y `text` → HTTP 422) como defensa en profundidad.
- `ram_copies` mantiene los datos en memoria del nodo; en un clúster real se usaría `disc_copies` con replicación entre nodos.

---

## ✅ Estado

Implementado y verificado (build + boot + health). Parte del **Lote 1** del roadmap v5.0 → v4.5.
