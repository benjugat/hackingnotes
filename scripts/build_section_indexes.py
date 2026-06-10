#!/usr/bin/env python
"""
build_section_indexes.py
Generate docs/<section>/index.md for every content section.

Each landing page has:
- title + description (front matter)
- A short intro paragraph
- A Material "grid cards" block listing every sub-page in the section
  with its title and a description (taken from the first non-heading
  paragraph of the source markdown file).

Sections are read directly from the `nav:` block of mkdocs.yml. The
"Network" top-level section is a virtual grouping that pulls together
`services/` and `hacking-wifi/`; the script generates an index.md for
both underlying folders and tags them with the appropriate title.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
MK = REPO / "mkdocs.yml"
DOCS = REPO / "docs"

# Per-section copy: short intro used as the landing-page lead.
# Keys are the actual folder names (filesystem), values are the labels
# that should appear on the index page title.
SECTION_INTRO: dict[str, tuple[str, str]] = {
    "active-directory": (
        "Active Directory",
        "Active Directory attack and defense: enumeration, lateral movement, persistence, privilege escalation, cross-trust abuse and AD CS exploitation.",
    ),
    "client-side-attacks": (
        "Client-Side Attacks",
        "Client-side payloads and delivery chains targeting end-user applications: malicious Office macros, HTA files, evil PDFs and HTML smuggling.",
    ),
    "enumeration": (
        "Enumeration",
        "Host and service enumeration: discovery, port scanning, OS fingerprinting, DNS harvesting and WAF evasion techniques.",
    ),
    "exploiting": (
        "Exploiting",
        "Exploit development notes, primarily memory-corruption bugs: buffer overflows on Windows and Linux.",
    ),
    "hacking-wifi": (
        "Hacking WiFi",
        "WiFi penetration testing: theory, WEP, WPA/WPA2 PSK and WPA/WPA2 Enterprise (PEAP).",
    ),
    "movil": (
        "Mobile",
        "iOS testing notes covering jailbroken and non-jailbroken devices.",
    ),
    "other": (
        "Other",
        "Miscellaneous topics: AWS, Python and PowerShell for offensive security.",
    ),
    "post-exploitation": (
        "Post-Exploitation",
        "What to do after you land a shell: AV / UAC bypass, credential gathering, password cracking, port forwarding, file transfer, and APPLocker / ATA evasion.",
    ),
    "privilege-escalation": (
        "Privilege Escalation",
        "Local privilege escalation on Linux and Windows, plus running commands as other users.",
    ),
    "reconnaissance": (
        "Reconnaissance",
        "Pre-engagement information gathering: OSINT, asset discovery and target profiling.",
    ),
    "services": (
        "Services",
        "Per-service attack and enumeration notes for common TCP/UDP services (FTP, SSH, SMB, HTTP, DNS, etc.).",
    ),
    "software": (
        "Software",
        "Pentesting notes for specific applications: CMS, mail servers, CI servers, app servers and Python package servers.",
    ),
    "web": (
        "Web",
        "Web application attacks and methodologies: OWASP Top 10, logic flaws, smuggling, deserialization, SSRF, JWT and more.",
    ),
}


def parse_front_matter(text: str) -> tuple[dict, str]:
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


def first_paragraph(body: str, max_len: int = 220) -> str:
    """Pick the first non-heading, non-empty paragraph from the body."""
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para:
            continue
        if para.startswith(("#", "!", "```", "|", ">", "<")):
            continue
        # Drop inline markdown noise
        para = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", para)
        para = re.sub(r"[`*_]", "", para)
        para = re.sub(r"\s+", " ", para).strip()
        if len(para) > max_len:
            para = para[: max_len - 1].rstrip() + "…"
        return para
    return "No description available."


def read_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    fm, _ = parse_front_matter(text)
    return fm.get("title", path.stem.replace("-", " ").title())


def read_description(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    _, body = parse_front_matter(text)
    return first_paragraph(body)


def collect_section_pages(section_folder: str) -> list[Path]:
    folder = DOCS / section_folder
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.glob("*.md") if p.name != "index.md")


def render_grid(pages: list[Path]) -> str:
    """Render a Material 'grid cards' block."""
    if not pages:
        return "_No pages in this section yet._\n"
    items = []
    for p in pages:
        title = read_title(p)
        desc = read_description(p)
        # The card syntax requires a blank line after `---` and uses 4-space indents.
        items.append(
            f"-   **[{title}]({p.name})**\n\n"
            f"    ---\n\n"
            f"    {desc}\n"
        )
    body = "\n".join(items).rstrip() + "\n"
    return (
        '<div class="grid cards" markdown>\n\n'
        + body
        + "\n</div>\n"
    )


def render_index(folder: str, title: str, intro: str) -> None:
    pages = collect_section_pages(folder)
    grid = render_grid(pages)
    target = DOCS / folder / "index.md"
    fm = (
        "---\n"
        f"title: {title}\n"
        f"description: {intro}\n"
        "---\n\n"
    )
    body = (
        f"# {title}\n\n"
        f"{intro}\n\n"
        f"## Contents\n\n"
        f"{grid}"
    )
    target.write_text(fm + body, encoding="utf-8")
    print(f"  wrote {target.relative_to(REPO)} ({len(pages)} pages)")


def load_nav() -> list:
    with open(MK, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("nav", [])


def main() -> None:
    nav = load_nav()
    print("Generating section landing pages…")
    generated = 0
    for entry in nav:
        if not isinstance(entry, dict):
            continue
        for nav_label, children in entry.items():
            # Top-level pages like `Home: index.md` have a string value.
            # Sections like `Web: [list of pages]` have a list value.
            if not isinstance(children, list):
                continue
            # Identify the unique folder(s) used by this nav section
            folders: set[str] = set()
            for child in children:
                if isinstance(child, str) and "/" in child:
                    folders.add(child.split("/", 1)[0])
                elif isinstance(child, dict):
                    # Nested section: take the keys (not used in our nav, but safe)
                    folders.update(child.keys())
            for folder in sorted(folders):
                if folder not in SECTION_INTRO:
                    print(f"  ! no intro configured for folder '{folder}' (skipped)")
                    continue
                title, intro = SECTION_INTRO[folder]
                render_index(folder, title, intro)
                generated += 1
    print(f"Done. Generated {generated} index.md files.")


if __name__ == "__main__":
    main()
