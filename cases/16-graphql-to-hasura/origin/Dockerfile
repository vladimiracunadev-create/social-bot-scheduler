# Emisor Apollo GraphQL (Case 16) — imagen slim, sin toolchain de build extra.
FROM node:20-alpine
WORKDIR /app
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable && corepack prepare pnpm@10.0.0 --activate
# Copiamos manifiestos primero para aprovechar la cache de capas de Docker.
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --prod
COPY . .
EXPOSE 4016
CMD ["node", "index.js"]
