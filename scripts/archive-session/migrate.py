#!/usr/bin/env python3
"""Migrate Dots.md entries into categorized individual files in Obsidian vault."""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# Load config
with open(Path.home() / "Scripts" / "archive-session" / "config.json") as f:
    config = json.load(f)

VAULT = Path(config["vault"])
CAT_KEYS = {
    "技術與系統": "技術與系統",
    "組織、資本與權力": "組織資本與權力",
    "組織、資本與權力": "組織資本與權力",  # handles the 、 variant
}
CATEGORIES = list(config["categories"].values())

# Build reverse mapping: raw heading text → directory name
HEADING_TO_DIR = {}
for raw, directory in config["categories"].items():
    HEADING_TO_DIR[raw] = directory
# Also handle the version without 、
HEADING_TO_DIR["組織資本與權力"] = "組織資本與權力"

def sanitize_filename(title: str) -> str:
    """Keep Chinese chars, ASCII alphanum, underscore, dash, dot; remove rest."""
    # Remove leading/trailing whitespace
    title = title.strip()
    # Replace problematic chars with underscore
    title = re.sub(r'[<>:"/\\|?*]', '_', title)
    # Collapse multiple underscores/spaces
    title = re.sub(r'[_\s]+', '_', title)
    # Limit length
    if len(title) > 120:
        title = title[:120]
    return title


def parse_notes_from_dots(dots_path: Path) -> list[dict]:
    """Parse Dots.md and return list of {category, title, content} dicts."""
    text = dots_path.read_text(encoding="utf-8")

    # Split into sections by top-level headings
    # But Dots.md uses # for categories... let me check
    # Actually looking at Dots.md again:
    # Lines after the --- separator:
    # # 技術與系統
    # - **Title** ...
    # # 組織、資本與權力
    # etc.

    # Find the separator line
    sep_idx = text.find("\n---\n")
    if sep_idx >= 0:
        text = text[sep_idx + 5:]  # skip past ---

    notes = []
    current_category = None
    # Pattern: - **Title**：Content or - **Title**: Content
    note_pattern = re.compile(r'^- \*\*(.+?)\*\*[：:](.*)', re.MULTILINE)

    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for category heading: # 技術與系統
        # Could be # or ##
        cat_match = re.match(r'^#+\s+(.+)$', line)
        if cat_match:
            heading = cat_match.group(1).strip()
            if heading in HEADING_TO_DIR:
                current_category = HEADING_TO_DIR[heading]
                i += 1
                continue

        # Check for note start (may be indented)
        note_match = re.match(r'^\s*- \*\*(.+?)\*\*[：:](\s*.*)', line)
        if note_match and current_category:
            title = note_match.group(1).strip()
            content_start = note_match.group(2).strip()

            # Collect subsequent lines that belong to this note
            # (continuation lines are indented or just continue the paragraph)
            note_content = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                # Stop at next note start or next category heading
                if re.match(r'^\s*- \*\*(.+?)\*\*[：:]', next_line):
                    break
                if re.match(r'^#+\s+.+', next_line) and re.sub(r'^#+\s+', '', next_line).strip() in HEADING_TO_DIR:
                    break
                if next_line.strip() == "":
                    # Empty line might be separator - check if next non-empty is a note or heading
                    note_content.append(next_line)
                    i += 1
                    continue
                note_content.append(next_line)
                i += 1

            full_note = "\n".join(note_content).strip()
            notes.append({
                "category": current_category,
                "title": title,
                "content": full_note,
            })
            continue

        i += 1

    return notes


def save_note(note: dict, vault: Path, dry_run: bool = False) -> str:
    """Save a single note to the vault. Returns status."""
    cat_dir = vault / note["category"]
    if not cat_dir.exists():
        if dry_run:
            print(f"  Would create directory: {cat_dir}")
        else:
            cat_dir.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(note["title"]) + ".md"
    filepath = cat_dir / filename

    today = date.today().isoformat()

    frontmatter = (
        "---\n"
        f"source: session-archive\n"
        f"archived: {today}\n"
        f"category: {note['category']}\n"
        f'title: "{note["title"]}"\n'
        "---\n"
    )

    content = frontmatter + "\n" + note["content"] + "\n"

    if filepath.exists():
        existing = filepath.read_text(encoding="utf-8")
        if existing == content:
            return "skip (identical)"
        else:
            # Add suffix
            stem = filepath.stem
            suffix_num = 1
            while True:
                new_path = cat_dir / f"{stem}_{suffix_num}.md"
                if not new_path.exists():
                    filepath = new_path
                    break
                suffix_num += 1
            return f"save (conflict → {filepath.name})"

    if not dry_run:
        filepath.write_text(content, encoding="utf-8")
    return f"saved → {filepath.name}"


def main():
    dry_run = "--dry-run" in sys.argv
    dots_path = VAULT / "Dots.md"
    if not dots_path.exists():
        print(f"Error: Dots.md not found at {dots_path}")
        sys.exit(1)

    notes = parse_notes_from_dots(dots_path)
    print(f"Found {len(notes)} notes in Dots.md\n")

    cat_counts = {}
    for note in notes:
        cat = note["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count} notes")

    if dry_run:
        print("\n[Dry run — no files written]")
        return

    print("\n---\n")
    saved = 0
    skipped = 0
    conflicts = 0
    for note in notes:
        result = save_note(note, VAULT)
        if result.startswith("saved"):
            saved += 1
        elif result.startswith("skip"):
            skipped += 1
        else:
            conflicts += 1
        print(f"  [{note['category']}] {note['title'][:40]:40s} → {result}")

    print(f"\n--- Summary ---")
    print(f"  Saved: {saved}")
    print(f"  Skipped (identical): {skipped}")
    print(f"  Conflicts (renamed): {conflicts}")
    if conflicts:
        print("  → Manually review conflict files")


if __name__ == "__main__":
    main()
