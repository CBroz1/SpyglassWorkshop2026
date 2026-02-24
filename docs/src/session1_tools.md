---
title: "Session 1: Tools for Scientific Computing"
author: Chris Broz
date: 01/2026
styles:
    style: dracula
---

# Calibration Slide

```
Window must be this wide ─────────────────────────────────────────────────►

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

- ⭕ GitHub: repos, branches, forks, pull requests, issues
- ⭕ VS Code: settings, extensions, and shortcuts
- ⭕ Jupyter: cells, kernel, and useful magics
- ⭕ Code quality: `ruff`, `isort`, and `pre-commit`
- ⭕ Debugging: breakpoints and `%debug`

---

# Overview

This session will cover ...

- 👀 GitHub: repos, branches, forks, pull requests, issues
- ⭕ VS Code: settings, extensions, and shortcuts
- ⭕ Jupyter: cells, kernel, and useful magics
- ⭕ Code quality: `ruff`, `isort`, and `pre-commit`
- ⭕ Debugging: breakpoints and `%debug`

---

# GitHub

## Why version control?

Science produces code that:

- Changes frequently as understanding grows
- Must be reproducible months or years later
- Is increasingly shared and reused by others

<!-- stop -->

Version control lets you ...

- Travel back to any previous state
- Work on new ideas without breaking what works
- Propose and review changes safely
- Collaborate without overwriting each other

---

# GitHub

## Key concepts

```
  ┌─────────────────────────────────────┐
  │  Remote (github.com)                │
  │                                     │
  │  upstream/main ──── your-fork/main  │
  │                            │        │
  └────────────────────────────┼────────┘
                               │ clone
                    ┌──────────▼──────────┐
                    │  Local              │
                    │                     │
                    │  main               │
                    │  └── your-branch    │
                    └─────────────────────┘
```

<!-- stop -->

| Term | Meaning |
| ---: | :------ |
| **Repository** | A project and its full history |
| **Commit** | A saved snapshot with a message |
| **Branch** | A parallel line of development |
| **Fork** | Your personal copy of someone else's repo |
| **Pull Request** | A proposal to merge one branch into another |
| **Issue** | A tracked bug, question, or feature request |

---

# GitHub

## Repository structure

A repository is just a directory with a standard layout:

```
SpyglassWorkshop2026/
├── .github/                 # issue templates and PR template
├── .gitignore               # files Git will never track (secrets, caches)
├── .pre-commit-config.yaml  # auto-formatting hooks (run on every commit)
├── README.md                # project overview — the front page on GitHub
├── LICENSE                  # how others may use this code
├── CHANGELOG.md             # human-readable history of releases
├── environment.yml          # conda environment (reproducible setup)
├── pyproject.toml           # package metadata and tool configuration
├── src/spyglass_workshop/   # library source code (importable package)
├── notebooks/               # Jupyter notebooks for demos and exercises
├── tests/                   # pytest test suite
└── docs/                    # MkDocs documentation source
```

<!-- stop -->

The `src/` layout keeps library code separate from scripts and notebooks —
you have to `pip install -e .` before you can `import` it, which prevents
accidentally importing stale or uninstalled code.

---

# GitHub

## Branches

- `main` is the stable, shared branch — don't break it.
- Create a branch for each feature, fix, or experiment.

<!-- stop -->

```bash
git checkout -b your-name/my-feature   # create and switch
git branch                             # list branches
git checkout main                      # switch back
```

<!-- stop -->

Good branch names are short and descriptive:

```
alice/add-filtering-notebook
fix/off-by-one-in-fibonacci
docs/update-readme
```

---

# GitHub

## Forks and Pull Requests

1. **Fork** creates your own copy of a repo on GitHub.
2. **Clone** downloads your fork to your laptop.
3. Make changes on a branch.
4. **Push** your branch to your fork.
5. Open a **Pull Request** to propose merging into upstream.

<!-- stop -->

```bash
# After forking on github.com:
git clone https://github.com/<you>/SpyglassWorkshop2026
cd SpyglassWorkshop2026

git checkout -b your-name/my-change
# ... edit files ...
git add changed_file.py
git commit -m "describe what and why"
git push origin your-name/my-change
# Then open a PR on github.com
```

---

# GitHub

## Issues

- Issues track bugs, questions, and feature requests.
- Reference them in commit messages: `fix #42` auto-closes.
- Useful even for solo projects — a searchable history of decisions.

```
Title: fibonacci_buggy.py: f(1) returns 0

Steps to reproduce:
  from spyglass_workshop.examples.fibonacci_buggy import f
  f(1)  # Expected: 1, Got: 0

Environment: Python 3.11, spyglass-workshop 0.1.0
```

---

# Overview

This session will cover ...

- ✅ GitHub: repos, branches, forks, pull requests, issues
- 👀 VS Code: settings, extensions, and shortcuts
- ⭕ Jupyter: cells, kernel, and useful magics
- ⭕ Code quality: `ruff`, `isort`, and `pre-commit`
- ⭕ Debugging: breakpoints and `%debug`

---

# VS Code

## Why a good editor matters

Your editor is where you spend most of your time.

Small productivity gains compound across thousands of hours:

- Instant feedback on errors (linting, type hints)
- Format on save — no mental overhead on style
- Jump to definition, rename across files
- Integrated terminal, git, and debugger

---

# VS Code

## Getting started

1. Open VS Code, then open the workshop folder:

```bash
code /path/to/SpyglassWorkshop2026
```

<!-- stop -->

2. Accept the prompt to install recommended extensions
   (from `.vscode/extensions.json`)

<!-- stop -->

3. Select the conda environment as your Python interpreter:

```
Ctrl+Shift+P  →  Python: Select Interpreter
→  spyglass-workshop
```

---

# VS Code

## Key settings (`.vscode/settings.json`)

```json
{
    "editor.rulers": [ 80 ],          // vertical guide at 80 chars
    "editor.stickyScroll.enabled": true, // always see current scope
    "files.autoSave": "onFocusChange",   // save when you switch tabs
    "[python]": {
        "editor.formatOnSave": true,     // ruff formats on every save
        "editor.defaultFormatter": "charliermarsh.ruff",
    },
    "notebook.lineNumbers": "on",        // line numbers in cells
    "notebook.formatOnSave.enabled": true,
}
```

These are already active — try saving a messy Python file.

---

# VS Code

## Recommended extensions

**Python development**

| Extension | Purpose |
| :-------- | :------ |
| `charliermarsh.ruff` | Fast linter + formatter |
| `ms-python.python` | Core Python support |
| `ms-python.vscode-pylance` | Type inference, autocomplete |
| `ms-python.debugpy` | Debugger |

<!-- stop -->

**Jupyter**

| Extension | Purpose |
| :-------- | :------ |
| `ms-toolsai.jupyter` | Notebook support |
| `ms-toolsai.vscode-jupyter-cell-tags` | Organise cells |
| `ms-toolsai.jupyter-keymap` | Familiar keybindings |

---

# VS Code

## Useful shortcuts

| Shortcut | Action |
| :------- | :----- |
| `Ctrl+Shift+P` | Command palette (search all commands) |
| `Ctrl+P` | Quick file open |
| `F12` | Go to definition |
| `Shift+F12` | Find all references |
| `F2` | Rename symbol everywhere |
| `Ctrl+/` | Toggle line comment |
| `Alt+↑/↓` | Move line up/down |
| `Ctrl+Shift+\`` | New terminal |

Try: `F12` on any imported function to jump to its source.

---

# Overview

This session will cover ...

- ✅ GitHub: repos, branches, forks, pull requests, issues
- ✅ VS Code: settings, extensions, and shortcuts
- 👀 Jupyter: cells, kernel, and useful magics
- ⭕ Code quality: `ruff`, `isort`, and `pre-commit`
- ⭕ Debugging: breakpoints and `%debug`

---

# Jupyter

## Why notebooks?

Notebooks let you interleave code, output, and prose.

They are well-suited for:

- Exploratory analysis — run one cell at a time, inspect results
- Teaching — explain *and* demonstrate in the same document
- Reproducible workflows — share as a readable narrative

<!-- stop -->

They are *less* well-suited for:

- Production code (use `.py` modules instead)
- Large collaborations (merge conflicts are painful)

---

# Jupyter

## Cell types

| Type | Purpose |
| :--- | :------ |
| **Code** | Executable Python. `Shift+Enter` to run. |
| **Markdown** | Formatted text, equations, images. |
| **Raw** | Passed through unmodified (e.g., for nbconvert). |

<!-- stop -->

Shortcuts (in command mode — press `Esc` first):

| Key | Action |
| :-- | :----- |
| `A` / `B` | Insert cell above / below |
| `M` / `Y` | Change cell to Markdown / Code |
| `D D` | Delete cell |
| `Shift+Enter` | Run cell and move to next |
| `Ctrl+Enter` | Run cell in place |

---

# Jupyter

## The kernel

The kernel is the Python process running behind the notebook.

```
Notebook (browser)  ←─-→  Kernel (Python process)
     cell source                 executes code
     cell output         ←──    returns result
```

<!-- stop -->

- All cells share the **same** namespace — order matters.
- If things get confusing: `Kernel → Restart & Run All`
- The kernel indicator (top-right) shows idle `○` vs busy `●`

<!-- stop -->

In VS Code: use the **Variables** panel (`View → Variables`)
to inspect all objects in the current kernel namespace.

---

# Jupyter

## Useful magics

IPython "magic" commands start with `%` (line) or `%%` (cell).

```python
%timeit f_list(100)      # benchmark a statement

%run my_script.py        # run a .py file in the kernel

%who                     # list all variables

%%capture                # suppress output from entire cell

import logging
%config Application.log_level = "INFO"  # adjust log level
```

<!-- stop -->

`%debug` is especially useful — we will cover it shortly.

---

# Jupyter

## Jupytext — notebooks in version control

`.ipynb` files store outputs and metadata alongside source, making `git diff`
noisy.  `jupytext` converts a notebook to a plain Python script — clean diffs,
no JSON, no embedded images.

<!-- stop -->

```bash
# Convert all notebooks to lightweight Python scripts
jupytext --to py:light notebooks/*.ipynb

# Move them to a dedicated folder and format
mv notebooks/*.py notebooks/py_scripts/
ruff format notebooks/py_scripts/
```

<!-- stop -->

The `# %%` markers in the `.py` files are understood by VS Code and
JupyterLab — run them interactively or as a plain script.

---

# Overview

This session will cover ...

- ✅ GitHub: repos, branches, forks, pull requests, issues
- ✅ VS Code: settings, extensions, and shortcuts
- ✅ Jupyter: cells, kernel, and useful magics
- 👀 Code quality: `ruff`, `isort`, and `pre-commit`
- ⭕ Debugging: breakpoints and `%debug`

---

# Code Quality

## Why it matters

Code is read far more often than it is written.

<!-- stop -->

*"Any fool can write code that a computer can understand.*
*Good programmers write code that humans can understand."*
— Martin Fowler

<!-- stop -->

Consistent style removes cognitive overhead:

- `black`/`ruff` format: you stop thinking about whitespace
- `isort`: imports are always in a predictable order
- Line limit (80): side-by-side diffs always fit on screen
- Linting: bugs flagged before you run the code

---

# Code Quality

## Atomizing

Working memory is limited — long functions force you to hold too much
in mind at once.  Extract pieces into the smallest chunk that deserves
a name:

| Level | Mechanism |
| :---- | :-------- |
| Conceptual group | Blank line (paragraph break) |
| Conditional value | Ternary or early assignment |
| Reusable step | Method on a class |
| Shared within a module | Helper function |
| Shared across a project | Utility module |

<!-- stop -->

A well-named helper turns code you have to *read* into a word you
already *know*.

---

# Code Quality

## `ruff`

`ruff` is a fast Python linter and formatter — it replaces
`black`, `isort`, `flake8`, and more with a single tool.

```bash
ruff check my_file.py       # report issues
ruff check --fix my_file.py # auto-fix what it can
ruff format my_file.py      # format in place
```

<!-- stop -->

It catches issues like:

- `F401` — imported but unused (`import json`)
- `E711` — comparison to `None` should use `is`
- `UP` — upgrades to modern Python syntax
- `I` — import ordering (replaces `isort`)

<!-- stop -->

In VS Code with `charliermarsh.ruff`, this runs on every save.

---

# Code Quality

## Import order

`isort` / `ruff I` enforces a standard import order:

```python
# 1. Standard library
import os
from typing import Union

# 2. Third-party packages
import datajoint as dj
import numpy as np

# 3. Local / relative imports
from spyglass_workshop.examples.fibonacci import f
```

<!-- stop -->

Why does order matter? It makes the dependency graph of a file
immediately readable at the top.

---

# Code Quality

## Type hints & docstrings

Type hints are not enforced at runtime but document intent so editors
and readers don't have to guess:

```python
def get_data_interface(
    nwbfile: pynwb.NWBFile,
    name: str,
    interface_class: type | None = None,
) -> NWBDataInterface | None:
```

<!-- stop -->

Docstrings power `help()` and auto-generated docs.  Spyglass uses
**NumPy style**:

```python
    """One-line description.

    Parameters
    ----------
    nwbfile : pynwb.NWBFile
        The NWB file to search.
    name : str
        Name of the data interface.

    Returns
    -------
    NWBDataInterface or None
    """
```

---

# Code Quality

## `pre-commit`

`pre-commit` runs checks automatically before every `git commit`.

```yaml
# .pre-commit-config.yaml (already in this repo)
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format
```

<!-- stop -->

```bash
pre-commit install           # one-time setup (already done)
pre-commit run --all-files   # run manually
```

If a hook fails, the commit is blocked and the file is fixed.
Re-stage and try again.

<!-- stop -->

This means bad style never reaches the repository... unless you intentionally
bypass it with `git commit --no-verify`.

---

# Overview

This session will cover ...

- ✅ GitHub: repos, branches, forks, pull requests, issues
- ✅ VS Code: settings, extensions, and shortcuts
- ✅ Jupyter: cells, kernel, and useful magics
- ✅ Code quality: `ruff`, `isort`, and `pre-commit`
- 👀 Debugging: breakpoints and `%debug`

---

# Debugging

## When print statements are not enough

Print-based debugging:

- Requires editing and re-running the file
- Only shows what you thought to print
- Gets messy fast

<!-- stop -->

A debugger lets you:

- **Pause** execution at any line
- **Inspect** every variable in scope
- **Step** through code line by line
- **Move** up and down the call stack

---

# Debugging

## Setting breakpoints in VS Code

1. Click in the **gutter** (left of line numbers) to add a red dot.
2. Run the file or notebook cell in **debug mode**:
   - Script: use the debug sidebar (`Ctrl+Shift+D`)
   - Notebook: use the dropdown next to the ▶ button → *Debug Cell*
3. Execution pauses at the breakpoint.
4. Use the debug toolbar: Step Over, Step Into, Step Out, Continue.

<!-- stop -->

The **Variables** panel shows all locals and their current values.
The **Debug Console** lets you evaluate expressions live.

---

# Debugging

## `%debug` in notebooks

After an exception in a cell, run `%debug` in a new cell:

```python
# Cell 1 — causes an error
from spyglass_workshop.examples.fibonacci_buggy import f
f(1)   # returns wrong answer — let's investigate

# Cell 2 — enter the debugger
%debug
```

<!-- stop -->

Inside `pdb`:

| Command | Action |
| :------ | :----- |
| `l` | list code around current line |
| `p expr` | print the value of an expression |
| `n` | next line (step over) |
| `s` | step into a function call |
| `u` / `d` | move up / down the call stack |
| `q` | quit the debugger |

---

# Debugging

## Exercise

`fibonacci_buggy.py` contains two bugs.

```python
from spyglass_workshop.examples.fibonacci_buggy import f, f_list

print(f(1))         # Expected: 1
print(f_list(5))    # Expected: [1, 1, 2, 3, 5]
```

<!-- stop -->

1. Run the cells in `notebooks/01_tools_exercises.ipynb`.
2. The outputs will be wrong. Use `%debug` or VS Code
   breakpoints to trace through the execution.
3. Fix the bugs in `fibonacci_buggy.py`.
4. Run `pytest tests/examples/test_fibonacci_buggy.py` to verify.

---

# Overview

This session will cover ...

- ✅ GitHub: repos, branches, forks, pull requests, issues
- ✅ VS Code: settings, extensions, and shortcuts
- ✅ Jupyter: cells, kernel, and useful magics
- ✅ Code quality: `ruff`, `isort`, and `pre-commit`
- ✅ Debugging: breakpoints and `%debug`

---

# Session 1 complete

Key takeaways:

- Fork → clone → branch → commit → push → PR
- VS Code settings live in `.vscode/` — they are already configured
- `ruff` and `pre-commit` enforce style automatically
- The debugger is faster than print statements

<!-- stop -->

After the break: **Session 2 — Spyglass & DataJoint Infrastructure**
