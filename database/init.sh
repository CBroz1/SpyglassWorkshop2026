#!/usr/bin/env bash
# database/init.sh
#
# Starts the workshop MySQL 8 container and prints connection details for
# attendees.  Run this script once before the workshop begins.
#
# Usage:
#   cd database/
#   cp .env.example .env          # then edit MYSQL_ROOT_PASSWORD
#   bash init.sh                  # start the database
#   bash init.sh stop             # gracefully stop the database
#   bash init.sh reset            # stop, remove volume, restart fresh
#
# Requirements: docker with the Compose plugin (docker compose).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
SERVICE="mysql"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

info()  { echo "[INFO]  $*"; }
warn()  { echo "[WARN]  $*" >&2; }
error() { echo "[ERROR] $*" >&2; exit 1; }

require_command() {
    command -v "$1" &>/dev/null || error "'$1' not found. Please install it."
}

# Get the first non-loopback LAN IP address (Linux and macOS).
lan_ip() {
    if command -v ip &>/dev/null; then
        ip route get 1.1.1.1 2>/dev/null \
            | awk '/src/ {print $7; exit}' \
            || hostname -I 2>/dev/null | awk '{print $1}'
    elif command -v ifconfig &>/dev/null; then
        ifconfig \
            | awk '/inet / && !/127\.0\.0\.1/ {print $2; exit}' \
            | sed 's/addr://'
    else
        echo "<unknown>"
    fi
}

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

require_command docker

if ! docker compose version &>/dev/null; then
    error "Docker Compose plugin not found. Run: docker install compose"
fi

if [ ! -f "$ENV_FILE" ]; then
    warn "'.env' file not found.  Copying '.env.example' → '.env'."
    warn "Edit '$SCRIPT_DIR/.env' and set a strong MYSQL_ROOT_PASSWORD."
    cp .env.example "$ENV_FILE"
fi

# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

ACTION="${1:-start}"

case "$ACTION" in

    start)
        info "Starting workshop database container..."
        docker compose -f "$COMPOSE_FILE" up -d --wait

        IP="$(lan_ip)"
        PORT=3306
        info "Database is ready."
        echo ""
        echo "  ┌─────────────────────────────────────────────────────┐"
        echo "  │  Connection details for attendees                   │"
        echo "  ├─────────────────────────────────────────────────────┤"
        printf  "  │  Host     : %-38s│\n" "$IP"
        printf  "  │  Port     : %-38s│\n" "$PORT"
        echo "  │  User     : sailor                                 │"
        echo "  │  Password : galley                                  │"
        echo "  └─────────────────────────────────────────────────────┘"
        echo ""
        echo "  Share the Host address above with attendees."
        echo "  They should replace HOST in notebook cell nb02-config-write."
        echo ""
        ;;

    stop)
        info "Stopping workshop database container..."
        docker compose -f "$COMPOSE_FILE" stop
        info "Container stopped.  Data volume preserved."
        ;;

    reset)
        warn "This will destroy all data in the database volume!"
        read -rp "Type 'yes' to confirm: " CONFIRM
        [ "$CONFIRM" = "yes" ] || { info "Aborted."; exit 0; }
        docker compose -f "$COMPOSE_FILE" down -v
        info "Volume removed.  Re-running init scripts on next start."
        docker compose -f "$COMPOSE_FILE" up -d --wait
        info "Fresh database is ready."
        ;;

    logs)
        docker compose -f "$COMPOSE_FILE" logs -f "$SERVICE"
        ;;

    status)
        docker compose -f "$COMPOSE_FILE" ps
        ;;

    *)
        echo "Usage: bash init.sh [start|stop|reset|logs|status]"
        exit 1
        ;;
esac
