#!/usr/bin/env python3
"""Phase 2: heading-based chunking for OCR'd textbook markdown.

Splits markdown by # and ## headings into chunks of 1500–3000 characters.
Small chunks are merged upward. Outputs numbered files to chunks/ directory.

Usage:
    python chunk.py input.md [--chunk-size 2500] [--outdir chunks]
"""

import re
import os
import sys
import argparse


def find_heading_boundaries(lines):
    """Find line indices where # or ## headings begin.

    Returns list of (line_idx, heading_text) tuples.
    Skips headings inside code blocks.
    """
    boundaries = []
    in_code_block = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        m = re.match(r'^(#{1,2})\s+(.+)$', stripped)
        if m:
            boundaries.append((i, stripped))
    return boundaries


def build_chunks(lines, boundaries, target_size=2500):
    """Group lines into chunks based on heading boundaries.

    Each chunk starts at a heading boundary. If a chunk is smaller than
    half of target_size, it's merged into the previous chunk.
    """
    if not boundaries:
        # No headings found: whole file as one chunk
        return [lines]

    chunks = []
    for bi, (start_idx, heading) in enumerate(boundaries):
        end_idx = boundaries[bi + 1][0] if bi + 1 < len(boundaries) else len(lines)
        chunk_lines = lines[start_idx:end_idx]
        chunk_text = '\n'.join(chunk_lines)
        chunks.append({
            'heading': heading,
            'text': chunk_text,
            'lines': chunk_lines,
            'size': len(chunk_text),
        })

    # Merge small chunks upward
    merged = []
    for chunk in chunks:
        if merged and chunk['size'] < target_size // 2:
            merged[-1]['text'] += '\n' + chunk['text']
            merged[-1]['lines'].extend(chunk['lines'])
            merged[-1]['size'] = len(merged[-1]['text'])
            merged[-1]['heading'] += ' | ' + chunk['heading']
        else:
            merged.append(chunk)

    # Sub-split oversized chunks
    final = []
    for chunk in merged:
        if chunk['size'] <= target_size * 2:
            final.append(chunk['lines'])
            continue
        sub_chunks = sub_split_chunk(chunk['lines'], chunk['heading'], target_size)
        final.extend(sub_chunks)

    return final


def sub_split_chunk(lines, heading, target_size):
    """Split an oversized chunk into smaller pieces.

    First tries ### sub-headings, then falls back to paragraph breaks.
    """
    # Find ### sub-heading positions (that are not inside code blocks)
    sub_boundaries = []
    in_code = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r'^###\s+', stripped):
            # Check this isn't the very first heading (already the parent heading)
            if i == 0 and re.match(r'^#{1,2}\s+', stripped):
                continue
            sub_boundaries.append(i)

    if sub_boundaries:
        # Split at ### boundaries
        chunks = []
        for bi, start in enumerate(sub_boundaries):
            end = sub_boundaries[bi + 1] if bi + 1 < len(sub_boundaries) else len(lines)
            chunk_lines = lines[start:end]
            chunks.append(chunk_lines)
        # If there's content before the first ###, merge it into the first chunk
        if sub_boundaries[0] > 0:
            for i in range(sub_boundaries[0] - 1, -1, -1):
                if lines[i].strip():
                    chunks[0] = [lines[i]] + chunks[0]
        # Merge any still-oversized chunks at paragraph breaks
        final = []
        for chunk_lines in chunks:
            text = ''.join(chunk_lines)
            if len(text) <= target_size * 2:
                final.append(chunk_lines)
            else:
                final.extend(_split_by_paragraph(chunk_lines, target_size))
        return final

    # Fallback: split by paragraph breaks
    return _split_by_paragraph(lines, target_size)


def _split_by_paragraph(lines, target_size):
    """Split lines at paragraph boundaries (double newlines) to roughly target_size."""
    # Group lines into paragraphs (separated by blank lines)
    paragraphs = []
    current_para = []
    for line in lines:
        if line.strip() == '' and current_para:
            paragraphs.append(current_para)
            current_para = []
        elif line.strip():
            current_para.append(line)
    if current_para:
        paragraphs.append(current_para)

    # Merge paragraphs into chunks at target_size boundaries
    chunks = []
    current = []
    current_size = 0
    for para in paragraphs:
        para_text = ''.join(para)
        para_size = len(para_text)
        if current_size + para_size > target_size and current:
            chunks.append(current)
            current = []
            current_size = 0
        current.extend(para)
        current_size += para_size
    if current:
        chunks.append(current)

    return chunks if chunks else [lines]


def heading_to_filename(heading):
    """Convert a heading like '# 第**1**章 绪论' to a filename-safe slug."""
    # Remove markdown bold/italic markers
    slug = re.sub(r'\*+', '', heading)
    # Remove leading # and spaces
    slug = re.sub(r'^#+\s*', '', slug)
    # Remove special characters for filename safety, keep CJK
    slug = re.sub(r'[^\w一-鿿\s-]', '', slug)
    slug = slug.strip()
    # Truncate
    if len(slug) > 40:
        slug = slug[:40]
    return slug


def main():
    parser = argparse.ArgumentParser(description="Heading-based markdown chunker")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("--chunk-size", type=int, default=2500,
                        help="Target chunk size in characters (default: 2500)")
    parser.add_argument("--outdir", default="chunks",
                        help="Output directory (default: chunks)")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    boundaries = find_heading_boundaries(lines)
    if not boundaries:
        print("No headings found, treating entire file as one chunk.", file=sys.stderr)
        chunks = [lines]
    else:
        print(f"Found {len(boundaries)} heading boundaries", file=sys.stderr)
        chunks = build_chunks(lines, boundaries, args.chunk_size)

    os.makedirs(args.outdir, exist_ok=True)

    for i, chunk_lines in enumerate(chunks):
        chunk_text = ''.join(chunk_lines)
        # Extract first heading for filename
        first_line = chunk_lines[0].strip() if chunk_lines else f"chunk-{i+1:03d}"
        slug = heading_to_filename(first_line)
        if not slug:
            slug = f"chunk-{i+1:03d}"
        filename = f"{i+1:03d}_{slug}.md"
        path = os.path.join(args.outdir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(chunk_text)
        print(f"  {filename} ({len(chunk_text)} chars)", file=sys.stderr)

    print(f"\n{len(chunks)} chunks → {args.outdir}/", file=sys.stderr)


if __name__ == '__main__':
    main()
