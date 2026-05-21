---
name: claude-audit
description: List all user additions to Claude Code since factory install. Trigger: "claude diff", "claude-audit", "Claude 差異", "搬遷 Claude", "what did I add to Claude".
---

# Skill: claude-audit

List all user additions to Claude Code since factory install. Baseline = empty Claude Code (no custom skills, no custom config, no hooks). Everything found is an addition.

Trigger: "claude diff", "claude-audit", "Claude 差異", "搬遷 Claude", "what did I add to Claude".

## What to scan

### 1. Skills

```
ls ~/.claude/skills/
```

### 2. Config

```
~/.claude/settings.json
~/.claude/settings.local.json
~/.claude/keybindings.json
```

### 3. Hooks

```
ls ~/.claude/hooks/
```

### 4. Scripts referenced by custom skills

Check each skill's SKILL.md for `~/Scripts/` references.

## Output

- Skills added
- Config changes
- Hooks installed
- Scripts that need to be carried over
