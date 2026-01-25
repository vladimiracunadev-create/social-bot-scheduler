# Case 07: Rust ➔ n8n ➔ Ruby
## 🏗️ Architecture
- **Origin**: Rust CLI Application (Reqwest - Blocking)
- **Bridge**: n8n Webhook
- **Destination**: Ruby Sinatra Service

## 🚀 How to Run
This case is part of the global `docker-compose.yml`.

### Via Master Launcher (Recommended)
Run `python setup.py` in the root directory and select **Option 7**.

### Manual Start
1. Start Destination:
   ```bash
   docker-compose up -d n8n dest-ruby
   ```
2. Start Origin:
   ```bash
   cd origin
   cargo run (Requires Rust installed)
   ```
