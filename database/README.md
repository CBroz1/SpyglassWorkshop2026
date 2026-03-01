# Workshop Database — Instructor Guide

This directory contains everything needed to run the shared MySQL 8 instance for
the Spyglass Workshop. All steps below are for the **instructor machine** only —
attendees connect as the `sailor` user and do not need to run these commands.

______________________________________________________________________

## Prerequisites

| Tool                  | Version | Install                                          |
| :-------------------- | :------ | :----------------------------------------------- |
| Docker                | ≥ 24.0  | <https://docs.docker.com/engine/install/ubuntu/> |
| Docker Compose plugin | ≥ 2.20  | `sudo apt install docker-compose-plugin`         |
| nfs-kernel-server     | any     | `sudo apt install nfs-kernel-server`[^1]         |

\[^1\]: Only for `serve-data`

______________________________________________________________________

## Quick Start

```bash
# 1. Copy the example env file and set a root password.
cd database/
cp .env.example .env
#    Edit .env: set MYSQL_ROOT_PASSWORD to something secure.

# 2. Place the mysqldump backup in the init directory.
#    See "Loading a Database Backup" below.

# 3. Run the single start command (from any working directory after first run).
bash init.sh
# or, after the symlink is created:
bash /tmp/workshop/init.sh
```

A single `bash init.sh` does everything in sequence:

1. Starts the MySQL container and waits for it to be healthy
2. Loads `init/02_data.sql` into the running container (skipped with a warning
   if absent)
3. Starts the NFS data share (skipped with a warning if `nfs-kernel-server` is
   not installed)
4. Creates `/tmp/workshop → database/` so subsequent commands are easy to type
5. Prints a summary box with the DB host, credentials, and NFS mount command

The init scripts in `database/init/` run **once** when the data volume is empty
(i.e. on the very first `docker compose up`). They are processed in alphabetical
order:

| File                       | Purpose                                |
| :------------------------- | :------------------------------------- |
| `01_roles_users.sql`       | Creates DB roles and the user accounts |
| `02_data.sql` *(optional)* | Pre-populate database with mysqldump   |

______________________________________________________________________

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

### Loading into an already-running container

If the container started without `02_data.sql` (e.g. the file was added later),
load it without resetting the volume:

```bash
bash init.sh load-data
```

This pipes `database/init/02_data.sql` directly into the running
`spyglass-workshop-db` container. Existing tables are overwritten by the dump;
roles and user accounts created by `01_roles_users.sql` are preserved.

To generate a fresh backup from the running container at any time:

```bash
docker exec spyglass-workshop-db \
    mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" \
    --all-databases --single-transaction --routines --triggers \
    > database/init/02_data.sql
```

______________________________________________________________________

## Distribute Credentials to Attendees

All attendees share the same MySQL account. Share the following:

```text
Host:     <LAN IP printed by init.sh>
Port:     3306
User:     sailor
Password: galley
```

Attendees paste the host into the first cell in the second notebook. Their
personal schema prefix is derived from their laptop OS username (e.g.
`alice_workshop`), so each attendee gets an isolated namespace even though they
share the `sailor` account.

______________________________________________________________________

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

______________________________________________________________________

## Common Operations

```bash
bash /tmp/workshop/init.sh            # start everything (DB + data + NFS)
bash /tmp/workshop/init.sh stop       # stop the container (data preserved)
bash /tmp/workshop/init.sh load-data  # (re-)load init/02_data.sql
bash /tmp/workshop/init.sh serve-data # (re-)start the NFS export
bash /tmp/workshop/init.sh logs       # stream container logs
bash /tmp/workshop/init.sh status     # show container status
bash /tmp/workshop/init.sh reset      # ⚠ destroy all data and reinitialize
```

> `/tmp/workshop` is a symlink created by `bash init.sh`. If the machine has
> rebooted since the last run, re-run `bash database/init.sh` once to recreate
> it.

______________________________________________________________________

## Exposing NWB Data Files (Optional)

Attendees can mount the data directory as a network filesystem so they can point
Spyglass's `base_dir` directly at it — no manual file downloads needed.

### 1. Populate the data directory

```bash
cp -r /path/to/nwb_files  database/data/
```

### 2. Start the NFS export

```bash
bash init.sh serve-data
```

This exports `database/data/` read-only via NFS and prints the exact mount
commands to share with attendees. Requires `nfs-kernel-server`:

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
mkdir -p ~/spyglass_data
sudo mount -t nfs <HOST>:/tmp/spyglass_data ~/spyglass_data

# macOS attendees
mkdir -p ~/spyglass_data
sudo mount -t nfs -o resvport,ro <HOST>:/tmp/spyglass_data ~/spyglass_data
```

`/tmp/spyglass_data` is a symlink created by `init.sh` that points to
`database/data/` — it gives attendees a short, stable path to type.

### 4. Attendees configure Spyglass

In their notebook or `~/.datajoint_config.json`:

```python
import spyglass as sg
sg.set_base_dir("~/spyglass_data")
```

Spyglass will read NWB files from the mount exactly as if they were local.

______________________________________________________________________

## Codespaces Fallback

If the LAN MySQL instance is unavailable, each attendee can open the repo in a
Codespace (browser or VS Code) to get a self-contained database running on
`localhost`.

1. Open the repository in a Codespace:

   ```text
   https://codespaces.new/<org>/<repo>
   ```

2. The `postCreateCommand` runs automatically and creates the workshop users.

3. Download the example NWB data file into the Codespace:

   ```bash
   mkdir -p data
   curl -L -o data/minirec20230622.nwb \
       https://ucsf.box.com/shared/static/k3sgql6z475oia848q1rgms4zdh4rkjn.nwb
   ```

4. In the attendee's notebook, set the host to `localhost` (or `127.0.0.1`):

   ```python
   dj.config["database.host"] = "127.0.0.1"
   dj.config["database.user"] = "sailor"
   dj.config["database.password"] = "galley"
   ```

### Credentials (identical to the LAN instance)

```text
Host     : 127.0.0.1
Port     : 3306
User     : sailor
Password : galley
```

______________________________________________________________________

## Teardown

At the end of the workshop, stop all services and remove resources:

```bash
bash init.sh stop-data          # remove NFS export (if serve-data was used)
bash init.sh stop               # stop the database container
docker compose -f database/docker-compose.yml down -v   # also remove the data volume
```
