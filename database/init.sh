#!/usr/bin/env bash
# database/init.sh
#
# Manages the workshop MySQL container and the NFS data share.
# Assumes an Ubuntu host machine.
#
# Usage:
#   cd database/
#   cp .env.example .env          # then edit MYSQL_ROOT_PASSWORD
#   bash init.sh                  # start the database
#   bash init.sh stop             # gracefully stop the database
#   bash init.sh reset            # stop, remove volume, restart fresh
#   bash init.sh serve-data       # export database/data/ via NFS
#   bash init.sh stop-data        # remove the NFS export
#
# Requirements:
#   docker with the Compose plugin  (docker compose)
#   nfs-kernel-server               (sudo apt install nfs-kernel-server)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
SERVICE="mysql"
DATA_DIR="${SCRIPT_DIR}/data"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

info()  { echo "[INFO]  $*"; }
warn()  { echo "[WARN]  $*" >&2; }
error() { echo "[ERROR] $*" >&2; exit 1; }

lan_ip() {
    ip route get 1.1.1.1 2>/dev/null | awk '/src/ {print $7; exit}'
}

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

command -v docker &>/dev/null || error "docker not found. See https://docs.docker.com/engine/install/"

docker compose version &>/dev/null \
    || error "Docker Compose plugin not found. Run: sudo apt install docker-compose-plugin"

if [ ! -f "$ENV_FILE" ]; then
    warn "'.env' not found — copying from '.env.example'."
    warn "Edit '$SCRIPT_DIR/.env' and set MYSQL_ROOT_PASSWORD before continuing."
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
        info "Database is ready.  Share these details with attendees:"
        echo ""
        echo "  Host     : $IP"
        echo "  Port     : 3306"
        echo "  User     : sailor"
        echo "  Password : galley"
        echo ""
        echo "  Attendees: paste the Host into notebook cell nb02-config-write."
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

    serve-data)
        command -v exportfs &>/dev/null \
            || error "nfs-kernel-server not found. Run: sudo apt install nfs-kernel-server"

        mkdir -p "$DATA_DIR"
        IP="$(lan_ip)"

        if ! grep -qF "$DATA_DIR" /etc/exports 2>/dev/null; then
            echo "$DATA_DIR *(ro,sync,no_subtree_check)" | sudo tee -a /etc/exports
        fi
        sudo exportfs -ra
        sudo systemctl start nfs-kernel-server

        info "NFS export active.  Share these details with attendees:"
        echo ""
        echo "  # Mount the data share"
        echo "  sudo mkdir -p /mnt/workshop_data"
        echo "  sudo mount -t nfs $IP:$DATA_DIR /mnt/workshop_data"
        echo ""
        echo "  # Configure Spyglass"
        echo "  import spyglass as sg"
        echo "  sg.set_base_dir('/mnt/workshop_data')"
        echo ""
        ;;

    stop-data)
        sudo exportfs -ua
        sudo systemctl stop nfs-kernel-server
        info "NFS export stopped."
        ;;

    *)
        echo "Usage: bash init.sh [start|stop|reset|logs|status|serve-data|stop-data]"
        exit 1
        ;;
esac
