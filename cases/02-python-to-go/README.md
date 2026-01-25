# Case 02: Python ➔ n8n ➔ Go
## 🏗️ Architecture
- **Origin**: Python Script
- **Bridge**: n8n Webhook
- **Destination**: Go 1.21 (Gin Gonic)

## 🚀 How to Run
This case is part of the global `docker-compose.yml`.

### Via Master Launcher (Recommended)
Run `python setup.py` in the root directory and select **Option 2**.

### Manual Start
1. Start Destination:
   ```bash
   docker-compose up -d n8n dest-go
   ```
2. Start Origin:
   ```bash
   cd origin
   python bot.py
   ```
