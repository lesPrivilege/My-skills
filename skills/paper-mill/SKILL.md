---
name: paper-mill
description: >
  Periodic note synthesis engine. Reviews archived index files to discover
  thematic clusters, assembles working-paper drafts from archive entries with
  external evidence補強, and reviews existing drafts for staleness. Trigger
  when the user says "paper-mill", "主題審視", "組裝", "補強", "review 舊文",
  or any reference to synthesising archived notes into structured arguments.
  Four modes: A (index review → theme proposals), B (assembly → working paper),
  C (fetch 補強 → evidence enrichment), D (staleness review of existing papers).
---

# Paper Mill

Synthesise archived notes into structured working-paper drafts. Pure midstream:
consumes upstream archive output, produces drafts for downstream publishing skills.

## File System Contract

```
Upstream (read-only for this skill):
  <obsidian-vault>/archive/*.md       ← note files
  <obsidian-vault>/archive/*.idx      ← hash indexes (from idx.py)
  ~/Scripts/archive-session/config.json        ← category map
  <obsidian-vault>/reading-notes/     ← reading-companion output

Downstream (this skill's output):
  <obsidian-vault>/working-papers/    ← create if absent
  <obsidian-vault>/working-papers/{slug}-{YYYY-MM-DD}.md   ← working paper
  <obsidian-vault>/working-papers/usage-index.md    ← consumption tracking (auto-maintained)

Tools:
  ~/Scripts/archive-session/idx.py        ← dedup/check/rebuild
  <obsidian-vault>/working-papers/usage-index.md    ← note consumption tracking
  reading-companion skill                 ← for Mode C fetch
```

Category map (from config.json):

| Category | Files | Format |
|----------|-------|--------|
| 技術與系統 | `tech.md` / `tech.idx` | atomic notes |
| 組織、資本與權力 | `power.md` / `power.idx` | atomic notes |
| 認知、哲學與心智 | `mind.md` / `mind.idx` | atomic notes |
| 數學、學習與方法論 | `method.md` / `method.idx` | atomic notes |
| 生活、決策與心智工具 | `life.md` / `life.idx` | atomic notes |
| 閱讀 | `reading.md` / `reading.idx` | free-form |
| 項目 | `projects.md` / `projects.idx` | narrative |

## Mode A: Index Review (辨章學術)

**Trigger**: "主題審視", "review index", "有什麼可以寫的", or periodic prompt.

**Input**: All `.idx` files (title-only, lightweight).

**Process**:

1. Read all `.idx` files. Parse each line as `hash | title`.
2. Identify thematic clusters: groups of 3+ titles across categories that share
   a structural argument, not just keyword overlap. Look for:
   - Titles that address the same phenomenon from different angles
     (e.g., tech mechanism + power implication + cognitive parallel)
   - Titles where one provides evidence for another's claim
   - Titles that form a chronological arc (earlier observation → later validation)
3. For each cluster, draft a one-sentence thesis that the entries could support.
4. Check `<obsidian-vault>/working-papers/` for existing drafts —
   flag if a proposed cluster substantially overlaps an existing paper.
   Also read `usage-index.md` — annotate any entries already consumed by
   previous papers (do not exclude, just flag with `[used by: {paper}]`).
   If all entries in a cluster are already consumed, flag as "potentially
   redundant with existing papers — review before proceeding."
5. Also flag: entries that contradict each other (tension = interesting paper),
   entries that have been superseded by newer ones in the same category.

**Output**: Conversational proposals, no files written. Format per cluster:

```
### Cluster: {proposed thesis, one sentence}

Sources (N entries):
- tech:  {title1}, {title2}
- power: {title3}
- mind:  {title4}

Overlap with existing: {filename} / none
Consumption: {N} entries already used by previous papers — {paper-names}
Tension: {description of internal contradictions, if any}
```

Wait for user to approve/modify/reject before proceeding to Mode B.

## Mode B: Assembly (組裝)

**Trigger**: User approves a Mode A cluster, or directly specifies a thesis + entry titles.

**Input**: A thesis direction + list of archive entry titles (or a cluster from Mode A).

**Process**:

> **Language rule**: All working paper output must be written in **Simplified Chinese**.
> Source notes (from archive) are in Traditional Chinese — the content,
> arguments, and insights carry over, but the prose is rewritten in
> Simplified Chinese during assembly. This keeps archive (繁) and
> working papers (简) separate.

1. Read the full text of selected entries from their `.md` files.
   Use `## 歸檔 · YYYY-MM-DD` section headers and `- **Title**: body` format
   to locate exact entries. For reading.md, locate by date section and content.
2. Determine argument structure:
   - Which entry establishes the framework (→ E1)?
   - Which entries provide empirical evidence?
   - Which entries extend the argument to adjacent domains?
   - Which entries create internal tension or qualify the claim?
3. Assemble into the working-paper template (see below).
4. Generate "已知弱點" by stress-testing each evidence link:
   - Is the mapping from source note to argument step a tight logical link
     or an analogy?
   - Is the evidence a single anecdote or a structural observation?
   - What would falsify this argument step?
5. Generate "待補充" table: what external evidence would strengthen the weakest links?
6. Generate slug: `{核心概念的英文短名}-{YYYY-MM-DD}`. Short name should be 1-3 English words
   capturing the thesis core (e.g. `discard-capability`, `externalization-ceiling`, `harness`).
   Avoid generic terms like `note`, `idea`, `analysis`.
7. Save to `<obsidian-vault>/working-papers/{slug}-{YYYY-MM-DD}.md`.
8. Update `usage-index.md`: append one row per consumed source entry.
   Each row includes: `{category}-{ordinal} | {source file} | {title} | {slug} | {date}`.
   Use ordinal numbers auto-incrementing per category (read last row of each category
   in usage-index.md to find current max, then increment).

**Working Paper Template**:

```markdown
# {Title}

> Working Paper · Draft · {YYYY-MM-DD}
> Source notes: {N} entries from {list of source files}

---

## 主張

{Core thesis, one paragraph. State the claim, the mechanism, and the
actionable implication. No hedging — save qualifications for 已知弱點.}

---

## 論據鏈

### E1. {Title}

> *來源：{original note title}（{category}.md:{note title}）*

{Reconstructed argument in the paper's voice. Not a copy of the note —
rewrite to serve the paper's thesis.}

**論據功能**：{One sentence: what role does this evidence play in the
argument chain? Framework-setting / empirical grounding / domain extension /
qualification.}

### E2. ...

(repeat for each evidence block)

---

## 論證結構圖

{ASCII diagram showing argument flow. Use the format from the
externalization-ceiling sample: tree structure with labeled edges
indicating logical relationships.}

---

## 已知弱點

### W1. {weakness title}

- **嚴重程度**：{高/中/低}
- **說明**：{What is weak, why it matters, what would fix it.}

(repeat)

---

## 待補充

| # | 需要什麼 | 為什麼需要 | 預期來源 |
|---|---------|-----------|---------|
| 1 | ... | ... | ... |

(repeat)

---

*{Provenance line: how this draft was generated, which source files were used.}*
```

**Idempotency**: If the same thesis is re-triggered with the same entries, check
`usage-index.md` — if all entries are already consumed by a single existing paper,
report "no update needed". If new entries added (not in usage-index), produce a
diff or updated draft (user chooses).

## Mode C: Evidence Enrichment (補強)

**Trigger**: "補強", "fetch evidence", or user points to a specific working paper's
待補充 table.

**Input**: A working paper file + its 待補充 table.

**Process**:

1. Read the working paper's 待補充 table.
2. For each row, determine fetch strategy:
   - Academic evidence → use reading-companion skill (arxiv pipeline)
   - Industry data → use reading-companion skill (web-article pipeline)
   - User-specified local reading notes → read from `<obsidian-vault>/reading-notes/`
3. Invoke reading-companion for each fetch target. Reading-companion saves
   its output to `<obsidian-vault>/reading-notes/` (side-effect: enriches
   the reading archive).
4. For each successful fetch, draft a new evidence block (E-format) and
   propose where it fits in the argument chain.
5. Update the working paper:
   - Add new E-blocks at proposed positions
   - Update 論證結構圖
   - Mark fulfilled rows in 待補充 as `✅ addressed in E{N}`
   - Re-evaluate 已知弱點 in light of new evidence
6. Present diff to user for approval before overwriting.

**Constraint**: paper-mill does NOT implement fetch logic itself. It delegates
entirely to reading-companion. If reading-companion is unavailable or fetch
fails, paper-mill reports the gap and moves on.

## Mode D: Staleness Review (舊文覆核)

**Trigger**: "review 舊文", "check papers", or periodic prompt.

**Input**: All files in `<obsidian-vault>/working-papers/`.

**Process**:

1. List all working papers with their dates and source entry references.
2. For each paper, cross-reference its E-block sources against current `.idx`:
   - Are source entries still present? (entries can be removed during archive edits)
   - Have newer entries been added to the same categories that are relevant
     to this paper's thesis?
3. Check temporal staleness:
   - Papers > 3 months old: flag for review
   - Papers whose thesis has become consensus (widely echoed in recent
     reading-notes): flag as "下沉為分論點" (demote to supporting argument)
   - Papers whose thesis has been falsified by newer evidence: flag for retraction or major revision
4. For each flagged paper, suggest one of:
   - **Update**: incorporate new entries, refresh argument
   - **Demote**: thesis is now consensus, reposition as background/分論點 in a newer paper
   - **Retire**: thesis falsified or no longer interesting
   - **No action**: still current

**Output**: Conversational report, no files modified without approval.

## What This Skill Does NOT Do

- Does NOT publish or format for any platform (downstream skill responsibility)
- Does NOT modify upstream archive files (`.md`, `.idx`)
- Does NOT implement fetch/scraping logic (delegates to reading-companion)
- Does NOT auto-execute without user approval at decision points (Mode A proposals,
  Mode B draft review, Mode C diff approval, Mode D action selection)
- Does NOT generate original arguments — it synthesises and structures existing
  archived observations. The user's judgment remains the source of thesis direction.

## Interaction Protocol

All modes produce proposals or drafts that require user sign-off before
any file is written or modified. The skill never silently writes to
working-papers/. Approval phrases: "OK", "寫入", "approved", "存".
Rejection phrases: "不要", "改", "重來". Modification: user states changes,
skill revises and re-presents.
