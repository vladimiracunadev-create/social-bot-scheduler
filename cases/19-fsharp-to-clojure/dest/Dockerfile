# ==================================================================================================
# Case 19 — Build del receptor Clojure/Ring + XTDB (uberjar con Leiningen).
# ==================================================================================================
FROM clojure:temurin-21-lein AS build
WORKDIR /src
COPY project.clj ./
RUN lein deps
COPY src ./src
COPY public ./public
RUN lein uberjar

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /src/target/receiver-standalone.jar ./app.jar
COPY --from=build /src/public ./public
EXPOSE 8080
ENV PORT=8080
CMD ["java", "-jar", "app.jar"]
