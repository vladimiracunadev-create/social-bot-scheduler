# Emisor Apollo GraphQL (Case 16) — imagen slim, sin toolchain de build extra.
FROM node:20-alpine
WORKDIR /app
# Copiamos manifiestos primero para aprovechar la cache de capas de Docker.
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY . .
EXPOSE 4016
CMD ["node", "index.js"]
