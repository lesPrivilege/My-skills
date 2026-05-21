You are extracting structured question data from OCR'd Chinese textbook markdown. Each chunk contains part of a textbook section. Output a JSON array of question objects conforming to the schema below.

## Context

SOURCE: {source}
SUBJECT: {subject}

## Output Schema

Each element in the JSON array is a question object:

```json
{
  "source": "{source}",
  "subject": "{subject}",
  "chapter": "1 绪论",
  "section": "1.1 数据结构的基本概念",
  "number": 1,
  "type": "choice | review",
  "question": "question text here",
  "options": ["A. option A", "B. option B", "C. option C", "D. option D"],
  "answer": "B",
  "explanation": "explanation text here",
  "tags": {
    "origin": "2019 统考真题",
    "exam_years": ["2019"],
    "frequency": ""
  }
}
```

### Field rules

- **type**: `choice` if the question has A-D options; `review` for all others (calculation, coding, short answer, fill-in)
- **options**: populated only for `choice` type; empty array `[]` for `review`
- **number**: the question number as it appears in the source (e.g., "01", "15", "3"). Used for cross-chunk dedup.
- **chapter**: extracted from the nearest `# 第X章` heading above this chunk. Format: "1 绪论", "2 线性表"
- **section**: section heading if applicable (e.g., "2.3.8 答案与解析"). Empty string `""` if not in a subsection.
- **answer**: the correct answer letter for choice, or the solution text for review. Populate from "答案与解析" sections.
- **explanation**: any explanation/discussion text accompanying the answer.
- **tags.origin**: extract from problem source markers (e.g., "【2019 统考真题】", "【经典题】", "【模拟题】"). Free text, do not normalize.
- **tags.exam_years**: array of years if marked (e.g., "【2019 统考真题】" → ["2019"]). Empty array if none.
- **tags.frequency**: only if explicitly stated. Otherwise empty string. Do not guess.

## Processing Rules

1. **Fix OCR** in question text, options, answers, and explanations:
   - Code: ElemTvpe→ElemType, BiTee→BiTree, SegList→SeqList
   - Repair broken LaTeX ($...$, $$...$$)
   - Fix escaped chars (\* → *, \_ → _)
   - Fix broken Chinese characters where context is clear
   - Preserve code blocks intact (fix indentation, backslash escapes)

2. **Question boundaries**: A new question starts with a numbered marker (`数字.` or `数字．`). Each question+answer pair is ONE object.

3. **Answer from answer sections**: If the chunk contains a "答案与解析" section, extract answer letters and explanations and pair with question numbers.

4. **Skip**: page images (![](_page_...)), TOC artifacts, front/back matter without questions.

## Output Constraints

- Output ONLY the JSON array. No markdown, no explanation, no commentary before/after.
- If no questions are found in this chunk, output an empty array `[]`.
- Ensure valid JSON — double-check commas, brackets, and quotes.
- **Escape any ASCII double quotes (`"`) inside string values as `\"`.** Use Chinese quotation marks (「」 or 『』) instead of ASCII `"` for quoting within explanations.
