# Emisor Spring Boot (Case 10) — build multi-stage; se ejecuta bajo demanda.
FROM gradle:8.11-jdk21 AS build
WORKDIR /src
COPY settings.gradle.kts build.gradle.kts ./
COPY src ./src
COPY posts.json ./posts.json
RUN gradle --no-daemon bootJar

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /src/build/libs/*.jar app.jar
COPY --from=build /src/posts.json ./posts.json
CMD ["java", "-jar", "app.jar"]
