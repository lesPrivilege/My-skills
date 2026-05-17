---
name: arxiv-browse
description: >
  On-demand arXiv paper browsing with AI summarization. Query arXiv by date range,
  category, keywords, and authors. Generates reading-companion format .md notes.
  Slash command: /arxiv-browse <query>.
---

# arxiv-browse

On-demand arXiv paper browsing with keyword/author filtering and DeepSeek summarization.
Output goes to `<obsidian-vault>/reading-notes/` in reading-companion format.

## Invocation

`/arxiv-browse <query>` — e.g. `/arxiv-browse today`, `/arxiv-browse last week cs.LG`

Backend script at `~/Scripts/arxiv-browse`.

## Query examples (free-form, Claude interprets the intent)

| You say | What happens |
|---------|-------------|
| `/arxiv-browse today` | today's papers, default categories + keywords |
| `/arxiv-browse yesterday` | yesterday's papers |
| `/arxiv-browse 2026-04-25` | single date |
| `/arxiv-browse 2026-04-20 to 2026-04-29` | date range, all default categories |
| `/arxiv-browse last 7 days` | last N days |
| `/arxiv-browse today --keywords attention,moE` | today, custom keywords |
| `/arxiv-browse last 3 days --categories cs.LG,stat.ML` | 3 days, custom categories |

## Workflow

1. **arXiv API query** — search by category + date range (up to 300 recent results)
2. **Filter** — keyword/title matching + author org matching against default or user-specified list
3. **Summarize** — call DeepSeek API for matching papers, using reading-companion structure
4. **Save** — write individual .md files to `~/reading-notes/` in reading-companion format
5. **Report** — present title + TL;DR index to user, offer to dive into specific papers

## Default Filters

- **Keywords (title only)**: `distillation, MoE, RLHF, alignment, scaling law, chain-of-thought`
- **Author names**: specific researchers
- **Categories**: `cs.LG, cs.AI, cs.CL`

Matching is title-only, not full abstract. This avoids false positives from papers
that merely mention a keyword in passing.

### Adding new keywords / authors

Edit `~/.config/arxiv-browse.json`:

```json
{ "keywords": ["your", "keywords"], "authors": ["Researcher Name"] }
```

Overrides at invocation: `--keywords new1,new2 --authors "Another Name"` (CLI takes precedence over config file).

Override with `--keywords`, `--authors`, `--categories`.

## Implementation

The script at `~/Scripts/arxiv-browse` uses:
- arXiv OAI API (HTTP/XML, no `arxiv` package needed)
- DeepSeek API via Chat Completions (same key from env)
- Built-in `xml.etree.ElementTree` and `urllib.request`
- Output format identical to the daily-arXiv-ai-enhanced GitHub Action
