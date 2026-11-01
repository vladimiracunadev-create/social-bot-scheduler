# Emisor Elixir (Case 11) — sólo se ejecuta bajo demanda para disparar el flujo.
FROM elixir:1.18-otp-28-alpine
WORKDIR /app
COPY . .
RUN mix local.hex --force && mix compile
CMD ["mix", "run", "-e", "Case11.Publisher.main()"]
