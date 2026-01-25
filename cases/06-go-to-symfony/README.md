# Case 06: Go ➔ n8n ➔ Symfony
## 🏗️ Architecture
- **Origin**: Go CLI Application
- **Bridge**: n8n Webhook
- **Destination**: Symfony (PHP 8.2 Apache)

## 🚀 How to Run
This case is part of the global `docker-compose.yml`.

### Via Master Launcher (Recommended)
Run `python setup.py` in the root directory and select **Option 6**.

### Manual Start
1. Start Destination:
   ```bash
   docker-compose up -d n8n dest-symfony
   ```
2. Start Origin:
   ```bash
   cd origin
   go run main.go
   ```
