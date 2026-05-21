---
name: audit-usage
description: Report Claude Code token consumption from local session files. Trigger: "查用量", "消耗", "token usage", "audit usage".
---

# Skill: audit-usage

Report Claude Code token consumption from local session files.

Trigger: "查用量", "消耗", "token usage", "audit usage".

## Usage

Invokes `~/Scripts/claude-usage` which queries `~/.claude/projects/*/*.jsonl` for `message.usage` data.

```bash
~/Scripts/claude-usage                  # all time
~/Scripts/claude-usage --days 7         # last 7 days
~/Scripts/claude-usage --days 1         # today
~/Scripts/claude-usage --since 2026-05-01  # since date
~/Scripts/claude-usage --json --days 3  # JSON output for processing
```

## Data sources

1. **Session files** (`~/.claude/projects/*/*.jsonl`): `type: assistant` entries with `message.usage` — contains input_tokens, output_tokens, cache_read_input_tokens, model name
2. **History** (`~/.claude/history.jsonl`): user request timeline — counts only, no token data

## Notes

- Token data is per-assistant-message, not per-user-request. One user request can spawn multiple assistant messages (sub-agents).
- Cache hit rate is calculated as cache_read / total.
- `<synthetic>` model entries have zero token usage (internal operations).
- Only covers the local machine. Does not query Anthropic Console.
