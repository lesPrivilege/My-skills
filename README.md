# My Skills

A curated set of Claude Code skills implementing a complete personal knowledge workflow: input → reading & research → archival → synthesis → publishing, plus independent design/prototyping and exam-prep paths.

## Design Philosophy

Skills are **invocation glue**, not logic containers. Each `SKILL.md` describes what a skill does and how it maps to the real work — the heavy logic lives in external scripts (`scripts/` in this repo, deployed to the user's `~/Scripts/`).

Skills produce structured output (JSON, markdown) that downstream consumers can use without knowing which LLM generated it. This keeps the pipeline modular and provider-independent at the integration boundaries.

The entire system serves a single arc:

**Input → Reading & Research → Archival → Synthesis → Publishing**

Alongside this pipeline, independent paths handle design/prototyping (HTML-based high-fidelity mockups with a complete design philosophy) and exam preparation (OCR-to-structured-questions).

## Pipeline

```
                      ┌──────────────────┐
                      │   fetch           │
                      │  reading-companion │
                      │   arxiv-browse     │
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
  │          ▼        │   │   (note synthesis      │
  │  questions.json   │   │    engine, 4 modes)    │
  └──────────────────┘   └──────────┬───────────┘
                                    │
                                    ▼
                            ┌──────────────────┐
                            │   packaging       │
                            │ (blog / thread /  │
                            │  newsletter)       │
                            └──────────────────┘

  Design/prototyping path (independent):
  design-prototype → huashu-design → design-migrate (back to source)
  aham-ppt → (standalone .pptx)

  Project-level design constraint:
  mini-srs-design (MiniSRS app visual spec)
```

## Skill Inventory

### Input & Conversion

| Skill | What it does |
|-------|-------------|
| `fetch` | Universal URL fetcher with domain routing, cache, readability extraction, and fallback chain |
| `markitdown` | Convert PDF/EPUB/DOCX/PPTX/XLSX/HTML/images to Markdown |
| `md-cleaner` | Strip ebook conversion artifacts (Calibre metadata, watermarks, ads) from markdown |
| `ocr-cleaner` | 5-phase pipeline: OCR'd textbook PDF → clean questions.json |
| `md-to-cards` | Markdown notes → MiniSRS Q&A flashcard JSON via LLM extraction |

### Reading & Research

| Skill | What it does |
|-------|-------------|
| `reading-companion` | Deep analysis of papers, repos, articles with structured critical notes |
| `arxiv-browse` | On-demand arXiv browsing with keyword/author filtering and LLM summarization |

### Archival & Synthesis

| Skill | What it does |
|-------|-------------|
| `archive` | Claude session archival → Auto Memory updates + categorized notes to Obsidian vault |
| `paper-mill` | 4-mode note synthesis: theme discovery → draft assembly → evidence enrichment → staleness review |

### Publishing

| Skill | What it does |
|-------|-------------|
| `packaging` | Working paper → blog / social thread / newsletter output |

### Design & Prototyping

| Skill | What it does |
|-------|-------------|
| `huashu-design` | Complete HTML-based design capability: prototypes, animations, slides, design direction consulting, expert critique |
| `design-prototype` | Package frontend project into single-file HTML visual spec |
| `design-migrate` | Migrate visual changes from redesigned prototype back to source code |
| `mini-srs-design` | Design system spec for the MiniSRS spaced-repetition app |
| `aham-ppt` | Full AI-powered .pptx presentation deck generation (McKinsey/Deloitte standard) |

## Collaboration Rules

`CLAUDE.md` at the repo root defines the conventions and invariants that govern how these skills interact — directory layout, fetch protocol, cleanup logic, and goal-driven execution rules.
