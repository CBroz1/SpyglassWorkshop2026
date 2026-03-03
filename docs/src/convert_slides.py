"""Convert a lookatme slide deck to a MkDocs reference page.

Usage
-----
    python docs/src/convert_slides.py docs/src/session1_tools.md
    python docs/src/convert_slides.py docs/src/session2_datajoint.md

Output path is derived automatically:
    session1_tools.md   →  session1_page.md
    session2_datajoint.md → session2_page.md

Transformations applied (in order)
-----------------------------------
1.  Extract title from YAML front matter; strip the block entirely.
2.  Remove the Calibration Slide (screen-sizing aid, no reading value).
3.  Remove slide separators (``___…`` and ``---`` lines after front matter).
4.  Remove ``<!-- stop -->`` progressive-reveal markers.
5.  Remove all remaining HTML comments (presenter notes, etc.).
6.  Collapse repeated ``# Overview`` progress-tracker slides → keep first,
    strip leading ⭕/👀/✅ emoji from bullets.
7.  Deduplicate repeated H1 headings (``# Infrastructure`` etc.).
8.  Strip ``*(time permitting…)*`` from heading lines only.
9.  Convert ``Open \`notebooks/…\`` notebook-cue lines to admonitions.
10. Remove pure presenter-cue lines (tour/try-it/break cues).
11. Prepend page-level H1 title and YAML front matter.
12. Collapse runs of 3+ blank lines to 2.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_TITLE_RE = re.compile(r'^title:\s*["\']?(.+?)["\']?\s*$', re.MULTILINE)
_SEPARATOR_RE = re.compile(r"^[-_]{3,}$", re.MULTILINE)
_STOP_RE = re.compile(r"^[ \t]*<!-- stop -->[ \t]*\n?", re.MULTILINE)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_H1_RE = re.compile(r"^# .+", re.MULTILINE)
_TIME_PERMITTING_RE = re.compile(
    r"\s*\*\(time permitting[^)]*\)\*", re.IGNORECASE
)
_NOTEBOOK_CUE_RE = re.compile(
    r"^Open `(notebooks/[^`]+\.ipynb)` — \*\*([^*]+)\*\*\.", re.MULTILINE
)
_PRESENTER_CUES = [
    re.compile(r"^Time for a quick tour!.*$", re.MULTILINE),
    re.compile(r"^Let's try it out.*$", re.MULTILINE),
    re.compile(r"^After the break:.*$", re.MULTILINE),
]
_EMOJI_BULLET_RE = re.compile(r"^(\s*-\s*)[⭕👀✅]\s*", re.MULTILINE)
_EXCESS_BLANKS_RE = re.compile(r"\n{3,}")


# ---------------------------------------------------------------------------
# Individual transformation functions
# ---------------------------------------------------------------------------


def _step1_extract_front_matter(text: str) -> tuple[str, str]:
    """Return (title, body_without_front_matter)."""
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        return "", text
    yaml_block = m.group(1)
    title_m = _TITLE_RE.search(yaml_block)
    title = title_m.group(1) if title_m else ""
    body = text[m.end() :]
    return title, body


def _step2_remove_calibration_slide(text: str) -> str:
    """Remove the block from '# Calibration Slide' to the next separator."""
    pattern = re.compile(
        r"# Calibration Slide\n.*?(?=^[-_]{3,}$|\Z)", re.DOTALL | re.MULTILINE
    )
    return pattern.sub("", text)


def _step3_remove_separators(text: str) -> str:
    """Remove ``___…`` and ``---`` slide-separator lines."""
    return _SEPARATOR_RE.sub("", text)


def _step4_remove_stop_markers(text: str) -> str:
    """Remove ``<!-- stop -->`` lines."""
    return _STOP_RE.sub("", text)


def _step5_remove_html_comments(text: str) -> str:
    """Remove all remaining HTML comments (presenter notes etc.)."""
    return _HTML_COMMENT_RE.sub("", text)


def _step6_collapse_overviews(text: str) -> str:
    """Keep only the first ``# Overview`` section; strip progress emoji."""
    # Split on H1 boundaries, preserving the heading line.
    segments = re.split(r"(?=^# )", text, flags=re.MULTILINE)

    first_overview_done = False
    out_segments = []
    for seg in segments:
        if re.match(r"^# Overview\b", seg):
            if not first_overview_done:
                # Strip leading emoji from bullet lines.
                seg = _EMOJI_BULLET_RE.sub(r"\1", seg)
                out_segments.append(seg)
                first_overview_done = True
            # else: drop duplicate overview segments
        else:
            out_segments.append(seg)

    return "".join(out_segments)


def _step7_deduplicate_h1(text: str) -> str:
    """Drop repeated identical H1 headings and the blank line after each drop."""
    lines = text.splitlines(keepends=True)
    out = []
    last_h1: str | None = None
    skip_next_blank = False
    for line in lines:
        stripped = line.rstrip("\n")
        if re.match(r"^# ", stripped):
            if stripped == last_h1:
                skip_next_blank = True
                continue  # drop duplicate H1
            else:
                last_h1 = stripped
                skip_next_blank = False
        elif skip_next_blank and stripped == "":
            skip_next_blank = False
            continue  # drop the orphan blank line after a dropped H1
        else:
            skip_next_blank = False
        out.append(line)
    return "".join(out)


def _step8_strip_time_permitting_headings(text: str) -> str:
    """Remove '*(time permitting…)*' only from heading lines."""
    lines = text.splitlines(keepends=True)
    out = []
    for line in lines:
        if re.match(r"^#{1,6} ", line):
            line = _TIME_PERMITTING_RE.sub("", line)
        out.append(line)
    return "".join(out)


def _step9_notebook_cues_to_admonitions(text: str) -> str:
    """Convert 'Open ``notebooks/…`` — **Section N**.' to tip admonitions."""

    def _repl(m: re.Match) -> str:
        nb = m.group(1)
        section = m.group(2)
        return f'!!! tip "Practice"\n    Open `{nb}` — **{section}**.'

    return _NOTEBOOK_CUE_RE.sub(_repl, text)


def _step10_remove_presenter_cues(text: str) -> str:
    """Remove live-session cue lines and any preceding blank line they orphan."""
    for pattern in _PRESENTER_CUES:
        text = pattern.sub("", text)
    # Collapse any double blanks created by removals (full collapse in step 12).
    return text


def _step11_prepend_title(text: str, title: str) -> str:
    """Prepend YAML front matter block and a page-level H1 heading."""
    front = f'---\ntitle: "{title}"\n---\n\n# {title}\n\n'
    return front + text.lstrip("\n")


def _step12_collapse_blanks(text: str) -> str:
    """Collapse runs of 3+ blank lines to exactly one blank line."""
    return _EXCESS_BLANKS_RE.sub("\n\n", text)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def convert(source: Path) -> str:
    """Run all transformations and return the page markdown string."""
    text = source.read_text(encoding="utf-8")

    title, text = _step1_extract_front_matter(text)
    text = _step2_remove_calibration_slide(text)
    text = _step3_remove_separators(text)
    text = _step4_remove_stop_markers(text)
    text = _step5_remove_html_comments(text)
    text = _step6_collapse_overviews(text)
    text = _step7_deduplicate_h1(text)
    text = _step8_strip_time_permitting_headings(text)
    text = _step9_notebook_cues_to_admonitions(text)
    text = _step10_remove_presenter_cues(text)
    text = _step11_prepend_title(text, title)
    text = _step12_collapse_blanks(text)

    return text


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <slide_file.md>")
        sys.exit(1)

    source = Path(sys.argv[1])
    if not source.exists():
        print(f"Error: {source} not found")
        sys.exit(1)

    # Derive output path: session1_tools.md → session1_page.md
    stem = source.stem  # e.g. "session1_tools"
    prefix = stem.split("_")[0]  # e.g. "session1"
    dest = source.parent / f"{prefix}_page.md"

    page = convert(source)
    dest.write_text(page, encoding="utf-8")
    print(f"Written: {dest}  ({len(page)} chars)")


if __name__ == "__main__":
    main()
