# Workshop Database — Instructor Guide

This directory contains everything needed to run the shared MySQL 8 instance
for the Spyglass Workshop.  All steps below are for the **instructor machine**
only — attendees connect as the `sailor` user and do not need to run these
commands.

---

## Prerequisites

| Tool | Version | Install |
| :--- | :------ | :------ |
| Docker | ≥ 24.0 | <https://docs.docker.com/engine/install/ubuntu/> |
| Docker Compose plugin | ≥ 2.20 | `sudo apt install docker-compose-plugin` |
| nfs-kernel-server | any | `sudo apt install nfs-kernel-server` *(only for `serve-data`)* |

---

## Quick Start

```bash
# 1. Copy the example env file and set a root password.
cd database/
cp .env.example .env
#    Edit .env: set MYSQL_ROOT_PASSWORD to something secure.

# 2. (Recommended) Place a mysqldump backup in the init directory.
#    See "Loading a Database Backup" below.

# 3. Start the container (first run also loads all init scripts).
bash init.sh

# 4. The script prints the LAN IP and connection details for attendees.
```

The init scripts in `database/init/` run **once** when the data volume is
empty (i.e. on the very first `docker compose up`).  They are processed in
alphabetical order:

| File | Purpose |
| :--- | :------ |
| `01_roles_users.sql` | Creates DB roles and the `sailor` / `captain` / `swab` user accounts |
| `02_data.sql` *(optional)* | Place a mysqldump backup here to pre-populate the database |

---

## Loading a Database Backup

All demo data is loaded from a mysqldump file you supply before the workshop.

1. Copy your backup file into `database/init/` and name it `02_data.sql`:

   ```bash
   cp /path/to/spyglass_backup.sql database/init/02_data.sql
   ```

2. Start (or reset) the container so the init scripts run:

   ```bash
   bash init.sh        # first-time start
   bash init.sh reset  # if the container already ran without the backup
   ```

The backup is loaded **after** `01_roles_users.sql`, so the `sailor` account
already exists when the data is restored.

To generate a fresh backup from the running container at any time:

```bash
docker exec spyglass-workshop-db \
    mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" \
    --all-databases --single-transaction --routines --triggers \
    > database/init/02_data.sql
```

---

## Distribute Credentials to Attendees

All attendees share the same MySQL account.  Share the following over the
workshop Slack channel or projector:

```
Host:     <LAN IP printed by init.sh>
Port:     3306
User:     sailor
Password: galley
```

Attendees paste the host into the first notebook cell (`nb02-config-write`)
to configure DataJoint on their machines.  Their personal schema prefix is
derived from their laptop OS username (e.g. `alice_workshop`), so each
attendee gets an isolated namespace even though they share the `sailor`
account.

---

## Verify Remote Connectivity

From an attendee laptop (replace `<HOST>` with the IP above):

```bash
# Using mysql client:
mysql -h <HOST> -P 3306 -u sailor -pgalley -e "SELECT 1;"

# Or using Python:
python -c "
import datajoint as dj
dj.config['database.host'] = '<HOST>'
dj.config['database.user'] = 'sailor'
dj.config['database.password'] = 'galley'
dj.conn().ping()
print('Connected!')
"
```

If the connection is refused, check:

1. The container is running: `bash init.sh status`
2. Port 3306 is not blocked by a firewall:
   - Linux: `sudo ufw allow 3306/tcp`
   - macOS: System Settings → Firewall → allow incoming connections for Docker
3. The attendee is on the same network as the instructor machine.

---

## Common Operations

```bash
bash init.sh start   # Start (or restart) the container
bash init.sh stop    # Stop the container (data preserved)
bash init.sh logs    # Stream container logs
bash init.sh status  # Show container status
bash init.sh reset   # ⚠ Destroy all data and reinitialise from init scripts
```

---

## Exposing NWB Data Files (Optional)

Attendees can mount the data directory as a network filesystem so they can
point Spyglass's `base_dir` directly at it — no manual file downloads needed.

### 1. Populate the data directory

```bash
cp -r /path/to/nwb_files  database/data/
```

### 2. Start the NFS export

```bash
bash init.sh serve-data
```

This exports `database/data/` read-only via NFS and prints the exact mount
commands to share with attendees.  Requires `nfs-kernel-server`:

```bash
sudo apt install nfs-kernel-server
```

Open port 2049 if the host firewall is active:

```bash
sudo ufw allow 2049/tcp
```

### 3. Attendees mount the share

Distribute the NFS path printed by `serve-data` (format: `<HOST>:<PATH>`).

```bash
# Linux attendees
sudo mkdir -p /mnt/workshop_data
sudo mount -t nfs <HOST>:<PATH> /mnt/workshop_data

# macOS attendees
sudo mkdir -p /mnt/workshop_data
sudo mount -t nfs -o resvport,ro <HOST>:<PATH> /mnt/workshop_data
```

### 4. Attendees configure Spyglass

In their notebook or `~/.datajoint_config.json`:

```python
import spyglass as sg
sg.set_base_dir("/mnt/workshop_data")
```

Spyglass will read NWB files from the mount exactly as if they were local.

---

## Codespaces Fallback

If the LAN MySQL instance is unavailable, a GitHub Codespace can serve as a
drop-in replacement with the same credentials and schema configuration.

### Option A — Attendee runs their own Codespace (self-contained)

Each attendee opens the repo in a Codespace (browser or VS Code), and points
their DataJoint config at `localhost` instead of the instructor's IP.

1. Open the repository in a Codespace:

   ```
   https://codespaces.new/<org>/<repo>
   ```

2. The `postCreateCommand` runs automatically and creates the workshop users.

3. In the attendee's notebook, set the host to `localhost` (or `127.0.0.1`):

   ```python
   dj.config["database.host"] = "127.0.0.1"
   dj.config["database.user"] = "sailor"
   dj.config["database.password"] = "galley"
   ```

### Option B — Instructor exposes the Codespace database over TCP

The instructor starts a Codespace and forwards port 3306 to their local
machine using the GitHub CLI, then shares their LAN IP as usual.

```bash
# Instructor machine — requires gh CLI authenticated
gh cs ports forward 3306:3306 --codespace <codespace-name>
```

While this command runs, attendees connect to the instructor's LAN IP on port
3306 exactly as if the Docker container were running locally.

### Credentials (identical to the LAN instance)

```
Host     : localhost  (Option A) or instructor LAN IP (Option B)
Port     : 3306
User     : sailor
Password : galley
```

---

## Teardown

At the end of the workshop, stop all services and remove resources:

```bash
bash init.sh stop-data          # remove NFS export (if serve-data was used)
bash init.sh stop               # stop the database container
docker compose -f database/docker-compose.yml down -v   # also remove the data volume
```
