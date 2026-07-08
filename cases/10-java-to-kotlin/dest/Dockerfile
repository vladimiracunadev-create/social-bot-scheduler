# ==================================================================================================
# Case 10 — Build multi-stage del receptor Ktor (fat-jar con Shadow) + runtime JRE slim.
# ==================================================================================================
FROM gradle:8.11-jdk21 AS build
WORKDIR /src
COPY settings.gradle.kts build.gradle.kts ./
# Precalienta dependencias (capa cacheable) antes de copiar el código.
RUN gradle --no-daemon dependencies > /dev/null 2>&1 || true
COPY src ./src
RUN gradle --no-daemon shadowJar

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /src/build/libs/*-all.jar app.jar
EXPOSE 8080
ENV PORT=8080
CMD ["java", "-jar", "app.jar"]
