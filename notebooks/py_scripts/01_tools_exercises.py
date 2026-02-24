# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: spyglass
#     language: python
#     name: spyglass
# ---

# # Session 1: Tools for Scientific Computing
#
# Work through this notebook alongside the slides. Each section has short
# exercises — complete them before moving on.
#
# **How to use this notebook**
#
# - Run a cell with **Shift+Enter** (runs and moves to the next cell).
# - Re-run any cell at any time — the kernel holds all state.
# - If the kernel gets into a bad state: **Kernel → Restart & Run All**.
# - Cells marked `# YOUR CODE HERE` are for you to complete.
#
# **Note on section order**
#
# The slides cover topics in this sequence:
# GitHub → VS Code → Jupyter → Code Quality → Debugging
#
# This notebook is not a strict follow-along. VS Code and Jupyter are
# demonstrated live, so this notebook skips them and focuses on the
# hands-on practice for GitHub, refactoring, debugging, and code quality.
# The sections are ordered to build on each other, not to mirror the slides
# exactly.

# ---
# ## GitHub
#
# The cells below use the `!` prefix to run shell commands from inside the
# notebook. This is equivalent to typing them in a terminal.

# View recent commit history
# !git log --oneline -8

# See all local branches (* marks the current one)
# !git branch

# Check for any uncommitted changes
# !git status --short

# ### Exercise 1.1 — Create a personal branch
#
# Create a branch named `your-name/session1` (replace `your-name` with your
# actual name or GitHub username). This is where you will save your work
# during the workshop.
#
# ```bash
# git checkout -b your-name/session1
# ```
#
# Fill in the cell below, then run it.

# +
# YOUR CODE HERE
# # !git checkout -b your-name/session1

# Verify you are on the new branch:
# !git branch
# -

# ### Exercise 1.2 — Inspect the repo structure
#
# Use the cells below to explore the repository layout.

# +
# Show the top-level directory tree
import os

repo_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
for entry in sorted(os.listdir(repo_root)):
    if not entry.startswith("."):
        print(entry)

# +
# Where does the installed package live?
import spyglass_workshop

print(spyglass_workshop.__file__)


# -

# ---
# ## Code Quality
#
# Good code is easy to re-read six months later. The following exercises are
# adapted from a talk on code reuse. Each exercise shows a working but
# hard-to-read function — your task is to identify the issues and improve it.
#
# Work through each example:
# 1. Read the code carefully.
# 2. Write down the questions that come to mind (what does this do? can it fail?).
# 3. Rewrite it in the solution cell.

# ### Exercise 2.1 — Formatting and readability
#
# The function below is syntactically correct but hard to read. What issues
# can you spot before running any tool?


# Read this function carefully before doing anything else.
def get_data_interface(
    nwbfile, data_interface_name, data_interface_class=None, unused_other_arg=None
):
    ret = []
    for module in nwbfile.processing.values():
        match = module.data_interfaces.get(data_interface_name, None)
        if match is not None:
            if data_interface_class is not None and not isinstance(
                match, data_interface_class
            ):
                continue
            ret.append(match)
    if len(ret) > 1:
        print(
            f"Multiple data interfaces with name '{data_interface_name}' found with identifier {nwbfile.identifier}."
        )
    if len(ret) >= 1:
        return ret[0]
    return None


# +
# Write the function above to a temporary file and run ruff on it.
# Read the output — how many of the issues did you already spot?

import tempfile, textwrap, subprocess

code = textwrap.dedent(
    """
    def get_data_interface(nwbfile, data_interface_name, data_interface_class=None, unused_other_arg=None):
        ret = []
        for module in nwbfile.processing.values():
            match = module.data_interfaces.get(data_interface_name, None)
            if match is not None:
                if data_interface_class is not None and not isinstance(match, data_interface_class):
                    continue
                ret.append(match)
        if len(ret) > 1:
            print(f"Multiple data interfaces with name '{data_interface_name}' found.")
        if len(ret) >= 1:
            return ret[0]
        return None
"""
)

with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
    f.write(code)
    tmp_path = f.name

result = subprocess.run(["ruff", "check", tmp_path], capture_output=True, text=True)
print(result.stdout or "No issues found.")
# -

# **Your turn:** Rewrite the function to address the issues. Some hints:
#
# - What is `unused_other_arg` for? Remove it.
# - The double `if len(ret) ...` pattern can be simplified.
# - The long `print` string can be split across lines.

# +
# YOUR CODE HERE — rewrite get_data_interface

# def get_data_interface(nwbfile, data_interface_name, data_interface_class=None):
#     ...
# -

# ### Model approach — control flow adjustments
#
# After formatting, we can do better by restructuring the logic to follow
# how we read:
#
# - **Decide once**: set a default filter class early so the loop body has
#   no branches.
# - **Generate with a comprehension**: the intent of the loop is clear at a
#   glance.
# - **Return with a ternary**: the "found or not" decision fits on one line.
#
# ```python
# from typing import Optional
#
# def get_data_interface(
#     nwbfile,
#     data_interface_name: str,
#     data_interface_class: Optional[type] = None,
# ) -> object:
#     """Return the first matching data interface, or None."""
#     filter_cls = data_interface_class or object  # decide the filter once
#
#     matches = [
#         module.data_interfaces[data_interface_name]
#         for module in nwbfile.processing.values()
#         if data_interface_name in module.data_interfaces
#         and isinstance(module.data_interfaces[data_interface_name], filter_cls)
#     ]
#
#     if len(matches) > 1:
#         print(
#             f"Multiple interfaces named '{data_interface_name}' "
#             f"in NWBFile '{nwbfile.identifier}'."
#         )
#     return matches[0] if matches else None
# ```

# ### Exercise 2.2 — Reducing nesting
#
# Deep nesting makes code hard to follow. Read through the function below
# and answer these questions before trying to refactor it:
#
# 1. Can `process` handle subjects other than `"alice"` and `"bob"`? What happens if you pass a new name?
# 2. Should `alice_settings` and `bob_settings` be defined inside the function, or passed in as a parameter?
# 3. What exception is the outer `try` catching, and what line actually raises it?
# 4. What errors does the inner `try` silently swallow — and is that safe?
# 5. What does `for ... else` do here? Is it triggered in the way the author intended?

# +
# Read carefully, then answer the questions above before refactoring below.
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes experiment files for a given subject."""

    def process(self, config):
        subject = config["subject"]
        alice_settings = {"gain": 1, "offset": 0}
        bob_settings = {"gain": 2, "offset": 5}
        try:
            if len(config["files"]) > 0:
                if subject == "alice":
                    settings = alice_settings
                elif subject == "bob":
                    settings = bob_settings
                else:
                    raise ValueError(f"Unknown subject: {subject}")
                for param, value in settings.items():
                    try:
                        if value == 1:
                            result = param
                        else:
                            result = value
                        print(f"processing {result}")
                    except KeyError:
                        print("file missing", config.get("session_id"))
                else:
                    print("no files processed")
        except IndexError:
            print("no data")


# -

# ### Reading with questions
#
# Before refactoring, *read* the code and number every question that arises.
# Then read again and pair each answer to its question (1Q → 1A, 2Q → 2A ...).
#
# ```python
# def process(self, config):
#     subject = config["subject"]               # 1Q. What subjects are supported?
#     alice_settings = {"gain": 1, "offset": 0} # 2Q. Should these be parameters?
#     bob_settings   = {"gain": 2, "offset": 5}
#     try:                                       # 3Q. What could raise here? Which line?
#         if len(config["files"]) > 0:          # 4Q. What happens when files is empty?
#             if subject == "alice":
#                 settings = alice_settings     # 2A. Decided here — conditional assign
#             elif subject == "bob":
#                 settings = bob_settings
#             else:                             # 1A. Only two — anything else raises
#                 raise ValueError(...)
#             for param, value in settings.items():
#                 try:                          # 5Q. What KeyError could occur here?
#                     ...
#                     print(f"processing {result}")
#                 except KeyError:             # 5A. The param lookup may be unreliable
#                     print("file missing", ...)
#             else:                            # 4A. for/else fires on normal completion,
#                 print("no files processed") #     NOT on empty list — bug!
#     except IndexError:                       # 3A. len() can't raise IndexError —
#         print("no data")                     #     this except is unreachable!
# ```
#
# Two real bugs revealed by reading carefully:
# - `for/else` fires after a *completed* loop, not a skipped one — it never
#   detects an empty list.
# - `len(config["files"])` cannot raise `IndexError`, so that `except` is
#   dead code.

# +
# YOUR CODE HERE — reduce nesting and clarify logic

# Hints:
#   - Use a single dict for subject settings instead of two separate variables.
#   - Use a guard clause (early return / raise) to handle unknown subjects
#     before entering the main logic — this flattens one level of nesting.
#   - Extract the inner per-file logic into a helper method so `process`
#     reads as a high-level sequence of steps.
#   - Replace print() with logger.error() / logger.info().
#   - Ask yourself: what should happen if config["files"] is empty?
#     Should that be an error, a warning, or silently ignored?

# class DataProcessorRefactored:
#     ...
# -

# ### Model approach — reduce nesting
#
# Key changes from the original:
#
# - **Guard clause**: `if subject not in SUBJECT_SETTINGS: raise` eliminates
#   one level of nesting and surfaces the error immediately.
# - **Class-level dict** `SUBJECT_SETTINGS`: adding a new subject requires
#   no changes to the method logic.
# - **`:=` walrus operator**: assigns and tests `subject` in one expression.
# - **Helper method** `_process_file`: gives the inner loop body a name,
#   so `process` reads as a high-level sequence of steps.
# - **`logger`** vs `print`: log level (`INFO`, `WARNING`) can be adjusted
#   at runtime without editing the code.

# +
import logging

logger = logging.getLogger(__name__)


class DataProcessorRefactored:
    """Processes experiment files for a given subject."""

    SUBJECT_SETTINGS = {
        "alice": {"gain": 1, "offset": 0},
        "bob": {"gain": 2, "offset": 5},
    }

    def _process_file(self, param: str, value: int, session_id: str) -> None:
        """Process one parameter entry, logging rather than printing."""
        result = param if value == 1 else value
        logger.info("processing %s", result)  # verbosity controlled at runtime

    def process(self, config: dict) -> None:
        """Process all files for the subject named in config."""
        # Guard clause: fail loudly and early for unknown subjects.
        if (subject := config["subject"]) not in self.SUBJECT_SETTINGS:
            raise ValueError(f"Unknown subject: {subject!r}")

        if not config["files"]:
            logger.warning("No files for %s — skipping", subject)
            return

        settings = self.SUBJECT_SETTINGS[subject]
        for param, value in settings.items():
            self._process_file(param, value, config.get("session_id", "unknown"))


# -

# ---
# ## Type hints & docstrings
#
# Type hints are not enforced at runtime but make function signatures
# self-documenting, and editors use them for autocomplete and error
# highlighting.
#
# ```python
# # Before
# def compute_stats(values, threshold=None, label="result"):
#
# # After
# def compute_stats(
#     values: list[float],
#     threshold: float | None = None,
#     label: str = "result",
# ) -> dict | None:
# ```
#
# Docstrings (NumPy style, used by Spyglass) power `help()` and API docs.
# The pattern: one-line summary → blank line → Parameters → Returns →
# Raises → Examples.
#
# ```python
# def compute_stats(
#     values: list[float],
#     threshold: float | None = None,
#     label: str = "result",
# ) -> dict | None:
#     """Return the mean of values above a threshold.
#
#     Parameters
#     ----------
#     values : list[float]
#         The raw measurements.
#     threshold : float, optional
#         If given, exclude values below this level before computing.
#     label : str
#         Key name for the mean in the returned dict.
#
#     Returns
#     -------
#     dict or None
#         ``{label: mean, "n": count}`` or ``None`` if no values pass
#         the threshold.
#     """
# ```
#
# **Exercise 2.3** — apply both to the function in the cell below.

# +
# YOUR CODE HERE — add type hints and a NumPy docstring to this function.


def compute_stats(values, threshold=None, label="result"):
    """YOUR DOCSTRING HERE"""
    if threshold is not None:
        values = [v for v in values if v >= threshold]
    if not values:
        return None
    mean = sum(values) / len(values)
    return {label: mean, "n": len(values)}


# Example call — run this to check your signature makes sense:
# compute_stats([1.0, 5.0, 3.0, 8.0, 2.0], threshold=3.0, label="filtered_mean")
# -

# ---
# ## Debugging
#
# `fibonacci_buggy.py` contains two bugs that produce wrong numerical
# outputs without raising exceptions. Your task is to find and fix them.
#
# **Strategy:**
# 1. Run the cells below to see the wrong outputs.
# 2. Use `%debug` (after a cell that produces wrong output) or set VS Code
#    breakpoints to step through execution.
# 3. Identify the lines with the bugs.
# 4. Fix them in `src/spyglass_workshop/examples/fibonacci_buggy.py`.
# 5. Restart the kernel (`Kernel → Restart`) and re-run from Section 3
#    to confirm the fix.

# +
from spyglass_workshop.examples.fibonacci_buggy import f, f_list
from spyglass_workshop.examples.fibonacci import f as f_correct

print("fibonacci_buggy.f(1) =", f(1), "  (expected 1)")
print("fibonacci_buggy.f(5) =", f(5), "  (expected 5)")
print()
print("fibonacci_buggy.f_list(5) =", f_list(5))
print("expected                  = [1, 1, 2, 3, 5]")
# -

# Side-by-side comparison for the first 10 values
print(f"{'n':>4}  {'buggy f(n)':>12}  {'correct f(n)':>12}  {'match':>6}")
print("-" * 42)
for n in range(1, 11):
    buggy = f(n)
    correct = f_correct(n)
    match = "✓" if buggy == correct else "✗"
    print(f"{n:>4}  {buggy:>12}  {correct:>12}  {match:>6}")

# ### Debugging `f(n)` with `%debug`
#
# Run the cell below to force an `AssertionError` when `f(1)` returns the
# wrong value, then run `%debug` in the next cell to enter the debugger.

result = f(1)
print(f"f(1) returned: {result}  (expected: 1)")
assert result == 1, f"f(1) should be 1, got {result}"

# Run this cell after the AssertionError above to enter the debugger.
# Inside pdb, try:
#   l         — list code around current frame
#   u         — go up one frame (into f())
#   l         — list the code in f()
#   p a, p b  — print variable values
#   q         — quit
# %debug

# ### Fix and verify
#
# Once you have identified both bugs:
#
# 1. Edit `src/spyglass_workshop/examples/fibonacci_buggy.py` in VS Code.
# 2. Restart this kernel (`Kernel → Restart`).
# 3. Re-run the cells in this section — all comparisons should show `✓`.
# 4. Run the test suite from the terminal:
#
# ```bash
# pytest tests/examples/test_fibonacci_buggy.py -v
# ```

# ---
# ## ruff
#
# In this section you will run `ruff` on a script with many linting issues
# and see how many problems it catches automatically.

# +
# %%writefile /tmp/bad_example.py
# # %%writefile is a Jupyter magic that writes the entire cell contents
# to a file on disk — handy for creating test scripts without leaving
# the notebook.
"""Syntactically valid Python script with many linting issues"""
# Incorrect import order
import os, sys
from math import *

# Unused import
import json


def MyFunction():
    print("Hello World")
    x = 10
    y = 20
    unused_variable = 0

    if x == 10:
        print("x is ten")
        y += 1

    print(z)


# Long line
a = "This is a very long string that should probably be split into multiple lines to adhere to best practices but isn't"

import os  # reimported


def too_many_arguments(arg1, arg2, arg3, arg4, arg5, arg6, arg7):
    return arg1 + arg2 + arg3 + arg4 + arg5 + arg6 + arg7


a = 1
b = 2
c = a + b

# +
import subprocess

result = subprocess.run(
    ["ruff", "check", "/tmp/bad_example.py"],
    capture_output=True,
    text=True,
)
print(result.stdout)

# +
# Apply automatic fixes and recheck
subprocess.run(["ruff", "check", "--fix", "/tmp/bad_example.py"])
subprocess.run(["ruff", "format", "/tmp/bad_example.py"])

# Show what remains (some issues require human judgement)
result = subprocess.run(
    ["ruff", "check", "/tmp/bad_example.py"],
    capture_output=True,
    text=True,
)
print(result.stdout or "No remaining issues.")

# Show the formatted file
print("\n--- formatted file ---")
with open("/tmp/bad_example.py") as fh:
    print(fh.read())
# -

# ### Exercise 4.1 — Fix the remaining issues
#
# After `ruff --fix` and `ruff format`, some issues require manual
# intervention because they involve judgement calls that a tool cannot
# make automatically (e.g., which variable name to use, whether an
# `import` is actually needed).
#
# The cell below prints the remaining warnings and the current file
# contents. Read them, then:
#
# 1. Edit `/tmp/bad_example.py` directly in VS Code (or with the cell
#    below) to address the remaining issues.
# 2. Re-run `ruff check` to confirm zero issues remain.

# +
from pathlib import Path

target = Path("/tmp/bad_example.py")

# Show remaining issues
remaining = subprocess.run(
    ["ruff", "check", str(target)], capture_output=True, text=True
)
print("Remaining issues:")
print(remaining.stdout or "  None — all fixed!")

# Show the file so you know what to edit
print("\n--- current file contents ---")
print(target.read_text())

# YOUR CODE HERE
# Edit the file contents below, then re-run ruff check to verify.
# Example:
#   fixed = target.read_text().replace("old_code", "new_code")
#   target.write_text(fixed)
#
# Re-check after your edit:
#   result = subprocess.run(["ruff", "check", str(target)], capture_output=True, text=True)
#   print(result.stdout or "✓ No issues found.")
# -

# ---
# ## Summary
#
# You have worked through:
#
# | Topic | Key takeaway |
# | :---- | :----------- |
# | GitHub | fork → clone → branch → commit → push → PR |
# | Refactoring | Remove nesting, extract helpers, use guard clauses |
# | Debugging | `%debug` and VS Code breakpoints give you a live inspector |
# | Code quality | `ruff` catches dozens of issues automatically |
#
# **Next:** after the break, open `notebooks/02_datajoint_spyglass.ipynb`.
