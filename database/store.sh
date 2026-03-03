#!/usr/bin/env bash
# database/store.sh
#
# Snapshot the workshop database and Spyglass data tree for distribution.
# Run this after all population scripts have been executed to pack up the
# demo dataset so attendees can download it or so it can seed a fresh host.
#
# Usage:
#   cd database/
#   bash store.sh               # mysqldump + create zip  (default: all)
#   bash store.sh dump          # only mysqldump → init/02_data.sql
#   bash store.sh pack          # only zip → SpyglassWorkshop2026Data.zip
#
# Outputs:
#   init/02_data.sql            — full mysqldump, loaded by init.sh on next start
#   SpyglassWorkshop2026Data.zip — Spyglass data tree (large raw files excluded)
#
# Requirements:
#   docker with the Compose plugin  (docker compose)
#   zip                             (sudo apt install zip)
#   MYSQL_ROOT_PASSWORD in .env     (same file used by init.sh)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE=".env"
DATA_DIR="${SCRIPT_DIR}/data"
SQL_FILE="${SCRIPT_DIR}/init/02_data.sql"
ZIP_FILE="${SCRIPT_DIR}/SpyglassWorkshop2026Data.zip"
CONTAINER="spyglass-workshop-db"

info()  { echo "[INFO]  $*"; }
warn()  { echo "[WARN]  $*" >&2; }
error() { echo "[ERROR] $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# dump: mysqldump all databases from the running workshop container.
#
# Writes to init/02_data.sql, which init.sh loads on the next `start`.
# The dump includes all schemas (spyglass_* plus the mysql system tables)
# so that user accounts and privileges are preserved across resets.
# ---------------------------------------------------------------------------

do_dump() {
    [ -f "$ENV_FILE" ] || error ".env not found — cannot get MYSQL_ROOT_PASSWORD"
    # shellcheck source=/dev/null
    source "$ENV_FILE"

    docker ps --filter "name=${CONTAINER}" --filter "status=running" --format '{{.Names}}' \
        | grep -q "${CONTAINER}" \
        || error "Container '${CONTAINER}' is not running. Start it with: bash init.sh"

    info "Dumping all databases from ${CONTAINER} → init/02_data.sql ..."
    docker exec "${CONTAINER}" \
        mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" \
            --all-databases --single-transaction --quick \
        > "$SQL_FILE"
    info "Dump complete: $(du -sh "$SQL_FILE" | cut -f1)"
}

# ---------------------------------------------------------------------------
# pack: zip the Spyglass data tree, excluding large and test-only files.
#
# Excluded paths (relative to database/data/):
#   raw/montague*.nwb               large tutorial recording (~15 GB)
#   raw/sub-despereaux*.nwb         irrelevant multi-session NWB files (~150 MB)
#   deeplabcut/projects/pytest*     CI test artifacts, not needed by attendees
#   tmp/*                           transient Spyglass scratch/lock files
#
# Empty directories are omitted automatically because `find -type f` only
# yields regular files; no zero-byte directory entries appear in the archive.
# ---------------------------------------------------------------------------

do_pack() {
    command -v zip &>/dev/null || error "zip not found. Run: sudo apt install zip"

    info "Creating SpyglassWorkshop2026Data.zip from database/data/ ..."
    rm -f "$ZIP_FILE"

    # cd into DATA_DIR so zip entries use relative paths (./analysis/...).
    # Pipe filenames via -@ to avoid shell ARG_MAX limits on large trees.
    (
        cd "$DATA_DIR"
        find . -type f \
            ! -path "*/raw/montague*.nwb" \
            ! -path "*/raw/sub-despereaux*.nwb" \
            ! -path "*/deeplabcut/projects/pytest*" \
            ! -path "*/tmp/*" \
        | zip "$ZIP_FILE" -@
    )
    info "Archive complete: $(du -sh "$ZIP_FILE" | cut -f1)"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

ACTION="${1:-all}"

case "$ACTION" in
    dump) do_dump ;;
    pack) do_pack ;;
    all)
        do_dump
        do_pack
        ;;
    *)
        echo "Usage: bash store.sh [dump|pack|all]"
        exit 1
        ;;
esac
