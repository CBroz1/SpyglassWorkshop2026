#!/usr/bin/env bash
# database/init.sh
#
# Manages the workshop MySQL container and the NFS data share.
# Assumes an Ubuntu host machine.
#
# Usage:
#   cd database/
#   cp .env.example .env          # then edit MYSQL_ROOT_PASSWORD
#   bash init.sh                  # start DB, load data, serve NFS, symlink /tmp/workshop
#   bash init.sh stop             # gracefully stop the database
#   bash init.sh reset            # stop, remove volume, restart fresh
#   bash init.sh load-data        # (re-)load init/02_data.sql into running container
#   bash init.sh serve-data       # (re-)export database/data/ via NFS
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
EXPORT_PATH="/tmp/spyglass_data"   # short symlink shown to attendees in mount cmd

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

info()  { echo "[INFO]  $*"; }
warn()  { echo "[WARN]  $*" >&2; }
error() { echo "[ERROR] $*" >&2; exit 1; }

lan_ip() {
    ip route get 1.1.1.1 2>/dev/null | awk '/src/ {print $7; exit}'
}

# Run mysql inside the workshop container, suppressing the noisy
# "password on command line" warning that appears on every invocation.
db_exec() {
    docker exec -i spyglass-workshop-db \
        mysql "$@" 2> >(grep -v "Using a password on the command line interface can be insecure" >&2)
}

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

command -v docker &>/dev/null || error "docker not found. Please install"

docker compose version &>/dev/null \
    || error "Missing plugin. Run: sudo apt install docker-compose-plugin"

if [ ! -f "$ENV_FILE" ]; then
    warn "'.env' not found — copying from '.env.example'."
    warn "Edit '$SCRIPT_DIR/.env' and set MYSQL_ROOT_PASSWORD"
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

        # Load 02_data.sql if present, then re-apply roles/users
        # (the dump may include the mysql schema and overwrite accounts)
        SQL_FILE="${SCRIPT_DIR}/init/02_data.sql"
        ROLES_FILE="${SCRIPT_DIR}/init/01_roles_users.sql"
        if [ -f "$SQL_FILE" ]; then
            # shellcheck source=/dev/null
            source "$ENV_FILE"
            BASE_NAME="$(basename "$SQL_FILE")"
            info "Loading ${BASE_NAME} into container ..."
            db_exec -u root -p"${MYSQL_ROOT_PASSWORD}" < "$SQL_FILE"
            info "Re-applying roles and users ..."
            db_exec -u root -p"${MYSQL_ROOT_PASSWORD}" < "$ROLES_FILE"
            info "Data loaded."
        else
            warn "init/02_data.sql not found — skipping data load."
        fi

        # Start NFS export if nfs-kernel-server is installed
        if command -v exportfs &>/dev/null; then
            mkdir -p "$DATA_DIR"
            ln -sfn "$DATA_DIR" "$EXPORT_PATH"
            if ! grep -qF "$EXPORT_PATH" /etc/exports 2>/dev/null; then
                echo "$EXPORT_PATH *(rw,sync,no_subtree_check,all_squash,anonuid=$(id -u),anongid=$(id -g))" | sudo tee -a /etc/exports
            fi
            sudo exportfs -ra
            sudo systemctl start nfs-kernel-server
            info "NFS export active."
        else
            warn "nfs-kernel-server not installed — skipping NFS export."
            warn "  sudo apt install nfs-kernel-server"
        fi

        # Symlink this directory to /tmp/workshop for easy access
        ln -sfn "$SCRIPT_DIR" /tmp/workshop
        info "Shortcut created: /tmp/workshop -> $SCRIPT_DIR"

        IP="$(lan_ip)"
        echo ""
        echo "  ┌─────────────────────────────────────────────┐"
        echo "  │  Workshop ready                             │"
        echo "  │                                             │"
        echo "  │  DB host     : $IP"
        echo "  │  DB port     : 3306                         │"
        echo "  │  User        : sailor  /  galley            │"
        echo "  │                                             │"
        echo "  │  Mount cmd   : sudo mount -t nfs \          │"
        echo "  │    $IP:$EXPORT_PATH ~/spyglass_data"
        echo "  │                                             │"
        echo "  └─────────────────────────────────────────────┘"
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

    load-data)
        SQL_FILE="${SCRIPT_DIR}/init/02_data.sql"
        ROLES_FILE="${SCRIPT_DIR}/init/01_roles_users.sql"
        [ -f "$SQL_FILE" ] || error "02_data.sql not found at ${SQL_FILE}"
        # shellcheck source=/dev/null
        source "$ENV_FILE"
        info "Loading ${SQL_FILE} into running container ..."
        db_exec -u root -p"${MYSQL_ROOT_PASSWORD}" < "$SQL_FILE"
        info "Re-applying roles and users ..."
        db_exec -u root -p"${MYSQL_ROOT_PASSWORD}" < "$ROLES_FILE"
        info "Data loaded successfully."
        ;;

    logs)
        docker compose -f "$COMPOSE_FILE" logs -f "$SERVICE"
        ;;

    status)
        docker compose -f "$COMPOSE_FILE" ps
        ;;

    serve-data)
        command -v exportfs &>/dev/null \
            || error "Missing nfs. Run: sudo apt install nfs-kernel-server"

        mkdir -p "$DATA_DIR"
        ln -sfn "$DATA_DIR" "$EXPORT_PATH"
        IP="$(lan_ip)"

        if ! grep -qF "$EXPORT_PATH" /etc/exports 2>/dev/null; then
            echo "$EXPORT_PATH *(rw,sync,no_subtree_check,all_squash,anonuid=$(id -u),anongid=$(id -g))" | sudo tee -a /etc/exports
        fi
        sudo exportfs -ra
        sudo systemctl start nfs-kernel-server

        info "NFS export active.  Share these details with attendees:"
        echo ""
        echo "  mkdir -p ~/spyglass_data"
        echo "  sudo mount -t nfs $IP:$EXPORT_PATH ~/spyglass_data"
        echo ""
        ;;

    stop-data)
        sudo exportfs -ua
        sudo systemctl stop nfs-kernel-server
        info "NFS export stopped."
        ;;

    *)
        echo "Usage: bash init.sh [start|stop|reset|load-data|logs|status|serve-data|stop-data]"
        exit 1
        ;;
esac
