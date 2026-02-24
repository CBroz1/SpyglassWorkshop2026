# Spyglass Workshop 2026

A hands-on workshop covering practical scientific computing tools and the
[Spyglass](https://github.com/LorenFrankLab/spyglass) neuroscience data
framework.

---

## Schedule

G6, Hugh Robson Building, University of Edinburgh

| Time | Session |
| ---: | :------ |
| 10:00 – 11:30 | **Session 1**: Tools for Scientific Computing |
| 11:30 – 12:30 | Break |
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

---

## Pre-Workshop Requirements

Please complete the following **before** the workshop:

1. **Create a [GitHub account](https://github.com/join)** if you do not already
   have one.
2. **Bring a Linux or macOS laptop.** Spyglass may have issues on Windows;
   Windows users are welcome to attend and report any problems they encounter.
3. **Install [VS Code](https://code.visualstudio.com/)** and
   **[Miniconda](https://docs.anaconda.com/miniconda/)** (or
   [Mamba](https://mamba.readthedocs.io/), recommended).
4. **Brush up on Python basics:** functions, classes, `for` loops, `if`/`else`,
   `try`/`except`, and shell commands (`pip install`, `conda activate`).
5. **Database credentials** will be distributed on the day. You do not need to
   configure anything in advance — Session 2 will walk through the setup.

---

## Setup

### 1. Fork and clone this repository

1. Click **Fork** at the top-right of this page, then **Create fork**.
2. Copy your fork URL: `https://github.com/<your-username>/SpyglassWorkshop2026`
3. Clone it locally:

```sh
git clone https://github.com/<your-username>/SpyglassWorkshop2026
cd SpyglassWorkshop2026
```

### 2. Create the conda environment

```sh
conda env create -f environment.yml
conda activate spyglass-workshop
```

### 3. Install the workshop package

```sh
pip install -e .
```

This makes `spyglass_workshop` importable from any notebook or script
in the repository. The `-e` flag means changes you make to the source
are reflected immediately without reinstalling.

### 4. Install pre-commit hooks

Pre-commit runs automatic code quality checks before each `git commit`.

```sh
pre-commit install
```

To run the checks manually at any time:

```sh
pre-commit run --all-files
```

### 5. Open VS Code

```sh
code .
```

When VS Code opens, accept any prompts to install the recommended extensions
listed in `.vscode/extensions.json`. Select the `spyglass-workshop` conda
environment as your Python interpreter (`Ctrl+Shift+P` →
`Python: Select Interpreter`).

### 6. Launch Jupyter

Notebooks are in the `notebooks/` directory. Open them in VS Code directly,
or start Jupyter Lab from the terminal:

```sh
jupyter lab
```

---

## Repository Structure

```
SpyglassWorkshop2026/
├── .vscode/                 # Recommended VS Code settings and extensions
├── docs/src/                # Workshop slides and documentation (mkdocs)
├── notebooks/               # Interactive Jupyter notebooks
├── src/spyglass_workshop/   # Python package (attendees will add code here)
└── tests/                   # Pytest test suite
```

---

## Resources

- [Spyglass documentation](https://lorenfranklab.github.io/spyglass/)
- [DataJoint documentation](https://datajoint.com/docs/)
- [VS Code Python docs](https://code.visualstudio.com/docs/languages/python)
- [conda cheatsheet](https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html)
- GitHub: [forking](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
  · [branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches)
  · [pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
