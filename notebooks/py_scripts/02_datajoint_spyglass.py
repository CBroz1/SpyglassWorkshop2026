# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: spy
#     language: python
#     name: python3
# ---

# # Session 2: Spyglass & DataJoint Infrastructure
#
# This notebook walks through the concepts covered in the Session 2 slides.
# Follow along to work at your own pace.
#
# **Prerequisites**
#
# - The workshop MySQL instance is running and you have received credentials.
# - Your Spyglass environment is active: `conda activate spyglass`.
# - The workshop package is installed: `pip install -e .` (run once,
#   from the repo root, as shown in the "On the Day" setup steps).
# - Spyglass is installed — confirmed by the check cell immediately below.

# +
# Verify that required packages are importable before proceeding.
# If either check fails, follow the fix instructions in the printed message.

missing = []
try:
    import datajoint  # type: ignore
except ImportError:
    missing.append("datajoint  →  run:  pip install datajoint")

import importlib

# NOTE: Importing spyglass attempts a database connection we will set up later
has_spyglass = importlib.util.find_spec("spyglass") is not None
if not has_spyglass:
    missing.append(
        "spyglass  →  from a cloned spyglass repo: `./scripts/install.py`"
    )


try:
    import spyglass_workshop  # noqa: F401
except ImportError:
    missing.append(
        'spyglass_workshop  →  from the repo root: pip install -e ".[workshop]"'
    )

if missing:
    print("Missing packages — install them and restart the kernel:\n")
    for msg in missing:
        print(" ", msg)
else:
    print("All required packages found. Ready to proceed.")
# -

# We'll stop here to review some slides: `docs/src/session2_datajoint.md`

# ---
# ## Mount the Shared Data
#
# The instructor has exported the NWB data files over the network (NFS).
#
# - **Linux / macOS** — run the cell below to mount the network share.
# - **Windows** — NFS mounting requires pre-installing optional Windows
#   features and uses a different syntax; the cell below will download
#   the example file instead.
#
# > **Linux / macOS:** replace `NFS_PATH` with the path shown on the
# > projector before running. It has the form `<HOST>:<EXPORT_PATH>`.
#

# +
import os
import sys
import urllib.request
from pathlib import Path

NFS_PATH = "INSTRUCTOR_IP:EXPORT_PATH"  # <-- Linux/macOS: replace with path on projector
NWB_URL = (
    "https://ucsf.box.com/shared/static/k3sgql6z475oia848q1rgms4zdh4rkjn.nwb"
)

if sys.platform in ("linux", "darwin"):
    MOUNT_POINT = "/mnt/workshop_data"
    if os.path.ismount(MOUNT_POINT):
        print(f"Already mounted at {MOUNT_POINT}")
    else:
        os.makedirs(MOUNT_POINT, exist_ok=True)
        opts = "" if sys.platform == "linux" else "-o resvport,ro "
        cmd = f"sudo mount -t nfs {opts}{NFS_PATH} {MOUNT_POINT}"
        # sudo may prompt for your password in the terminal where Jupyter runs.
        ret = os.system(cmd)
        if ret != 0:
            print(f"Mount failed (exit {ret}). Run in a terminal:\n  {cmd}")

else:  # Windows — download the example NWB file
    MOUNT_POINT = str(Path.home() / "workshop_data")
    nwb_path = Path(MOUNT_POINT) / "raw" / "minirec20230622.nwb"
    if nwb_path.exists():
        print(f"Already downloaded: {nwb_path}")
    else:
        nwb_path.parent.mkdir(parents=True, exist_ok=True)
        print("Downloading minirec20230622.nwb (may take several minutes) ...")

        def _progress(n, block_size, total):
            pct = min(100, n * block_size * 100 // total)
            print(f"\r  {pct:3d}%", end="", flush=True)

        urllib.request.urlretrieve(NWB_URL, nwb_path, reporthook=_progress)
        print(f"\nSaved to {nwb_path}")

if Path(MOUNT_POINT).exists():
    print("Contents:", os.listdir(MOUNT_POINT))
# -

# **If the mount or download fails**, check these common causes:
#
# | Symptom | Likely cause | Fix |
# | :------ | :----------- | :-- |
# | `No such file or directory` (Linux/macOS) | Wrong export path | Confirm the exact path with the instructor |
# | `Permission denied` (Linux/macOS) | sudo password needed | Run the mount command in a terminal instead |
# | Connection refused or timeout (Linux/macOS) | Port 2049 blocked | Confirm you are on the same network as the instructor machine |
# | `already mounted` (Linux/macOS) | Cell run twice | The mount is active — continue to the next cell |
# | Download stalls or errors (Windows) | Network interruption | Re-run the cell — `urlretrieve` will overwrite the partial file |
#

# +
import spyglass as sg

sg.set_base_dir(MOUNT_POINT)
print(f"Spyglass base_dir set to: {MOUNT_POINT}")
# -

# ---
# ## The Config File
#
# DataJoint reads connection settings from either `dj_local_conf.json` in the
# current directory, or `~/.datajoint_config.json`.
# The cell below writes that file using the workshop credentials.
#
# > **Note:** Replace `HOST` with the IP address given to you by the
# > instructor. The password for user `sailor` is `galley`.

# +
import json
from pathlib import Path

HOST = "127.0.0.1"  # <-- replace with the instructor's IP address

config = {
    "database.host": HOST,
    "database.port": 3306,
    "database.user": "sailor",
    "database.password": "galley",
    "database.use_tls": False,
    "custom": {"spyglass_dirs": {"base": "YOUR_MOUNT_POINT_HERE"}},
}

config_path = Path("dj_local_conf.json")
config_path.write_text(json.dumps(config, indent=2))
print(f"Config written to {config_path}")

# +
import datajoint as dj  # type: ignore

dj.config.load(str(Path.home() / ".datajoint_config.json"))

conn = dj.conn()
conn.ping()
print("Connected to", dj.config["database.host"])
# -

# **If `conn.ping()` raises an error**, work through this checklist:
#
# | Symptom | Likely cause | Fix |
# | :------ | :----------- | :-- |
# | `Connection refused` or timeout | Wrong IP address | Ask the instructor for the correct IP; update `HOST` above and re-run the config cell |
# | `Access denied for user` | Wrong username or password | Confirm credentials with the instructor; re-run the config cell |
# | Hangs for 10–30 s then times out | Firewall or VPN blocking port 3306 | Disconnect from any VPN; confirm you are on the same network as the server |
# | `ModuleNotFoundError: datajoint` | Package not installed | Run `pip install datajoint` in the terminal, then restart the kernel |
#
# Once the fix is applied, re-run the two cells above (config write and connect).

# ---
# ## Explore Existing Spyglass Tables
#
# Spyglass tables are already declared in the workshop database.
# Let's explore the `common` schema — the shared backbone of every pipeline.

# List all schemas your user can see
schemas = dj.list_schemas()
print("Available schemas:")
for s in sorted(schemas):
    print(" ", s)

# +
from spyglass.common import Nwbfile, Session, Subject

# See the table
Nwbfile()
# -

# Show the table definition
Subject.describe()

# Fetch all subjects as a list of dicts.
# as_dict=True  →  returns a list of plain Python dicts; easy to inspect
# fetch("KEY")  →  returns only the primary-key fields, as a numpy recarray;
#                  used when you need keys to pass into another table
subjects = Subject.fetch(as_dict=True)
print(f"{len(subjects)} subjects in the database")
subjects[:3]

# Draw the dependency graph for a subset of the common schema.
# dj.Diagram supports operator overloading:
#   diagram + N  adds N levels downstream  (tables that depend on this one)
#   diagram - N  adds N levels upstream    (tables this one depends on)
#   diagram1 + diagram2  merges two diagrams
(
    dj.Diagram(Subject)
    + dj.Diagram(Session)
    + 1  # show one level downstream from Session
).draw()

# ### Restricting and joining tables
#
# DataJoint uses `&` to restrict (filter) and `*` to join tables.

# +
# Restrict: fetch subjects whose species is 'Mus musculus'
mice = Subject & {"species": "Mus musculus"}
print(f"{len(mice)} mice")

# String-based restriction (SQL WHERE clause syntax)
recent = Session & "session_start_time > '2024-01-01'"
print(f"{len(recent)} sessions since 2024")
# -

# Join: combine Subject and Session
subj_sessions = Subject * Session
# Fetch just the columns we care about
subj_sessions.fetch(
    "subject_id", "session_id", "session_start_time", as_dict=True, limit=5
)

# ### Exercise 1.1 — Query the database
#
# Using the patterns above, answer the following:
#
# 1. How many sessions are associated with subjects of species `'Rattus norvegicus'`?
# 2. Fetch the `subject_id` and `session_start_time` for the five most recent sessions.

# +
# YOUR CODE HERE

# 1. Sessions for Rattus norvegicus

# 2. Five most recent sessions (hint: use order_by='session_start_time DESC')
#    and fetch('subject_id', 'session_start_time', ...)
# -

# ---
# ## Declare Your Own Schema
#
# `schema_template.py` defines a minimal Parameter → Selection → Analysis
# pipeline. Importing it registers all tables under your personal schema
# prefix (`<your-username>_workshop`).

# +
import spyglass_workshop.schema_template as st
from spyglass_workshop.utils import SCHEMA_PREFIX

print(f"Your schema prefix: {SCHEMA_PREFIX}")
print(f"Tables live in:     {SCHEMA_PREFIX}_workshop")
# -

# Draw the full dependency graph for your schema.
# - 1 adds one level upstream so the Subject table is shown as context.
(
    dj.Diagram(st.schema)
    + dj.Diagram(Subject)
    - 1  # show one level upstream (Subject and its parents)
).draw()

# Inspect each table's definition
for table_cls in [st.MyParams, st.MyAnalysisSelection, st.MyAnalysis]:
    print(f"{'=' * 60}")
    print(f"{table_cls.__name__}  ({table_cls.full_table_name})")
    table_cls.describe()
    print()

# Insert the default parameter sets
st.MyParams.insert_default()
st.MyParams()

# ---
# ## Run the Pipeline
#
# Now we will populate the Selection table and trigger `populate()` on the
# Analysis table.

# +
# Pair the first two subjects with the 'default' parameter set
subject_keys = Subject.fetch("KEY", limit=2)

st.MyAnalysisSelection.insert(
    [{**k, "param_name": "default"} for k in subject_keys],
    skip_duplicates=True,
)
st.MyAnalysisSelection()
# -

# Run the analysis for all pending Selection rows.
# display_progress=True shows a progress bar.
st.MyAnalysis.populate(display_progress=True)

# +
# Inspect the Analysis results
print("MyAnalysis rows:")
print(st.MyAnalysis())

# Part tables are nested inside their master class and share its primary key.
# Access them as an attribute: MasterTable.PartTable()
print("\nMyPart rows (first 10):")
print(st.MyAnalysis.MyPart().fetch(limit=10, as_dict=True))
# -

# Use the built-in helper to summarize one result
first_key = st.MyAnalysis.fetch("KEY", limit=1)[0]
st.MyAnalysis.summarize(first_key)

# ### Exercise 3.1 — Run with a different parameter set
#
# Insert a new set of Selection rows using the `'quick'` parameter set and
# re-run `populate()`. Then compare the `total_result` values between the
# two parameter sets.

# +
# YOUR CODE HERE

# 1. Insert Selection rows with param_name='quick'

# 2. Call populate()

# 3. Fetch total_result for both param sets and compare
# -

# ---
# ## Extend the Pipeline
#
# > **Open-ended extension:** This section is intentionally exploratory and
# > may not be completed during the session — you are encouraged to finish
# > it afterwards at your own pace.
#
# Your task is to add a `mean_result : float` secondary field to `MyAnalysis`
# that stores the mean of all part results for that key.
#
# **Steps:**
#
# 1. Open `src/spyglass_workshop/schema_template.py` in VS Code.
# 2. Add `mean_result : float` below `total_result` in `MyAnalysis.definition`.
# 3. In `make`, compute the mean of the `result` values in `part_rows`.
# 4. Add `mean_result` to the `self.insert1(...)` dict.
# 5. **Restart this kernel** (`Kernel → Restart`) so DataJoint re-reads the
#    updated definition.
# 6. **Uncomment and run the delete cell below** to drop the rows that were
#    computed without this field — DataJoint will refuse to insert with a
#    mismatched definition otherwise.
# 7. Re-import `schema_template`, re-insert parameters and selections, then
#    re-run `populate()`.
#
# > **Why delete first?** DataJoint validates inserts against the stored
# > definition. Rows computed before you added `mean_result` lack that field,
# > so `populate()` would fail until the old rows are removed.

# +
# STEP 6: After restarting the kernel and editing schema_template.py,
# uncomment the line below and run this cell to drop the old Analysis rows.
# This must happen before populate() can insert rows with the new field.

# import spyglass_workshop.schema_template as st
# st.MyAnalysis.delete(safemode=False)

# +
# YOUR CODE HERE
# After editing the schema and restarting the kernel:

# import spyglass_workshop.schema_template as st
# st.MyParams.insert_default()
# st.MyAnalysisSelection.insert_all()   # or re-insert manually
# st.MyAnalysis.populate(display_progress=True)
# st.MyAnalysis()
# -

# ### Verify
#
# Run the cell below to check that `mean_result` is now present and
# consistent with the part table values.

# +
import numpy as np

for key in st.MyAnalysis.fetch("KEY"):
    part_results = (st.MyAnalysis.MyPart & key).fetch("result")
    stored_mean = (st.MyAnalysis & key).fetch1("mean_result")
    computed_mean = float(np.mean(part_results))
    match = "✓" if abs(stored_mean - computed_mean) < 1e-6 else "✗"
    print(
        f"{key}  stored={stored_mean:.2f}  computed={computed_mean:.2f}  {match}"
    )
# -

# ---
# ## Summary
#
# | Topic | Key takeaway |
# | :---- | :----------- |
# | Connection | `dj_local_conf.json` holds credentials; `dj.conn().ping()` verifies |
# | Exploring tables | `Table.describe()`, `Table.fetch()`, `&` restrict, `*` join |
# | Declaring tables | `@schema` + class definition registers the table on import |
# | Running analysis | `Selection.insert()` then `Analysis.populate()` |
# | Extending tables | Edit `definition`, delete old rows, re-populate |
#
# See [Spyglass docs](https://lorenfranklab.github.io/spyglass/) for the
# full API reference and pipeline examples.
