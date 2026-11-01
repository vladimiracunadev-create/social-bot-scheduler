# Emisor Apollo GraphQL (Case 16) — imagen slim, sin toolchain de build extra.
FROM node:24-alpine
WORKDIR /app
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable && corepack prepare pnpm@11.2.2 --activate
# Copiamos manifiestos primero para aprovechar la cache de capas de Docker.
# pnpm-workspace.yaml trae la política de supply-chain (scripts de instalación
# bloqueados, cuarentena de 24 h y pisos de versión por CVE).
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --prod --frozen-lockfile
COPY . .
EXPOSE 4016
CMD ["node", "index.js"]
