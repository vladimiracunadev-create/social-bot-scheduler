# ==================================================================================================
# Case 18 — Build multi-stage del receptor Crystal/Kemal.
# ==================================================================================================
FROM crystallang/crystal:1.14-alpine AS build
WORKDIR /src
COPY shard.yml ./
RUN shards install
COPY src ./src
COPY public ./public
RUN crystal build src/app.cr --release --no-debug -o app

FROM crystallang/crystal:1.14-alpine
WORKDIR /app
COPY --from=build /src/app ./app
COPY --from=build /src/public ./public
EXPOSE 8080
ENV PORT=8080
CMD ["./app"]
