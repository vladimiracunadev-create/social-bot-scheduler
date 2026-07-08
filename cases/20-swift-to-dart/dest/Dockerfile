# ==================================================================================================
# Case 20 — Build del receptor Dart/Shelf (compilado AOT a binario nativo).
# ==================================================================================================
FROM dart:stable AS build
WORKDIR /src
COPY pubspec.yaml ./
RUN dart pub get
COPY bin ./bin
COPY public ./public
RUN dart pub get --offline && dart compile exe bin/server.dart -o server

FROM debian:stable-slim
WORKDIR /app
COPY --from=build /src/server ./server
COPY --from=build /src/public ./public
EXPOSE 8080
ENV PORT=8080
CMD ["./server"]
