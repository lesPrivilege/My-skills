---
name: md-cleaner
description: >
  Clean and normalize markdown files converted from ebooks (Calibre/zlibrary exports).
  Use this skill whenever the user uploads a .md file and asks to "clean", "wash",
  "normalize", "strip ads", "tidy up", or "格式清洗" — or when an uploaded .md
  contains telltale signs of ebook conversion artifacts (Calibre metadata headers,
  zlibrary download watermarks, inline app ads, broken static_images references).
  Also trigger when the user says "clean this markdown", "去广告", "清理格式",
  or shares a markdown file that visibly contains ebook conversion noise.
---

# MD Cleaner

Clean markdown files exported from ebook tools (primarily Calibre → zlibrary pipeline).
The goal: strip conversion artifacts and ads, normalize structure, preserve all editorial content verbatim.

## When to Use

The input is a `.md` file (or text block) showing one or more of these symptoms:

- Calibre metadata block (`**Title:**`, `**Authors:** Kovid Goyal`, `**Identifier:**`, etc.)
- zlibrary download watermark lines (`This article was downloaded by [zlibrary]...`)
- App advertisement blocks (e.g., "优质App推荐", Duolingo/欧路词典/英阅阅读器 ads)
- Internal `.html` navigation links (`* [Section](hexhash.html)`)
- Broken local image references (`![...](static_images/...)`)
- HTML entities in text (`&AMP;`, `&amp;`, etc.)
- `![None](...)` placeholder images

## Processing Rules

Apply these transformations in order. **Never alter article body text, bylines, or editorial content.**

### 1. Remove Calibre metadata header

Strip everything from the start of the file through the `**Identifier:**` line (inclusive), plus any immediately following blank lines. This block typically looks like:

```
**Title:** ...
**Authors:** Kovid Goyal
**Language:** en
**Description:** Articles in this issue:
...
**Identifier:** xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 2. Remove advertisement blocks

Delete the entire "优质App推荐" section and similar ad blocks. Pattern: a heading (any level) containing promotional language, followed by image-link + description lines for apps. Remove from the heading through the last ad entry (inclusive).

Known ad patterns:
- `# 优质App推荐` followed by `[![Image N](static_images/...)](...) AppName - description [点击下载](...)`
- Any similar promotional block not part of the publication's editorial content

### 3. Remove download watermarks

Delete every line matching either pattern:
```
This article was downloaded by [zlibrary](https://z-lib.io) from <https://...>
This article was downloaded by **calibre** from <https://...>
```
Also remove the blank line immediately preceding it if present.

### 4. Remove internal HTML navigation links

Delete lines that are list items or blockquotes linking to internal `.html` files:

**Standalone list items:**
```
* [Section Name](hexstring.html)
* [Article Title](index_split_001.html#filepos1234)
* [Features](feed_0/index_u16.html)
```

**Pipe-separated navigation bars:**
```
| [Next section](../feed_1/index_u12.html) | [Main menu](../index_u4.html) |
```

Patterns removed:
- `* [any text](hex{20,}.html)` — hex-hash Calibre internal cross-references
- `* [any text](index_split_NNN.html...)` — New Yorker EPUB TOC entries
- `* [any text](feed_N/index_uNN.html)` / `* [any text](article_N/index.html)` — Atlantic/Wired Calibre TOC
- `| ... `.html` links ... |` — pipe-separated navigation bars
- `> > > [text](index_split_...)` — blockquote TOC entries
- Consecutive `---` horizontal rules (collapse to single)

Also remove section-level table-of-contents blocks that consist entirely of such links (including their preceding heading if the heading is just a section name duplicated from the article title below).

**Inline cross-references:** Convert `[text](../../feed_N/article_N/index_uN.html)` → `text` (strip broken Calibre href, keep editorial link text).

### 5. Remove cover and masthead images

Delete lines matching:
```
![Cover](static_images/cover.jpg)
![](static_images/mastheadImage.jpg)
```
And the date line that follows the masthead if it stands alone (e.g., `January 4th 2025` on its own line between removed elements).

### 6. Normalize broken image references

For `![None](static_images/...)` — remove the entire line (these are placeholder images with no meaningful alt text, typically data tables rendered as images).

For other `![alt text](static_images/...)` — **keep** them but add a comment that the image path is local-only:
```
![alt text](static_images/...)  <!-- local image, may not render -->
```
This preserves editorial images (photos, charts) with their captions while flagging that the paths won't resolve outside the ebook bundle.

### 7. Decode HTML entities

Replace common HTML entities with their plain-text equivalents:
- `&AMP;` → `&`
- `&amp;` → `&`
- `&lt;` → `<`
- `&gt;` → `>`
- `&nbsp;` → ` `
- `&quot;` → `"`

### 8. Deduplicate section headers

When a section name appears as both a standalone line (from the ToC) and as a heading (`# ...`) immediately after, remove the standalone duplicate. Example:

```
The world this week       ← remove (ToC residue)

# The world this week    ← keep (actual heading)
```

Pattern: a plain-text line whose content matches the `# heading` that follows within 1-2 lines.

### 9. Collapse excessive blank lines

Replace 3+ consecutive blank lines with exactly 2.

### 10. Preserve article separators

The category-pipe-subcategory lines (e.g., `Leaders | Northern lights`, `Culture | Strange and familiar places`) serve as article delimiters. **Keep these** — they provide structural information about section and article identity.

## Execution

1. Read the uploaded `.md` file
2. Write a Python script applying the rules above (regex-based, sequential passes)
3. Save the cleaned output to `{original_filename_without_ext}_cleaned.md` (or overwrite in place if same path given)
4. Report: number of lines removed, categories of removals (ads, watermarks, nav links, metadata, etc.), and any anomalies encountered
5. Present the cleaned file to the user

## Script Location

The cleaning script lives at `~/.claude/skills/md-cleaner/clean.py`. Read it before running if it already exists; create it if it doesn't.

## Edge Cases

- **Multiple articles in one file**: Common for magazine exports. Each article has its own watermark line — remove all of them.
- **Non-English ad blocks**: Ad blocks may be in Chinese or mixed language. Match by structural pattern (image-link + download link), not language.
- **Legitimate external links**: Do NOT remove `[text](https://...)` links within article body text. Only remove internal `.html` hex-hash links and zlibrary watermark links.
- **Editorial images with captions**: Lines like `![Thousands of demonstrators...](static_images/...)` are editorial photo captions. Keep these (with the local-image comment).
