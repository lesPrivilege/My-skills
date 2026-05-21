---
name: reading-companion
description: >
  Analyze technical papers, repos, or articles. Produce structured critical notes.
  Prefers provided content over fetching. Trigger on: any arxiv/github/blog URL
  pasted alone or with a request; or when user says read, review, summarize, audit,
  or extract insights from any technical source. Even a bare URL with no instruction
  should trigger this skill.
---

# Reading Companion

Analyze technical content. Produce structured reading notes with critical review.

## Core Principles

1. **Context First** — If content is already in context (pasted text, uploaded file, prior fetch), use it. Do not re-fetch.
2. **Truth Hierarchy** — User-provided file/text > official source > official mirror > secondary summary. When using non-primary sources, mark `Confidence: medium` or `low`.
3. **Minimum Necessary Reading** — Read only enough to answer well. No exhaustive crawling unless requested.
4. **Separate Fact from Inference** — If information is missing or uncertain, say so. Never fill gaps with plausible-sounding guesses.

## Modes

Infer from request. Default: `deep-review`.

- **quick-summary** — 6-10 sentence overview, skip Evidence and Open Questions sections
- **deep-review** — full template, critical analysis

## Source Routing

| Signal | Route |
|--------|-------|
| `arxiv.org`, research PDF, "paper" | paper |
| `github.com`, `gitee.com`, "repo", "project" | repo |
| Blog, docs, article, release notes | article |
| Uploaded file, pasted text, content already in context | local |

If a bare URL is pasted with no instruction, infer the route from the URL and run `deep-review`.

---

## Fetch Rules (all routes)

Only fetch when content is not already available. Use the decoupled **fetch protocol**
(see `fetch` skill): try WebFetch first; if blocked, fall back to
`~/Scripts/fetch-url <url>` (curl → Playwright → user's network).

### Fallback chain

1. **WebFetch** — docs, GitHub raw, arxiv, simple pages
2. **`~/Scripts/fetch-url <url>`** — curl + readability; if JS-challenged, Playwright + readability
3. **Web search** — if steps 1-2 fail (Cloudflare, paywall, empty extract), search `"<article title>" site:36kr.com OR site:sspai.com OR site:datalearner.com OR site:zhihu.com` for third-party coverage

When using third-party sources:
- Set `Confidence: medium` (or `low` if summary is thin)
- Note `来源: 第三方转载，非原文`
- Cross-reference with at least 2 sources if possible

### Limits

- **Max 3 total attempts** per source (across all fallback paths)
- **Max 1 fallback mirror** — try primary, then one alternative. Stop.
- **Abort any single attempt >30 seconds** (60s for PDF downloads)
- **Paywall or login wall** — stop immediately, report
- **Non-primary source** — if content comes from a secondary summary or cache rather than the original, set `Confidence: medium` or `low` and note the actual source

On failure:

```
❌ Fetch failed: {URL}
   Methods tried: WebFetch, curl, Playwright, web search
   Last error: {error}
   → Provide file/text or alternate source.
```

---

## Route: Paper

### Fetch sequence (stop at first success)

1. HTML: `https://arxiv.org/html/{id}`
2. Abstract page: `https://arxiv.org/abs/{id}` + PDF: `https://arxiv.org/pdf/{id}` → convert via `markitdown`
3. Web-search paper title → try alternative host (Semantic Scholar, OpenReview)
4. After 3 total failures → stop and report

### Read priority

1. Abstract
2. Introduction
3. Method / Approach
4. Experiments (main results table + key numbers)
5. Conclusion

Skip: acknowledgements, author bios, appendix (unless user asks).

### Evidence standard

Never cite results without:
- Metric name
- Benchmark name
- Baseline compared against
- Delta / improvement magnitude
- Notable caveats (dataset size, cherry-picked splits, missing error bars)

### Figures and formulas

No multimodal capability. For figures: record `[Figure N: {caption text}]`. If a figure appears critical, flag: `⚠️ Figure N appears central but cannot be interpreted (text-only mode)`. For noisy LaTeX from PDF conversion: clean obvious artifacts, flag uncertain passages with `[formula uncertain]`.

---

## Route: Repo

### Fetch sequence (stop at first success)

1. README raw: `https://raw.githubusercontent.com/{owner}/{repo}/main/README.md` (try `master` if 404)
2. GitHub API: `https://api.github.com/repos/{owner}/{repo}`
3. Gitee mirror: `https://gitee.com/{owner}/{repo}`
4. After 3 total failures → stop and report

### Inspect priority

Do NOT trust README alone. Read in order, stop when sufficient:

1. README
2. Directory tree (1-2 levels)
3. Entrypoint files (e.g., `main.py`, `app.py`, `index.ts`, `src/lib.rs`)
4. Core modules (identify from imports in entrypoint)
5. Dependency files (`requirements.txt`, `pyproject.toml`, `package.json`, `Cargo.toml`)
6. Config files if present

**Max 10 files inspected** unless user requests more.

### Evaluate

Answer these questions:
- What problem does it solve?
- How does it work? (architecture in 2-3 sentences)
- How to run it?
- Production-ready or prototype?
- Main technical risks?
- Maintenance signals? (last commit, open issues, release frequency)

---

## Route: Article / Docs

### Fetch sequence

1. Fetch URL directly
2. Web-search title → try cached/alternative
3. After 2 failures → stop and report

### Extract

- Main thesis
- Key claims with supporting evidence
- Practical implications

### Detect

- Marketing language vs substantive claims
- Unsupported assertions
- Missing tradeoffs
- Outdated assumptions

---

## Route: Local

Use supplied content directly. No fetch.

If document is long: scan structure first, prioritize relevant sections, then summarize.

---

## Output Template

```markdown
# {Title}

- **来源**: {URL or "uploaded file" or "pasted text"}
- **日期**: {publication date if known}
- **作者/机构**: {authors or organisation}
- **类型**: paper | repo | article | local
- **置信度**: high | medium | low
- **模式**: quick-summary | deep-review

## 核心问题

{1-3 sentences. What gap or limitation does this work address?}

## 核心方案

{Numbered list. Each item: mechanism name + 1-2 sentence explanation.}

## 证据

{Key results with metric, benchmark, baseline, delta.
For repos: stars, commit frequency, adoption signals.
For articles: cited data or sources.
Skip if no quantitative evidence exists.}

## 风险与弱点

{Bulleted with ⚠️ prefix. Hidden assumptions, unacknowledged limitations,
methodological concerns, engineering risks.}

## 待验证问题

{What you'd want to verify, test, or investigate further before trusting this work.
Frame as questions, not judgments.}
```

For `quick-summary` mode: output only Core Problem + Core Approach + a 1-sentence risk note. Skip other sections.

---

## Confidence Follow-up

When output confidence is `medium` or `low`, append at the end:

```
→ 完整分析需要全文。可提供 PDF、粘贴原文、或指定本地文件路径。
```

This reminds the user the analysis can be deepened with better source material.

## Language

Output in Chinese with English technical terms preserved. Specifically:

- Section headers in Chinese (核心问题, 核心方案, 证据, 风险与弱点, 待验证问题)
- Explanatory prose in Chinese
- Technical terms, proper nouns, method names, benchmark names, metric names in English as-is (e.g., "LAnR", "HotpotQA", "Exact Match", "[PRED] token", "MLP control head")
- Code snippets and formulas in original form

This matches natural bilingual technical reading style: Chinese for comprehension flow, English for precision where translation would lose meaning.

## Behaviour Rules

- Be analytical, not promotional
- Prefer precise claims over broad praise
- If information is missing, say so — do not infer
- If request is simple, compress output
- If request is complex, go deep automatically
- Never hallucinate benchmark numbers or code understanding from README alone
- Never pretend to read content that was inaccessible

## Save Behaviour

**Only save if user explicitly requests.** Do not auto-create files or directories.

When saving:
- Path: `<obsidian-vault>/reading-notes/{YYYY-MM-DD}_{slug}.md`
- Create directory if needed
- Confirm path to user after save
