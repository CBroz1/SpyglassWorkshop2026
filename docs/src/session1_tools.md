---
title: 'Session 1: Tools for Scientific Computing'
author: Chris Broz
date: 03/2026
styles:
  style: dracula
---

# Calibration Slide

```text
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

______________________________________________________________________

# Preparation

If you haven't already done so...

1. Open `https://github.com/CBroz1/SpyglassWorkshop2026`
2. Click 'Fork' in the top right, accept defaults
3. Copy the new URL
4. Open a terminal to a path where you store projects.
5. Run the following:

> ```bash
> git clone https://github.com/YOU/SpyglassWorkshop2026 # clone your fork
> conda activate spyglass
> conda env update -f ./SpyglassWorkshop2026/environment.yml
> python -m ipykernel install --user --name spyglass
> ```

These slides are available at `SpyglassWorkshop2026/docs/src/session1_tools.md`

# Overview

This session will cover ...

- ⭕ VS Code: editor tour and settings
- ⭕ Jupyter: cells, kernel, and useful magics
- ⭕ GitHub: repos, branches, forks, pull requests
- ⭕ Code quality: docstrings, `ruff`, and refactoring
- ⭕ Debugging: breakpoints and `%debug` *(time permitting)*

______________________________________________________________________

# Overview

This session will cover ...

- 👀 VS Code: editor tour and settings
- ⭕ Jupyter: cells, kernel, and useful magics
- ⭕ GitHub: repos, branches, forks, pull requests
- ⭕ Code quality: docstrings, `ruff`, and refactoring
- ⭕ Debugging: breakpoints and `%debug` *(time permitting)*

______________________________________________________________________

# VS Code

## Why a good editor matters

Your editor is where you spend most of your time.

Small productivity gains compound across many hours:

- Instant feedback on errors (linting, type hints)
- Format on save — no mental overhead on style
- Jump to definition, rename across files
- Integrated terminal, git, and debugger

______________________________________________________________________

# VS Code

## Getting started

1. Open VS Code, then open the workshop folder:

```bash
code /path/to/SpyglassWorkshop2026
```

2. Accept the prompt to install recommended extensions (from
   `.vscode/extensions.json`)

3. Select the conda environment as your Python interpreter:

```text
Ctrl+Shift+P  →  Python: Select Interpreter
→  spyglass
```

______________________________________________________________________

# VS Code

## Interface tour

- Can VSCode do that? Try `Ctrl+Shift+P`
- Extensions
- File Explorer

[Shortcuts cheatsheet](https://quickref.me/vscode.html)

<!-- stop -->

## Repository structure

A repository is just a directory with a standard layout:

```text
SpyglassWorkshop2026/
├── .vscode/                 # Workspace settings and recommended extensions
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

______________________________________________________________________

# Overview

This session will cover ...

- ✅ VS Code: editor tour and settings
- 👀 Jupyter: cells, kernel, and useful magics
- ⭕ GitHub: repos, branches, forks, pull requests
- ⭕ Code quality: docstrings, `ruff`, and refactoring
- ⭕ Debugging: breakpoints and `%debug` *(time permitting)*

______________________________________________________________________

# Jupyter

## Why notebooks?

Notebooks let you interleave prose, code, and output.

They are well-suited for:

- Exploratory analysis — run one cell at a time, inspect results
- Teaching — explain *and* demonstrate in the same document
- Reproducible workflows — share as a readable narrative

<!-- stop -->

They are *less* well-suited for:

- Production code (use `.py` modules instead)
- Large collaborations (merge conflicts are painful)

<!-- stop -->

## Cell types

| Type         | Purpose                                          |
| :----------- | :----------------------------------------------- |
| **Code**     | Executable Python. `Shift+Enter` to run.         |
| **Markdown** | Formatted text, equations, images.               |
| **Raw**      | Passed through unmodified (e.g., for nbconvert). |

[Markdown Cheatsheet](https://www.markdownguide.org/cheat-sheet/)

______________________________________________________________________

# Jupyter

## The kernel

The kernel is the Python process running behind the notebook.

```text
Notebook       <->   Kernel (Python)
  cell source          executes code
  cell output  <--    returns result
```

<!-- stop -->

- All cells share the **same** namespace — order matters.
- If things get confusing: `Kernel → Restart & Run All`
- The kernel indicator (top-right) shows idle `○` vs busy `●`

<!-- stop -->

In VS Code: use the **Variables** panel (`View → Variables`) to inspect all
objects in the current kernel namespace.

<!-- stop -->

Time for a quick tour!

______________________________________________________________________

# Overview

This session will cover ...

- ✅ VS Code: editor tour and settings
- ✅ Jupyter: cells, kernel, and useful magics
- 👀 GitHub: repos, branches, forks, pull requests
- ⭕ Code quality: docstrings, `ruff`, and refactoring
- ⭕ Debugging: breakpoints and `%debug` *(time permitting)*

______________________________________________________________________

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

______________________________________________________________________

# GitHub

## Key concepts

```text
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

|             Term | Meaning                                     |
| ---------------: | :------------------------------------------ |
|   **Repository** | A project and its full history              |
|       **Commit** | A saved snapshot with a message             |
|       **Branch** | A parallel line of development              |
|         **Fork** | Your personal copy of someone else's repo   |
| **Pull Request** | A proposal to merge one branch into another |
|        **Issue** | A tracked bug, question, or feature request |
|       **Action** | An automated script run by GitHub           |

______________________________________________________________________

# GitHub

## Branches

- `main` is canonically the stable, shared branch
- Create a branch for each feature, fix, or experiment.

<!-- stop -->

## Forks and Pull Requests

1. **Fork** your personal copy of a repository.
2. **Clone** downloads your fork to your laptop.
3. Make changes on a branch.
4. **Push** your branch to your fork.
5. Open a **Pull Request** to propose merging into upstream.

<!-- stop -->

## Git Commits

Commits happen in 4 phases:

1. Edit: Saving changes to a file
2. Stage: 'Adding' files to a forthcoming commit `git add <file pattern>`
3. Commit: Saving staged changes as a commit `git commit -m <message>`
4. Pushing: Pushing the commit history to a remote branch `git push origin main`

There are plenty of tools to help manage this process, as well as diverging
branches and conflicts, including the `Source Control` tab in VSCode
(`Ctrl+Shift+G`).

______________________________________________________________________

# GitHub

## Jupytext — notebooks in version control

`.ipynb` files store outputs and metadata alongside source, making `git diff`
noisy. `jupytext` converts a notebook to a plain Python script — clean diffs, no
JSON, no embedded images.

```bash
# Convert all notebooks to lightweight Python scripts
jupytext --to py:light notebooks/*.ipynb

# Move them to a dedicated folder and format
mv notebooks/*.py notebooks/py_scripts/
ruff format notebooks/py_scripts/
```

The `# %%` markers in the `.py` files are understood by VS Code and JupyterLab —
run them interactively or as a plain script.

This means your notebook source is just another file in the repo — it travels
through the fork → branch → commit → PR workflow alongside your Python modules.

______________________________________________________________________

# GitHub

Now that we've covered the basics, let's try it out!

See `/notebooks/01_tools_exercise.ipynb` **Section 1**

______________________________________________________________________

# Overview

This session will cover ...

- ✅ VS Code: editor tour and settings
- ✅ Jupyter: cells, kernel, and useful magics
- ✅ GitHub: repos, branches, forks, pull requests
- 👀 Code quality: docstrings, `ruff`, and refactoring
- ⭕ Debugging: breakpoints and `%debug` *(time permitting)*

______________________________________________________________________

# Code Quality

## Why it matters

Code is read far more often than it is written.

*"Any fool can write code that a computer can understand.* *Good programmers
write code that humans can understand."* — Martin Fowler

<!-- stop -->

- Consistent style removes cognitive load of formatting preferences
- Docstrings and type hints make intent visible without running code
- Many automatic tools catch common issues and enforce best practices

______________________________________________________________________

# Code Quality

## Type hints & docstrings

Type hints are not enforced at runtime but document intent so editors and
readers don't have to guess:

```python
def get_data_interface(
    nwbfile: pynwb.NWBFile,
    name: str,
    interface_class: type | None = None,
) -> NWBDataInterface | None:
```

<!-- stop -->

Docstrings power `help()` and auto-generated docs.

Spyglass uses **NumPy style**:

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

______________________________________________________________________

# Code Quality

## `ruff`

`ruff` is a fast Python linter and formatter — it replaces `black` `flake8`, and
more with a single tool.

```bash
ruff check my_file.py       # report issues
ruff check --fix my_file.py # auto-fix what it can
ruff format my_file.py      # format in place
```

It catches issues like:

- `F401` — imported but unused (`import json`)
- `E711` — comparison to `None` should use `is`
- `UP` — upgrades to modern Python syntax
- `I` — import ordering (replaces `isort`)

<!-- stop -->

Try writing `a='1'` and saving — `ruff` will change it to `a = '1'`
automatically.

______________________________________________________________________

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

If a hook fails, the commit is blocked and the file is fixed. Re-stage and try
again.

This means bad style never reaches the repository... unless you intentionally
bypass it with `git commit --no-verify`.

<!-- stop -->

## Exercises

Try out exercises in **Sections 2 and 3** of the notebook.

______________________________________________________________________

# Code Quality

## Atomizing

Working memory is limited — long functions force you to hold too much in mind at
once. Extract pieces into the smallest chunk that deserves a name:

| Level                   | Mechanism                    |
| :---------------------- | :--------------------------- |
| Conceptual group        | Blank line (paragraph break) |
| Conditional value       | Early assignment             |
| Reusable step           | Method on a class            |
| Shared within a module  | Helper function              |
| Shared across a project | Utility module               |

A well-named helper turns code you have to *read* into a word you already
*know*.

______________________________________________________________________

# Code Quality

## Nesting

Deep nesting is a sign of doing too much in one function.

```python
def nested(input):
    if input > 0
        do_something()
        if input < 10:
            do_something_else()
```

Refactor to use guard clauses and named helpers:

```python
def refactored(input):
    if input <= 0:
        return
    do_something()
    if input >= 10:
        return
    do_something_else()
```

<!-- stop -->

Or, even better:

```python
def new_refactored(input):
    if input <= 0 or input >= 10:
        return
    do_something(also_else=bool(input < 10))
```

______________________________________________________________________

# Code quality

Try out exercises in **Section 4** of the notebook.

______________________________________________________________________

# Overview

This session will cover ...

- ✅ VS Code: editor tour and settings
- ✅ Jupyter: cells, kernel, and useful magics
- ✅ GitHub: repos, branches, forks, pull requests
- ✅ Code quality: docstrings, `ruff`, and refactoring
- 👀 Debugging: breakpoints and `%debug` *(time permitting)*

______________________________________________________________________

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

______________________________________________________________________

# Debugging

## Manual breakpoints

Insert `breakpoint()` anywhere in your code to pause execution there.

<!-- stop -->

## Debugging in IPython

If you hit an error either in a notebook or an ipython session, you can run
`%debug` in a new cell to enter the post-mortem debugger.

```python
%debug
```

<!-- stop -->

## Debugging in VS Code

1. Either...
   - Script: **Run and Debug** sidebar (`Ctrl+Shift+D`)
   - Notebook: use the dropdown next to the ▶ button → *Debug Cell*
2. Execution pauses at errors and/or breakpoints.
3. Use the debug toolbar: Step Over, Step Into, Step Out, Continue.

The **Variables** panel shows all locals and their current values. The **Debug
Console** lets you evaluate expressions live.

<!-- stop -->

Let's try it out in **Section 5** of the notebook!

______________________________________________________________________

# Overview

This session will cover ...

- ✅ VS Code: editor tour and settings
- ✅ Jupyter: cells, kernel, and useful magics
- ✅ GitHub: repos, branches, forks, pull requests
- ✅ Code quality: docstrings, `ruff`, and refactoring
- ✅ Debugging: breakpoints and `%debug` *(time permitting)*

Key takeaways:

- VS Code settings live in `.vscode/` — they are already configured
- Fork → clone → branch → commit → push → PR
- Docstrings and type hints make intent visible without running code
- `ruff` and `pre-commit` enforce style automatically
- Guard clauses and named helpers make code easier to follow
- The debugger is faster than print statements

After the break: **Session 2 — Spyglass & DataJoint Infrastructure**
