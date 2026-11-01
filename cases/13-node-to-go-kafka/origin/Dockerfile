# Productor Node/Kafka (Case 13) — se ejecuta bajo demanda.
FROM node:24-alpine
WORKDIR /app
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable && corepack prepare pnpm@11.2.2 --activate
# pnpm-workspace.yaml trae la política de supply-chain (scripts de instalación
# bloqueados, cuarentena de 24 h y pisos de versión por CVE).
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --prod --frozen-lockfile
COPY . .
CMD ["node", "producer.js"]
