# Subscriber MQTT + receiver REST (Case 17) — imagen slim de Node.
FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]
