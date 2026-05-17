# Home Rules

## Directories

```
~/Projects/     active work, one folder each
~/Scripts/      personal utility scripts
~/Reading/      papers, magazines, reading notes
~/Study/        exam prep materials
~/Archives/     done projects, kept for reference
```

## Invariants

1. **No loose files in ~/** — everything goes into one of the directories above.
2. **One folder per project** — when done, move to `Archives/`.
3. **Downloads/ is a inbox** — sort and clear. Never treat it as storage.
4. **Claude output stays in the project folder** — never write to `~/` or `~/Downloads/`.
5. **Scripts in `~/Scripts/`, not in `.claude/skills/`** — skills are just the invocation glue.
6. **Confirm root cause before changing code** — if you find yourself typing a fix without a hypothesis, stop and read.

## Fetch Protocol

Source: `~/Scripts/fetch-url` (cache → domain route → fetch → readability → markdown)

### When fetching external URLs

1. **WebFetch** (built-in) — docs, GitHub raw, arxiv, API.
2. **`~/Scripts/fetch-url <url>`** — if WebFetch blocked. Uses local network (VPN,
   proxy). Domain routing (raw/docs→curl, articles→readability, JS-heavy→Playwright).
   24h SHA1 cache. Mozilla Readability extraction for clean article content. JSON
   logs to stderr, markdown to stdout.
3. **Ask user** — if all methods fail.

### Dependency note

`~/Scripts/fetch-url` calls node scripts with `NODE_PATH=$(npm root -g)` for global
modules (playwright, @mozilla/readability, jsdom). These are global installs.

### Skills

The `fetch` skill (`/fetch <url>`) encodes this protocol. Skills that fetch URLs
reference this protocol — do not duplicate it.

## Cleanup Logic

When asked "check for trash" or "any redundancy?" — use ad hoc commands
(`find`, `brew`, `du`, `pip list`, `mdfind`, `ls /Applications`) to
discover issues. The invariants above define what's normal; anything
outside them is suspect. Cross-reference when possible:

- `/Applications/` vs `brew list --cask` → orphaned manual installs
- `which -a python3` → multiple layers of Python (conda, pyenv, brew, .org)
- `ls ~/Projects/` vs `~/Archives/` → stale or unclassified projects
- `ls ~/Desktop/` `~/Downloads/` → misplaced coding files
- `brew list --formula` vs `brew uses --installed` → orphaned libs
- `~/Library/Application\ Support/` old entries → uninstalled app residues

Safety: never delete or confirm anything final without user sign-off.

## Goal-Driven Execution

Transform imperative tasks into verifiable goals. Instead of "add validation",
say "write tests for invalid inputs, then make them pass." For multi-step tasks,
state a brief plan with verify checks:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

Strong success criteria let me loop independently. Weak criteria ("make it work")
drift.
