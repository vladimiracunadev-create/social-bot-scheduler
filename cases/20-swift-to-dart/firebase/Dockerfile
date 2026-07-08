# ==================================================================================================
# Case 20 — Emulador de Firestore. firebase-tools exige JDK 21+; base temurin-21 + Node 20.
# ==================================================================================================
FROM eclipse-temurin:21-jdk-jammy
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g firebase-tools
WORKDIR /app
COPY firebase.json firestore.rules ./
# Pre-descarga el JAR del emulador de Firestore para que el arranque no dependa de red.
RUN firebase setup:emulators:firestore
EXPOSE 8200
CMD ["firebase", "emulators:start", "--only", "firestore", "--project", "demo-lab"]
