---
title: "Session 2: Spyglass & DataJoint Infrastructure"
author: Chris Broz
date: 01/2026
styles:
    style: dracula
---

<!-- PRESENTER: resize your terminal to match the calibration slide below -->
# Calibration Slide

```
Window must be this wide ─────────────────────────────────────────────────────►

And this tall
│
│
│
│
│
│
│
│
│
│
│
│
│
│
│
│
│
│
│
│
│
│
▼
For use with `lookatme`, a terminal-based presentation tool.
```

---

# Overview

This session will cover ...

- ⭕ DataJoint Infrastructure
- ⭕ DataJoint Table Tiers and Declaration Syntax
- ⭕ Spyglass Table Types, including Merge Tables
- ⭕ Creating a Custom Pipeline
- ⭕ Common DataJoint Errors

---

# Overview

- 👀 DataJoint Infrastructure
- ⭕ DataJoint Table Tiers and Declaration Syntax
- ⭕ Spyglass Table Types, including Merge Tables
- ⭕ Creating a Custom Pipeline
- ⭕ Common DataJoint Errors

---

# Infrastructure

## What are we connecting to?

```
        ┌────────────────┐
        │   OS           │
        │┌──────────────┐│
        ││  Python      ││
        ││┌────────────┐││
        │││ Jupyter    │││
        │││┌──────────┐│││
        ││││Some Code ││││
        │││└──────────┘│││
        ││└────────────┘││
        │└──────────────┘│
        └────────────────┘
```

---

# Infrastructure

## What are we connecting to?

```
        ┌────────────────┐
        │   OS           │
        │┌──────────────┐│
        ││  Python      ││
        ││┌────────────┐││
        │││ Jupyter    │││
        │││┌──────────┐│││  ┌────────┐
        ││││DataJoint─┼┼┼┼──┼─> MySQL│
        │││└──────────┘│││  └────────┘
        ││└────────────┘││
        │└──────────────┘│
        └────────────────┘
```

---

# Infrastructure

## DataJoint's Role

```
        ┌──────────┐  ┌────────┐
        │DataJoint─┼──┼─> MySQL│
        └──────────┘  └────────┘
```

<!-- stop -->

When you import a DataJoint table, it ...

1. Connects to the MySQL server using credentials from a local config file
   (we will create this in the notebook — Section 0)
2. Checks whether that table exists in the database
3. If not, declares it using the Python `definition`

<!-- stop -->

At its core, DataJoint maps Python ↔ SQL:

- Python class definitions → SQL `CREATE TABLE` statements
- Python `insert` / `fetch` calls → SQL `INSERT` / `SELECT` queries
- Python `populate` calls → SQL transactions triggered by upstream changes

---

# Infrastructure

## The Config File

The minimal fields needed to connect to the workshop database:

```json
{
    "database.host":     "INSTRUCTOR_IP",
    "database.user":     "sailor",
    "database.password": "galley",
    "database.port":     3306,
    "database.use_tls":  false,
    "safemode":          true,
    "fetch_format":      "array"
}
```

<!-- stop -->

In the notebook we write this file programmatically, then load it with:

```python
import datajoint as dj
dj.config.load("path/to/dj_local_conf.json")
dj.conn().ping()   # raises an error if the connection fails
```

> The full Spyglass config also declares `stores` paths for NWB files.
> For this workshop, only the `database.*` fields are needed.

---

# Infrastructure

## SQL's Role

A given experiment might have separate spreadsheets for ...

1. Subjects
2. Sessions
3. Analysis parameters
4. Analysis results

...with the experimenter keeping track of relationships between them.

<!-- stop -->

SQL replaces this with tables that *know* their relationships:

```
     ┌───────────────┐
     │SUBJECT        │
     │*subj_id*, name│
     └───────┬───────┘
             ▼
     ┌─────────────────────────────┐  ┌───────────────────────────┐
     │SESSION                      │  │ PARAMETERS                │
     │*subj_id*, *session_id*, time│  │ *param_id*, param1, param2│
     └─────────────┬───────────────┘  └────────────┬──────────────┘
                   └──────────────────┬─────────────┘
                                      ▼
                       ┌──────────────────────────────┐
                       │ANALYSIS                      │
                       │*subj_id*, *session_id*,      │
                       │*param_id*                    │
                       └──────────────────────────────┘
```

---

# Infrastructure

## Key Terminology

- *Upstream* / *Downstream*: direction of data flow in the dependency graph
- *Primary key*: the set of fields that uniquely identifies each row (`*`)
- *Secondary key*: additional data stored per row; values may repeat
- *Foreign key*: a reference to the primary key of another table

```
     ┌───────────────┐
     │SUBJECT        │
     │*subj_id*, name│   subj_id is the primary key
     └───────┬───────┘
             ▼
     ┌─────────────────────────────┐
     │SESSION                      │
     │*subj_id*, *session_id*, time│   subj_id is a foreign key
     └─────────────────────────────┘
```

<!-- stop -->

**Database design is mapping our conceptual model of the data to a set of
tables, relationships, fields, and contents.**

---

# Infrastructure

## DataJoint's Constraints

DataJoint is *opinionated* — it limits the full power of SQL to enforce
good practices:

<!-- stop -->

- Every table must have a primary key.
- Foreign keys must reference existing tables.
- `populate` respects the dependency graph (no orphaned rows).
- Deletes cascade upstream to protect data integrity.

<!-- stop -->

Python stores **two things** that can drift out of sync with each other:

- A copy of your table *definitions* (the Python class)
- The *data* that was inserted under a previous definition

<!-- stop -->

Good data provenance requires **good version control** to keep these in sync.

---

# Infrastructure

## Explore Existing Spyglass Tables

Spyglass pre-populates a shared `common` schema for every dataset.

Open `notebooks/02_datajoint_spyglass.ipynb` — **Section 1**.

```python
from spyglass.common import Subject, Session

# Show the table definition
Subject.describe()

# Fetch all subjects
subjects = Subject.fetch(as_dict=True)
print(f"{len(subjects)} subjects in the database")

# Restrict: & filters; join: * combines tables
mice = Subject & {"species": "Mus musculus"}
subj_sessions = Subject * Session
```

---

# Overview

- ✅ DataJoint Infrastructure
- 👀 DataJoint Table Tiers and Declaration Syntax
- 👀 Spyglass Table Types, including Merge Tables
- ⭕ Creating a Custom Pipeline
- ⭕ Common DataJoint Errors

---

# Python Structure

A DataJoint schema file has two sections:

1. **Front matter**
    - Imports — pulling in code from other modules
    - Schema declaration — telling DataJoint/SQL where the tables live
2. **Tables**
    - Class inheritance — which base classes to extend
    - Table type — how the table is populated
    - Definition — the SQL-like column specification
    - Methods — additional functionality

---

# Python Structure

## Front Matter: Imports

```python
import os                          # standard library

from typing import Union           # individual class import
import datajoint as dj             # aliased package import

from spyglass.common import (      # individual imports from a package
    Nwbfile,                       # noqa: F401 silences "unused" linter warning
    Subject,
)
from spyglass.utils import SpyglassMixin

from spyglass_workshop.utils import SCHEMA_PREFIX   # relative import
```

<!-- stop -->

Import types in order (enforced by `ruff`):

1. Standard library (`os`, `typing`, …)
2. Third-party packages (`datajoint`, `spyglass`, …)
3. Local / relative imports (`spyglass_workshop.utils`, …)

---

# Python Structure

## Front Matter: Schema Declaration

```python
schema = dj.schema(SCHEMA_PREFIX + "_workshop")
```

<!-- stop -->

- Database permissions are managed **by schema prefix**
- Spyglass uses shared prefixes (`common_*`, `lfp_*`, …) — **do not add to these**
- Use your username or a project-specific prefix for your own tables

```python
# example: attendee "alice" gets tables in "alice_workshop"
import os
SCHEMA_PREFIX = os.getenv("USER", "workshop")
```

<!-- stop -->

```python
# Spyglass shared tables live under their own prefixes:
Subject.full_table_name       # "`common_subject`.`subject`"
Nwbfile.full_table_name       # "`common`.`_nwbfile`"
```

---

# Python Structure

## Table Syntax: Class Inheritance

```python
@schema
class ExampleTable(SpyglassMixin, dj.Manual):
    pass
```

The parentheses list the **base classes** this table inherits from:

<!-- stop -->

- `dj.Manual` — the DataJoint table *tier* (how it gets populated)
- `SpyglassMixin` — adds Spyglass-specific helpers (`restrict_by`, `find_insert_fail`, …)

<!-- stop -->

`@schema` is a *decorator* that registers the class with the database and
creates the SQL table on first import if it doesn't exist.

> **What is a decorator?** The `@name` syntax above a class (or function)
> wraps it to add behaviour. Here, `@schema` is shorthand for
> `ExampleTable = schema(ExampleTable)` — it hands the class to DataJoint,
> which maps it to a SQL table and stores the mapping.

---

# Python Structure

## Table Syntax: DataJoint Table Tiers

| Tier | Populated by | Use case |
| :--- | :----------- | :------- |
| `dj.Manual` | A person, via `insert` | Subjects, sessions, selections |
| `dj.Lookup` | Declared in `contents` | Parameter sets, lookup values |
| `dj.Imported` | `make`, reading external files | NWB ingestion |
| `dj.Computed` | `make`, from upstream tables | Analysis results |
| `dj.Part` | Master table's `make` | One-to-many sub-records |

---

# Python Structure

## Table Syntax: Spyglass Conceptual Types

| Spyglass Type | DataJoint Tier | Role |
| ------------: | :------------- | :--- |
| Data | Manual, Imported | Starting point — raw or ingested |
| Parameter | Lookup (or Manual) | Analysis settings |
| Selection | Manual | Pair data with parameters |
| Analysis | Computed | Run `make`, store results |
| Merge | `_Merge` with Parts | Unify outputs from multiple pipelines |

---

# Python Structure

## Table Types: Diagram

```
               ┌────┐
               │Data│
               └─┬──┘   ┌─────────────┐
    ┌────────────┼───┐  │  ┌──────────┼─────┐
    │Schema      │   │  │  │Merge     │     │
    │            │   │  │  │Schema    │     │
    │┌─────────┐ │   │  │  │          │     │
    ││Parameter│ │   │  │  │┌─────┐   │     │
    │└────┬────┘ │   │  │  ││Merge│   │     │
    │     ▼      ▼   │  │  │└───┬─┘   │     │
    │    ┌─────────┐ │  │  │    ▼     ▼     │
    │    │Selection│ │  │  │  ┌──────────┐  │
    │    └────┬────┘ │  │  │  │Merge Part│  │
    │         ▼      │  │  │  └──────────┘  │
    │    ┌─────────┐ │  │  │                │
    │    │Analysis │ │  │  │                │
    │    └────┬────┘ │  │  │                │
    └─────────┼──────┘  │  └────────────────┘
              └─────────┘
```

*Tip:* `dj.Diagram(schema)` draws the actual dependency graph for any schema.

---

# Python Structure

## Table Syntax: Definitions

```python
@schema
class ExampleTable(SpyglassMixin, dj.Manual):
    """One-line description of what this table stores."""

    definition = """  # table-level comment shown in dj.Diagram
    primary_key1 : uuid        # unique random ID
    primary_key2 : int         # integer
    ---
    secondary_field : varchar(32)  # string, max 32 chars
    blob_field      : blob         # any Python object (dict, array, …)
    -> Subject                     # foreign key: inherits Subject's PK
    -> Subject.proj(src='subject_id')  # foreign key with renamed column
    """
```

<!-- stop -->

- Everything above `---` is a **primary key** field
- Everything below is a **secondary** (non-identifying) field
- `->` inherits the primary key of the referenced table
- FK-referenced tables must be imported in the same file

---

# Python Structure

## Table Syntax: Methods

```python
@schema
class SubjBlinded(SpyglassMixin, dj.Manual):
    ...

    @property                    # accessed as SubjBlinded().pk (no call)
    def pk(self):
        return self.heading.primary_key

    @staticmethod                # no access to class or instance
    def _hash(subject_id):
        return dj.hash.key_hash({"subject_id": subject_id})

    @classmethod                 # access to class but not instance
    def insert_default(cls):
        cls().insert(cls.contents, skip_duplicates=True)

    def blind_subjects(self, restriction):   # full instance access
        keys = (Subject & restriction).fetch("KEY")
        self.insert([{**k, "subject_id": self._hash(k)} for k in keys])
```

---

# Python Structure

## Declare Your Own Schema

Open `notebooks/02_datajoint_spyglass.ipynb` — **Section 2**.

`schema_template.py` implements the patterns from this section.
Importing it registers your personal schema in the database:

```python
import spyglass_workshop.schema_template as st

# Visualise the dependency graph
dj.Diagram(st.schema).draw()

# Inspect each table's definition
for table_cls in [st.MyParams, st.MyAnalysisSelection, st.MyAnalysis]:
    table_cls.describe()

# Populate the Lookup table with default parameter sets
st.MyParams.insert_default()
```

---

# Overview

- ✅ DataJoint Infrastructure
- ✅ DataJoint Table Tiers and Declaration Syntax
- ✅ Spyglass Table Types, including Merge Tables
- 👀 Creating a Custom Pipeline
- ⭕ Common DataJoint Errors

---

# Custom Pipelines

Designing a pipeline means deciding:

1. What are your **parameters**?
2. What is your **input data**?
3. Do you need a **selection** staging table?
4. What does your **analysis** compute?
5. How do foreign keys connect everything?
6. Should your output feed into a **Merge** table?

---

# Custom Pipelines

## Parameters

```python
@schema
class MyParams(SpyglassMixin, dj.Lookup):
    """Analysis parameters."""

    definition = """
    param_name : varchar(32)
    ---
    params     : blob           # dict of parameter values
    """
    contents = [
        ["default", {"window_s": 1.0, "threshold": 0.5}],
        ["fast",    {"window_s": 0.5, "threshold": 0.5}],
    ]

    @classmethod
    def insert_default(cls):
        cls().insert(cls.contents, skip_duplicates=True)
```

<!-- stop -->

- `dj.Lookup` contents are inserted once on first import
- `blob` stores any Python object — flexible but not queryable by field
- Use explicit fields instead if you need to query by parameter value

---

# Custom Pipelines

## Data (1/2) — Preprocessed Input

```python
@schema
class SubjBlinded(SpyglassMixin, dj.Manual):
    """Subjects with anonymised IDs for blinded analysis."""

    definition = """
    subject_id : uuid
    ---
    -> Subject.proj(actual_id='subject_id')
    """

    def blind_subjects(self, restriction):
        """Insert all subjects matching restriction with hashed IDs."""
        keys = (Subject & restriction).fetch("KEY")
        self.insert(
            [{**k, "subject_id": dj.hash.key_hash(k)} for k in keys],
            skip_duplicates=True,
        )
```

---

# Custom Pipelines

## Data (2/2) — Grouping with Part Tables

Use a Part table when one upstream entry maps to *many* rows:

```python
@schema
class MyGrouping(SpyglassMixin, dj.Manual):
    """A named group of upstream units."""

    definition = """
    group_id : int auto_increment
    ---
    group_name : varchar(64)
    """

    class MyUnit(SpyglassMixin, dj.Part):
        definition = """
        -> MyGrouping
        -> UpstreamUnit
        """
```

---

# Custom Pipelines

## Selection

```python
@schema
class MyAnalysisSelection(SpyglassMixin, dj.Manual):
    """Pairs of input data and parameters to be analysed."""

    definition = """
    -> SubjBlinded
    -> MyParams
    """
```

<!-- stop -->

- `populate` on the downstream `Computed` table will process every row here
- The Selection table is a *staging area* — insert only the combinations
  you actually want to run

---

# Custom Pipelines

## Analysis

```python
@schema
class MyAnalysis(SpyglassMixin, dj.Computed):
    """Results of the analysis."""

    definition = """
    -> MyAnalysisSelection
    ---
    -> AnalysisNwbfile    # by convention, results go into an NWB file
    """

    def make(self, key):
        params = (MyParams & key).fetch1("params")
        # ... do work ...
        analysis_file = AnalysisNwbfile().create(key["nwb_file_name"])
        # Delay all inserts until computation succeeds (atomicity)
        AnalysisNwbfile().add(analysis_file, result_object)
        self.insert1({**key, "analysis_file_name": analysis_file})
```

<!-- stop -->

- `MyAnalysis().populate()` runs `make` for every unprocessed Selection row
- Postpone `insert` / `insert1` to the **very end** of `make`

---

# Custom Pipelines

## Run the Pipeline

Open `notebooks/02_datajoint_spyglass.ipynb` — **Section 3**.

```python
# Pair subjects with the 'default' parameter set
subject_keys = Subject.fetch("KEY", limit=2)
st.MyAnalysisSelection.insert(
    [{**k, "param_name": "default"} for k in subject_keys],
    skip_duplicates=True,
)

# Process every pending Selection row
st.MyAnalysis.populate(display_progress=True)

# Inspect results and the nested Part table
st.MyAnalysis()
st.MyAnalysis.MyPart()
```

---

# Custom Pipelines

## Foreign Key References

Primary vs Secondary and Foreign Key vs Field are orthogonal concepts:

| | Primary (unique identifier) | Secondary (extra data) |
| :- | :-------------------------- | :--------------------- |
| **Foreign** | Another processing step | Associated resource (e.g. NWB file) |
| **Native** | Arbitrary unique ID | Arbitrary data field |

<!-- stop -->

Foreign **primary** key — sole FK means one-to-one:

```python
definition = """
-> UpstreamTable    # inherits upstream PK; this row IS that result
---
result : float
"""
```

Multiple FK primary keys mean a pairing (Selection pattern):

```python
definition = """
-> UpstreamTable1
-> UpstreamTable2   # every row is a unique (T1, T2) combination
"""
```

---

# Custom Pipelines

## Foreign Secondary Key

As a secondary key indicates either ...

**1.** A linked resource that does not uniquely identify the row:

```python
definition = """
-> UpstreamTable
---
-> AnalysisNwbfile   # file that stores the result; not part of the PK
"""
```

<!-- stop -->

**2.** A *buried* PK — aliases inherited columns when too many pile up:

```python
definition = """
merge_id : uuid      # single new PK buries all inherited keys
---
-> UpstreamTable1
-> UpstreamTable2
"""
```

This is how Merge tables work.

---

# Custom Pipelines

## Merge Tables

Merge tables let downstream analyses be agnostic about *which* upstream
pipeline produced their input:

```python
@schema
class MyAnalysis(SpyglassMixin, dj.Computed):
    definition = """
    -> LFPOutput         # LFPOutput is a Merge table — any source works
    -> MyParams
    ---
    -> AnalysisNwbfile
    """

    def make(self, key):
        params = (MyParams & key).fetch1("params")
        # Fetch from whichever part table holds this merge_id
        parent = LFPOutput().merge_get_parent(key)
        data = parent.fetch_nwb()[0]
        ...
        self.insert1({**key, "analysis_file_name": new_file})
```

<!-- stop -->

See [Merge table docs](https://lorenfranklab.github.io/spyglass/latest/api/utils/dj_merge_tables/)
for the full `merge_*` method reference.

---

# Custom Pipelines

## Extend the Pipeline

Open `notebooks/02_datajoint_spyglass.ipynb` — **Section 4**.

Add `mean_result : float` to `MyAnalysis`:

1. Edit `schema_template.py` — add the field and compute it in `make`
2. Restart the kernel — DataJoint re-reads the definition on import
3. Delete old rows — `st.MyAnalysis.delete(safemode=False)`
4. Re-run `populate()` and verify the new field is present

---

# Overview

- ✅ DataJoint Infrastructure
- ✅ DataJoint Table Tiers and Declaration Syntax
- ✅ Spyglass Table Types, including Merge Tables
- ✅ Creating a Custom Pipeline
- 👀 Common DataJoint Errors

---

# Common Errors

- Debug mode
- `IntegrityError`
- `OperationalError` / Permission denied
- `TypeError`
- `KeyError`
- `DataJointError`

---

# Common Errors

## Debug Mode

An error traceback has multiple *frames*. To inspect a specific one:

**In Jupyter** — run `%debug` in the next cell after an exception:

```python
%debug   # opens pdb at the frame where the error occurred
```

**In VS Code** — add a breakpoint and run in debug mode (covered in Session 1).

**Anywhere** — insert a breakpoint in the source code:

```python
breakpoint()   # built-in since Python 3.7; opens pdb at this line
```

Inside `pdb`: `u`/`d` to move frames, `p var` to inspect, `l` to list code,
`q` to quit.

---

# Common Errors

## IntegrityError

```console
IntegrityError: Cannot add or update a child row: a foreign key constraint fails
  (`schema`.`_table`, CONSTRAINT `_table_ibfk_1`
   FOREIGN KEY (`field`) REFERENCES `other_schema`.`parent` (`field`)
   ON DELETE RESTRICT ON UPDATE CASCADE)
```

**Cause:** Something in the key you are inserting does not exist in the
parent table.

<!-- stop -->

The table name after `REFERENCES` tells you where to look.

<!-- stop -->

For `SpyglassMixin` tables, use `find_insert_fail`:

```python
my_key = {"subject_id": "alice_1", "param_name": "default"}
MyAnalysisSelection.insert1(my_key)   # fails here

# Find which parent tables have no matching row:
MyAnalysisSelection().find_insert_fail(my_key)
# → [SubjBlinded, MyParams]  — whichever are empty for this key
```

---

# Common Errors

## OperationalError / Permission Denied

```console
('Insufficient privileges.',
 "INSERT command denied to user 'sailor'@'%' for table '_my_table'",
 'INSERT INTO `alice_workshop`.`_my_table` ...')
```

**Cause:** Your MySQL user does not have `INSERT` permission on that schema.

<!-- stop -->

Check your current grants:

```python
dj.conn().query("SHOW GRANTS FOR CURRENT_USER();").fetchall()
```

<!-- stop -->

Common fix: the schema prefix does not match your user's granted prefixes.
Use `SCHEMA_PREFIX = os.getenv("USER", "workshop")` and confirm your
username matches what the database admin configured.

---

# Common Errors

## TypeError

```console
TypeError: make() got an unexpected keyword argument 'extra_arg'
```

→ Check `help(MyAnalysis.make)` — you passed an argument the function does not accept.

<!-- stop -->

```console
TypeError: 'NoneType' object is not iterable
```

→ A variable you expected to contain data is `None`.
Use `type(variable)` to check, then trace back to where it was set.

---

# Common Errors

## KeyError

```console
KeyError: 'param_name'
```

→ Accessing `mydict["param_name"]` but the key is absent.

```python
mydict.keys()                         # see what is there
mydict.get("param_name", default)     # safe access with fallback
```

---

# Common Errors

## DataJointError

```console
DataJointError: Attempt to delete part table MyPart before deleting
from its master MyAnalysis first.
```

→ You tried to delete from a Part table directly.
Delete the **master** table entry first — DataJoint will cascade.

<!-- stop -->

```console
DataJointError: Relation is already declared.
```

→ The class has been imported and registered twice in the same session
(e.g., two imports of the same module). Restart the kernel.

---

# Overview

- ✅ DataJoint Infrastructure
- ✅ DataJoint Table Tiers and Declaration Syntax
- ✅ Spyglass Table Types, including Merge Tables
- ✅ Creating a Custom Pipeline
- ✅ Common DataJoint Errors

---

# Session 2 complete

Key takeaways:

- DataJoint is a Python ↔ MySQL bridge — version control your definitions
- Four DataJoint tiers: `Manual`, `Lookup`, `Computed`/`Imported`, `Part`
- Spyglass pattern: Parameter → Selection → Analysis (→ Merge)
- `populate()` runs `make` for every unprocessed Selection row
- When things go wrong: `find_insert_fail`, `SHOW GRANTS`, `%debug`

---

<!--
PRESENTER NOTE
To present these slides:
    pip install lookatme
    lookatme docs/src/session2_datajoint.md --live
-->
