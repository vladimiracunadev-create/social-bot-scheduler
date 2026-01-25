# Case 01: Python ➔ n8n ➔ PHP
## 🏗️ Architecture
- **Origin**: Python Script (Standard Library + Requests)
- **Bridge**: n8n Webhook
- **Destination**: PHP 8.2 (Apache)

## 🚀 How to Run
This case is part of the global `docker-compose.yml`.

### Via Master Launcher (Recommended)
Run `python setup.py` in the root directory and select **Option 1**.

### Manual Start
1. Start Destination:
   ```bash
   docker-compose up -d n8n dest-php
   ```
2. Start Origin:
   ```bash
   cd origin
   # Ensure .env is configured
   python bot.py
   ```
