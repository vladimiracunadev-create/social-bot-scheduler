# ==================================================================================================
# Case 11 — Build multi-stage del receptor Erlang/Cowboy (release OTP con ERTS embebido).
# ==================================================================================================
FROM erlang:27-alpine AS build
WORKDIR /src
# Cache de dependencias: copiamos primero rebar.config.
COPY rebar.config ./
RUN rebar3 get-deps
COPY src ./src
COPY priv ./priv
RUN rebar3 as prod release

# --- Runtime: imagen limpia; el release trae su propio ERTS ---
FROM erlang:27-alpine
WORKDIR /app
RUN apk add --no-cache libstdc++ ncurses
COPY --from=build /src/_build/prod/rel/social_bot_dest ./
EXPOSE 8080
ENV PORT=8080
CMD ["bin/social_bot_dest", "foreground"]
