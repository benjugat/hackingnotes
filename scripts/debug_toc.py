#!/usr/bin/env python
"""Build and inspect toc for a few files."""
import os
import sys
from pathlib import Path

os.chdir("C:/Users/mvaliente/Documents/Hacking/test2/hackingnotes")
sys.path.insert(0, ".")

from mkdocs.config import load_config
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from mkdocs.commands.build import _populate_page

config = load_config("mkdocs.yml")

# Build the file list the way mkdocs does
from mkdocs.structure.files import File

# Build a list of File objects
file_objs = []
for md in all_md:
    rel = str(md).replace(os.sep, "/")
    try:
        f = File(
            generated_by="docs",
            path=rel,
            src_dir=Path("docs"),
            dest_dir=Path("site"),
            use_directory_urls=config.use_directory_urls,
        )
        file_objs.append(f)
    except Exception as e:
        pass

files_obj = Files(file_objs)

# Render a few files
for target in ["docs/web/sqli.md", "docs/web/file-inclusion.md"]:
    try:
        f = files_obj.get_file_from_path(target)
        page = Page(title="X", file=f, config=config)
        _populate_page(page, config, files_obj, dirty=True)
        print(f"\n=== {target} ===")
        print(f"toc count: {len(page.toc.toc_items)}")
        for item in page.toc.toc_items[:5]:
            print(f"  lvl {item.level}: {item.title}")
        if len(page.toc.toc_items) > 5:
            print(f"  ... and {len(page.toc.toc_items) - 5} more")
    except Exception as e:
        print(f"ERROR {target}: {e}")
