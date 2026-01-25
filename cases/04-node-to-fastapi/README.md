# Case 04: Node.js ➔ n8n ➔ FastAPI
## 🏗️ Architecture
- **Origin**: Node.js Script (Axios)
- **Bridge**: n8n Webhook
- **Destination**: Python FastAPI (Uvicorn)

## 🚀 How to Run
This case is part of the global `docker-compose.yml`.

### Via Master Launcher (Recommended)
Run `python setup.py` in the root directory and select **Option 4**.

### Manual Start
1. Start Destination:
   ```bash
   docker-compose up -d n8n dest-fastapi
   ```
2. Start Origin:
   ```bash
   cd origin
   npm install
   node index.js
   ```
