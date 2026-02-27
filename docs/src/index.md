# Spyglass Workshop 2026

**NOTE**: This workshop is currently in development and subject to change.
Please check back for updates on March 4th, 2026.

A hands-on workshop covering practical scientific computing tools and the
[Spyglass](https://github.com/LorenFrankLab/spyglass) neuroscience data
framework.

______________________________________________________________________

## Contents

- [Pre-Workshop Requirements](#pre-workshop-requirements)
- [On the Day](#on-the-day)
- [Schedule](#schedule)
- [Resources](#resources)

______________________________________________________________________

## Pre-Workshop Requirements

Please complete **all** of the following **before arriving**.

1. **Create a [GitHub account](https://github.com/join)** if you do not already
   have one.

2. **Bring laptop.** Linux or macOS preferred. Spyglass may have issues on
   Windows; Windows users are welcome to attend and report any problems they
   encounter.

3. **Install [VS Code](https://code.visualstudio.com/)** and
   **[Miniconda](https://docs.anaconda.com/miniconda/)** (or
   [Mamba](https://mamba.readthedocs.io/), recommended).

4. **Install Spyglass** using its installer script:

   May take up to **45 minutes** on a new machine.

   ```sh
   git clone https://github.com/LorenFrankLab/spyglass
   cd spyglass
   python scripts/install.py --minimal # full install not required
   ```

   This creates a `spyglass` conda environment containing Spyglass and its core
   dependencies.

   Skip the database setup step — credentials will be provided on the day.

5. **Verify the install:**

   ```sh
   conda activate spyglass
   python -c "import spyglass; print('OK')"
   ```

   You should see `OK`. If you see an `ImportError`, re-run the installer or ask
   for help before the workshop day: `Chris.Broz[at]ucsf.edu`

6. **Brush up on Python basics:** functions, classes, `for` loops, `if`/`else`,
   `try`/`except`, and shell commands (`pip install`, `conda activate`).

______________________________________________________________________

## On the Day

### 1. Fork and clone this repository

Click **Fork** at the top-right of this page → **Create fork**, then:

```sh
git clone https://github.com/<your-username>/SpyglassWorkshop2026
cd SpyglassWorkshop2026
```

### 2. Add the workshop to your Spyglass environment

```sh
conda activate spyglass
pip install -e .
pre-commit install
```

This installs the workshop package and its tools (`ruff`, `pytest`,
`pre-commit`, `jupytext`) into the `spyglass` environment you set up before the
workshop.

### 3. Open VS Code

```sh
code .
```

When VS Code opens, accept any prompts to install the recommended extensions
listed in `.vscode/extensions.json`. Select the `spyglass` conda environment as
your Python interpreter (`Ctrl+Shift+P` → `Python: Select Interpreter`).

______________________________________________________________________

## Schedule

G6, Hugh Robson Building, University of Edinburgh

|          Time | Session                                            |
| ------------: | :------------------------------------------------- |
| 10:00 – 11:30 | **Session 1**: Tools for Scientific Computing      |
| 11:30 – 12:30 | Break                                              |
| 12:30 – 14:00 | **Session 2**: Spyglass & DataJoint Infrastructure |

### Session 1: Tools for Scientific Computing (90 min)

Practical tools and workflows for scientific Python development:

- Overview of GitHub: repositories, branches, forks, pull requests, and issues
- Setting up VS Code for Python and Jupyter development
- Working interactively with Jupyter notebooks
- Code style and quality tools: `ruff` (replaces `black` and `isort`)
- Debugging your first installable Python package

### Session 2: Spyglass & DataJoint Infrastructure (120 min)

Introduction to relational databases and the Spyglass framework:

- DataJoint infrastructure: Python–MySQL connection
- Table tiers and declaration syntax
- Spyglass design patterns: Parameter, Selection, Analysis, and Merge tables
- Ingesting data into Spyglass
- Designing a custom Spyglass pipeline

______________________________________________________________________

## Resources

- [Spyglass documentation](https://lorenfranklab.github.io/spyglass/)
- [DataJoint documentation](https://datajoint.com/docs/)
- [VS Code Python docs](https://code.visualstudio.com/docs/languages/python)
- [conda cheatsheet](https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html)
- [Jupyter shortcuts](https://jupyter-tutorial.readthedocs.io/en/24.1.0/notebook/shortcuts.html)
- [Markdown syntax](https://www.markdownguide.org/cheat-sheet/)
- [VSCode shortcuts](https://quickref.me/vscode.html)
- GitHub:
  [forking](https://docs.github.com/en/get-started/quickstart/fork-a-repo) ·
  [branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches)
  ·
  [pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
