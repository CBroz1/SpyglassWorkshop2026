---
title: 'Session 2: Spyglass & DataJoint Infrastructure'
author: Chris Broz
date: 03/2026
styles:
  style: dracula
---

# Calibration Slide

```text
Window must be this wide ──────────────────────────────────────────────────────────────────────────────►

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

______________________________________________________________________

# Prerequisites

If you haven't already done so, please ...

1. Install Spyglass
   1. `git clone https://github.com/LorenFrankLab/spyglass`
   2. `python spyglass/scripts/install.py --minimal` # Takes time
2. Install this workshop's repo
   1. `git clone https://github.com/CBroz1/SpyglassWorkshop2026`
   2. Install as editable: `pip install -e ./SpyglassWorkshop2026`
   3. Add kernel:
      `conda run -n spyglass python -m ipykernel install --user --name spyglass`
   4. Run the first cell in `./notebooks/02_datajoint_spyglass.ipynb`
   5. Write down IP for later: TBD:/tmp/spyglass_data
   6. Optionally, poke around `./docs` and `./notebooks`

# Overview

This session will cover ...

- ⭕ DataJoint Infrastructure
- ⭕ DataJoint Table Tiers and Declaration Syntax
- ⭕ Spyglass Table Types, including Merge Tables
- ⭕ Table Operators
- ⭕ Creating a Custom Pipeline
- ⭕ Common DataJoint Errors

______________________________________________________________________

# Overview

- 👀 DataJoint Infrastructure
- ⭕ DataJoint Table Tiers and Declaration Syntax
- ⭕ Spyglass Table Types, including Merge Tables
- ⭕ Table Operators
- ⭕ Creating a Custom Pipeline
- ⭕ Common DataJoint Errors

______________________________________________________________________

# Infrastructure

## What are we connecting to?

```text
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

______________________________________________________________________

# Infrastructure

## What are we connecting to?

```text
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

______________________________________________________________________

# Infrastructure

## DataJoint's Role

```text
        ┌──────────┐  ┌────────┐
        │DataJoint─┼──┼─> MySQL│
        └──────────┘  └────────┘
```

<!-- stop -->

When you import a DataJoint table, it ...

1. Connects to the MySQL server using credentials from a local config file (we
   will create this in the notebook)
2. Checks whether that table exists in the database
3. If not, declares it using the Python `definition`

<!-- stop -->

At its core, DataJoint maps Python ↔ SQL:

- Python class definitions → SQL `CREATE TABLE` statements
- Python `insert` / `fetch` calls → SQL `INSERT` / `SELECT` queries
- Python `populate` calls → SQL transactions triggered by upstream changes

______________________________________________________________________

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

```text
     ┌───────────────┐
     │SUBJECT        │
     │*subj_id*, name│
     └───────┬───────┘
             ▼
     ┌─────────────────────────────┐  ┌───────────────────────────┐
     │SESSION                      │  │ PARAMETERS                │
     │*subj_id*, *session_id*, time│  │ *param_id*, param1, param2│
     └─────────────┬───────────────┘  └────────────┬──────────────┘
                   └──────────────────┬────────────┘
                                      ▼
               ┌───────────────────────────────────────────┐
               │ANALYSIS                                   │
               │*subj_id*, *session_id*, *param_id*, result│
               └───────────────────────────────────────────┘
```

______________________________________________________________________

# Infrastructure

## Key Terminology

- *Upstream* / *Downstream*: direction of data flow in the dependency graph
- *Primary key*: the set of fields that uniquely identifies each row (`*`)
- *Secondary key*: additional data stored per row; values may repeat
- *Foreign key*: a reference to the primary key of another table

```text
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

______________________________________________________________________

# Infrastructure

## Syncing Code and Database

Experiments evolve.

DataJoint's role as interface means YOU must keep track.

```text
┌──────────────────────────┐     ┌──────────────────────────┐
│  Python  (in git)        │     │  Database  (persistent)  │
│                          │     │                          │
│  class definition   ─────┼────►│  table structure         │
│  insert logic       ─────┼────►│  computed rows           │
└──────────────────────────┘     └──────────────────────────┘
```

<!-- stop -->

- Changing **`definition`** → table structure no longer matches the class
- Changing **function logic** → existing rows were produced by old logic

<!-- stop -->

Git commit history is a link between a row and the code that made it.

**Version-control your schema** alongside your data.

______________________________________________________________________

# Infrastructure

Follow along in `notebooks/02_datajoint_spyglass.ipynb` — **Section 1**.

## Shared Drives

Spyglass relies on shared network drives for data files.

```bash
mkdir -p ~/spyglass_data
# Linux:
sudo mount -t nfs <TBD>:/tmp/spyglass_data ~/spyglass_data
# macOS:
sudo mount -t nfs -o resvport <TBD>:/tmp/spyglass_data ~/spyglass_data
```

If on Windows, download from and unpack to your data directory.

`https://ucsf.box.com/v/SpyglassWorkshop2026Data`

______________________________________________________________________

# Infrastructure

Follow along in `notebooks/02_datajoint_spyglass.ipynb` — **Section 1**.

## Database Connection & The Config File

The minimal fields needed to connect to the workshop database:

```json
{
    "database.host":   "TBD",
    "database.user":     "sailor",
    "database.password": "galley",
    "database.port":     3306,
    "database.use_tls":  false,
    "custom": {
        "spyglass_dirs": {
            "base": "/home/YOU/spyglass_data",
        }
    }

}
```

<!-- stop -->

1. Local config: `./dj_local_conf.json`
2. Global config: `~/.datajoint_config.json`

```python
import datajoint as dj
dj.config.load("path/to/dj_local_conf.json")
dj.conn().ping()   # raises an error if the connection fails
```

______________________________________________________________________

# Overview

- ✅ DataJoint Infrastructure
- 👀 DataJoint Table Tiers and Declaration Syntax
- 👀 Spyglass Table Types, including Merge Tables
- ⭕ Table Operators
- ⭕ Creating a Custom Pipeline
- ⭕ Common DataJoint Errors

______________________________________________________________________

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

______________________________________________________________________

# Python Structure

## Front Matter: Imports

```python
import os                          # standard library

from typing import Union           # individual class import
import datajoint as dj             # aliased package import

from spyglass.common import (      # individual imports from a package
    Nwbfile, # noqa: F401          # noqa: F401 silences "unused" linter warning
    Subject,
)
from spyglass.utils import SpyglassMixin

from .utils import SCHEMA_PREFIX   # relative import
```

______________________________________________________________________

# Python Structure

## Front Matter: Schema Declaration

```python
schema = dj.schema("workshop_<YourName>")

@schema
class ExampleTable(...):
    pass
```

<!-- stop -->

- Database permissions are managed **by schema prefix**
- Spyglass uses shared prefixes (e.g., `common_*`) - **do not add to these**
- Use your username or a project-specific prefix for your own tables

______________________________________________________________________

# Python Structure

## Table Syntax: Decorator

```python
schema = dj.schema("workshop_<YourName>")

@schema
class ExampleTable(...):
    pass
```

<!-- stop -->

`@schema` is a *decorator* that registers the class with the database.

> **What is a decorator?** The `@` syntax above wraps a class or function to add
> behavior. Here, it passes the definition for declaration or fetching.

When inspecting existing tables, we can see their full names:

```python
from datajoint.utils import to_camel_case

# Spyglass shared tables live under their own prefixes:
ExampleTable.full_table_name == "`workshop_name`.`example_table`"
to_camel_case(ExampleTable.table_name) == "ExampleTable"
```

______________________________________________________________________

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
- `SpyglassMixin` — adds helpers (`<<`, `find_insert_fail`, etc.)

```python
from spyglass.position.position_merge import PositionOutput

# What does this table inherit from?
PositionOutput.__bases__

# What does that class do?
help(PositionOutput.__bases__[1].__bases__[-1])
dir(PositionOutput.__bases__[1].__bases__[-1])
```

______________________________________________________________________

# Python Structure

## Table Syntax: DataJoint Table Tiers

| Tier          | prefix    | Populated by           | Use case                |
| :------------ | :-------- | :--------------------- | :---------------------- |
| `dj.Manual`   | *(none)*  | A person, via `insert` | Subjects, selections    |
| `dj.Lookup`   | `#`       | Declared in `contents` | Paramsets, lookup vals  |
| `dj.Imported` | `_`       | `make`, reading files  | NWB ingestion           |
| `dj.Computed` | `__`      | `make`, from upstream  | Analysis results        |
| `dj.Part`     | `<tbl>__` | Any of the above       | One-to-many sub-records |

Note: `Imported` vs `Computed` is an unenforced convention.

<!-- stop -->

## Table Syntax: Spyglass Conceptual Types

| Spyglass Type | DataJoint Tier      | Role                                  |
| ------------: | :------------------ | :------------------------------------ |
|          Data | Manual, Imported    | Starting point — raw or ingested      |
|     Parameter | Lookup (or Manual)  | Analysis settings                     |
|     Selection | Manual              | Pair data with parameters             |
|      Analysis | Computed            | Run `make`, store results             |
|         Merge | `_Merge` with Parts | Unify outputs from multiple pipelines |

<!-- stop -->

```python
from spyglass.ripple.v1.ripple import schema

tbls = schema.list_tables()  # shows all tables in the schema
tbls = [
    '#ripple_parameters',
    'ripple_l_f_p_selection',
    'ripple_l_f_p_selection__ripple_l_f_p_electrode',
    '__ripple_times_v1'
]

```

______________________________________________________________________

# Python Structure

## Table Types: Overview

```text
               ┌────┐
               │Data│
               └─┬──┘   ┌──────────────┐
    ┌────────────┼───┐  │  ┌───────────┼───────┐
    │Schema      │   │  │  │Merge      │       │
    │            │   │  │  │Schema     │       │
    │┌─────────┐ │   │  │  │           │       │
    ││Parameter│ │   │  │  │┌──────┐   │       │
    │└────┬────┘ │   │  │  ││Merge │   │       │
    │     ▼      ▼   │  │  │└────┬─┘   │       │
    │    ┌─────────┐ │  │  │     ▼     ▼       │
    │    │Selection│ │  │  │    ┌───────────┐  │
    │    └────┬────┘ │  │  │    │Merge Part │  │
    │         ▼      │  │  │    └───────────┘  │
    │    ┌─────────┐ │  │  │                   │
    │    │Analysis │ │  │  │                   │
    │    └────┬────┘ │  │  │                   │
    └─────────┼──────┘  │  └───────────────────┘
              └─────────┘
```

*Tip:* `dj.Diagram(schema)` draws the dependency graph,
[docs](https://docs.datajoint.com/how-to/read-diagrams/)

```Python
dj.Diagram(schema) - 1  # shows direct parents
dj.Diagram(MyTable) - 2 # shows grandparents
dj.Diagram(MyTable) + 1 # shows direct children
dj.Diagram(MyTable) - 1 + 1 # shows children of parents (siblings)
dj.Diagram(MyTable) + dj.Diagram(MyOtherTable) # shows relationships
```

______________________________________________________________________

# Python Structure

## Table Types: With Downstream Schema

```text
               ┌────┐
               │Data│
               └─┬──┘   ┌──────────────┐          ┌──────────────┐
    ┌────────────┼───┐  │  ┌───────────┼───────┐  │  ┌───────────┼───────┐
    │Schema      │   │  │  │Merge      │       │  │  │New        │       │
    │            │   │  │  │Schema     │       │  │  │Schema     │       │
    │┌─────────┐ │   │  │  │           │       │  │  │           ▼       │
    ││Parameter│ │   │  │  │┌──────┐   │       │  │  │    ┌───────────┐  │
    │└────┬────┘ │   │  │  ││Merge │   │       │  │  │    │Next Table │  │
    │     ▼      ▼   │  │  │└─┬──┬─┘   │       │  │  │    └───────────┘  │
    │    ┌─────────┐ │  │  │  │  ▼     ▼       │  │  │                   │
    │    │Selection│ │  │  │  │ ┌───────────┐  │  │  │                   │
    │    └────┬────┘ │  │  │  │ │Merge Part │  │  │  │                   │
    │         ▼      │  │  │  │ └───────────┘  │  │  │                   │
    │    ┌─────────┐ │  │  │  │                │  │  │                   │
    │    │Analysis │ │  │  │  │                │  │  │                   │
    │    └────┬────┘ │  │  │  │                │  │  │                   │
    └─────────┼──────┘  │  └──┼────────────────┘  │  └───────────────────┘
              └─────────┘     └───────────────────┘
```

Downstream, reference the **Merge** table directly — not a Merge Part

______________________________________________________________________

# Python Structure

## Table Syntax: Definitions

<!-- stop -->

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
    [unique] some_id: uuid         # enforced unique key
    -> [nullable] Table            # foreign key: inherits Table's PK
    -> Table.proj(dest='src')      # foreign key with renamed column
    """
```

<!-- stop -->

- Everything above `---` is a **primary key** field
- Everything below is a **secondary** (non-identifying) field
- `->` inherits the primary key of the referenced table
- FK-referenced tables must be imported in the same file

______________________________________________________________________

# Python Structure

## Declaration Limitations (*time permitting*)

<!-- stop -->

### Naming

- Class names must be `CamelCase`; attribute names `snake_case` only
- Attribute names must be lowercase, no spaces or hyphens

### Primary key

- Every table must have a primary key
- Primary key fields cannot be nullable or have default values (except
  `auto_increment`)
- Blobs, JSON, and filepaths cannot be primary key fields

<!-- stop -->

### Foreign keys

- Must reference an existing base table — not a query expression
- Only `[nullable]` and `[unique]` modifiers are allowed

### Part tables

- Part tables cannot be nested (no parts of parts)
- Parts cannot be deleted or dropped directly — delete from the master

<!-- stop -->

### After declaration

- Primary keys, foreign keys, and indexes **cannot be altered** — you must
  delete all downstream data and redeclare the table
- New tables cannot be declared from inside a `make`/`populate` call

______________________________________________________________________

# Python Structure

## Explore Existing Tables

Now that we have seen table declaration syntax, explore Spyglass tables using
the same operators.

Think of Spyglass like a graph. How can you get from A to B?

Open `notebooks/02_datajoint_spyglass.ipynb` — **Section 2**.

______________________________________________________________________

# Overview

- ✅ DataJoint Infrastructure
- ✅ DataJoint Table Tiers and Declaration Syntax
- ✅ Spyglass Table Types, including Merge Tables
- 👀 Table Operators
- ⭕ Creating a Custom Pipeline
- ⭕ Common DataJoint Errors

______________________________________________________________________

# Table Operators

DataJoint provides Python operators for querying across tables.

| Operator         | What it does                                               |
| :--------------- | :--------------------------------------------------------- |
| `A & r`          | **Restrict** — filter `A` rows by dict, string, or table   |
| `A * B`          | **Join** — combine columns in `A` and `B` where keys match |
| `A - B`          | **Minus** — rows of `A` whose keys do not appear in `B`    |
| `A.proj()`       | **Project** — select or rename specific columns            |
| `A.insert()`     | **Insert** — add new rows to `A`                           |
| `A.fetch()`      | **Fetch** — query results as Python objects                |
| `A.aggr(B, ...)` | **Aggregate** — group by `A` and compute stats on `B`      |

______________________________________________________________________

# Table Operators

## Restrict `&` and Join `*`

**Restrict** filters rows of a table by a condition (dict, string or other
table)

- **Dicts** match one exact value per field
- **Strings** accept any condition — patterns, ranges, and combinations

```python
Subject & {"subject_id": "alice_1"}          # only "alice_1"
Subject & "subject_id LIKE 'alice%'"         # everyone starting with "alice"
Subject & "subject_id LIKE '%_1'"            # any subject ending in "_1"
Session & "session_date > '2024-01-01'"      # date range
Subject & "sex = 'F' AND age > 365"          # multiple conditions

recorded  = Session & Nwbfile     # sessions that have a linked NWB file

# Join: combine columns from two tables that share primary key fields
subj_sessions = Subject * Session   # one row per (subject, session) pair

# Chain — operations compose left-to-right
alice_sessions = Subject * Session & "subject_id LIKE 'alice%'"
```

______________________________________________________________________

# Table Operators

## Long-Distance Restriction: `<<` and `>>`

Standard `&` requires the restriction field to exist in the table's own primary
key. `SpyglassMixin` adds operators that walk the dependency graph to find a
compatible ancestor or descendant:

| Operator | Direction                      | Reads as                         |
| :------- | :----------------------------- | :------------------------------- |
| `A << r` | **Upstream** — toward roots    | "restrict A by ancestor field"   |
| `A >> r` | **Downstream** — toward leaves | "restrict A by descendant field" |

```python
# All LFP results for subjects whose ID starts with "alice"
lfp_results = LFPOutput() << "subject_id LIKE 'alice%'"

# All upstream subjects linked to sessions after a cutoff date
subjects = Subject() >> "session_date > '2024-01-01'"
```

**NOTE:** May be fickle with dict restrictions.

<!-- stop -->

If `<<` returns `None`, the search may have taken the wrong path. Ban
intermediate tables to make the path unambiguous:

```python
table.ban_search_table(UnwantedIntermediate)
result = table << "subject_id LIKE 'alice%'"
```

______________________________________________________________________

# Table Operators

## Practice

Open `notebooks/02_datajoint_spyglass.ipynb` — **Section 3**.

```python
import spyglass_workshop.schema_template as st

# 1. Dict vs string restriction — compare the results
Subject & {"subject_id": "alice_1"}          # exact match
Subject & "subject_id LIKE 'alice%'"         # all subjects starting with "alice"

# 2. Join and chain
mice   = Subject & "species LIKE '%musculus%'"
joined = mice * Session
print(f"{len(joined)} subject-session pairs")

# 3. Long-distance restriction — upstream
st.MyAnalysis() << "subject_id LIKE 'alice%'"

# 4. Long-distance restriction — downstream
st.MyParams() >> "subject_id LIKE 'alice%'"
```

______________________________________________________________________

# Overview

- ✅ DataJoint Infrastructure
- ✅ DataJoint Table Tiers and Declaration Syntax
- ✅ Spyglass Table Types, including Merge Tables
- ✅ Table Operators
- 👀 Creating a Custom Pipeline
- ⭕ Common DataJoint Errors

______________________________________________________________________

# Custom Pipelines

Designing a pipeline means deciding:

1. What are your **parameters**?
2. What is your **input data**?
3. Do you need a **selection** staging table?
4. What does your **analysis** compute?
5. How do foreign keys connect everything?
6. Should your output feed into a **Merge** table?

______________________________________________________________________

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

______________________________________________________________________

# Custom Pipelines

## Data (1/2) — Preprocessed Input

```python
@schema
class SubjBlinded(SpyglassMixin, dj.Manual):
    """Subjects with anonymized IDs for blinded analysis."""

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

______________________________________________________________________

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

______________________________________________________________________

# Custom Pipelines

## Selection

```python
@schema
class MyAnalysisSelection(SpyglassMixin, dj.Manual):
    """Pairs of input data and parameters to be analyzed."""

    definition = """
    -> SubjBlinded
    -> MyParams
    """
```

<!-- stop -->

- `populate` on the downstream `Computed` table will process every row here
- The Selection table is a *staging area* — insert only the combinations you
  actually want to run

______________________________________________________________________

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

______________________________________________________________________

# Custom Pipelines

## Run the Pipeline

Open `notebooks/02_datajoint_spyglass.ipynb` — **Section 4**.

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

______________________________________________________________________

# Custom Pipelines

## Foreign Key References

Primary vs Secondary and Foreign Key vs Field are orthogonal concepts:

|             | Primary (unique identifier) | Secondary (extra data)          |
| :---------- | :-------------------------- | :------------------------------ |
| **Foreign** | Another processing step     | Associated resource (e.g. file) |
| **Native**  | Arbitrary unique ID         | Arbitrary data field            |

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

______________________________________________________________________

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

______________________________________________________________________

# Custom Pipelines

## Merge Tables

Merge tables let downstream analyses be agnostic about *which* upstream pipeline
produced their input:

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
        # resolves merge_id → returns the Part table holding this result
        parent = LFPOutput().merge_get_parent(key)
        data = parent.fetch_nwb()[0]
        ...
        self.insert1({**key, "analysis_file_name": new_file})
```

<!-- stop -->

See
[Merge table docs](https://lorenfranklab.github.io/spyglass/latest/api/utils/dj_merge_tables/)
for the full `merge_*` method reference.

______________________________________________________________________

# Custom Pipelines

## `schema_template.py`

The workshop package ships with a ready-to-run minimal pipeline:
`src/spyglass_workshop/schema_template.py`

## Exercise Time

Open `notebooks/02_datajoint_spyglass.ipynb` to *Section 4*

______________________________________________________________________

# Custom Pipelines

## Extend the Pipeline

Open `notebooks/02_datajoint_spyglass.ipynb` — **Section 4**.

Add `mean_result : float` to `MyAnalysis`:

1. Edit `schema_template.py` — add the field and compute it in `make`
2. Restart the kernel — DataJoint re-reads the definition on import
3. Delete old rows — `st.MyAnalysis.delete(safemode=False)`
4. Re-run `populate()` and verify the new field is present

______________________________________________________________________

# Overview

- ✅ DataJoint Infrastructure
- ✅ DataJoint Table Tiers and Declaration Syntax
- ✅ Spyglass Table Types, including Merge Tables
- ✅ Table Operators
- ✅ Creating a Custom Pipeline
- 👀 Common DataJoint Errors

______________________________________________________________________

# Common Errors *(time permitting)*

- Debug mode
- `IntegrityError`
- `OperationalError` / Permission denied
- `TypeError`
- `KeyError`
- `DataJointError`

______________________________________________________________________

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

Inside `pdb`: `u`/`d` to move frames, `p var` to inspect, `l` to list code, `q`
to quit.

______________________________________________________________________

# Common Errors

## IntegrityError

```console
IntegrityError: Cannot add or update a child row: a foreign key constraint fails
  (`schema`.`_table`, CONSTRAINT `_table_ibfk_1`
   FOREIGN KEY (`field`) REFERENCES `other_schema`.`parent` (`field`)
   ON DELETE RESTRICT ON UPDATE CASCADE)
```

**Cause:** Something in the key you are inserting does not exist in the parent
table.

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

______________________________________________________________________

# Common Errors

## OperationalError / Permission Denied

```console
('Insufficient privileges.',
 "INSERT command denied to user 'sailor'@'%' for table '_my_table'",
 'INSERT INTO `workshop_alice`.`_my_table` ...')
```

**Cause:** Your MySQL user does not have `INSERT` permission on that schema.

<!-- stop -->

Check your current grants:

```python
dj.conn().query("SHOW GRANTS FOR CURRENT_USER();").fetchall()
```

<!-- stop -->

Common fix: the schema prefix does not match your user's granted prefixes. Use
`SCHEMA_PREFIX = os.getenv("USER", "workshop")` and confirm your username
matches what the database admin configured.

______________________________________________________________________

# Common Errors

## TypeError

```console
TypeError: make() got an unexpected keyword argument 'extra_arg'
```

→ Check `help(MyAnalysis.make)` — you passed an argument the function does not
accept.

<!-- stop -->

```console
TypeError: 'NoneType' object is not iterable
```

→ A variable you expected to contain data is `None`. Use `type(variable)` to
check, then trace back to where it was set.

______________________________________________________________________

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

______________________________________________________________________

# Common Errors

## DataJointError

```console
DataJointError: Attempt to delete part table MyPart before deleting
from its master MyAnalysis first.
```

→ You tried to delete from a Part table directly. Delete the **master** table
entry first — DataJoint will cascade.

<!-- stop -->

```console
DataJointError: Relation is already declared.
```

→ The class has been imported and registered twice in the same session (e.g.,
two imports of the same module). Restart the kernel.

______________________________________________________________________

# Overview

- ✅ DataJoint Infrastructure
- ✅ DataJoint Table Tiers and Declaration Syntax
- ✅ Spyglass Table Types, including Merge Tables
- ✅ Table Operators
- ✅ Creating a Custom Pipeline
- ✅ Common DataJoint Errors

______________________________________________________________________

# Session 2 complete

Key takeaways:

- DataJoint is a Python ↔ MySQL bridge — version control your definitions
- Four DataJoint tiers: `Manual`, `Lookup`, `Computed`/`Imported`, `Part`
- Spyglass pattern: Parameter → Selection → Analysis (→ Merge)
- `populate()` runs `make` for every unprocessed Selection row
- When things go wrong: `find_insert_fail`, `SHOW GRANTS`, `%debug`
