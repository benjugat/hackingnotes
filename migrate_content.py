#!/usr/bin/env python
"""
Migration script: _docs/ (Jekyll) -> docs/ (MkDocs)
- Copies .md files
- Strips Jekyll-specific front matter (keeps title)
- Rewrites absolute /hackingnotes/ links and images to relative ones
- Also handles index.md, 404.md, posts
"""

import os
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent
SRC_DOCS = REPO / "_docs"
SRC_POSTS = REPO / "_posts"
SRC_IMAGES = REPO / "images"
DST = REPO / "docs"

# Page links in the form: /hackingnotes/<section>/<page>/  (jekyll pretty permalinks)
# We exclude the /images/ path because that's an image asset, not a page.
PAGE_LINK_RE = re.compile(r"\(/hackingnotes/(?!images/)([a-zA-Z0-9_\-\./]+?)/?\)")
IMAGE_RE = re.compile(r"(!\[[^\]]*\])\(/hackingnotes/images/([^)]+)\)")


def parse_front_matter(text: str):
    """Return (front_matter_dict, body). Handles CRLF / LF / CR."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_raw.splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, body


def serialize_front_matter(fm: dict) -> str:
    """Keep only the title key. Return '---\ntitle: ...\n---\n'."""
    if "title" in fm and fm["title"]:
        return f"---\ntitle: {fm['title']}\n---\n\n"
    return ""


def relpath_to(dst_file: Path, target: str) -> str:
    """
    Compute a relative path from dst_file's directory (the MkDocs destination)
    to `target` (resolved against the docs/ root).
    """
    dst_dir = dst_file.parent
    target_path = (DST / target).resolve()
    try:
        rel = os.path.relpath(target_path, start=dst_dir)
    except ValueError:
        rel = str(target_path)
    return rel.replace(os.sep, "/")


def rewrite_content(dst_file: Path, text: str) -> str:
    """Rewrite page links and image refs to relative ones."""

    def page_sub(m):
        target = m.group(1)  # e.g., 'active-directory/ad-attacks'
        rel = relpath_to(dst_file, target)
        return f"({rel}.md)"

    def img_sub(m):
        alt = m.group(1)  # includes the leading '![...'
        fname = m.group(2)
        rel = relpath_to(dst_file, f"images/{fname}")
        return f"{alt}({rel})"

    text = PAGE_LINK_RE.sub(page_sub, text)
    text = IMAGE_RE.sub(img_sub, text)
    return text


def migrate_file(src: Path, dst: Path):
    text = src.read_text(encoding="utf-8")
    fm, body = parse_front_matter(text)
    body = rewrite_content(dst, body)
    # Make sure body has no leading junk front matter
    body = body.lstrip("\n")
    new_text = serialize_front_matter(fm) + body
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)


def copy_images():
    if SRC_IMAGES.exists():
        dst_images = DST / "images"
        if dst_images.exists():
            shutil.rmtree(dst_images)
        shutil.copytree(SRC_IMAGES, dst_images)
        print(f"[images] copied {len(list(SRC_IMAGES.iterdir()))} files to {dst_images.relative_to(REPO)}")


def copy_docs_tree():
    count = 0
    for src_md in SRC_DOCS.rglob("*.md"):
        rel = src_md.relative_to(SRC_DOCS)
        # Drop the _defaults.md template files
        if rel.name == "_defaults.md":
            continue
        dst_md = DST / rel
        migrate_file(src_md, dst_md)
        count += 1
    print(f"[docs] migrated {count} markdown files")


def migrate_index():
    src = REPO / "index.md"
    if not src.exists():
        return
    dst = DST / "index.md"
    text = src.read_text(encoding="utf-8")
    fm, body = parse_front_matter(text)
    body = rewrite_content(dst, body).lstrip("\n")
    new_text = serialize_front_matter(fm) + body
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    print(f"[home] migrated index.md")


def migrate_changelog():
    """Replace Jekyll changelog.html with a static changelog.md.
    Lists the two existing posts so the changelog isn't lost."""
    dst = DST / "changelog.md"
    content = """# Changelog

A short history of notable updates to **Hacking Notes**.

!!! note
    This page replaces the previous Jekyll-based changelog. Future entries
    should be appended below as new bullet items, ideally with a date and
    short summary.

## 2016

- **2016-02-05** — General fixes and improvements *(major)*.
- **2016-01-12** — Media support *(major)*.
"""
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"[changelog] wrote docs/changelog.md")


def copy_static_assets():
    """Copy siteicon/touch-icon/apple-touch-icon to docs/images/ if missing."""
    dst_images = DST / "images"
    dst_images.mkdir(parents=True, exist_ok=True)
    for asset in ["apple-touch-icon.png", "siteicon.png", "touch-icon.png"]:
        src = REPO / asset
        if src.exists():
            shutil.copy2(src, dst_images / asset)
            print(f"[assets] copied {asset}")


def write_root_readme_redirect():
    """The top-level README should be the new MkDocs README. The migration
    script doesn't write it — handled separately in phase 8."""


if __name__ == "__main__":
    print(f"Repo root: {REPO}")
    print(f"Source: {SRC_DOCS}")
    print(f"Destination: {DST}")
    DST.mkdir(exist_ok=True)
    copy_images()
    copy_static_assets()
    copy_docs_tree()
    migrate_index()
    migrate_changelog()
    print("Done.")
