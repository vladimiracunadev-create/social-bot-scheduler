# Emisor Zig (Case 18) — descarga el toolchain Zig 0.13 y compila un binario estático.
FROM alpine:3.20 AS build
RUN apk add --no-cache curl xz
WORKDIR /src
RUN curl -fsSL https://ziglang.org/download/0.13.0/zig-linux-x86_64-0.13.0.tar.xz | tar -xJ \
    && mv zig-linux-x86_64-0.13.0 /opt/zig
ENV PATH="/opt/zig:${PATH}"
COPY build.zig ./
COPY src ./src
COPY posts.json ./posts.json
RUN zig build -Doptimize=ReleaseSmall

FROM alpine:3.20
WORKDIR /app
COPY --from=build /src/zig-out/bin/publisher ./publisher
COPY --from=build /src/posts.json ./posts.json
CMD ["./publisher"]
