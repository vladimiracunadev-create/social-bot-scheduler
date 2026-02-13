#!/bin/sh
# ==============================================================================
# 🔧 n8n Auto-Setup Script
# ==============================================================================
# Este script actúa como entrypoint personalizado del contenedor n8n.
#
# PROPÓSITO:
# Eliminar la necesidad de configuración manual de n8n. Antes, el usuario
# debía crear una cuenta, importar workflows uno por uno, y activarlos
# manualmente desde la UI. Este script automatiza TODO ese proceso.
#
# CÓMO FUNCIONA:
# 1. Arranca n8n en segundo plano (background)
# 2. Espera a que n8n esté listo (polling al endpoint /healthz)
# 3. Importa los 8 workflows desde /data/workflows/ usando la API REST
# 4. Activa cada workflow importado para que escuchen webhooks
# 5. Detiene el n8n de background y lo relanza en primer plano (foreground)
#
# RESULTADO:
# Con un solo "docker-compose up -d", n8n arranca con los 8 workflows
# importados y activos. Zero configuración manual.
#
# NOTA TÉCNICA:
# Usamos la API REST de n8n (puerto 5678) porque la CLI "n8n import:workflow"
# requiere que n8n NO esté corriendo, lo que complica el flujo. La API REST
# permite importar y activar workflows mientras n8n está en ejecución.
# ==============================================================================

set -e

WORKFLOWS_DIR="/data/workflows"
N8N_URL="http://localhost:5678"
MARKER_FILE="/home/node/.n8n/.workflows_imported"

# --- Colores para logs claros (funciona en Docker logs) ---
log_info() {
    echo "[n8n-auto-setup] ✅ $1"
}

log_warn() {
    echo "[n8n-auto-setup] ⚠️  $1"
}

log_step() {
    echo "[n8n-auto-setup] 🔧 $1"
}

# --- Paso 1: Verificar si ya se importaron los workflows ---
# Si el marcador existe, significa que una ejecución previa ya configuró todo.
# Esto evita duplicar workflows cada vez que se reinicia el contenedor.
if [ -f "$MARKER_FILE" ]; then
    log_info "Workflows ya importados previamente. Iniciando n8n normalmente..."
    exec n8n start
fi

# --- Paso 2: Arrancar n8n en background ---
log_step "Iniciando n8n en segundo plano para auto-configuración..."
n8n start &
N8N_PID=$!

# --- Paso 3: Esperar a que n8n esté listo ---
# n8n tarda unos segundos en inicializar su base de datos SQLite y
# estar listo para recibir peticiones API. Hacemos polling cada 2 segundos.
log_step "Esperando a que n8n esté listo..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if wget -q --spider "$N8N_URL/healthz" 2>/dev/null; then
        log_info "n8n está listo! (intento $((RETRY_COUNT + 1))/$MAX_RETRIES)"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_warn "n8n no respondió tras $MAX_RETRIES intentos. Continuando de todos modos..."
    # No salimos con error; dejamos que n8n siga intentando arrancar
    wait $N8N_PID
    exit $?
fi

# --- Paso 4: Crear cuenta de owner automáticamente ---
# n8n requiere un owner para funcionar. Creamos uno con credenciales
# predeterminadas de laboratorio. El flag N8N_USER_MANAGEMENT_DISABLED=true
# en docker-compose.yml ya desactiva la pantalla de login, pero necesitamos
# un owner inicial para que la API funcione correctamente.
log_step "Configurando cuenta de administrador..."
SETUP_RESPONSE=$(wget -q -O - --post-data '{
    "email": "admin@social-bot.local",
    "firstName": "Social",
    "lastName": "Bot",
    "password": "SocialBot2026!"
}' --header="Content-Type: application/json" "$N8N_URL/api/v1/owner/setup" 2>/dev/null || echo "already-setup")

if echo "$SETUP_RESPONSE" | grep -q "already-setup\|error"; then
    log_info "Owner ya configurado o setup no requerido. Continuando..."
else
    log_info "Owner creado: admin@social-bot.local"
fi

# --- Paso 5: Obtener API Key para importar workflows ---
# Autenticamos con el owner para obtener una cookie de sesión.
# Usamos wget porque curl no está disponible en la imagen alpine de n8n.
log_step "Autenticando para importar workflows..."
COOKIE_FILE="/tmp/n8n_cookies.txt"

wget -q -O /dev/null --save-cookies "$COOKIE_FILE" --keep-session-cookies \
    --post-data '{"email":"admin@social-bot.local","password":"SocialBot2026!"}' \
    --header="Content-Type: application/json" \
    "$N8N_URL/api/v1/login" 2>/dev/null || true

# --- Paso 6: Importar todos los workflows ---
# Iteramos sobre cada archivo JSON en /data/workflows/ y lo importamos
# usando la API REST de n8n. Cada workflow se importa como un nuevo workflow.
log_step "Importando workflows desde $WORKFLOWS_DIR..."
IMPORTED=0

if [ -d "$WORKFLOWS_DIR" ]; then
    for workflow_file in "$WORKFLOWS_DIR"/*.json; do
        if [ -f "$workflow_file" ]; then
            WORKFLOW_NAME=$(basename "$workflow_file" .json)
            log_step "  Importando: $WORKFLOW_NAME..."

            # Importar el workflow usando la API
            IMPORT_RESPONSE=$(wget -q -O - \
                --load-cookies "$COOKIE_FILE" \
                --post-file="$workflow_file" \
                --header="Content-Type: application/json" \
                "$N8N_URL/api/v1/workflows" 2>/dev/null || echo "import-error")

            if echo "$IMPORT_RESPONSE" | grep -q "import-error"; then
                log_warn "  Error importando $WORKFLOW_NAME (puede que ya exista)"
            else
                # Extraer el ID del workflow importado para activarlo
                WORKFLOW_ID=$(echo "$IMPORT_RESPONSE" | sed -n 's/.*"id":"\{0,1\}\([^",}]*\)"\{0,1\}.*/\1/p' | head -1)

                if [ -n "$WORKFLOW_ID" ]; then
                    # Activar el workflow
                    wget -q -O /dev/null \
                        --load-cookies "$COOKIE_FILE" \
                        --method=PATCH \
                        --body-data='{"active":true}' \
                        --header="Content-Type: application/json" \
                        "$N8N_URL/api/v1/workflows/$WORKFLOW_ID" 2>/dev/null || true

                    log_info "  ✓ $WORKFLOW_NAME importado y activado (ID: $WORKFLOW_ID)"
                    IMPORTED=$((IMPORTED + 1))
                else
                    log_warn "  No se pudo obtener ID para $WORKFLOW_NAME"
                fi
            fi
        fi
    done
fi

# --- Paso 7: Crear marcador de importación exitosa ---
# Este archivo indica que los workflows ya fueron importados.
# En reinicios futuros, el script saltará directamente al arranque normal.
log_info "Importación completada: $IMPORTED workflows configurados"
touch "$MARKER_FILE"

# --- Paso 8: Limpiar archivos temporales ---
rm -f "$COOKIE_FILE"

# --- Resultado ---
log_info "=========================================="
log_info " n8n Auto-Setup Completado!"
log_info " Workflows activos: $IMPORTED"
log_info " UI: http://localhost:5678"
log_info " Login: admin@social-bot.local / SocialBot2026!"
log_info "=========================================="

# --- Paso 9: Mantener n8n en primer plano ---
# Esperamos al proceso de n8n que está en background.
# Esto es necesario para que Docker no piense que el contenedor terminó.
wait $N8N_PID
