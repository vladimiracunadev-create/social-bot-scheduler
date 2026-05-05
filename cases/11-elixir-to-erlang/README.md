# 🧩 Caso 11: 💧 Elixir (Phoenix) -> 🌉 n8n -> 🔴 Erlang (Cowboy)

[![Status: Planned](https://img.shields.io/badge/Status-Planned-orange.svg)]()
[![Language: Elixir](https://img.shields.io/badge/Language-Elixir-4B275F?logo=elixir&logoColor=white)](https://elixir-lang.org/)
[![Language: Erlang](https://img.shields.io/badge/Language-Erlang-A90533?logo=erlang&logoColor=white)](https://www.erlang.org/)
[![Runtime: BEAM](https://img.shields.io/badge/Runtime-BEAM-purple.svg)]()

> [!WARNING]
> **🚧 Caso pendiente de implementación.** Solo scaffolding y diseño. Aún sin código funcional.

Demuestra el modelo de **concurrencia por actores** sobre la **BEAM VM** — un paradigma que ningún caso actual cubre. Phoenix LiveView para emisión, Cowboy puro para recepción.

---

## 🏗️ Arquitectura del Flujo (Propuesta)

1. **📤 Origen**: `lib/publisher.ex` (Elixir + Phoenix Channel) — emite eventos vía `HTTPoison`.
2. **🌉 Puente**: **n8n** (Webhook).
3. **📥 Destino**: `cowboy_handler.erl` (Erlang puro con Cowboy 2.x).
4. **📁 Persistencia**: **Mnesia** (DB nativa BEAM, distribuida) o ETS para hot-storage.

---

## 🎯 Objetivos didácticos

- Modelo de actores: cada request = un proceso BEAM ligero (~2 KB).
- "Let it crash": demostrar supervisión OTP frente a fallos.
- Hot code reloading sin downtime.
- Mnesia: la única DB de la matriz que vive *dentro* del runtime de la app.

---

## 📋 TODO de implementación

- [ ] `mix.exs` con dependencias Phoenix + HTTPoison.
- [ ] Supervisor tree con `OneForOne` strategy.
- [ ] `rebar3` para el módulo Erlang.
- [ ] Workflow n8n `case11-beam.json`.
- [ ] Tests con ExUnit y Common Test.
- [ ] Perfil `case11` en `docker-compose.yml`.

---

*Pendiente — parte del roadmap v5.0.*
