---
name: source-audit
description: >
  Use when fact-checking claims in a document/review against actual
  source code and documentation in one or more repositories.
  Trigger: "source audit", "claim verification", "repo audit",
  "fact-check", "事实核验", "claim audit", "evidence audit",
  "源码审计", "verify claims", or any request to check a review
  document against source code. Also triggered by "audit repo
  claims" or cross-referencing claims with implementations.
---

# Source Audit

Methodology for auditing claims made about repositories against their actual source code, documentation, tests, and benchmarks. Produces structured evidence-grounded reports distinguishing verified claims from unsupported ones.

## When to Use

- Given a document/review/article that makes claims about one or more open-source repos
- Need to verify which claims are supported by actual source code vs README promises vs author vision vs unsubstantiated
- Preparing a fact-checked revision or response based on source evidence
- Evaluating whether a third-party assessment of a project is accurate

**Not for:** Code quality audits (use `project-audit`), UX reviews (use `ux-audit`), architecture assessment (use `project-audit`).

## Input

- **Claims document**: The text whose claims need verification (path or paste)
- **Target repo(s)**: Local clone path(s) or GitHub URL(s) to fetch
- Optionally: focus areas if the claims document is large (specify which sections)

## Evidence Levels

Every finding must be classified into one of these four levels:

| Level | Meaning | What to say |
|-------|---------|-------------|
| **Implemented** | Found in source code; function/struct/class exists with matching behavior | "repo implements X in `file.rs:42-89`" |
| **Declared** | Found in README, docs, or issue tracker, but not yet confirmed in code | "README claims X, but no code path found" |
| **Envisioned** | Found in author blog posts, roadmap, or vision docs, not in current code | "author envisions X (link), not in current release" |
| **Inferred** | Not stated anywhere; appears to be the auditor's own extrapolation | "no evidence; appears to be inference" |

Also mark claims as **Unsupported** when no evidence found at any level.

## Workflow

### Stage 0: Read Claims Document

Read the claims document first. Extract the claims per repo (or relevant section). If the document has no explicit claim list, extract inline claims as you go.

### Stage 1: Per-Repo Audit

For each target repo:

1. **Read README/docs** — establish official positioning, feature list, architecture
2. **Scan source structure** — directory layout, entry points, key modules
3. **Verify each claim** — for each claim in the document about this repo:
   - Search code for implementation (`grep` / `read` relevant files)
   - Check docs for declarations
   - Check test files for usage patterns
   - Check benchmarks if performance claims exist
4. **Classify** — assign evidence level to each claim
5. **Suggest wording** — for unsupported/weak claims, provide safer alternative

Question categories to guide investigation:

1. **Product positioning** — what does README/docs actually say vs what's claimed?
2. **Feature existence** — does the feature actually exist in code? search for key functions/structs
3. **Architecture claims** — does the code structure match described architecture?
4. **Performance/benchmark claims** — are numbers from repo benchmarks? what constraints apply?
5. **API surface claims** — does the actual API match what's described?
6. **Comparison claims** — are comparisons with other tools from README or the auditor's opinion?
7. **Status/quality claims** — does the repo self-declare as alpha/beta/stable? any disclaimers?

Output per repo (see template below).

### Stage 2: Cross-Repo Synthesis (if multiple repos)

After all per-repo audits complete, synthesize:

1. **Shared patterns** — what claims appear across repos? are they consistent?
2. **Layer mapping** — if repos form a stack (app → agent loop → inference), does each claim map to the right layer?
3. **Core thesis assessment** — does the document's central thesis hold up? needs weakening?
4. **Revision guide** — what stays? what gets weakened? what gets removed? what gets added?

## Output Format

### Per-Repo Audit

```markdown
# {Repo Name} — Source Audit

## Supported Claims
| Claim | Evidence | Suggested Wording |
|-------|----------|-------------------|
| ... | `file.rs:42-89` | ... |

## Partially Supported / Needs Weakening
| Claim | Evidence | Problem | Safer Wording |
|-------|----------|---------|---------------|
| ... | ... | ... | ... |

## Unsupported — Remove
| Claim | Search Performed | Reason |
|-------|------------------|--------|
| ... | grep patterns tried | no evidence at any level |

## New Observations Worth Adding
| Observation | Evidence | Relevance |
|-------------|----------|-----------|
| ... | `file.rs:42-89` | why it matters |

## Revision Notes
5-8 bullet-point revision instructions for the claims document regarding this repo.
```

### Cross-Repo Synthesis

```markdown
# Cross-Repo Synthesis

## Keep
{claims fully supported by evidence}

## Weaken
{claims partially supported, need softer language}

## Remove
{claims with no evidence}

## Add
{new observations from audit worth including}

## Revised Core Thesis
{one-paragraph reformulation of the document's thesis}

## Suggested New Outline
{brief outline for revised document}
```

## Constraints

- **Read-only** — never modify source during audit
- **Cite evidence** — every finding must reference a file path + function/struct/paragraph; line numbers when possible
- **Be honest about absence** — "not found" is a valid finding; don't over-search to prove a claim
- **Distinguish levels** — never conflate levels 2-4 with level 1
- **Don't rewrite the document** — audit first; revision suggestions come after
- **Parallelize** — use subagents for auditing multiple repos simultaneously
- **If file count > 100** — focus on README, entry points, key modules matching claims; skip generated/test data

## Language

- Output in Chinese for explanatory prose
- Technical terms, file names, function names in English (preserve originals)
- Code snippets in original form
- Tables for structured data
- File references as `file_path:line_number`

