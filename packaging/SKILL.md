---
name: packaging
description: >
  Transform a working paper into platform-specific output. Use this skill whenever
  the user wants to publish, package, format, or distribute a working paper
  (working-papers/{slug}.md) to one or more target platforms. Triggers include:
  "package this", "publish to blog", "make a thread",
  "newsletter version", "write up for Bluesky/Twitter",
  or any mention of converting a working paper into a distributable format.
  Also trigger when the user says "下游", "打包", "發佈", "推文串", or references
  the packaging/distribution layer of the pipeline.
---

# Packaging

Transform a single `working-papers/{slug}.md` into one or more platform-specific outputs.

## Position in Pipeline

```
archive (upstream) → paper-mill (midstream) → **packaging (downstream)**
```

Input: a working paper produced by paper-mill Mode B. The file lives at
`working-papers/{slug}.md` and follows a fixed structure:

```
# {Title}
## 主张 (Thesis)
## 论据链 (Argument chain)
## 论证结构图 (Structure diagram — optional)
## 已知弱点 (Known weaknesses)
## 待补充 (Gaps to fill)
```

All headers are in Simplified Chinese (paper-mill Mode B output language).
The bottom provenance line (`*生成：paper-mill Mode B*`) provides meta info
— no separate `## Meta` section needed.

If the input file doesn't match this structure, stop and tell the user — don't guess.

## Target Platforms

| Platform | ID | Output | Key constraint |
|---|---|---|---|
| Long-form blog | `blog` | `published/{slug}/blog.md` | Full argument; keep weaknesses section as intellectual honesty signal |
| Social thread | `thread` | `published/{slug}/thread.md` | Thesis + strongest single evidence chain; ≤15 posts; each post ≤280 chars (CJK ~140 chars) |
| Newsletter | `newsletter` | `published/{slug}/newsletter.md` | Conversational register; thesis + evidence + one weakness as "honest caveat" |

The user picks one or more platforms per invocation. If none specified, ask.

## Extraction Logic

Each platform extracts a different slice from the same working paper. The core
principle: **never fabricate content beyond what the working paper contains**. You
are a packager, not a co-author. Rewrite for register and density, but all claims
must trace back to the source document.

### blog

Full-fidelity rendering. Preserve the entire argument chain and the weaknesses
section. Restructure for readability:

1. Open with the thesis as a one-paragraph hook (no academic hedging).
2. Walk through the argument chain — each node becomes a section.
3. Include the "known weaknesses" as a dedicated section near the end (label it
   something like "Where this breaks down" — the honesty is a feature, not a bug).
4. Close with the implications or open questions from 待补充.
5. **Colophon (文末固定，不省略)**: append a one-paragraph production note:

   ```
   ---
   *本文由日常阅读笔记经 LLM 辅助组装，作者审核论证结构但未逐句校对事实细节。如发现错误欢迎指出。*
   ```

   This is not a disclaimer — it's a colophon (版权页/工艺说明). Fixed text,
   no customization per post. Placed after the closing paragraph, before any
   comment/discussion callout.

Tone: direct, technical but accessible. Write for a reader who has domain context
but hasn't seen this specific argument. No bullet lists in the body — prose
paragraphs. Code blocks and diagrams are fine.

Output metadata header:

```yaml
---
title: {title}
date: {today YYYY-MM-DD}
source: working-papers/{slug}.md
status: draft
---
```

### thread

Maximum compression. The goal is a self-contained social media thread that makes
the reader want to read the full blog post.

Structure:
- Post 1: Thesis statement — provocative, standalone.
- Posts 2–N-1: One supporting point per post. Pick the strongest evidence nodes
  from the argument chain. Each post must be independently comprehensible.
- Final post: Link placeholder `[→ full version: {URL}]` + one-line restatement.

Constraints:
- Max 15 posts total. Prefer 5–8.
- Each post ≤140 CJK characters (count actual CJK, not a "budget").
  Post-generation: measure every post. If any exceeds 140 chars, rewrite
  that post more tightly before finalizing. The `1/N`, `2/N` prefix counts
  toward the limit — budget accordingly.
- Number each post: `1/N`, `2/N`, etc.
- No hashtags unless the user requests them.
- If argument chain has >8 strong nodes, prioritize by: (a) novelty, (b) concreteness,
  (c) counter-intuitive value. Cut the rest.

### newsletter

Conversational, first-person register. Structure:

1. Hook: 1-2 sentences framing why this matters *now*.
2. Core argument: prose walkthrough of the thesis and key evidence. Shorter than
   blog — aim for 500-800 words total.
3. Honest caveat: pick the most interesting weakness and present it as "here's
   where I'm less sure."
4. Pointer: "I wrote the full version here: [link placeholder]"

Tone: thoughtful, direct, mildly informal. Like writing to a smart friend.

## Workflow

1. **Read the working paper.** Use `view` to read the full `working-papers/{slug}.md`.
   Verify it matches the expected structure. If not, stop.

2. **Confirm targets.** If the user didn't specify platforms, ask which ones.
   If they said "all", produce all three.

3. **Create output directory.** `mkdir -p published/{slug}/`

4. **Generate each target.** For each requested platform, produce the output file
   following the platform spec above. Write files to `published/{slug}/{platform}.md`.

5. **Cross-check.** After generating:
   - Verify every factual claim traces back to the working paper. If you catch a
     drift (added claim, softened weakness, invented example), fix it.
   - If thread was generated: count each post's CJK characters. If any post
     exceeds 140, rewrite that post. Do not skip this step.

6. **Report.** Summarize what was produced:
   ```
   ✅ published/{slug}/blog.md      (~{word_count} words)
   ✅ published/{slug}/thread.md    ({N} posts)
   ✅ published/{slug}/newsletter.md (~{word_count} words)
   ```

## What This Skill Does NOT Do

- Does NOT post to any platform. Output is local files. The user handles distribution.
- Does NOT modify the source working paper.
- Does NOT fill gaps — if 待补充 lists missing evidence, flag it in the output
  but don't fabricate a substitute. Use `⚠️ [gap: {description}]` inline.
- Does NOT translate. Output language matches the working paper's language unless
  the user explicitly requests otherwise.
