#!/usr/bin/env python3
"""Phase 1: regex-based pre-cleaning of OCR'd markdown.

Usage:
    python clean_rules.py input.md output.md [--config config.yaml]

Built-in rules are applied in order. If --config is provided and contains
ocr_fixes, those additional substitutions are applied as well.
"""

import re
import sys
import os
import argparse


# ── Built-in rules ──────────────────────────────────────────────────

def strip_html_tags(text):
    """Remove HTML/XML tags that leaked from PDF conversion."""
    text = re.sub(r'</?[a-zA-Z][^>]*>', '', text)
    text = re.sub(r'<![^>]+>', '', text)
    return text


def decode_html_entities(text):
    """Replace common HTML entities with plain-text equivalents."""
    entities = {
        '&amp;': '&', '&AMP;': '&', '&lt;': '<', '&gt;': '>',
        '&nbsp;': ' ', '&quot;': '"', '&#39;': "'", '&#x27;': "'",
        '&#x2F;': '/', '&#x60;': '`', '&#x3D;': '=', '&#x22;': '"',
    }
    for ent, char in entities.items():
        text = text.replace(ent, char)
    return text


def normalize_punctuation(text):
    """Convert fullwidth CJK punctuation to halfwidth where appropriate."""
    fullwidth_to_halfwidth = {
        '，': ',', '。': '.', '（': '(', '）': ')',
        '：': ':', '；': ';', '！': '!', '？': '?',
        '【': '[', '】': ']', '“': '"', '”': '"',
        '‘': "'", '’': "'", '《': '<', '》': '>',
        '～': '~', '　': ' ',
    }
    for fw, hw in fullwidth_to_halfwidth.items():
        text = text.replace(fw, hw)
    return text


def fix_escaped_chars(text):
    r"""Fix backslash-escaped characters from OCR (e.g. \* → *, \_ → _)."""
    text = re.sub(r'\\([*_])', r'\1', text)
    text = re.sub(r'\\([\[\]])', r'\1', text)
    return text


def compress_blank_lines(text):
    """Replace 3+ consecutive blank lines with exactly 2."""
    return re.sub(r'\n{3,}', '\n\n', text)


def remove_footer_artifacts(text):
    """Remove page number lines, page header artifacts, and similar noise.

    Matches lines that are:
    - Standalone numbers (page numbers)
    - Lines with patterns like "│ 2027年 │" (table-of-contents artifacts)
    - Lines like "![](_page_N_Figure_N.jpeg)" (image references)
    """
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip bare page numbers (1-3 digits, whole line)
        if re.match(r'^\d{1,3}$', stripped):
            continue
        # Skip TOC table artifacts
        if re.match(r'^[\s│｜┃]*第?\d*\s*[章节]?\s*[\s│｜┃]+', stripped):
            continue
        # Skip page-image references
        if re.match(r'^!\[\]\(_page_\d+_', stripped):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)


def normalize_latex_delimiters(text):
    """Normalize LaTeX inline and display math delimiters."""
    # Some converters use \(...\) or $$...$$ inconsistently
    text = re.sub(r'\\\(', '$', text)
    text = re.sub(r'\\\)', '$', text)
    return text


def clean_markitdown_artifacts(text):
    """Remove common markitdown/marker conversion artifacts."""
    # Remove stray "![]()" that are just blank image references
    text = re.sub(r'!\[\]\(\)', '', text)
    # Remove "<!-- ... -->" comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text


def apply_ocr_fixes(text, fixes):
    """Apply config-driven ocr_fixes (list of [pattern, replacement] pairs)."""
    for pattern, replacement in fixes:
        try:
            text = re.sub(pattern, replacement, text)
        except re.error:
            # Simple string replacement if regex fails
            text = text.replace(pattern, replacement)
    return text


BUILTIN_RULES = [
    ("Strip HTML tags", strip_html_tags),
    ("Decode HTML entities", decode_html_entities),
    ("Normalize punctuation", normalize_punctuation),
    ("Fix escaped chars", fix_escaped_chars),
    ("Normalize LaTeX delimiters", normalize_latex_delimiters),
    ("Remove markitdown artifacts", clean_markitdown_artifacts),
    ("Remove footer/page artifacts", remove_footer_artifacts),
    ("Compress blank lines", compress_blank_lines),
]


def main():
    parser = argparse.ArgumentParser(description="OCR markdown pre-cleaner")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", nargs="?", help="Output markdown file (default: stdout)")
    parser.add_argument("--config", help="Optional config.yaml with ocr_fixes")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()

    changes = []
    for name, rule in BUILTIN_RULES:
        before = text
        text = rule(text)
        if text != before:
            changes.append(name)

    # Apply config-level ocr_fixes if provided
    if args.config:
        import yaml
        with open(args.config, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        fixes = cfg.get('ocr_fixes', [])
        if fixes:
            text = apply_ocr_fixes(text, fixes)
            print(f"  Config fixes applied ({len(fixes)} patterns)", file=sys.stderr)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        sys.stdout.write(text)

    print(f"Rules applied: {', '.join(changes)}", file=sys.stderr)
    print(f"Input: {len(open(args.input).read())} chars → Output: {len(text)} chars", file=sys.stderr)


if __name__ == '__main__':
    main()
