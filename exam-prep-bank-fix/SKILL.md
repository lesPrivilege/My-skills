---
name: exam-prep-bank-fix
description: >
  Fix questions.json entries with missing answers, OCR noise, or broken parser output.
  Use when: questions have empty answer fields, garbled text from OCR extraction,
  or need answer completion via subagent.
---

# Exam Prep Bank Fix

Repair questions.json entries with missing answers or OCR corruption.

## When to Use

- `questions.json` has entries where `answer` is empty string or null
- Question text contains OCR artifacts (`<b>` tags, broken Unicode, garbled math)
- Options are missing or malformed
- Need to fill `explanation` field for existing questions

## Input

Read `questions.json` from `bank/{subject}/` directory. Filter entries where `answer` is empty or null.

## Pipeline

This skill operates as **Phase 4** of the `ocr-cleaner` pipeline — after Phase 3 (LLM extraction from chunks) but before Phase 5 (merge). The fix preserves all existing fields including `metadata`.

Full pipeline:
```
PDF → markitdown/marker → dirty MD
  → [ocr-cleaner Phase 1-3] → per-chapter JSON (some answers empty)
  → [exam-prep-bank-fix Phase 4] → fixed per-chapter JSON (answers filled)
  → [ocr-cleaner Phase 5] → merged questions.json → Mnemos
```

**Why Phase 4 runs before merge**: Phase 3 extracts questions from OCR chunks. Questions and their answers often land in different chunks (text and answer sections). Phase 4 fills these gaps using LLM reasoning on individual questions, then Phase 5 merges the fixed per-chapter files.

## Workflow

### Step 1: Classify each question

| Category | Condition | Action |
|----------|-----------|--------|
| OCR-heavy | question contains HTML tags, broken chars, or <5 readable Chinese chars | Full repair: fix OCR + infer answer |
| Parser-broken | `options` array is empty but type is `choice` | Skip options, mark `needs_review: true` |
| Missing answer only | question/options look clean | Just infer answer from context |

### Step 2: Repair via subagent

For each question needing repair, spawn a subagent with this prompt template:

```
You are a Chinese CS exam question repair assistant.

Given a question object, fix OCR noise and infer the answer.

RULES:
1. Fix OCR noise ONLY — do NOT rewrite or paraphrase the question
2. For choice questions: answer MUST be one of the existing options (A/B/C/D)
3. If options are missing or question is too garbled, set needs_review: true
4. Preserve original Chinese technical terms exactly
5. explanation should be concise (1-2 sentences max)

OUTPUT JSON:
{
  "question": "cleaned question text",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "A",
  "explanation": "brief explanation",
  "confidence": 0.0-1.0,
  "changes": ["what was fixed"],
  "needs_review": false
}
```

### Step 3: Merge results

For each question, merge subagent output:
- Always preserve original `id`, `subject`, `chapter`, `type`, `metadata`
- Update `question` only if OCR was fixed and confidence >= 0.9
- Update `answer` only if confidence >= 0.7
- Set `metadata.fixed: true` for any modified question
- Add `metadata.confidence`, `metadata.changes`, `metadata.needs_review`
- For confidence < 0.7: update nothing, keep original empty fields

### Step 5: Output

Write fixed questions back to `questions.json`. Generate report:
- Total processed
- Fixed (high confidence)
- Flagged for review (low confidence or needs_review)
- Unfixable (no API response or parse error)

## Confidence Thresholds

| Confidence | Action |
|------------|--------|
| >= 0.9 | Auto-apply, no review needed |
| 0.7 - 0.9 | Apply but mark `confidence` in output |
| < 0.7 | Mark `needs_review: true`, do NOT apply answer |

## Edge Cases

- **No options**: If `options` is empty array, set `needs_review: true` and skip answer inference
- **Multiple correct answers**: Some questions have "all of the above" — handle by checking if any option contains "以上" or "都"
- **OCR in options**: Clean OCR noise in options too, not just question text
- **Calculation questions**: For `type: "calculation"`, only fix OCR in question text, leave answer for manual entry

## Script Location

A local knowledge-base fix script exists at `~/.claude/skills/exam-prep-bank-fix/fix.js` for subjects with known answer patterns. It uses a curated answer dictionary, not an LLM. Only use it for well-known patterns (e.g. computer-organization questions with known answers). For general repair, use the subagent approach above.
