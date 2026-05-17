#!/usr/bin/env python3
"""Normalize archive/*.md files to a consistent format.

Rules:
1. Strip trailing whitespace from every line
2. No consecutive blank lines
3. # heading  → followed by one blank line
4. ## heading → followed by one blank line
5. Each note (- **...) followed by one blank line
6. File ends with exactly one newline
"""

import sys
import re
from pathlib import Path


def normalize(text: str) -> str:
    lines = text.splitlines()

    # Step 1: strip trailing whitespace
    lines = [line.rstrip() for line in lines]

    # Step 2: filter out blank lines, we'll reinsert as needed
    nonblank = [line for line in lines if line.strip() != ""]

    # Step 3: build output with proper spacing
    out = []
    for i, line in enumerate(nonblank):
        out.append(line)

        # Is the next non-blank line a note or a heading?
        next_is_note = (i + 1 < len(nonblank) and nonblank[i + 1].startswith("- **"))
        next_is_heading = (i + 1 < len(nonblank) and re.match(r"^#{1,2}\s", nonblank[i + 1]))

        # After heading lines → always blank
        if re.match(r"^#{1,2}\s", line):
            out.append("")
            continue

        # After note lines → blank if next is also a note (separation)
        if line.startswith("- **"):
            if next_is_note:
                out.append("")
            continue

    # Ensure file ends with exactly one newline
    result = "\n".join(out).rstrip("\n") + "\n"
    return result


def main():
    if len(sys.argv) < 2:
        vault = Path.home() / "Documents/Obsidian/archive"
        files = sorted(vault.glob("*.md"))
    else:
        files = [Path(f) for f in sys.argv[1:]]

    if not files:
        print("No files found.")
        return

    for fp in files:
        original = fp.read_text(encoding="utf-8")
        cleaned = normalize(original)
        if cleaned == original:
            print(f"  {fp.name}: already clean")
        else:
            fp.write_text(cleaned, encoding="utf-8")
            orig_lines = original.splitlines()
            clean_lines = cleaned.splitlines()
            diff = len(clean_lines) - len(orig_lines)
            sign = "+" if diff >= 0 else ""
            print(f"  {fp.name}: normalized ({sign}{diff} lines)")


if __name__ == "__main__":
    main()
