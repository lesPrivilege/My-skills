#!/usr/bin/env python3
"""
Hash-based index for archive note dedup.

Index file format: <sha256_prefix>|<title>
One line per entry, stored at {vault}/archive/{category}.idx

Titles are normalized before hashing: NFKC + strip whitespace + strip punctuation + lowercase.
This catches near-duplicates like 「哥布林禁令是…」vs「哥布林禁令是...」.

Usage:
    idx.py dedup <category> [title ...]
        → prints titles NOT in index (new), one per line
    idx.py rebuild <category>
        → rebuilds .idx from existing .md
    idx.py check <category> <title>
        → returns 0 (EXISTS) or 1 (NEW)
"""

import hashlib
import json
import os
import re
import sys
import unicodedata

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
TITLE_PATTERN = re.compile(r'^\s*-\s+\*\*(.+?)\*\*')


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def normalize_title(title):
    """Stable normalization for hash-based dedup."""
    t = unicodedata.normalize("NFKC", title.strip())
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[，。、！？：；\"\"''「」『』【】《》（）…—·,.:;!?\'()\\[\\]{}]", "", t)
    return t.lower()


def hash_title(title):
    """Return first 12 hex chars of SHA-256 of normalized title."""
    norm = normalize_title(title)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def _paths(category):
    cfg = load_config()
    base = os.path.join(cfg["vault"], cfg["archive_dir"])
    return os.path.join(base, f"{category}.idx"), os.path.join(base, f"{category}.md")


def load_index(category):
    """Return {hash: title} dict."""
    path, _ = _paths(category)
    result = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if "|" in line:
                    h, t = line.split("|", 1)
                    result[h] = t
    except FileNotFoundError:
        pass
    return result


def title_exists(category, title):
    return hash_title(title) in load_index(category)


def cmd_dedup(category, titles):
    """Print titles not in index (one per line)."""
    existing = load_index(category)
    for t in titles:
        if hash_title(t) not in existing:
            print(t)


def cmd_check(category, title):
    if title_exists(category, title):
        sys.exit(0)
    sys.exit(1)


def cmd_rebuild(category):
    """Rebuild .idx from .md by extracting all titles."""
    _, md = _paths(category)
    idx_path_val, _ = _paths(category)

    titles = []
    try:
        with open(md) as f:
            for line in f:
                m = TITLE_PATTERN.match(line)
                if m:
                    titles.append(m.group(1))
    except FileNotFoundError:
        print(f"NOT FOUND: {md}")
        sys.exit(1)

    with open(idx_path_val, "w") as f:
        for t in titles:
            f.write(f"{hash_title(t)}|{t}\n")

    print(f"REBUILT {category}.idx: {len(titles)} entries")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__.strip())
        sys.exit(1)

    command = sys.argv[1]
    category = sys.argv[2]

    if command == "dedup":
        cmd_dedup(category, sys.argv[3:])
    elif command == "check":
        if len(sys.argv) < 4:
            print("Usage: idx.py check <category> <title>")
            sys.exit(1)
        cmd_check(category, sys.argv[3])
    elif command == "rebuild":
        cmd_rebuild(category)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
