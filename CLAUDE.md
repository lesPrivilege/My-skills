# My Skills — Commit & Collaboration Rules

## Structure

```
~/.claude/skills/
├── README.md         ← catalog — must match skills/ directory exactly
├── CLAUDE.md         ← this file
├── .gitignore
├── fetch/            ← skill directories (each contains SKILL.md)
│   └── SKILL.md
├── project-audit/
│   └── SKILL.md
├── ...
└── source-audit/
    └── SKILL.md
```

Non-skill files at root level (`.gitignore`, `scripts/`) are ignored by the skill loader. Scripts live in `~/Scripts/` — copies in this repo are convenience snapshots.

## Invariants

1. **README inventory must include every skill directory at repo root.** Add a new skill → add a row. Remove a skill → remove the row. No stale entries.
2. **Every SKILL.md must have YAML frontmatter** with `name` and `description`. The `description` field is the auto-trigger source — keep trigger keywords at the front.
3. **One skill, one directory.** No splitting a skill across directories; no merging two skills into one. Each SKILL.md is self-contained.
4. **No scripts or binaries in skill directories.** Scripts go in `~/Scripts/`. Skills reference them by absolute path.
5. **Repo is live.** `~/.claude/skills/` IS this repo. Edits are immediate. Push from here.

## Commit Rules

### When to commit

- Adding a new skill
- Removing a skill (mark as deleted in README first)
- Updating a SKILL.md (behavior changes, trigger words, usage)
- Adding a new category to the README

Do NOT commit for:
- Trivial typo fixes (just push)
- Changes that only touch `~/Scripts/` (scripts are versioned separately)

### Commit message format

```
<scope>: <action>

Examples:
  fetch: add Playwright fallback strategy
  repo: remove aham-ppt, huashu-design, mini-srs-design
  archive: align reading.md format with Archived.md spec
  README: add audit & environment category
```

Scope is the skill directory name, or `repo` / `README` for structural changes.

### Before commit

1. `comm -12 <(ls -d */ | sed 's|/||' | sort) <(grep -oP '`\K[^`]+(?=`)' README.md | sort)` — README catalog must match skill directories. If mismatch, fix README first.
2. Every new/existing SKILL.md must parse: `head -3 <name>/SKILL.md | grep -q '^---$'` on lines 1 and 3.
3. Verify: `ls ~/.claude/skills/ | sort` matches expected skills.
