# Emisor Next.js (Case 14) — se ejecuta bajo demanda (CLI emit.mjs).
FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY . .
CMD ["node", "emit.mjs"]
