#!/usr/bin/env python3
"""Phase 3 merge: validate, dedup, merge chunk-level JSON into questions.json.

Usage:
    python validate.py <cleaned-dir> <output.json> [--source <source>]

Reads per-chunk JSON files from <cleaned-dir> (each output by claude -p),
validates each question object against the v2 schema, merges by chapter+number
across chunks, generates IDs, and writes the final questions.json.

Also accepts per-chunk JSON via stdin (single line per chunk) with --stdin.
"""

import json
import os
import re
import sys
import argparse


# ── ID generation ────────────────────────────────────────────────────

def chapter_num_from_str(chapter_str):
    """Extract leading number from '2 线性表' → 2."""
    m = re.match(r'(\d+)', str(chapter_str).strip())
    return int(m.group(1)) if m else 0


def generate_id(source, chapter_str, number):
    """Generate globally unique ID: {source}-ch{NN}-{NNN}."""
    ch = chapter_num_from_str(chapter_str)
    return f"{source}-ch{ch:02d}-{number:03d}"


# ── Schema validation ────────────────────────────────────────────────

REQUIRED_FIELDS = ['source', 'subject', 'chapter', 'type', 'question', 'options', 'answer']
OPTIONAL_FIELDS = ['section', 'explanation', 'number', 'tags']
VALID_TYPES = {'choice', 'review'}


def validate_question(q, idx, filename):
    """Validate a single question object. Returns list of error messages."""
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in q or q[field] is None:
            errors.append(f"q[{idx}] missing required field: {field}")

    if 'type' in q and q['type'] not in VALID_TYPES:
        errors.append(f"q[{idx}] invalid type '{q['type']}'; must be one of {VALID_TYPES}")

    if q.get('type') == 'choice' and not q.get('options'):
        errors.append(f"q[{idx}] type=choice but options is empty")

    if q.get('type') == 'review' and q.get('options'):
        # Warn but don't fail — LLM might include options for a non-choice by mistake
        pass

    if not q.get('question', '').strip():
        errors.append(f"q[{idx}] question text is empty")

    if 'id' in q:
        errors.append(f"q[{idx}] id field should not be in LLM output; will be auto-generated")

    return errors


# ── Cross-chunk merge ───────────────────────────────────────────────

def merge_key(q):
    """Generate merge key from chapter + number (cross-chunk dedup)."""
    ch = chapter_num_from_str(q.get('chapter', ''))
    num = q.get('number', 0)
    # If number is missing, use a hash of the question text
    if not num:
        text = q.get('question', '')[:80]
        return f"ch{ch:02d}:text:{text}"
    return f"ch{ch:02d}:q{int(num):03d}"


def merge_questions(existing, incoming):
    """Merge two question objects for the same question.

    Strategy: prefer non-empty fields. This handles:
    - Question text in chunk A, answer in chunk B
    - More complete explanation in one chunk
    """
    merged = dict(existing)
    for key, value in incoming.items():
        if key == 'id':
            continue
        if not existing.get(key) or (isinstance(value, (list, dict)) and value):
            merged[key] = value
        elif isinstance(value, str) and value.strip():
            merged[key] = value
    # Merge tags specially
    merged_tags = dict(existing.get('tags', {}))
    incoming_tags = incoming.get('tags', {})
    for tag_key in merged_tags.keys() | incoming_tags.keys():
        existing_val = merged_tags.get(tag_key, '')
        incoming_val = incoming_tags.get(tag_key, '')
        if isinstance(existing_val, list) and isinstance(incoming_val, list):
            merged_tags[tag_key] = list(set(existing_val + incoming_val))
        elif not existing_val and incoming_val:
            merged_tags[tag_key] = incoming_val
    merged['tags'] = merged_tags
    return merged


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validate, dedup, and merge chunk JSON into questions.json")
    parser.add_argument("cleaned_dir", help="Directory with per-chunk JSON files from Phase 3")
    parser.add_argument("output", help="Output questions.json path")
    parser.add_argument("--source", help="Override source field if missing from chunk output")
    args = parser.parse_args()

    if not os.path.isdir(args.cleaned_dir):
        print(f"Error: directory not found: {args.cleaned_dir}", file=sys.stderr)
        sys.exit(1)

    # Read all chunk JSON files
    all_questions = []
    file_errors = []

    for fname in sorted(os.listdir(args.cleaned_dir)):
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(args.cleaned_dir, fname)
        raw = open(fpath, 'r', encoding='utf-8').read()
        # Strip ```json / ``` code fences that claude -p may add
        raw = re.sub(r'^```(?:json)?\s*\n?', '', raw, flags=re.MULTILINE)
        raw = re.sub(r'\n```\s*$', '', raw)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            # Try fallback: replace ASCII " inside CJK text with Chinese quotes
            raw_fixed = re.sub(
                r'(?<=[一-鿿　-〿＀-￯])"'
                r'(?=[一-鿿　-〿＀-￯])',
                '“', raw  # left double quotation mark
            )
            raw_fixed = re.sub(
                r'(?<=[一-鿿　-〿＀-￯])"'
                r'(?=[，。、；：）\]\)])',
                '”', raw_fixed  # right double quotation mark
            )
            try:
                data = json.loads(raw_fixed)
                file_errors.append(f"{fname}: recovered from unescaped quotes in explanation text")
            except json.JSONDecodeError as e2:
                file_errors.append(f"{fname}: JSON parse error: {e} (fallback also failed)")
                continue

        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get('questions', data.get('items', []))
        else:
            file_errors.append(f"{fname}: unexpected JSON structure (not array or object)")
            continue

        for idx, q in enumerate(items):
            errs = validate_question(q, idx, fname)
            if errs:
                file_errors.append(f"{fname} q[{idx}]: {'; '.join(errs)}")
                continue
            all_questions.append(q)

    # Report validation errors
    if file_errors:
        print(f"Validation warnings ({len(file_errors)}):", file=sys.stderr)
        for err in file_errors[:20]:
            print(f"  {err}", file=sys.stderr)
        if len(file_errors) > 20:
            print(f"  ... and {len(file_errors) - 20} more", file=sys.stderr)

    # Cross-chunk merge (same question from different chunks)
    merged_map = {}
    for q in all_questions:
        key = merge_key(q)
        if key in merged_map:
            merged_map[key] = merge_questions(merged_map[key], q)
        else:
            merged_map[key] = dict(q)

    # Generate IDs and build final list
    final = []
    seen_ids = set()
    duplicate_ids = 0

    for q in merged_map.values():
        qid = generate_id(q.get('source', args.source or ''), q.get('chapter', ''), q.get('number', 0))
        # Ensure no duplicate IDs (fallback: append counter)
        if qid in seen_ids:
            counter = 2
            while f"{qid}-{counter}" in seen_ids:
                counter += 1
            qid = f"{qid}-{counter}"
        seen_ids.add(qid)
        q['id'] = qid

        # Ensure all optional fields exist
        q.setdefault('section', '')
        q.setdefault('explanation', '')
        q.setdefault('tags', {})
        q['tags'].setdefault('origin', '')
        q['tags'].setdefault('exam_years', [])
        q['tags'].setdefault('frequency', '')

        final.append(q)

    # Sort by source, chapter, number
    def sort_key(q):
        ch = chapter_num_from_str(q.get('chapter', '999'))
        return (q.get('source', ''), ch, q.get('number', 0))
    final.sort(key=sort_key)

    # Write output
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"Questions: {len(final)} (from {len(all_questions)} raw, "
          f"{len(merged_map)} unique after merge, {duplicate_ids} id duplicates resolved)",
          file=sys.stderr)
    print(f"Output: {args.output}", file=sys.stderr)
    print(f"Validation: {len(file_errors)} warnings", file=sys.stderr)


if __name__ == '__main__':
    main()
