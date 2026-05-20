# My Skills — Commit & Collaboration Rules

## Structure

```
my-skills/
├── README.md         ← catalog — must match skills/ directory exactly
├── CLAUDE.md         ← this file
└── skills/
    ├── <name>/
    │   └── SKILL.md  ← frontmatter + usage
    └── ...
```

There are no other files in this repo. Scripts live in `~/Scripts/`, not here.

## Invariants

1. **README inventory must include every directory in `skills/`.** Add a new skill → add a row. Remove a skill → remove the row. No stale entries.
2. **Every SKILL.md must have YAML frontmatter** with `name` and `description`. The `description` field is the auto-trigger source — keep trigger keywords at the front.
3. **One skill, one directory.** No splitting a skill across directories; no merging two skills into one. Each SKILL.md is self-contained.
4. **No scripts or binaries in skill directories.** Scripts go in `~/Scripts/`. Skills reference them by absolute path.
5. **Live is a symlink.** `~/.claude/skills/<name>/` → `skills/<name>/` in this repo. Edit here, changes take effect immediately. Do not edit the live directory directly.

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

1. `diff <(ls skills/ | sort) <(grep -oP '`\K[^`]+(?=`)' README.md | sort)` — README catalog must match skills/ directory. If mismatch, fix README first.
2. Every new/existing SKILL.md must parse: `head -3 skills/<name>/SKILL.md | grep -q '^---$'` on lines 1 and 3.
3. Verify symlink on live: `readlink ~/.claude/skills/<name>` points to this repo's `skills/<name>/`.

### After commit

Run `ls ~/.claude/skills/ | sort` to confirm live picked up the change. If a symlink is broken, the skill simply won't load — no crash, but log a warning.
