# Emisor Swift (Case 20) — build Swift en Linux; se ejecuta bajo demanda.
FROM swift:6.0 AS build
WORKDIR /src
COPY Package.swift ./
COPY Sources ./Sources
COPY posts.json ./
RUN swift build -c release

FROM swift:6.0-slim
WORKDIR /app
COPY --from=build /src/.build/release/Publisher ./Publisher
COPY --from=build /src/posts.json ./posts.json
CMD ["./Publisher"]
