#!/usr/bin/env bash
# .devcontainer/setup-db.sh
#
# Applies workshop MySQL configuration and creates roles/users.
# Runs once as postCreateCommand when the Codespace is first built.
#
# Matches the docker-compose settings in database/docker-compose.yml so
# attendees can use identical credentials regardless of which instance they
# connect to.

set -euo pipefail

ROOT_PASSWORD="tutorial"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INIT_SQL="$REPO_ROOT/database/init/01_roles_users.sql"

# ---------------------------------------------------------------------------
# 1. Write MySQL config to match docker-compose flags
# ---------------------------------------------------------------------------

sudo tee /etc/mysql/conf.d/workshop.cnf > /dev/null <<'EOF'
[mysqld]
default_authentication_plugin  = mysql_native_password
activate_all_roles_on_login    = ON
character-set-server           = utf8mb4
collation-server               = utf8mb4_unicode_ci
EOF

# Restart so the config takes effect before we run SQL.
sudo service mysql restart

# ---------------------------------------------------------------------------
# 2. Create workshop roles and users
# ---------------------------------------------------------------------------

mysql -u root -p"${ROOT_PASSWORD}" < "$INIT_SQL"

# ---------------------------------------------------------------------------
# 3. Done
# ---------------------------------------------------------------------------

echo ""
echo "Workshop database ready.  Connect with:"
echo ""
echo "  Host     : localhost  (or 127.0.0.1)"
echo "  Port     : 3306"
echo "  User     : sailor"
echo "  Password : galley"
echo ""
echo "  Admin    : captain / bridge"
echo "  Read-only: swab    / bilge"
echo ""
