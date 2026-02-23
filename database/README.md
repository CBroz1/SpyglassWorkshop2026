# Workshop Database — Instructor Guide

This directory contains everything needed to run the shared MySQL 8 instance
for the Spyglass Workshop.  All steps below are for the **instructor machine**
only — attendees connect as the `sailor` user and do not need to run these
commands.

---

## Prerequisites

| Tool | Version | Install |
| :--- | :------ | :------ |
| Docker | ≥ 24.0 | <https://docs.docker.com/engine/install/> |
| Docker Compose plugin | ≥ 2.20 | included with Docker Desktop; `apt install docker-compose-plugin` on Linux |

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

If attendees need to download NWB files from the instructor machine for
ingestion exercises:

1. Create `database/data/` and copy NWB files into it.
2. Uncomment the `DATA_DIR` volume line in `docker-compose.yml` (the files
   will be mounted read-only at `/mnt/nwb_data` inside the container).
3. Serve them over HTTP so attendees can download without shell access:

   ```bash
   python3 -m http.server 8080 --directory database/data/
   # Attendees download at: http://<HOST>:8080/
   ```

---

## Teardown

At the end of the workshop, stop and remove all resources:

```bash
docker compose -f database/docker-compose.yml down -v
# -v also removes the named data volume.
```
