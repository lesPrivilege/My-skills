#!/usr/bin/env python3
"""Clean markdown files exported from Calibre/zlibrary ebook conversions."""

import re
import sys
from pathlib import Path


def clean_md(text: str) -> tuple[str, dict]:
    """Apply cleaning rules sequentially. Returns (cleaned_text, stats)."""
    stats = {
        "metadata_header": 0,
        "ad_blocks": 0,
        "watermarks": 0,
        "nav_links": 0,
        "cover_masthead": 0,
        "none_images": 0,
        "html_entities": 0,
        "dup_headers": 0,
        "lines_before": 0,
        "lines_after": 0,
    }
    lines = text.split("\n")
    stats["lines_before"] = len(lines)

    # === Rule 1: Remove Calibre metadata header ===
    identifier_idx = None
    for i, line in enumerate(lines):
        if line.startswith("**Identifier:**"):
            identifier_idx = i
            break
    if identifier_idx is not None:
        # Remove through identifier line + trailing blanks
        end = identifier_idx + 1
        while end < len(lines) and lines[end].strip() == "":
            end += 1
        removed = end
        lines = lines[end:]
        stats["metadata_header"] = removed

    # === Rule 2: Remove ad blocks ===
    ad_start_re = re.compile(r"^#+\s*优质App推荐", re.IGNORECASE)
    # Ad entry pattern: [![Image...](static_images/...)](url) text [点击下载](url)
    ad_entry_re = re.compile(r"^\[!\[Image", re.IGNORECASE)
    cleaned = []
    i = 0
    while i < len(lines):
        if ad_start_re.match(lines[i]):
            stats["ad_blocks"] += 1
            i += 1  # skip heading
            # skip all ad entries and blank lines until next non-ad content
            while i < len(lines):
                stripped = lines[i].strip()
                if stripped == "" or ad_entry_re.match(stripped):
                    i += 1
                    continue
                break
        else:
            cleaned.append(lines[i])
            i += 1
    lines = cleaned

    # === Rule 3: Remove download watermark lines ===
    watermark_zlibrary_re = re.compile(
        r"^This article was downloaded by \[zlibrary\]"
    )
    watermark_calibre_re = re.compile(
        r"^This article was downloaded by \*\*calibre\*\*"
    )
    cleaned = []
    for i, line in enumerate(lines):
        if watermark_zlibrary_re.match(line) or watermark_calibre_re.match(line):
            stats["watermarks"] += 1
            # also remove preceding blank line
            if cleaned and cleaned[-1].strip() == "":
                cleaned.pop()
            continue
        cleaned.append(line)
    lines = cleaned

    # === Rule 4: Remove internal HTML navigation links ===
    # Pattern A: hex-hash links (original Calibre format)
    hex_link_re = re.compile(r"^\*\s+\[.*?\]\([0-9a-f]{20,}\.html\)$")
    # Pattern B: index_split links as list items (New Yorker TOC)
    index_split_re = re.compile(r"^\*?\s*\[.*?\]\(index_split_\d+\.html")
    # Pattern C: feed/article Calibre internal links (Atlantic/Wired format)
    # Matches: feed_N/index_uNN.html, article_N/index.html,
    #          article_N/index_uN_split_NNN.html (hybrid format)
    calibre_index_re = re.compile(
        r"^\*?\s*\[.*?\]\((\.\./)*(feed_\d+|article_\d+)/index(_u\d+)?(_split_\d+)?\.html"
    )
    # Pattern D: pipe-separated navigation bars with .html links
    pipe_nav_re = re.compile(r"^\s*\|.*\.html.*\|")
    # Pattern E: blockquote TOC entries with index_split links
    bq_index_split_re = re.compile(r"^>\s*(>*\s*)*\[.*?\]\(index_split_\d+\.html")
    # Pattern F: standalone horizontal rules used as nav separators (keep only one)
    hr_re = re.compile(r"^---+$")
    cleaned = []
    consecutive_hrs = 0
    for line in lines:
        s = line.strip()
        if (hex_link_re.match(s)
                or index_split_re.match(s)
                or calibre_index_re.match(s)
                or pipe_nav_re.match(s)
                or bq_index_split_re.match(s)):
            stats["nav_links"] += 1
            continue
        # Collapse consecutive --- separators (keep at most one)
        if hr_re.match(s):
            consecutive_hrs += 1
            if consecutive_hrs > 1:
                stats["nav_links"] += 1
                continue
        else:
            consecutive_hrs = 0
        cleaned.append(line)
    lines = cleaned

    # === Rule 4b: Strip Calibre cross-reference hrefs from inline body links ===
    # Convert [text](../../feed_N/article_N/index_uN.html) → text
    # These are editorial cross-references that point to Calibre internal files
    calibre_href_re = re.compile(
        r"\[([^\]]+)\]\((\.\./)*(feed_\d+/)?(article_\d+/)?index(_u\d+)?(_split_\d+)?\.html[^)]*\)"
    )
    cleaned = []
    for line in lines:
        new_line = calibre_href_re.sub(r"\1", line)
        cleaned.append(new_line)
    lines = cleaned

    # === Rule 5: Remove cover/masthead images ===
    cover_re = re.compile(r"^!\[Cover\]\(static_images/cover\.jpg\)$")
    masthead_re = re.compile(r"^!\[\]\(static_images/mastheadImage\.jpg\)$")
    cleaned = []
    for line in lines:
        s = line.strip()
        if cover_re.match(s) or masthead_re.match(s):
            stats["cover_masthead"] += 1
            continue
        cleaned.append(line)
    lines = cleaned

    # === Rule 6: Normalize broken image references ===
    none_img_re = re.compile(r"^!\[None\]\(static_images/.*?\)$")
    local_img_re = re.compile(
        r"^(!\[.+?\]\(static_images/.*?\))(\s*)$"
    )
    cleaned = []
    for line in lines:
        s = line.strip()
        # Remove ![None](...) entirely
        if none_img_re.match(s):
            stats["none_images"] += 1
            continue
        # Consecutive None images on same line: ![None](...)![None](...)
        if "![None]" in s and "static_images/" in s:
            # Check if line is ONLY None images
            remaining = re.sub(r"!\[None\]\(static_images/[^)]*\)", "", s).strip()
            if remaining == "":
                stats["none_images"] += 1
                continue
        cleaned.append(line)
    lines = cleaned

    # === Rule 7: Decode HTML entities ===
    entity_map = {
        "&AMP;": "&",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&nbsp;": " ",
        "&quot;": '"',
    }
    entity_re = re.compile("|".join(re.escape(k) for k in entity_map.keys()))
    cleaned = []
    for line in lines:
        new_line = entity_re.sub(lambda m: entity_map[m.group()], line)
        if new_line != line:
            stats["html_entities"] += 1
        cleaned.append(new_line)
    lines = cleaned

    # === Rule 8: Deduplicate section headers ===
    # Handles: plain text matching a heading, or a higher-level heading (##) matching
    # a lower-level heading (#) with the same text within a few lines
    cleaned = []
    i = 0
    while i < len(lines):
        current = lines[i].strip()
        if current and not current.startswith("!"):
            # Extract text from current (may or may not be a heading)
            current_heading = re.match(r"^(#{1,6})\s+(.+)$", current)
            current_text = current_heading.group(2).strip() if current_heading else current
            current_level = len(current_heading.group(1)) if current_heading else 0

            # Look ahead for a heading with matching text
            skip = False
            for offset in range(1, 12):
                if i + offset >= len(lines):
                    break
                ahead = lines[i + offset].strip()
                if ahead == "":
                    continue
                ahead_heading = re.match(r"^(#{1,6})\s+(.+)$", ahead)
                if ahead_heading:
                    ahead_text = ahead_heading.group(2).strip()
                    ahead_level = len(ahead_heading.group(1))
                    # Match if same text and current is plain or higher-level (##) than ahead (#)
                    if ahead_text == current_text and (current_level == 0 or current_level > ahead_level):
                        stats["dup_headers"] += 1
                        skip = True
                        break
                    else:
                        break  # different heading = stop
                # Non-heading non-blank: if it's the same text as current (another dup),
                # skip over it and keep looking; otherwise stop
                if ahead == current_text:
                    continue
                break
            if skip:
                i += 1
                continue
        cleaned.append(lines[i])
        i += 1
    lines = cleaned

    # === Rule 8b: Remove orphaned standalone date line at file start ===
    # After metadata removal, a bare date like "January 4th 2025" may be first content
    date_re = re.compile(
        r"^(January|February|March|April|May|June|July|August|September|"
        r"October|November|December)\s+\d{1,2}(st|nd|rd|th)\s+\d{4}$"
    )
    while lines and lines[0].strip() == "":
        lines.pop(0)
    if lines and date_re.match(lines[0].strip()):
        lines.pop(0)
        # remove trailing blanks after removed date
        while lines and lines[0].strip() == "":
            lines.pop(0)

    # === Rule 9: Collapse excessive blank lines ===
    cleaned = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)
    lines = cleaned

    # Strip leading/trailing blank lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    stats["lines_after"] = len(lines)
    return "\n".join(lines) + "\n", stats


def main():
    if len(sys.argv) < 2:
        print("Usage: clean.py <input.md> [output.md]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.with_stem(input_path.stem + "_cleaned")

    text = input_path.read_text(encoding="utf-8")
    cleaned, stats = clean_md(text)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(cleaned, encoding="utf-8")

    removed = stats["lines_before"] - stats["lines_after"]
    print(f"Done. {stats['lines_before']} → {stats['lines_after']} lines ({removed} removed)")
    print(f"  Metadata header:   {stats['metadata_header']} lines")
    print(f"  Ad blocks:         {stats['ad_blocks']}")
    print(f"  Watermarks:        {stats['watermarks']}")
    print(f"  Nav links:         {stats['nav_links']}")
    print(f"  Cover/masthead:    {stats['cover_masthead']}")
    print(f"  None images:       {stats['none_images']}")
    print(f"  HTML entities:     {stats['html_entities']} lines")
    print(f"  Dup headers:       {stats['dup_headers']}")


if __name__ == "__main__":
    main()
