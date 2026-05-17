#!/usr/bin/env python3
"""Consolidate individual notes into per-category archive files.

Reads all notes from categorized directories, then writes one file per
category in archive/ with session-dated sections.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
with open(Path.home() / "Scripts" / "archive-session" / "config.json") as f:
    config = json.load(f)

VAULT = Path(config["vault"])
ARCHIVE_DIR = VAULT / "archive"

# Mapping: category name → short English filename stem
CAT_FILE = {
    "技術與系統": "tech",
    "組織資本與權力": "power",
    "認知哲學與心智": "mind",
    "數學學習與方法論": "method",
    "生活決策與心智工具": "life",
}
CATEGORIES = list(CAT_FILE.keys())

HEADING_TO_DIR = dict(config["categories"])
HEADING_TO_DIR["組織資本與權力"] = "組織資本與權力"


# ── Parse ───────────────────────────────────────────────────────────

def parse_notes_from_dots(dots_path: Path) -> list[dict]:
    """Parse Dots.md → list of {category, title, content}."""
    text = dots_path.read_text(encoding="utf-8")

    # Find separator line after instructions
    sep_idx = text.find("\n---\n")
    if sep_idx >= 0:
        text = text[sep_idx + 5:]

    notes = []
    current_category = None
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        cat_match = re.match(r'^#+\s+(.+)$', line)
        if cat_match:
            heading = cat_match.group(1).strip()
            if heading in HEADING_TO_DIR:
                current_category = HEADING_TO_DIR[heading]
                i += 1
                continue

        note_match = re.match(r'^\s*- \*\*(.+?)\*\*[：:](\s*.*)', line)
        if note_match and current_category:
            title = note_match.group(1).strip()
            note_lines = [line]
            i += 1
            while i < len(lines):
                nl = lines[i]
                if re.match(r'^\s*- \*\*(.+?)\*\*[：:]', nl):
                    break
                if re.match(r'^#+\s+.+', nl):
                    ch = re.sub(r'^#+\s+', '', nl).strip()
                    if ch in HEADING_TO_DIR:
                        break
                note_lines.append(nl)
                i += 1
            notes.append({
                "category": current_category,
                "title": title,
                "content": "\n".join(note_lines).strip(),
            })
            continue
        i += 1
    return notes


# ── Consolidate ─────────────────────────────────────────────────────

def fmt_entry(note: dict) -> str:
    """Format a single note as an archive list item."""
    return note["content"]


def consolidate(category: str, notes: list[dict], output_path: Path, dry_run: bool = False):
    """Write (or dry-run) the consolidated file for one category."""
    short = CAT_FILE[category]
    title_map_jp = {c: s for s, c in CAT_FILE.items()}
    cn_name = title_map_jp[short]

    sections = {}  # date string → list of note contents

    for note in notes:
        sec = "2026-04-26"  # all current notes come from Dots.md
        sections.setdefault(sec, []).append(note)

    # Sort dates
    lines = [f"# {cn_name}\n"]
    for sec_date in sorted(sections.keys(), reverse=True):
        lines.append(f"\n## 歸檔 · {sec_date}\n")
        for note in sections[sec_date]:
            lines.append(note["content"] + "\n")

    if dry_run:
        print(f"  [{short}] {len(notes)} notes → {output_path.name}")
        return

    output_path.write_text("".join(lines), encoding="utf-8")


# ── Main ────────────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    clean = "--clean" in sys.argv  # remove old individual files after success

    # Parse from Dots.md
    dots_path = VAULT / "Dots.md"
    if not dots_path.exists():
        print("Error: Dots.md not found")
        sys.exit(1)

    all_notes = parse_notes_from_dots(dots_path)
    print(f"Parsed {len(all_notes)} notes from Dots.md")

    # Group by category
    cat_notes: dict[str, list] = {}
    for note in all_notes:
        cat_notes.setdefault(note["category"], []).append(note)

    # Build section header per category
    print("\n--- Consolidating ---")
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for cat in CATEGORIES:
        notes = cat_notes.get(cat, [])
        fname = CAT_FILE[cat] + ".md"
        out_path = ARCHIVE_DIR / fname
        consolidate(cat, notes, out_path, dry_run=dry_run)

    # Also save prompt.md pointer to config
    if not dry_run:
        print("\nArchive files created:")
        for cat in CATEGORIES:
            fname = CAT_FILE[cat] + ".md"
            size = (ARCHIVE_DIR / fname).stat().st_size
            print(f"  archive/{fname}  ({size:,} bytes)")

    # Clean up old individual files
    if clean and not dry_run:
        print("\n--- Cleaning up individual files ---")
        for cat in CATEGORIES:
            dir_path = VAULT / cat
            if dir_path.exists():
                for f in dir_path.glob("*.md"):
                    f.unlink()
                # rmdir if empty
                try:
                    dir_path.rmdir()
                    print(f"  Removed {cat}/")
                except OSError:
                    # Not empty — shouldn't happen since we just deleted .md files
                    print(f"  Deleted .md files in {cat}/  (dir not empty)")
        print("Cleanup done.")


if __name__ == "__main__":
    main()
