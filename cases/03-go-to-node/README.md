# Case 03: Go ➔ n8n ➔ Node.js
## 🏗️ Architecture
- **Origin**: Go CLI Application
- **Bridge**: n8n Webhook
- **Destination**: Node.js (Express)

## 🚀 How to Run
This case is part of the global `docker-compose.yml`.

### Via Master Launcher (Recommended)
Run `python setup.py` in the root directory and select **Option 3**.

### Manual Start
1. Start Destination:
   ```bash
   docker-compose up -d n8n dest-node
   ```
2. Start Origin:
   ```bash
   cd origin
   go run main.go
   ```
