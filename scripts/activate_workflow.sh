#!/bin/sh
set -e
N8N_URL="http://localhost:5678"
COOKIE_FILE="/tmp/n8n_cookies.txt"

echo "Logging in..."
wget -q -O /dev/null --save-cookies "$COOKIE_FILE" --keep-session-cookies \
    --post-data '{"email":"admin@social-bot.local","password":"SocialBot2026!"}' \
    --header="Content-Type: application/json" \
    "$N8N_URL/api/v1/login"

echo "Activating workflow rp7O6hcoFzsRhuBx..."
wget -q -O - \
    --load-cookies "$COOKIE_FILE" \
    --method=PATCH \
    --body-data='{"active":true}' \
    --header="Content-Type: application/json" \
    "$N8N_URL/api/v1/workflows/rp7O6hcoFzsRhuBx"

echo "Done."
