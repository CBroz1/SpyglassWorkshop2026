"""Generate API reference pages and navigation for spyglass_workshop.

Adapted from the Spyglass docs build:
https://github.com/LorenFrankLab/spyglass/blob/main/docs/src/api/make_pages.py
"""

from pathlib import Path

import mkdocs_gen_files

# Resolve the package source directory from this script's location:
#   docs/src/api/make_pages.py  →  repo_root/src/spyglass_workshop
SRC = Path(__file__).parents[3] / "src" / "spyglass_workshop"

# Files to omit from API docs
SKIP = {"__init__"}

nav = mkdocs_gen_files.Nav()

for path in sorted(SRC.glob("**/*.py")):
    if path.stem in SKIP or "__pycache__" in path.parts:
        continue

    rel_path = path.relative_to(SRC)
    parts = path.with_suffix("").relative_to(SRC).parts
    module_path = "spyglass_workshop." + ".".join(parts)
    doc_path = rel_path.with_suffix("").as_posix() + ".md"

    with mkdocs_gen_files.open(f"api/{doc_path}", "w") as f:
        print(f"::: {module_path}", file=f)

    nav[rel_path.with_suffix("").parts] = doc_path

with mkdocs_gen_files.open("api/navigation.md", "w") as nav_file:
    nav_file.write("* [Overview](../api/index.md)\n")
    nav_file.writelines(nav.build_literate_nav())
