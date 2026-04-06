#!/bin/sh

set -e

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"

if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
fi

N8N_URL="${N8N_URL:-http://localhost:5678}"
N8N_OWNER_EMAIL="${N8N_OWNER_EMAIL:-change-me@local.invalid}"
N8N_OWNER_PASSWORD="${N8N_OWNER_PASSWORD:-ChangeMe-Local-Only!}"
WORKFLOW_ID="${WORKFLOW_ID:-rp7O6hcoFzsRhuBx}"
COOKIE_FILE="/tmp/n8n_cookies.txt"

printf 'Logging in to %s as %s...\n' "$N8N_URL" "$N8N_OWNER_EMAIL"
wget -q -O /dev/null \
    --save-cookies "$COOKIE_FILE" \
    --keep-session-cookies \
    --post-data "{\"email\":\"$N8N_OWNER_EMAIL\",\"password\":\"$N8N_OWNER_PASSWORD\"}" \
    --header="Content-Type: application/json" \
    "$N8N_URL/api/v1/login"

printf 'Activating workflow %s...\n' "$WORKFLOW_ID"
wget -q -O - \
    --load-cookies "$COOKIE_FILE" \
    --method=PATCH \
    --body-data='{"active":true}' \
    --header="Content-Type: application/json" \
    "$N8N_URL/api/v1/workflows/$WORKFLOW_ID"

rm -f "$COOKIE_FILE"
echo "Done."
