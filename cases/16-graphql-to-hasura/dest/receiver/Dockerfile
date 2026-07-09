# Micro-receiver Case 16 — imagen slim, sólo runtime de Node.
FROM node:20-alpine
WORKDIR /app
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable && corepack prepare pnpm@10.0.0 --activate
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --prod
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]
