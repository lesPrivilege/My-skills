# Harness Engineering Practices — AI 輔助知識工作的 skill pipeline

非 coding 場景的 harness 實踐體系：從資訊獲取、閱讀分析、歸檔整理、觀點合成到發佈輸出的完整 pipeline，以及獨立的考試準備、設計原型、建置自動化與系統審計路徑。每個 skill 是 Claude Code 的調用入口，直接管理在 `~/.claude/skills/`（git repo）。

Skills are **invocation glue**, not logic containers. Each `SKILL.md` describes trigger terms and behavior—the heavy logic lives in external scripts (`~/Scripts/`). Skills produce structured output (JSON, markdown) that downstream consumers can use without knowing which LLM generated it. This keeps the pipeline modular and provider-independent at the integration boundaries.

### Pipeline

These skills form an end-to-end harness for knowledge work. Each stage produces structured output that the next stage consumes:

```
                       ┌──────────────────┐
                       │   fetch           │
                       │  reading-companion │
                       │   arxiv-browse    │
                       └────────┬──────────┘
                                │
  ┌──────────────────┐   ┌──────────────────────┐
  │ markitdown        │   │   archive            │
  │ md-cleaner        │   │   (session archival  │
  │                   │   │    → Auto Memory      │
  │ ocr-cleaner       │   │    → Obsidian vault)  │
  │  ├─ Phases 1-3    │   │                      │
  │  ├─ Phase 4       │   └──────────┬───────────┘
  │  │  exam-prep-    │              │
  │  │  bank-fix      │              ▼
  │  └─ Phase 5 merge │   ┌──────────────────────┐
  │          │        │   │   paper-mill          │
  │          ▼        │   │   (note synthesis     │
  │  questions.json   │   │    engine, 4 modes)   │
  └──────────────────┘   └──────────┬───────────┘
                                    │
                                    ▼
                            ┌──────────────────┐
                            │   packaging       │
                            │ (blog / thread /  │
                            │  newsletter)       │
                            └──────────────────┘

  Design & build (independent):
  design-prototype → design-migrate (back to source)
  build-apk (standalone Mnemos APK)
```

The arc: discover information (fetch, reading-companion, arxiv-browse) → convert and clean it (markitdown, md-cleaner, ocr-cleaner) → archive to knowledge base (archive) → sift and synthesize (paper-mill) → publish (packaging). The exam-prep, design, and audit paths run independently alongside this core flow.

### SKILL.md Format

Every skill in this repo follows this frontmatter contract consumed by Claude Code's skill loader:

```yaml
---
name: <skill-name>
description: >
  <one-line trigger description with keywords>
---
```

- `name` — lowercase, hyphen-separated, matches the directory name
- `description` — the auto-trigger source; trigger keywords go at the front, as Claude Code matches these against user intent
- No additional fields. Everything else (workflow, references, constraints) lives in the markdown body after the frontmatter

## Skill Inventory

### Input & Conversion

| Skill | What it does |
|-------|-------------|
| `fetch` | Universal URL fetcher with domain routing, cache, readability, fallback chain |
| `markitdown` | Convert PDF/EPUB/DOCX/PPTX/XLSX/HTML/images to Markdown |
| `md-cleaner` | Strip ebook conversion artifacts (Calibre metadata, watermarks, ads) |
| `ocr-cleaner` | 5-phase pipeline: OCR'd textbook PDF → clean questions.json |
| `md-to-cards` | Markdown notes → MiniSRS Q&A flashcard JSON via LLM |
| `exam-prep-bank-fix` | Fix questions.json with missing answers / OCR noise / broken parser output |

### Reading & Research

| Skill | What it does |
|-------|-------------|
| `reading-companion` | Deep analysis of papers, repos, articles — structured critical notes |
| `arxiv-browse` | On-demand arXiv browsing with keyword/author filtering + summarization |
| `post` | Analyze/summarize community posts, threads, discussions |

### Archival & Synthesis

| Skill | What it does |
|-------|-------------|
| `archive` | Session archival → Auto Memory + categorized notes to Obsidian vault |
| `paper-mill` | 4-mode note synthesis: theme discovery → draft assembly → evidence enrichment → staleness review |

### Publishing

| Skill | What it does |
|-------|-------------|
| `packaging` | Working paper → blog / social thread / newsletter output |

### Design & Prototyping

| Skill | What it does |
|-------|-------------|
| `design-prototype` | Package frontend project into single-file HTML visual spec |
| `design-migrate` | Migrate visual changes from redesigned HTML back to source code |
| `build-apk` | Build Mnemos Android debug APK (vite → cap sync → gradle) |

### Audit & Environment

| Skill | What it does |
|-------|-------------|
| `project-audit` | Codebase audit: architecture, modules, routes, coupling, dead code, UI |
| `source-audit` | Fact-check claims in docs/reviews against actual source code |
| `system-audit` | Scan dev environment — installed tools, brew/pip/npm layers |
| `session-audit` | Audit/manage Claude Code local session storage |
| `audit-usage` | Report Claude Code token consumption from local session files |
| `claude-audit` | List all user additions to Claude Code since factory install |


## Repo Structure

```
~/.claude/skills/
├── README.md         ← this file — skill catalog
├── CLAUDE.md         ← commit rules & collaboration conventions
├── .gitignore
├── scripts/          ← utility scripts (referenced by skills via ~/Scripts/)
├── fetch/            ← skill directories (each contains SKILL.md)
│   └── SKILL.md
├── project-audit/
│   └── SKILL.md
├── ...
└── source-audit/
    └── SKILL.md
```

This repo is cloned directly to `~/.claude/skills/`. Claude Code loads any directory containing a `SKILL.md` as a skill. Non-skill files at root level (`scripts/`, `README.md`, `CLAUDE.md`, `.gitignore`) are ignored by the skill loader.

