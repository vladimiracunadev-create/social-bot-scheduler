#!/bin/sh

set -e

WORKFLOWS_DIR="/data/workflows"
N8N_URL="${N8N_INTERNAL_URL:-http://localhost:5678}"
N8N_PUBLIC_URL="${N8N_EDITOR_BASE_URL:-${N8N_WEBHOOK_URL:-http://localhost:5678}}"
MARKER_FILE="/home/node/.n8n/.workflows_imported"
N8N_OWNER_EMAIL="${N8N_OWNER_EMAIL:-change-me@local.invalid}"
N8N_OWNER_PASSWORD="${N8N_OWNER_PASSWORD:-ChangeMe-Local-Only!}"

log_info() {
    echo "[n8n-auto-setup] INFO  $1"
}

log_warn() {
    echo "[n8n-auto-setup] WARN  $1"
}

log_step() {
    echo "[n8n-auto-setup] STEP  $1"
}

contains_placeholder() {
    echo "$1" | grep -qi "change-me\|local.invalid"
}

build_owner_payload() {
    cat <<EOF
{"email":"$N8N_OWNER_EMAIL","firstName":"Social","lastName":"Bot","password":"$N8N_OWNER_PASSWORD"}
EOF
}

build_login_payload() {
    cat <<EOF
{"email":"$N8N_OWNER_EMAIL","password":"$N8N_OWNER_PASSWORD"}
EOF
}

if contains_placeholder "$N8N_OWNER_EMAIL" || contains_placeholder "$N8N_OWNER_PASSWORD"; then
    log_warn "N8N owner credentials still look like placeholders. Replace them in .env before sharing the lab."
fi

if [ -f "$MARKER_FILE" ]; then
    log_info "Workflows already imported. Starting n8n normally."
    exec n8n start
fi

log_step "Starting n8n in background for bootstrap."
n8n start &
N8N_PID=$!

log_step "Waiting for n8n health endpoint."
MAX_RETRIES=30
RETRY_COUNT=0

while [ "$RETRY_COUNT" -lt "$MAX_RETRIES" ]; do
    if wget -q --spider "$N8N_URL/healthz" 2>/dev/null; then
        log_info "n8n is ready on attempt $((RETRY_COUNT + 1))/$MAX_RETRIES."
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 2
done

if [ "$RETRY_COUNT" -eq "$MAX_RETRIES" ]; then
    log_warn "n8n did not become healthy in time. Handing control back to the main process."
    wait "$N8N_PID"
    exit $?
fi

log_step "Creating owner account if needed."
SETUP_RESPONSE=$(
    wget -q -O - \
        --post-data "$(build_owner_payload)" \
        --header="Content-Type: application/json" \
        "$N8N_URL/api/v1/owner/setup" 2>/dev/null || echo "already-setup"
)

if echo "$SETUP_RESPONSE" | grep -q "already-setup\|error"; then
    log_info "Owner already configured or setup endpoint no longer required."
else
    log_info "Owner configured for $N8N_OWNER_EMAIL."
fi

log_step "Authenticating to import workflows."
COOKIE_FILE="/tmp/n8n_cookies.txt"

wget -q -O /dev/null \
    --save-cookies "$COOKIE_FILE" \
    --keep-session-cookies \
    --post-data "$(build_login_payload)" \
    --header="Content-Type: application/json" \
    "$N8N_URL/api/v1/login" 2>/dev/null || true

log_step "Importing workflows from $WORKFLOWS_DIR."
IMPORTED=0

if [ -d "$WORKFLOWS_DIR" ]; then
    for workflow_file in "$WORKFLOWS_DIR"/*.json; do
        if [ -f "$workflow_file" ]; then
            WORKFLOW_NAME=$(basename "$workflow_file" .json)
            log_step "Importing $WORKFLOW_NAME."

            IMPORT_RESPONSE=$(
                wget -q -O - \
                    --load-cookies "$COOKIE_FILE" \
                    --post-file="$workflow_file" \
                    --header="Content-Type: application/json" \
                    "$N8N_URL/api/v1/workflows" 2>/dev/null || echo "import-error"
            )

            if echo "$IMPORT_RESPONSE" | grep -q "import-error"; then
                log_warn "Import failed for $WORKFLOW_NAME (it may already exist)."
            else
                WORKFLOW_ID=$(echo "$IMPORT_RESPONSE" | sed -n 's/.*"id":"\{0,1\}\([^",}]*\)"\{0,1\}.*/\1/p' | head -1)

                if [ -n "$WORKFLOW_ID" ]; then
                    wget -q -O /dev/null \
                        --load-cookies "$COOKIE_FILE" \
                        --method=PATCH \
                        --body-data='{"active":true}' \
                        --header="Content-Type: application/json" \
                        "$N8N_URL/api/v1/workflows/$WORKFLOW_ID" 2>/dev/null || true

                    log_info "$WORKFLOW_NAME imported and activated (ID: $WORKFLOW_ID)."
                    IMPORTED=$((IMPORTED + 1))
                else
                    log_warn "Could not extract an ID for $WORKFLOW_NAME."
                fi
            fi
        fi
    done
fi

log_info "Workflow import completed: $IMPORTED configured."
touch "$MARKER_FILE"
rm -f "$COOKIE_FILE"

log_info "UI: $N8N_PUBLIC_URL"
log_info "Owner email: $N8N_OWNER_EMAIL"
log_info "Owner password is sourced from environment variables."

wait "$N8N_PID"
