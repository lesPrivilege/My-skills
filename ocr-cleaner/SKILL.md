---
name: ocr-cleaner
description: >
  Clean and normalize markdown files converted from scanned textbook PDFs
  (via markitdown or marker). 5-phase pipeline: Phase 1 regex pre-clean,
  Phase 2 heading-based chunking, Phase 3 subagent LLM extraction → JSON,
  Phase 4 subagent answer/exclamation fix (LLM-inferred), Phase 5 merge.
  Works with any structured textbook/guide — CS, math, language, medicine, etc.
  Not limited to exam-prep. Trigger on: "ocr clean", "教辅清洗", "预处理教材",
  "清洗OCR", or uploading a .md with OCR artifacts (HTML tag remnants, broken
  LaTeX, escaped chars, merged question lines, code block noise).
---

# OCR Cleaner

Pipeline: `source PDF → markitdown/marker → [ocr-cleaner] → questions.json`

The three phases progressively transform raw OCR'd markdown into clean,
structured question data. Phase 3 (LLM) directly outputs JSON — no
intermediate MD step, no regex re-parsing.

## Flow

1. **Phase 1** (`python clean_rules.py input.md input_cleaned.md`)
   — regex-based pre-clean
   - Strips HTML tags, normalizes punctuation, compresses blank lines
   - Decodes HTML entities, removes page-number/header artifacts
   - Fixes escaped chars (`\*` → `*`, `\_` → `_`)
   - Applies per-subject ocr_fixes from config.yaml if available

2. **Phase 2** (`python chunk.py input_cleaned.md`)
   — heading-based chunking
   - Splits by `#` / `##` heading boundaries
   - Each chunk 1500–3000 characters
   - Small chunks merged upward
   - Output: `chunks/001_第1章_绪论.md`, `chunks/002_...`

3. **Phase 3** — subagent LLM extraction → per-chapter JSON
   - Spawn subagents (one per chapter or per chunk group) with a structured JSON-extraction prompt
   - Subagent reads chunk files, outputs JSON array of question objects (v2 schema below)
   - Output: per-chapter JSON files (e.g. `wangdao-ch01.json`, `wangdao-ch02.json`)

4. **Phase 4** — subagent answer fix (optional, recommended)
   - Asks for each per-chapter JSON where `answer` or `explanation` is missing
   - Spawn subagents to infer correct answers from question context (LLM reasoning)
   - Only fills `answer` (from existing options for choice) and `explanation`
   - Does NOT modify question text, options, or id
   - Marks fixed questions with `metadata.fixed: true`
   - See `exam-prep-bank-fix` skill for the detailed fix prompt template

5. **Phase 5** — merge per-chapter JSONs → final questions.json
   - Concatenate arrays, sort by id, validate schema
   - Output: `{source}_questions.json` in the original file's directory

## Output Schema (v2)

```json
{
  "id": "wangdao-ds-ch01-001",
  "source": "wangdao-ds",
  "subject": "data-structure",
  "chapter": "1 绪论",
  "section": "1.1 数据结构的基本概念",
  "number": 1,
  "type": "choice | review",
  "question": "...",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "B",
  "explanation": "...",
  "solution_path": null,
  "tags": {
    "origin": "2019 统考真题",
    "exam_years": ["2019"],
    "frequency": "",
    "image": null
  }
}
```

Key points:
- `type` only `choice` (has A-D options) or `review` (all else)
- `options` empty array for review questions
- `tags` for metadata — ALL fields optional. For exam-prep: origin, exam_years, frequency.
  For general textbooks: leave tags empty. Populated by LLM from text markers if present.
- `id` auto-generated as `{source}-ch{NN}-{NNN}`
- No `status`/`attempts` — those are app-level runtime state

## Downstream Consumption

This schema is consumed by **Mnemos** (`questionParser.js`). The mapping:

| ocr-cleaner field | Mnemos field | Note |
|-------------------|-------------|------|
| `id` | `id` | 透傳 |
| `subject` | `subject` | 透傳 |
| `chapter` | `chapter` | normalized (e.g. `1 绪论` → `第1章 绪论`) |
| `type` | `type` | 只收 `choice` / `review` |
| `question`, `options`, `answer`, `explanation` | same | 透傳 |
| `solution_path` | `solution_path` | 也從 `tags.image` 自動提取 |
| `tags.origin`, `tags.exam_years`, `tags.frequency` | `metadata.origin`, `metadata.exam_years`, `metadata.frequency` | 保留，不丟失 |
| `number` | `metadata.number` | 保留，不丟失 |

Full pipeline:
```
PDF → markitdown/marker → dirty MD → ocr-cleaner → questions.json → Mnemos import → usable quiz
```

## Config Support

If a `config.yaml` exists alongside the input file, Phase 1 reads its
`ocr_fixes` list and applies those regex substitutions.

## Format Adaptation

Phase 2 chunking assumes `#`/`##` heading structure. For different formats:

| Source type | Heading pattern | Adapt chunk-size | Note |
|------------|----------------|-----------------|------|
| Chinese exam-prep (王道等) | `## 一、单项选择题`, `## 第1章 绪论` | 2500 | 預設，正常 chunk |
| English textbook | `## Chapter 1`, `## Exercises` | 3000 | English needs more chars |
| Language textbook | `## 第1課`, `## 練習問題` | 2000 | Shorter chunks for grammar |
| Medical/nursing | `## 第一章 解剖学`, `## A型题` | 2500 | Same as CS exam-prep |
| Flashcards / notes | `## Topic` (no exercises) | Phase 3 only | No choice type, all `review` |
| Unstructured / article | No clear headings | Skip Phase 2 | Subagent reads whole file |

For Phase 3 extraction, adapt the subagent prompt to the content type:
- **Exam-prep**: Extract `choice` + `review`, populate `tags.origin/exam_years` from text markers
- **General textbook**: All `review` type, tags left empty, focus on Q&A pairs
- **Language learning**: `review` type, preserve original + translation in `explanation`

## Chunk Boundary Handling

Phase 2 splits at heading boundaries, which can separate questions from answers
(when answers are in a different section). Phase 3 subagent should handle this:
- Leave `answer` empty if not in chunk — Phase 4 fix will handle it
- OCR-damaged questions (truncated code, missing options) are flagged in the
  subagent output report — do a second pass with the full context

## Practical Lessons (from 王道数据结构 2027 run)

| Issue | How to handle |
|-------|--------------|
| Chapters with missing H1 headings (OCR loss) | Search by content patterns (`^## 树`, `^## 图`) rather than strict `^# 第X章` |
| Chinese quotation marks in JSON values (`"左根右"`) | Replace with `「」` before JSON parse, or use CJK-aware escape |
| Questions in table-cell format | Phase 3 subagent handles naturally (unlike regex) |
| Answers in separate "答案与解析" section from questions | Leave answer empty in extraction — Phase 4 infers from question context |
| Very large chunks (>100K chars) | Sub-split by `## 一、单项选择题` / `## 二、综合应用题` boundaries

## Edge Cases

- **Non-teaching materials**: Phase 1 only (articles, papers). Phase 2/3 skipped.
- **Questions spanning chunks**: merge output by (chapter, number).
  Question text from one chunk, answer from another — combined.
- **No questions found**: Phase 3 returns empty array, validate.py produces
  empty output.
- **Missing metadata (exam_years, frequency)**: LLM leaves empty; validate.py
  fills defaults.
