# ==================================================================================================
# Case 17 — Build multi-stage del emisor Rust (binario estático pequeño).
# ==================================================================================================
FROM rust:1.99-alpine AS build
RUN apk add --no-cache musl-dev
WORKDIR /src
COPY Cargo.toml Cargo.lock ./
COPY src ./src
COPY posts.json ./
RUN cargo build --release

FROM alpine:3.23.7
WORKDIR /app
COPY --from=build /src/target/release/publisher ./publisher
COPY --from=build /src/posts.json ./posts.json
CMD ["./publisher"]
