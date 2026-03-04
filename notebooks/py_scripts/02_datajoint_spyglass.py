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
    missing.append("spyglass  →  from a cloned spyglass repo: `./scripts/install.py`")


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

# ## Section 1: Connecting
#
# To fully run Spyglass, you'll need to connect to a shared drive and database.
#
# ### Mount the Shared Data
#
# The instructor has exported the NWB data files over the network (NFS).
#
# - **GitHub Codespaces** — data is pre-downloaded; run the cell as-is.
# - **Linux / macOS** — run the cell below to mount the network share.
# - **Windows** — NFS mounting is not supported; the cell below will
#   download and unzip the workshop data archive instead.
#
# > **Linux / macOS:** replace `NFS_PATH` with the path shown on the
# > projector before running. It has the form `<HOST>:<EXPORT_PATH>`.

# +
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

FORCE_DOWNLOAD = False  # True to download the zip, not mount the NFS share

NFS_PATH = "INSTRUCTOR_IP:EXPORT_PATH"  # <-- Linux/macOS: replace with shared path
ZIP_URL = "https://ucsf.box.com/shared/static/biwz0jx2zzhin1h1io4vi4gwdwm580cn.zip"
MOUNT_POINT = str(Path.home() / "spyglass_data")


def _has_data(mount_point):
    marker = Path(mount_point) / "raw" / "minirec20230622.nwb"
    return marker.exists()


if os.environ.get("CODESPACES"):
    # Data was pre-downloaded by the devcontainer setup script.
    print(f"Codespaces: using pre-downloaded data at {MOUNT_POINT}")

elif sys.platform in ("linux", "darwin") and not FORCE_DOWNLOAD:
    MOUNT_POINT = str(Path.home() / "spyglass_data")
    if not _has_data(MOUNT_POINT):
        os.makedirs(MOUNT_POINT, exist_ok=True)
        opts = "" if sys.platform == "linux" else "-o resvport "
        cmd = f"sudo mount -t nfs {opts}{NFS_PATH} {MOUNT_POINT}"
        # sudo may prompt for your password in the terminal where Jupyter runs.
        ret = os.system(cmd)
        if ret != 0:
            print(f"Mount failed (exit {ret}). Run in a terminal:\n  {cmd}")

else:  # Windows — download and unzip the workshop data archive
    MOUNT_POINT = str(Path.home() / "spyglass_data")
    if not _has_data(MOUNT_POINT):
        zip_tmp = Path.home() / "spyglass_data.zip"
        print("Downloading spyglass data archive (may take a few minutes) ...")

        def _progress(n, block_size, total):
            pct = min(100, n * block_size * 100 // total)
            print(f"\r  {pct:3d}%", end="", flush=True)

        urllib.request.urlretrieve(ZIP_URL, zip_tmp, reporthook=_progress)
        print(f"\nUnpacking to {MOUNT_POINT} ...")
        with zipfile.ZipFile(zip_tmp) as zf:
            zf.extractall(MOUNT_POINT)
        zip_tmp.unlink()
        print(f"Done. Data saved to {MOUNT_POINT}")

if Path(MOUNT_POINT).exists():
    print("Contents:", os.listdir(MOUNT_POINT))
else:
    print(f"Data directory {MOUNT_POINT} not found.")
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

# ### The Config File
#
# DataJoint reads connection settings from either `dj_local_conf.json` in the
# current directory, or `~/.datajoint_config.json`.
# The cell below writes that file using the workshop credentials.
#
# > **Note:** Replace `HOST` with the IP address given to you by the
# > instructor. The password for user `sailor` is `galley`.

# +
import datajoint as dj  # type: ignore

HOST = "127.0.0.1"  # <-- replace with the instructor's IP address

MOUNT_POINT = str(Path.home() / "spyglass_data")
config = {
    "database.host": HOST,
    "database.port": 3306,
    "database.user": "sailor",
    "database.password": "galley",
    "database.use_tls": False,
    "custom": {"spyglass_dirs": {"base": f"{MOUNT_POINT}"}},
}

dj.config.update(config)
dj.config.save_local()  # persist for Spyglass and workshop exercises

print("Config written to 'dj_local_conf.json'")
# -

# Now, we'll try connecting

conn = dj.conn()
conn.ping()
print("Connected to", dj.config["database.host"])

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

# ## Section 2: Explore Existing Tables
#
# Spyglass tables are already declared in the workshop database.
# Let's explore the `common` schema — the shared backbone of every pipeline.

# +
from spyglass.utils.database_settings import SHARED_MODULES

# List all schemas your user can see in SHARED_MODULES
schemas = dj.list_schemas()
print("Available schemas:")
for s in sorted(schemas):
    if s.split("_")[0] in SHARED_MODULES:  # others are remnants of pytest
        print(" ", s)

# +
from spyglass.common import Nwbfile, Session, Subject

# See the table. Users with unzipped data can only access minirec files
Nwbfile()
# -

# Can you spot the difference between `describe()` and `heading`? What do you
# think each is useful for?

# +
from pprint import pprint

# Show the table definition
pprint(Session.describe())
# -

pprint(Session.heading)

# +
from spyglass.lfp.lfp_merge import LFPOutput

# tables that directly reference LFPOutput (its Part tables)
LFPOutput.children(as_objects=True)
# see also: parents, descendants, ancestors
# -

# Draw the dependency graph for a subset of tables.
#
# **NOTE**: `dj.Diagram` may display `full_table_name` for unimported tables
#
# dj.Diagram supports operator overloading:
# - diagram + N  adds N levels downstream  (tables that depend on this one)
# - diagram - N  adds N levels upstream    (tables this one depends on)
# - `diagram + 1 - 1` == `(diagram + 1) - 1` != `diagram + 0`
# - diagram0 + diagram2  merges two diagrams

# +
from spyglass.common import common_filter as filter_schema
from spyglass.lfp.v1.lfp import schema as lfp_schema

# Star import used here so DataJoint can find all tables in the module
# when building the diagram — ruff F403 suppressed intentionally.
from spyglass.lfp.v1.lfp_artifact import *  # noqa: F403

dj.Diagram(filter_schema) + dj.Diagram(lfp_schema)
# -

# #### Exercise 2.1: Diagram
#
# Now, try drawing a diagram around a Merge table.
#
#
# To find them in the codebase, search for `class .*Output\(` in Spyglass
# with regular expressions on (`Alt+R`)

# +
from spyglass.utils.dj_helper_fn import declare_all_merge_tables

DecodingOutput, LFPOutput, PositionOutput, SpikeSortingOutput = (
    declare_all_merge_tables()
)


# YOUR CODE HERE: Draw a dependency graph around a Merge table
# -

# <details><summary>Solution</summary>
#
# The codebase search works, but the `+`/`-` operators on `dj.Diagram` are
# simpler — they expand the graph N levels up or downstream:
#
# ```python
# dj.Di(PositionOutput.TrodesPosV1) - 1 + 1
# ```
#
# Note that the diagram grows unwieldy fast with large schemas.
#
# </details>

# ## Section 3: Restrictions and joins
#
# DataJoint uses `&` to restrict (filter) and `*` to join tables.
#
# ### Restrict

# +
from spyglass.common import Session  # noqa: I001

# Restrict: fetch subjects whose species is 'Mus musculus'
mice = Subject & {"species": "Mus musculus"}
print(f"{len(mice)} mice")

# String-based restriction (SQL WHERE clause syntax)
recent = Session & "session_start_time > '2024-01-01'"
print(f"{len(recent)} sessions since 2024")

mock_mice = Subject & 'description LIKE "%mock%"'  # % is a wildcard in SQL
print(f"{len(mock_mice)} mock mice")
# -

Subject()

Session()

# ### Joins

# Join: combine Subject and Session
(Subject * Session).proj()  # `proj` drops all secondary attributes

# Joins can traverse a long way

# +
from spyglass.spikesorting.v1.curation import CurationV1
from spyglass.spikesorting.v1.sorting import (
    SpikeSorterParameters,
    SpikeSorting,
    SpikeSortingSelection,
)

# print(SpikeSorterParameters().fetch('sorter'))
(
    SpikeSorterParameters & "sorter LIKE 'clust%'"
) * SpikeSortingSelection * SpikeSorting.proj() * CurationV1
# -

# Or, we can restrict the current table by a field elsewhere.

CurationV1() << "sorter LIKE 'clust%'"

# ### Fetch
#
# We can fetch data from any table or join (also called `QueryExpression`)

# +
from spyglass.common.common_ephys import Electrode, ElectrodeGroup, Probe, Raw

my_query = ElectrodeGroup * Probe

my_query.fetch(
    "electrode_group_name",
    "contact_side_numbering",
    as_dict=True,
    order_by="electrode_group_name ASC",
)[0:5]
# -

my_query.fetch(format="frame").head()  # dataframe

help(my_query.fetch)

# Intentional error: `my_query` is a QueryExpression, not a base table.
# QueryExpressions don't have a .definition attribute.
# This demonstrates what you'll see if you try to inspect a join or restriction.
my_query.definition  # This will raise AttributeError

# #### Fetch dataframe and NWB *(optional — requires both DataJoint fetch and NWB knowledge)*
#
# Spyglass tables with foreign-key references to `AnalysisNwbfile` often store
# dataframes. `fetch1_dataframe()` retrieves the stored dataframe for a single
# row; `fetch_nwb()` returns the full NWB object(s) associated with the result.

# +
from spyglass.position.v1.position_trodes_position import TrodesPosV1

one_result = TrodesPosV1 & dj.Top(limit=1)  # `Top` just grabs the first
one_result.fetch1_dataframe()
# -

# We can also inspect the full NWB file:

one_result.fetch_nwb()

# ### Exercise 3.1 - Fix this join
#
# This join throws an error. Can you figure out a fix?

# +
from spyglass.spikesorting.v1 import CurationV1, SpikeSorting

SpikeSorting * CurationV1  # YOUR CODE HERE
# -

# <details><summary>Solution</summary>
#
# "Cannot join query expressions on dependent attribute" indicates there's a
# secondary key blocking the join. We can drop this by using `proj` first
#
# ```python
# SpikeSorting.proj() * CurationV1
# ```

# ### Exercise 3.2: Query the database
#
# 1. How many interval names start with `01`?
# 2. Try fetching subject ID and session description for the five most recent sessions.

# +
from spyglass.common import IntervalList

IntervalList()  # 1. YOUR CODE HERE
# -

# <details><summary>Hint</summary>
#
# Try restricting with a wildcard: `something LIKE "begin%"`
#
# </details>
#
# <details><summary>Solution</summary>
#
# ```python
# from spyglass.common import IntervalList
#
# IntervalList & 'interval_list_name LIKE "01%"'
# ```
#
# </details>
#

# +
# 2. YOUR CODE HERE
# -

# <details><summary>Hint</summary>
#
# Recency can be done with `order_by='session_start_time DESC'`
#
# </details>
#
# <details><summary>Solution</summary>
#
# ```python
# (Subject * Session).fetch(
#     "subject_id",
#     "session_description",
#     order_by="session_start_time DESC",
#     limit=5, # could also be done with splicing after the fetch
#     as_dict=True, # optional
# )
# ```
#
# </details>

# ### Exercise 3.3 (tough)
#
# 1. Review `aggr` [syntax](https://docs.datajoint.com/reference/specs/master-part/#63-aggregating-parts)
# 2. Show the number of electrodes in each LFP electrode group in a query expression.

# +
# YOUR CODE HERE
# -

# <details><summary>Hint 1</summary>
#
# ```python
# from spyglass.lfp import LFPElectrodeGroup
#
# LFPElectrodeGroup.LFPElectrode()
# ```
#
# </details>
#
# <details><summary>Hint 2</summary>
#
# ```python
# from spyglass.lfp import LFPElectrodeGroup
#
# LFPElectrodeGroup.aggr(LFPElectrodeGroup.LFPElectrode(), xx="yy")
# ```
#
# </details>
#
# <details><summary>Solution</summary>
#
# ```python
# from spyglass.lfp import LFPElectrodeGroup
#
# LFPElectrodeGroup.aggr(LFPElectrodeGroup.LFPElectrode(), count="count(*)")
# ```
#
# </details>

# Review "Custom Pipeline" slides before continuing.
#
# ---
#
# ## Section 4: Declare Your Own Schema
#
# `schema_template.py` defines a minimal Parameter → Selection → Analysis
# pipeline. Importing it registers all tables under your personal schema
# prefix (`workshop_<username>`).
#
# > **Warning:** The schema name is derived from your OS username. If two
# > attendees share the same username, their tables will collide and produce
# > confusing downstream errors. Change the schema declaration in
# > `schema_template.py` before importing if your username is not unique.
#
# ### Exercise 4.1: Explore the schema template

# +
# this will warn about the prefix not in SHARED_MODULES, ignore
import spyglass_workshop.schema_template as st

print(f"Your personal schema: workshop_{st.this_user}")
# -

# Draw the full dependency graph for your schema.
dj.Diagram(st.schema)

# +
from pprint import pprint

# Inspect each table's definition
for table_cls in [st.MyParams, st.MyAnalysisSelection, st.MyAnalysis]:
    print(f"{table_cls.__name__}  ({table_cls.full_table_name})")
    pprint(table_cls.describe())
    print()
# -

# Insert the default parameter sets
st.MyParams.insert_default()
st.MyParams()

# ### Exercise 4.2: Run the Pipeline
#
# Now we will populate the Selection table and trigger `populate()` on the
# Analysis table.

# +
# Pair the first two subjects with the 'default' parameter set
subject_keys = st.MySubject.fetch("KEY", limit=2)

st.MyAnalysisSelection.insert(
    [{**k, "param_name": "default"} for k in subject_keys],
    skip_duplicates=True,
)
st.MyAnalysisSelection()
# -

# Run the analysis for all pending Selection rows.
# display_progress=True shows a progress bar.
st.MyAnalysis.populate(display_progress=True)

# Inspect the Analysis results
print("MyAnalysis rows:")
print(st.MyAnalysis())

# Part tables are nested inside their master class and share its primary key.
# Access them as an attribute: MasterTable.PartTable()
print("\nMyPart rows (first 10):")
print(st.MyAnalysis.MyPart().fetch(format="frame").head(10))

# Use the built-in helper to summarize one result
first_key = st.MyAnalysis.fetch("KEY", limit=1)[0]
st.MyAnalysis.summarize(first_key)

# ### Exercise 4.3 — Run with a different parameter set
#
# Insert a new set of Selection rows using the `'quick'` parameter set and
# re-run `populate()`. Then compare the `total_result` values between the
# two parameter sets.
#
# Available parameter sets: `st.MyParams()`

# +
# YOUR CODE HERE

# 1. Insert Selection rows with param_name='quick'

# 2. Call populate()

# 3. Fetch total_result for both param sets and compare
# -

# <details><summary>Hint</summary>
#
# Use `MyAnalysisSelection.insert()` with `param_name='quick'`, then call
# `MyAnalysis.populate()`. Fetch results with `st.MyAnalysis()` or
# `.fetch("subject_id", "param_name", "total_result", as_dict=True)`.
#
# </details>

# <details><summary>Solution</summary>
#
# ```python
# st.MyAnalysisSelection.insert(
#     [{**k, "param_name": "quick"} for k in st.MySubject.fetch("KEY")],
#     skip_duplicates=True,
# )
# st.MyAnalysis.populate(display_progress=True)
#
# # Compare results
# st.MyAnalysis()
# ```
#
# </details>

# ### Exercise 4.4 - Revise the pipeline
#
# > **Open-ended extension:** This section is intentionally exploratory and
# > may not be completed during the session — you are encouraged to finish
# > it afterwards at your own pace.
#
# **Steps:**
#
# 1. Make a copy of `src/spyglass_workshop/schema_template.py` in the same folder.
# 2. Change the schema declaration to something new: `workshop_yourrandomtext`
# 2. Change these tables to foreign-key reference a Spyglass table.
# 3. In `make`, fetch from the Spyglass table to print some piece of the stored data.
# 4. Restart the kernel, and run `populate` on your modified table
#
# **Optional**: Work with other members of the workshop on shared tables with
# `sleep` making long computes. Can you figure out the `populate` arguments that
# reserve jobs across machines?

# +
# YOUR CODE HERE
# After editing the schema and restarting the kernel:

# import spyglass_workshop.YOUR_SCHEMA_NAME as yt
# yt.MyParams.insert_default()
# yt.MyAnalysisSelection.insert(  # insert rows manually, e.g.:
#     [{**k, "param_name": "default"} for k in yt.MySubject.fetch("KEY")],
#     skip_duplicates=True,
# )
# yt.MyAnalysis.populate(display_progress=True)
# yt.MyAnalysis()
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

# ---

# ## Advanced Exercises *(homework)*
#
# These exercises reinforce the session material using the live Spyglass demo
# database. They are designed to be run **after the workshop** in one of two
# environments:
#
# | Environment | How to open |
# | :---------- | :---------- |
# | **Demo JupyterHub** | [Launch spyglass-demo on hhmi.2i2c.cloud](https://spyglass.hhmi.2i2c.cloud/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2FLorenFrankLab%2Fspyglass-demo&urlpath=lab%2Ftree%2Fspyglass-demo%2Fnotebooks%2F02_Insert_Data.ipynb&branch=main) |
# | **GitHub Codespace** | Re-open this repo's Codespace |

# ### Exercise 5.1 — Operator drills on real data *(~15 min)*
#
# The five queries below use the operators from Section 3. Each has a blank
# `# YOUR CODE HERE` block — fill it in, run the cell, and compare to the
# solution.
#
# **Imports** — run this cell first:

import datajoint as dj  # type: ignore
from spyglass.common import (
    Electrode,
    ElectrodeGroup,
    IntervalList,
    Nwbfile,
    Session,
    Subject,
)
from spyglass.spikesorting.v1.curation import CurationV1

# +
# 1. How many sessions are in the database? How many NWB files?

# YOUR CODE HERE
# -

# <details><summary>Hint</summary>
#
# `len(Table())` counts the rows in a table.
#
# </details>

# <details><summary>Solution</summary>
#
# ```python
# print(len(Session()), "sessions")
# print(len(Nwbfile()), "NWB files")
# ```
#
# </details>

# +
# 2. Which subjects have more than one session?

# YOUR CODE HERE
# -

# <details><summary>Hint</summary>
#
# Use `Subject.aggr(Session, n="count(*)")` to count sessions per subject,
# then restrict the result with `& "n > 1"`.
#
# </details>

# <details><summary>Solution</summary>
#
# ```python
# Subject.aggr(Session, n="count(*)") & "n > 1"
# ```
#
# </details>

# +
# 3. How many electrodes does each electrode group contain?

# YOUR CODE HERE
# -

# <details><summary>Hint</summary>
#
# This builds directly on Exercise 3.3. Use `ElectrodeGroup.aggr(Electrode, ...)`.
#
# </details>

# <details><summary>Solution</summary>
#
# ```python
# ElectrodeGroup.aggr(Electrode, n_electrodes="count(*)")
# ```
#
# </details>

# +
# 4. How many interval lists have names that start with "pos"?

# YOUR CODE HERE
# -

# <details><summary>Hint</summary>
#
# Use a SQL `LIKE` pattern with a `%` wildcard:
# `IntervalList & 'interval_list_name LIKE "pos%"'`
#
# </details>

# <details><summary>Solution</summary>
#
# ```python
# pos_intervals = IntervalList & 'interval_list_name LIKE "pos%"'
# print(len(pos_intervals), "pos intervals")
# ```
#
# </details>

# +
# 5. Find all CurationV1 results whose session happened after 2024-01-01

# YOUR CODE HERE
# -

# <details><summary>Hint</summary>
#
# Use `<<` for a long-distance restriction through related tables:
# `CurationV1() << 'subject_id LIKE "%mango%"'`
#
# </details>

# <details><summary>Solution</summary>
#
# ```python
# CurationV1() << 'subject_id LIKE "%mango%"'
# # If mango is not a subject, substitute any name from: Subject.fetch("subject_id")
# ```
#
# </details>

# ### Exercise 5.2 — Trace a result through a Merge table *(~20 min)*
#
# `PositionOutput` is a Merge table that unifies every position-tracking
# pipeline (Trodes, DLC, etc.) under a single interface. The `merge_*`
# methods let you inspect, restrict, and fetch without knowing which
# Part table holds any given result.
#
# **Goal:** start from the Merge table and fetch a position dataframe,
# then compute the duration of the tracked interval.

# +
from spyglass.position.position_merge import PositionOutput

# Step 1: How many results are in the merge table?
#         Which Part tables have entries?

PositionOutput._merge_repr()
# -

PositionOutput.parts(
    as_objects=True
)  # tables that directly reference PositionOutput (its Part tables)

# +
# Step 2: Restrict the merge table to a single NWB file.
#         Hint: use PositionOutput.merge_restrict(restriction_dict)
#         and pick the nwb_file_name from Nwbfile.fetch("nwb_file_name")[0]

# `file_like` is a help that replaces `nwb_file_name LIKE '%mini%'`

nwb_file = Nwbfile().file_like("mini").fetch("nwb_file_name")[0]
print("Using:", nwb_file)

# YOUR CODE HERE: restrict PositionOutput to this NWB file

# What would it look like to run a join for this restriction?
# -

# <details><summary>Hint</summary>
#
# For a plain join you could also write
# `PositionOutput * (Nwbfile & {"nwb_file_name": nwb_file})`, but
# `merge_restrict` handles the Part-table routing for you.
#
# </details>

# <details><summary>Solution</summary>
#
# ```python
# restricted = PositionOutput.merge_restrict({"nwb_file_name": nwb_file})
# print(len(restricted), "results for", nwb_file)
# ```
#
# </details>

Nwbfile().file_like("mini")
# equivalent to `Nwbfile() & "nwb_file_name LIKE '%mini%'"`
# also works for analysis nwb files

# +
# Step 3: Pick one result key and resolve which Part table holds it.
#         merge_get_parent returns the actual Part table restricted to this key.

key = PositionOutput.fetch("KEY", limit=1)[0]
parent = PositionOutput().merge_get_parent_class(key)  # resolves merge_id → Part table

print("Part table entry:")
parent

# +
# Step 4: Fetch the position dataframe from the parent table.
#         How long (in seconds) is the tracked interval?

# YOUR CODE HERE: call parent.fetch1_dataframe() and compute duration
# -

# <details><summary>Hint</summary>
#
# `parent.fetch1_dataframe()` returns a pandas DataFrame indexed by time.
#
# But it only works for a query with one result
#
# The duration is `df.index[-1] - df.index[0]`.
#
# </details>

# <details><summary>Solution</summary>
#
# ```python
# df = (parent & dj.Top()).fetch1_dataframe()
# duration = df.index[-1] - df.index[0]
# print(f"Tracked interval: {duration:.2f} s  ({len(df)} samples)")
# ```
#
# </details>

# +
# Step 5: Plot the x/y position trajectory for the full interval.
#         Label the axes and add a title that includes the NWB file name.

import matplotlib.pyplot as plt

# YOUR CODE HERE
# -

# <details><summary>Hint</summary>
#
# Use `df["position_x"]` and `df["position_y"]` as the x and y axes.
# `ax.set_aspect("equal")` keeps the trajectory proportional.
#
# </details>

# <details><summary>Solution</summary>
#
# ```python
# fig, ax = plt.subplots(figsize=(5, 5))
# ax.plot(df["position_x"], df["position_y"], lw=0.5, alpha=0.7, color="steelblue")
# ax.set_xlabel("x position (cm)")
# ax.set_ylabel("y position (cm)")
# ax.set_title(nwb_file)
# ax.set_aspect("equal")
# plt.tight_layout()
# plt.show()
# ```
#
# </details>

# > **If `PositionOutput` is empty:** the demo database may not have position
# > results pre-computed. Open the demo notebook
# > `20_Position_Trodes.ipynb` in the spyglass-demo repo, run it through the
# > `TrodesPosV1.populate()` call, then return here.

# ### Exercise 5.3 — Declare a Computed table against live data *(~30 min)*
#
# In Section 4 you populated a pipeline with mock subjects. Now declare an
# `IntervalSummary` table that foreign-key references `IntervalList` — one row
# per named interval list — and uses the `Interval` utility class.
#
# `fetch_interval()` wraps a single `IntervalList` row's `valid_times` in an
# `Interval` object, unlocking set-algebra methods without `np.concatenate`:
#
# | Method | What it does |
# | :----- | :----------- |
# | `(IntervalList & key).fetch_interval()` | Fetch one row as an `Interval` |
# | `.consolidate()` | Merge any overlapping sub-intervals |
# | `.by_length(min_length)` | Keep only sub-intervals ≥ that long |
# | `a.intersect(b)` | Return time covered by **both** `a` and `b` |
#
# **Schema:** `IntervalList` → `IntervalSummary`
#
# | Field | Type | Description |
# | :---- | :--- | :---------- |
# | `n_sub_intervals` | `int` | Number of `[start, end]` pairs in `valid_times` |
# | `n_long_sub_intervals` | `int` | Pairs ≥ 0.5 s after consolidation |
# | `total_valid_s` | `float` | Total valid time (seconds) |
#
# **Steps:**
# 1. Fill in `make` — call `fetch_interval()`, then `consolidate()`,
#    `by_length(min_length=0.5)`, and sum the durations via
#    `np.sum(consolidated.times[:, 1] - consolidated.times[:, 0])`.
# 2. Run `IntervalSummary.populate(display_progress=True)`.
# 3. Inspect the results with `IntervalSummary()`.
# 4. *(Extension)* In a new cell, fetch `"pos 0 valid times"` and `"01_s1"`
#    for the same NWB file using `fetch_interval()`, then call `intersect()`
#    to find their overlap and compare the three durations.

# +
import os

import datajoint as dj  # type: ignore
import numpy as np
from spyglass.common import IntervalList
from spyglass.common.common_interval import Interval
from spyglass.utils import SpyglassMixin

schema = dj.schema(f"workshop_{os.getenv('USER', 'demo')}")


@schema
class IntervalSummary(SpyglassMixin, dj.Computed):
    """Per-interval-list summary using the Interval utility class."""

    definition = """
    -> IntervalList
    ---
    n_sub_intervals      : int    # number of [start, end] pairs in valid_times
    n_long_sub_intervals : int    # pairs >= 0.5 s after consolidation
    total_valid_s        : float  # total valid time (seconds)
    """

    def make(self, key):
        # YOUR CODE HERE
        # Steps:
        # 1. Fetch:   interval = (IntervalList & key).fetch_interval()
        # 2. Compute: consolidated = interval.consolidate()
        # 3. Filter:  long_iv = consolidated.by_length(min_length=0.5)
        # 4. Sum:     total_s = float(np.sum(
        #                 consolidated.times[:, 1] - consolidated.times[:, 0]))
        # 5. Insert:  self.insert1({**key, ...})
        pass


# Preview: how many rows will be populated?
print(f"Rows to populate: {len(IntervalList() - IntervalSummary())}")
IntervalSummary.populate(display_progress=True)
# -

# Inspect the results as a DataFrame
IntervalSummary().fetch(format="frame")

# <details><summary>Solution — make method</summary>
#
# ```python
# def make(self, key):
#     interval = (IntervalList & key).fetch_interval()
#     consolidated = interval.consolidate()
#     long_iv = consolidated.by_length(min_length=0.5)
#     total_s = float(
#         np.sum(consolidated.times[:, 1] - consolidated.times[:, 0])
#     )
#     self.insert1(
#         {
#             **key,
#             "n_sub_intervals": len(interval),
#             "n_long_sub_intervals": len(long_iv),
#             "total_valid_s": round(total_s, 4),
#         }
#     )
# ```
#
# </details>
#
# <details><summary>Extension — intersect two interval lists</summary>
#
# Pick an NWB file and compare its position valid-times to the first epoch.
#
# ```python
# import numpy as np
# from spyglass.common import IntervalList
# from spyglass.common.common_interval import Interval
#
# nwb = IntervalList.fetch("nwb_file_name", limit=1)[0]
#
# pos_iv = (
#     IntervalList
#     & {"nwb_file_name": nwb, "interval_list_name": "pos 0 valid times"}
# ).fetch_interval()
#
# epoch_iv = (
#     IntervalList
#     & {"nwb_file_name": nwb}
#     & 'interval_list_name LIKE "01_%"'
# ).fetch_interval()
#
# overlap = pos_iv.intersect(epoch_iv)
#
#
# def total_s(iv):
#     return float(np.sum(iv.times[:, 1] - iv.times[:, 0]))
#
#
# print(f"pos valid-times : {total_s(pos_iv):.2f} s")
# print(f"01_* epoch      : {total_s(epoch_iv):.2f} s")
# print(f"overlap         : {total_s(overlap):.2f} s")
# ```
#
# </details>

#
# > **Going further:** see the full Spyglass tutorials at
# > `spyglass/notebooks`:
# >
# > - start with **LFP** (notebook 30) and **Ripple Detection** (notebook 32)
# > for two complete analysis pipelines built on the same Parameter → Selection
# > → Analysis pattern you used today.
