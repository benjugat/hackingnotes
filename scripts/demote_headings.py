#!/usr/bin/env python
"""Demote all markdown headings by one level, in non-index.md files only.

Skips lines inside fenced code blocks (``` or ~~~).
Skips lines inside HTML comments.
Only acts on lines matching the strict ATX heading pattern: ^#{1,6}\s

Run from the repo root: python scripts/demote_headings.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
HEADING_RE = re.compile(r"^(#{1,6})(\s)")
CODE_FENCE_RE = re.compile(r"^\s*(```+|~~~+)")


def demote_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    in_code = False
    in_comment = False
    changes = 0
    new_lines = []
    for line in lines:
        stripped = line.lstrip()

        if CODE_FENCE_RE.match(line):
            in_code = not in_code
            new_lines.append(line)
            continue
        if in_code:
            new_lines.append(line)
            continue

        if "<!--" in line:
            in_comment = True
        if in_comment:
            new_lines.append(line)
            if "-->" in line:
                in_comment = False
            continue

        m = HEADING_RE.match(line)
        if m:
            new_line = "#" + m.group(1) + m.group(2) + line[m.end():]
            if new_line != line:
                changes += 1
                new_lines.append(new_line)
                continue
        new_lines.append(line)

    if changes > 0:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("".join(new_lines))
    return changes


def main() -> int:
    total = 0
    files_changed = 0
    for f in sorted(DOCS.rglob("*.md")):
        if f.name == "index.md":
            continue
        n = demote_file(f)
        if n > 0:
            files_changed += 1
            total += n
            print(f"  {f.relative_to(ROOT)}: {n} heading(s) demoted")
    print(f"\nTotal: {total} headings demoted in {files_changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
