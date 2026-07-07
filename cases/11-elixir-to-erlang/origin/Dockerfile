# Emisor Elixir (Case 11) — sólo se ejecuta bajo demanda para disparar el flujo.
FROM elixir:1.17-otp-27-alpine
WORKDIR /app
COPY . .
RUN mix local.hex --force && mix compile
CMD ["mix", "run", "-e", "Case11.Publisher.main()"]
