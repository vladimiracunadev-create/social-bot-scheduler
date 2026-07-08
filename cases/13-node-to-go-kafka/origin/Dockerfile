# Productor Node/Kafka (Case 13) — se ejecuta bajo demanda.
FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY . .
CMD ["node", "producer.js"]
