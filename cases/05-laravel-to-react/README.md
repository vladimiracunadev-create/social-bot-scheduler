# Case 05: Laravel ➔ n8n ➔ React
## 🏗️ Architecture
- **Origin**: Laravel (PHP Artisan Command)
- **Bridge**: n8n Webhook
- **Destination**: React (Node.js Serve)

## 🚀 How to Run
This case is part of the global `docker-compose.yml`.

### Via Master Launcher (Recommended)
Run `python setup.py` in the root directory and select **Option 5**.

### Manual Start
1. Start Destination:
   ```bash
   docker-compose up -d n8n dest-react
   ```
2. Start Origin:
   ```bash
   cd origin
   php artisan social:post
   ```
