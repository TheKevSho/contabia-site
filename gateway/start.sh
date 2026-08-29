#!/bin/bash
# ── Hermes Gateway Entrypoint ──────────────────────────────────────────
# Generates .env files from Railway/env vars, then starts the gateway.
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-/etc/hermes}"

# ── Generate profiles/.env from prefixed env vars ──────────────────────
# Railway convention: BUSINESS__OPENROUTER_API_KEY → business profile .env
#                      TAYRONA__OPENROUTER_API_KEY  → tayrona profile .env
# Unprefixed shared vars (API_SERVER_KEY, OPENROUTER_API_KEY) go into both.

PROFILES_DIR="${HERMES_HOME}/profiles"

write_env() {
    local profile="$1"
    local env_file="${PROFILES_DIR}/${profile}/.env"
    mkdir -p "$(dirname "$env_file")"
    > "$env_file"

    local prefix="${profile^^}__"
    while IFS='=' read -r key value; do
        [[ -z "$key" ]] && continue
        if [[ "$key" == "${prefix}"* ]]; then
            local bare_key="${key#${prefix}}"
            echo "${bare_key}=${value}" >> "$env_file"
        fi
    done < <(env)

    for shared_key in API_SERVER_KEY OPENROUTER_API_KEY; do
        if ! grep -q "^${shared_key}=" "$env_file" 2>/dev/null; then
            local val="${!shared_key:-}"
            if [[ -n "$val" ]]; then
                echo "${shared_key}=${val}" >> "$env_file"
            fi
        fi
    done

    echo "[start] wrote ${env_file}"
}

write_env "business"
write_env "tayrona"

# ── Railway PORT mapping ───────────────────────────────────────────────
# Railway injects $PORT. Map it to API_SERVER_PORT if not already set.
if [[ -z "${API_SERVER_PORT:-}" && -n "${PORT:-}" ]]; then
    export API_SERVER_PORT="$PORT"
fi
# Always bind to all interfaces inside the container
export API_SERVER_HOST="${API_SERVER_HOST:-0.0.0.0}"

echo "[start] Hermes gateway starting..."
echo "[start] API_SERVER_HOST=${API_SERVER_HOST} API_SERVER_PORT=${API_SERVER_PORT:-8642}"
echo "[start] Profiles: business, tayrona (multiplexed at /p/<profile>/)"

# Start gateway in foreground
exec hermes gateway run