# Case 08: C# ➔ n8n ➔ Flask
## 🏗️ Architecture
- **Origin**: C# Console Application (.NET 6.0)
- **Bridge**: n8n Webhook
- **Destination**: Python Flask Application

## 🚀 How to Run
This case is part of the global `docker-compose.yml`.

### Via Master Launcher (Recommended)
Run `python setup.py` in the root directory and select **Option 8**.

### Manual Start
1. Start Destination:
   ```bash
   docker-compose up -d n8n dest-flask
   ```
2. Start Origin:
   ```bash
   cd origin
   # Requires .NET SDK 6.0+
   dotnet run
   ```
