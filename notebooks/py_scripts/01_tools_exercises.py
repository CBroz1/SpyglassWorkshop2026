# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: spyglass
#     language: python
#     name: python3
# ---

# # Session 1: Tools for Scientific Computing
#
# Work through this notebook alongside the slides. Each section has short
# exercises — complete at your own pace.
#
# > **Kernel setup (one-time):** this notebook must run inside the `spyglass`
# > conda environment.
# >
# > If you have not already registered it as a Jupyter kernel,
# > open a terminal and run:
# > ```bash
# > conda activate spyglass
# > python -m ipykernel install --user --name spyglass
# > ```
# > Then select **spyglass** from the kernel picker (top-right in VS Code).
#
# **How to use this notebook**
#
# - Run a cell with **Shift+Enter** (runs and moves to the next cell).
# - Re-run any cell at any time — the kernel holds all state.
# - If the kernel gets into a bad state: **Kernel → Restart**.
# - Cells marked `# YOUR CODE HERE` are for you to complete.
#
# **Note on section order**
#
# The slides cover topics in this sequence:
# VS Code → Jupyter → GitHub → Code Quality → Debugging
#
# VS Code and Jupyter are demonstrated live. This notebook focuses on the
# hands-on practice: GitHub commands, type hints & docstrings, ruff,
# refactoring, and debugging — in the same order as the slides.
#

print("Hello world!")

a = 1 + 2
print(a)


# Use `Ctrl+Shift+P` -> `Focus on Jupyter Variables View` and then assign a new
# variable (e.g., `b=4`)

# +
# YOUR CODE HERE
# -

# Shortcuts:
#
# | Key | Action |
# | :-- | :----- |
# | `Enter` | Edit cell |
# | `Esc` | Exit cell |
# | `A` / `B` | Insert cell above / below |
# | `M` / `Y` | Change cell to Markdown / Code |
# | `Shift+Enter` | Run cell and move to next |
# | `Ctrl+Enter` | Run cell in place |
#
# [Shortcut Cheatsheet](https://jupyter-tutorial.readthedocs.io/en/24.1.0/notebook/shortcuts.html)

# ---
# ## Section 1: GitHub
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
# Let's create a branch. This is where you will save your work
# during the workshop.

# +
# YOUR CODE HERE: decide the branch name.
# # !git checkout -b <new-branch-name>
# -

# Verify you are on the new branch:
# !git branch

# ### Exercise 1.2 - Create a commit

# Next, we'll make a commit with the outstanding edits to this notebook.
#
# > **Prerequisite:** This commit will only have content if you save
# > edits to this file, like cell outputs.

# !git add 01_tools_exercises.ipynb
# !git commit -m "Example commit"

# We can see it reflected in the log

# !git log --oneline -3

# ## Section 2: Type hints & docstrings
#
# Type hints are not enforced at runtime but make function signatures
# self-documenting, and editors use them for autocomplete and error
# highlighting.
#
# <details><summary>Before</summary>
#
# ```python
# def compute_stats(values, threshold=None, label="result"):
# ```
#
# </details>
#
# <details><summary>After</summary>
#
# ```python
# def compute_stats(
#     values: list[float],
#     threshold: float | None = None,
#     label: str = "result",
# ) -> dict | None:
# ```
#
# </details>
#
# Docstrings (NumPy style, used by Spyglass) power `help()` and API docs.
# The pattern: one-line summary → blank line → Parameters → Returns →
# Raises → Examples.
#
# <details><summary>Example</summary>
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
# </details>
#
# ### Exercise 2.1: add type hints & docstring


# +
# YOUR CODE HERE
def bytes_to_human_readable(size, sum_inputs=False):
    if sum_inputs:
        size = sum(size)

    msg_template = "{size:.2f} {unit}"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return msg_template.format(size=size, unit=unit)
        size /= 1024

    return msg_template.format(size=size, unit="PB")


# Example call — run this to check your signature makes sense:
print(bytes_to_human_readable([1024, 2048], sum_inputs=True))
print(bytes_to_human_readable(123456789, sum_inputs=False))
# -

# ---
# ## Section 3: `ruff`
#
# In this section you will run `ruff` on a script with many linting issues
# and see how many problems it catches automatically.

# The cell below writes this intentionally broken script to `temp_bad_example.py`:
#
# <details><summary><code>temp_bad_example.py</code></summary>
#
# ```python
# """Syntactically valid Python script with many linting issues"""
# # Incorrect import order
# import os, sys
# from math import *
#
# # Unused import
# import json
#
#
# def MyFunction():
#     print('Hello World')
#     x = 10
#     y = 20
#     unused_variable = 0
#
#     if x == 10:
#         print('x is ten')
#         y += 1
#
#     print(z)
#
#
# # Long line
# a = "This is a very long string that should probably be split into multiple lines to adhere to best practices but isn't"
#
# import os  # reimported
#
#
# def too_many_arguments(arg1, arg2, arg3, arg4, arg5, arg6, arg7):
#     return arg1 + arg2 + arg3 + arg4 + arg5 + arg6
#
#
# a = 1
# b = 2
# c = a + b
# ```
#
# </details>

# +
from pathlib import Path

BAD_CODE = '''
"""Syntactically valid Python script with many linting issues"""
# Incorrect import order
import os, sys
from math import *

# Unused import
import json


def MyFunction():
    print('Hello World')
    x = 10
    y = 20
    unused_variable = 0

    if x == 10:
        print('x is ten')
        y += 1

    print(z)


# Long line
a = "This is a very long string that should probably be split into multiple lines to adhere to best practices but isn't"

import os  # reimported


def too_many_arguments(arg1, arg2, arg3, arg4, arg5, arg6, arg7):
    return arg1 + arg2 + arg3 + arg4 + arg5 + arg6


a = 1
b = 2
c = a + b
'''

Path("temp_bad_example.py").write_text(BAD_CODE.lstrip("\n"))
print("Written to temp_bad_example.py")
# -

# Try opening that file directly, and then look at the 'Problems' window.
#
# `Ctrl+Alt+P` -> `View: Focus Problems`

# +
import subprocess

# Click 'scrollable element' to view full output in Jupyter,
# or run this in your terminal: ruff check /tmp/bad_example.py
result = subprocess.run(
    ["ruff", "check", "temp_bad_example.py"],
    capture_output=True,
    text=True,
)
print(result.stdout)

# +
# Apply automatic fixes and recheck
subprocess.run(["ruff", "check", "--fix", "temp_bad_example.py"])
subprocess.run(["ruff", "format", "temp_bad_example.py"])

# Show what remains (some issues require human judgement)
result = subprocess.run(
    ["ruff", "check", "temp_bad_example.py"],
    capture_output=True,
    text=True,
)
print(result.stdout or "No remaining issues.")
# -

# ### Exercise 3.1: Fix the remaining issues
#
# After `ruff --fix` and `ruff format`, some issues require manual
# edits because they involve judgement calls that a tool cannot
# make automatically (e.g., which variable name to use, whether an
# `import` is actually needed).
#
# 1. Edit `temp_bad_example.py` directly in VS Code to address the remaining issues.
# 2. Re-run `ruff check` to confirm zero issues remain.
#
# Use `Ctrl+Shift+P` -> `Focus Problems` to see issues as you edit.

# +
from pathlib import Path

target = Path("temp_bad_example.py")

# Show remaining issues
remaining = subprocess.run(
    ["ruff", "check", str(target)], capture_output=True, text=True
)
print("Remaining issues:")
print(remaining.stdout)


# -

# ---
# ## Section 4: Readable Code
#
# Good code is easy to re-read six months later. The exercises below prompt you
# to revise existing code for readability
#
#
#

# ### Exercise 4.1 — Reducing nesting
#
# Deep nesting makes code hard to follow and raised more questions than it answers.
#
# **Q/A annotation method:**
#
# 1. Number every question that arises as you read (`1Q`, `2Q`, …) as comments.
# 2. Read again and pair each answer to its question (`1A`, `2A`, …).
# 3. Refactor so to reduce the distance between question and answers.
#
# These questions might be something like...
#
# 1. Which subjects can this handle?
# 2. What does this `try` do?
#


class DataProcessor:
    """Processes experiment files for a given subject."""

    def process(self, config):
        subject = config["subject"]  # Q1: < Fill in the blank >
        alice_settings = {"gain": 1, "offset": 0}  # Q2: < etc. >
        bob_settings = {"gain": 2, "offset": 5}
        try:
            if len(config["files"]) > 0:
                if subject == "alice":
                    settings = alice_settings
                elif subject == "bob":
                    settings = bob_settings
                else:  # A1: < Fill in the blank >
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


# What other questions come up as you read line-by-line?
#
# <details><summary>Completed Q/A set</summary>
#
# ```python
# def process(self, config):
#     subject = config["subject"]               # 1Q. What subjects are supported?
#     alice_settings = {"gain": 1, "offset": 0} # 2Q. How do we handle this dict?
#     bob_settings   = {"gain": 2, "offset": 5}
#     try:                                      # 3Q. What could raise here? Which line?
#         if len(config["files"]) > 0:          # 4Q. What happens when files is empty?
#             if subject == "alice":
#                 settings = alice_settings     # 2A. Conditional assignment
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
#                 print("no files processed")  #     Oh, this is an indentation bug.
#     except IndexError:                       # 3A. len() can't raise IndexError —
#         print("no data")                     #     this except is unreachable!
# ```
#
# Two real bugs revealed by reading carefully:
# - `for/else` fires after a *completed* loop, not a skipped one — it never
#   detects an empty list.
# - `len(config["files"])` cannot raise `IndexError`, so that `except` is
#   dead code.
#
# </details>
#
# We tend to think `A -> B -> C -> D -> E`
#
# But code like the above turns that into `if D -> (C -> (A or B)) -> E`
#
# Now, let's try to refactor to make all Q's right next to their answer.

# +
# YOUR CODE HERE — reduce nesting and clarify logic

# class DataProcessorRefactored:
#     ...
# -

# <details><summary>Hint one</summary>
#
# - Ask yourself: what should happen if <code>config["files"]</code> is empty?
#   Should that be an error, a warning, or silently ignored?
# - Use a single dict for subject settings instead of two separate variables.
#
# </details>
#
# <details><summary>Hint two</summary>
#
# - Extract the inner per-file logic into a helper method so `process`
#   reads as a high-level sequence of steps.
#
# </details>
#
# <details><summary>Hint three</summary>
#
# - Use a guard clause (early return / raise) to handle unknown subjects
#   before entering the main logic
# - Replace print() with logger.error() / logger.info().
#
# </details >
#
# <details><summary>One solution</summary>
#
# ```python
# import logging
#
# logger = logging.getLogger(__name__)
#
#
# class DataProcessorRefactored:
#     """Processes experiment files for a given subject."""
#
#     SUBJECT_SETTINGS = {  # Q1: Which subjects can this handle?
#         "alice": {"gain": 1, "offset": 0},  # Q2: How do we use these settings?
#         "bob": {"gain": 2, "offset": 5},  # A1: Two subjects: Alice and Bob
#     }
#
#     # Q3: How do we process file?
#     def _process_file(self, param: str, value: int, session_id: str) -> None:
#         """Process one parameter entry, logging process."""
#         # A3: If value is 1, log the param name; otherwise log the value.
#         result = param if value == 1 else value
#
#         logger.info("%s: processing %s", (session_id, result))
#
#     def process(self, config: dict) -> bool:
#         """Process all files for the subject named in config."""
#         # Q4: What do we expect in a config?
#
#         # Guard clause: fail loudly and early for unknown subjects.
#         if (subject := config.get("subject")) not in self.SUBJECT_SETTINGS:
#             # A4: We expect a subject key
#             raise ValueError(f"Unknown subject: {subject!r}")
#
#         if not config.get("files"):  # A4: We expect a files key
#             logger.warning("No files for %s — skipping", subject)
#             return False # Q5: What are we returning?
#
#         settings = self.SUBJECT_SETTINGS[subject]
#         for param, value in settings.items():  # A2: Loop over settings
#             self._process_file(param, value, config.get("session_id", "unknown"))
#
#         return True # A5: Success state - could be answered by docstrings
# ```
#
# Key changes from the original:
#
# - **Guard clause**: `if subject not in SUBJECT_SETTINGS: raise` eliminates
#   one level of nesting and surfaces the error immediately.
# - **Class-level dict** `SUBJECT_SETTINGS`: adding a new subject requires
#   no changes to the method logic.
# - **`:=` walrus operator**: `(subject := config.get("subject"))` assigns the
#   result of `config.get("subject")` to `subject` *and* evaluates it as part
#   of the `if` condition in a single expression — a Python 3.8+ feature.
# - **Helper method** `_process_file`: gives the inner loop body a name,
#   so `process` reads as a high-level sequence of steps.
# - **`logger`** vs `print`: log level (`INFO`, `WARNING`) can be adjusted
#   at runtime without editing the code.
#
# Not all questions have immediate answers, but this structure isolates
# functionality.
#
# </details>

# ### Exercise 4.2: Formatting and readability
#
# The function below is syntactically correct but hard to read and has some bugs.
#
# What issues can you spot?


# Read this function carefully before doing anything else.
def get_data_interface(
    nwbfile,
    data_interface_name,
    data_interface_class=None,
    other_arg=None,
):
    din, dic = data_interface_name, data_interface_class
    ret = []
    for module in nwbfile.processing.values():
        match = module.data_interfaces[din]
        if match is not None:
            if not isinstance(match, dic):
                continue
            ret.append(match)
    if len(ret) > 1:
        print(
            f"Multiple data interfaces with name '{data_interface_name}' found with identifier {nwbfile.identifier}."
        )
    if len(ret) == 1:
        return ret[0]
    return None


# **Your turn:** Rewrite the function to address the issues. Some hints:
#

# +
# YOUR CODE HERE — rewrite get_data_interface

# def get_data_interface(...):
#     ...
# -

# <details><summary>Hint 1</summary>
#
# - What is `other_arg` for? Remove it.
# - Add docstrings and type hints
#
# </details>
#
# <details><summary>Hint 2</summary>
#
# - The long `print` string can be split across lines.
# - Check if keys exist in dicts with `get`
# - Avoid aliasing variables within a function
#
# </details>
# <details><summary>Hint 3</summary>
#
# - The double `if len(ret) ...` pattern can be simplified.
# - Use a one-line conditional return
#
# </details>
#
# <details><summary>One solution</summary>
#
# ```python
# import pynwb
#
#
# def get_data_interface(
#     nwbfile: pynwb.NWBFile,
#     data_interface_name: str,
#     data_interface_class: type | None = None,
# ) -> object:  # Add type hints for clarity
#     """Return the first matching data interface, or None.
#
#     Parameters
#     ----------
#     nwbfile : NWBFile
#         The NWBFile to search for the data interface.
#     data_interface_name : str
#         The name of the data interface to find.
#     data_interface_class : type, optional
#         If provided, only return the data interface if it is an instance of
#         this class.
#
#     Returns
#     -------
#     object or None
#         The first matching data interface, or None if no matches are found.
#
#     Raises
#     ------
#     ValueError
#         If multiple matching data interfaces are found.
#     """
#     filter_cls = data_interface_class or object  # decide the filter once
#
#     matches = []  # Clear variable name for clarity
#     for module in nwbfile.processing.values():
#         interface = module.data_interfaces.get(data_interface_name)
#         if interface is not None and isinstance(interface, filter_cls):
#             matches.append(interface)  # Check for 'good' case and append
#
#     if len(matches) > 1:
#         raise ValueError(  # Raise an error for more transparent handling
#             f"Multiple interfaces named '{data_interface_name}' "
#             f"in NWBFile '{nwbfile.identifier}'."
#         )
#
#     return matches[0] if matches else None  # One-liner return for clarity
# ```
#
# </details>
#

# ## Section 5: Debugging (time permitting)
#
# > **Guided walkthrough:** This section is run as a class demo with the
# > instructor.
#

# ### Debugging with `%debug`
#
# `channel_stats_buggy.py` contains three bugs that raises an exception
# deep in a 4-level call stack — the kind of crash where the error message
# alone doesn't tell you what went wrong.
#
# ```
# summarize(channels)
#   └─ _channel_stats(signal)               ← which channel failed?
#        ├─ _mean(values)                   ← Bug 1 crashes here
#        ├─ _z_scores(signal, mu, sigma)    ← Bug 2 crashes here
#        └─ _std(values, mu)
#             └─ _variance(values, mu)      ← Bug 3 buried here
# ```
#
# The cell below shows the traceback. First, we'll explore this traceback with
# `%debug` using the following shortcuts:
#
# Inside pdb, try:
# -  `l`, `ll` - list code around current frame, `ll` for larger context
# -  `u`,`d`   - go up/down one frame
# -  `p a`, `p b`  - print variable values
# -  `q`       - quit
#
# Note that list comprehensions don't receive their own frames.

# +
from spyglass_workshop.channel_stats_buggy import summarize

recording = [
    [1.0, 2.0, 3.0, 4.0, 5.0],  # normal channel
    [7.0],  # single-sample burst  ← hits Bug 1
    [3.0, 3.0, 3.0, 3.0],  # dead/flat electrode  ← hits Bug 2
]

result = summarize(recording)
# -

# %debug

# `%debug` can be helpful, but this UI is clunky.
#
# **Alternative 1: IPython terminal with `%debug`**
#
# 1. Launch `ipython -i src/spyglass_workshop/channel_stats_buggy.py`, executing `__main__` clause.
# 2. Inspect the error stack.
# 3. Run `%debug`
# 4. Navigate stack (`u`, `d`, `l`, etc.)
# 5. Fix error
# 6. Fully quit out (`quit` and `quit` again) and rerun.
#
# **Alternative 2: VS Code Run and Debug**
#
# 1. Either...
#
#     1. Press `Ctrl+Shift+D` → click **▶ Run and Debug** (or `F5`).
#     2. Click the down arrow on the cell: **Debug Cell**.
#
# 2. Look at the **Call Stack** panel on the left to see the various functions called.
# 3. In the **Variables** panel, find `n` inside `_std` — why is it `0`?
# 5. Fix a bug, then re-run (`F5`).

# ---

# ## Summary
#
# You have worked through:
#
# | Topic | Key takeaway |
# | :---- | :----------- |
# | GitHub | fork → clone → branch → commit → push → PR |
# | Docstrings | NumPy style: summary → Parameters → Returns |
# | `ruff` | catches dozens of issues automatically; runs on save in VS Code |
# | Readable code | guard clauses and named helpers reduce nesting |
# | Debugging | `%debug` and VS Code breakpoints give you a live inspector |
#
# **Next:** after the break, open `notebooks/02_datajoint_spyglass.ipynb`.

# ---
#

# ## Section 6: Advanced Exercises *(take-home)*
#
# The exercises below extend the session material into a complete developer
# workflow. Expected time: 30-60m
#
# **You will need:**
# - The branch you created in Exercise 1.1 (make sure you are on it: `git branch`)
# - The `spyglass` conda environment active
# - The package installed in editable mode: `pip install -e .`

# ### Exercise 5.1 — Write a function and its pytest
#
# Add a `format_duration` function to `src/spyglass_workshop/utils.py`
# that converts a duration to a human-readable string. Then, add tests.
#
# **Specification**
#
# ```python
# def format_duration(seconds: float) -> str:
#     """Return a human-readable string for a duration in seconds."""
# ```
#
# | Input | Expected output |
# | :---- | :-------------- |
# | `0.001` | `"1.00 ms"` |
# | `0.5` | `"500.00 ms"` |
# | `1.0` | `"1.00 s"` |
# | `30.75` | `"30.75 s"` |
# | `60.0` | `"1 min 0.00 s"` |
# | `75.3` | `"1 min 15.30 s"` |
# | `3661.5` | `"1 h 1 min 1.50 s"` |
# | `−1.0` | raises `ValueError` |
#
# **Steps**
#
# 1. Open `src/spyglass_workshop/utils.py` in VS Code and add the function with
#    a complete NumPy-style docstring and type hints.
# 2. Open `tests/test_utils.py` and write tests using `pytest.mark.parametrize`
#    (for valid inputs) and `pytest.raises` (for the `ValueError` case).
# 3. Run your tests from the terminal:
#
# ```bash
# pytest tests/test_utils.py -v
# ```
#
# 4. Iterate until all tests pass, then run the full suite to make sure nothing
#    else broke:
#
# ```bash
# pytest
# ```
#
# <details><summary>Function Hint</summary>
#
# Try modeling your function after
# `spyglass.utils.dj_helper_fn.bytes_to_human_readable`
#
#
# </details>
#
# <details><summary>Function Solution</summary>
#
# ```python
# def format_duration(seconds: float) -> str:
#     """Return a human-readable string for a duration in seconds.
#
#     Parameters
#     ----------
#     seconds : float
#         Non-negative duration in seconds.
#
#     Returns
#     -------
#     str
#         Formatted string, e.g. ``"1 min 15.30 s"`` or ``"500.00 ms"``.
#
#     Raises
#     ------
#     ValueError
#         If *seconds* is negative.
#
#     Examples
#     --------
#     >>> format_duration(0.5)
#     '500.00 ms'
#     >>> format_duration(75.3)
#     '1 min 15.30 s'
#     """
#     if seconds < 0:
#         raise ValueError(f"seconds must be non-negative, got {seconds}")
#     if seconds < 1:
#         return f"{seconds * 1000:.2f} ms"
#     if seconds < 60:
#         return f"{seconds:.2f} s"
#     minutes, secs = divmod(seconds, 60)
#     if minutes < 60:
#         return f"{int(minutes)} min {secs:.2f} s"
#     hours, minutes = divmod(minutes, 60)
#     return f"{int(hours)} h {int(minutes)} min {secs:.2f} s"
# ```
#
# </details>
#
# <details><summary>Test Hint</summary>
#
# Look at the tests in this package,
# `tests/test_fibonacci.test_fibonacci`, for an example of how to test
# inputs and outputs.
#
# We should also test the error case. For an example, see
# [documentation](https://docs.pytest.org/en/7.1.x/how-to/assert.html#assertions-about-expected-exceptions).
#
# </details>
#
# <details><summary>Test Solution</summary>
#
# ```python
# import pytest
# from spyglass_workshop.utils import format_duration
#
#
# @pytest.mark.parametrize(
#     "seconds, expected",
#     [
#         (0.001, "1.00 ms"),
#         (0.5,   "500.00 ms"),
#         (1.0,   "1.00 s"),
#         (30.75, "30.75 s"),
#         (60.0,  "1 min 0.00 s"),
#         (75.3,  "1 min 15.30 s"),
#         (3661.5, "1 h 1 min 1.50 s"),
#     ],
# )
# def test_format_duration(seconds, expected):
#     assert format_duration(seconds) == expected
#
#
# def test_format_duration_negative_raises():
#     with pytest.raises(ValueError, match="non-negative"):
#         format_duration(-1.0)
# ```
#
# </details>

# ### Exercise 5.2 — Edit and publish the docs
#
# Every `.py` file in `src/spyglass_workshop/` is **automatically documented**:
# the `mkdocs` build reads every docstring and renders it as an HTML API
# reference page. That means `format_duration`, including its `Examples`
# block and parameter table — will appear in the live site the moment it has
# a docstring.
#
# **Steps**
#
# 1. **Preview locally** — in a terminal (not a notebook cell), run:
#
#    ```bash
#    mkdocs serve --config-file docs/mkdocs.yml
#    ```
#
#    This output will show warnings for any possible issues.
#
#    Open `http://localhost:8000` in a browser. Navigate to
#    **API Reference → utils** and verify that `format_duration` appears with
#    its full docstring rendered. Press `Ctrl+C` to stop the server when done.
#
# 2. **Add a personal note to `README.md`** — open it in VS Code and add
#    a sentence or two: your name, one thing you found interesting today, or
#    a question to follow up on. This gives your PR a visible change beyond
#    code.
#
# 3. **Stage and commit** all three modified files:
#
#    ```bash
#    git add src/spyglass_workshop/utils.py tests/test_utils.py README.md
#    git commit -m "Add format_duration utility with tests"
#    ```
#
#    The `pre-commit` hooks will run `ruff` automatically. If they reformat
#    anything, re-stage and commit again.
#
# 4. **Push to your fork:**
#
#    ```bash
#    git push origin <your-branch-name>
#    ```
#
# 5. *(Optional)* **Open a pull request.** Go to
#    `https://github.com/CBroz1/SpyglassWorkshop2026/compare`, choose your
#    fork and branch as the *compare* side, and open a PR with a short
#    description of what `format_duration` does and why it is useful.
#
# > **What happens in CI?** What can you do to trigger the GitHub Actions
# > for tests and docs?
