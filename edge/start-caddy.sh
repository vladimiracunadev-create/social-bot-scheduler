#!/bin/sh

set -eu

CADDYFILE="/tmp/Caddyfile"

EDGE_N8N_HOST="${EDGE_N8N_HOST:-n8n.localhost}"
EDGE_GRAFANA_HOST="${EDGE_GRAFANA_HOST:-}"
EDGE_CASE09_HOST="${EDGE_CASE09_HOST:-}"
EDGE_BASIC_AUTH_USER="${EDGE_BASIC_AUTH_USER:-labadmin}"
EDGE_BASIC_AUTH_HASH="${EDGE_BASIC_AUTH_HASH:-}"

if [ -z "$EDGE_BASIC_AUTH_HASH" ]; then
    echo "[edge-proxy] EDGE_BASIC_AUTH_HASH is required before enabling the edge profile."
    echo "[edge-proxy] Generate it with: docker run --rm caddy:2.10.2-alpine caddy hash-password --plaintext '<your-password>'"
    exit 1
fi

cat > "$CADDYFILE" <<EOF
{
    admin off
}
EOF

write_site() {
    host="$1"
    upstream="$2"

    if [ -z "$host" ]; then
        return
    fi

    cat >> "$CADDYFILE" <<EOF

$host {
    encode zstd gzip

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        Referrer-Policy "strict-origin-when-cross-origin"
        Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:"
        Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=(), usb=(), interest-cohort=()"
    }

    basic_auth {
        $EDGE_BASIC_AUTH_USER $EDGE_BASIC_AUTH_HASH
    }

    reverse_proxy $upstream {
        header_up X-Forwarded-Host {host}
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-For {remote_host}
        flush_interval -1
    }
}
EOF
}

write_site "$EDGE_N8N_HOST" "n8n:5678"
write_site "$EDGE_GRAFANA_HOST" "grafana:3000"
write_site "$EDGE_CASE09_HOST" "dest-gateway-09:8000"

echo "[edge-proxy] Generated edge proxy config for:"
echo "[edge-proxy]  - n8n: $EDGE_N8N_HOST"
[ -n "$EDGE_GRAFANA_HOST" ] && echo "[edge-proxy]  - grafana: $EDGE_GRAFANA_HOST"
[ -n "$EDGE_CASE09_HOST" ] && echo "[edge-proxy]  - gateway: $EDGE_CASE09_HOST"

exec caddy run --config "$CADDYFILE" --adapter caddyfile
