---
name: session-audit
description: Audit and manage Claude Code local session storage. Trigger: "sessions", "session audit", "会话审计", "session list", "查看会话", "清除session", "delete session".
---

# Skill: session-audit

Audit and manage Claude Code local session storage.

Trigger: "sessions", "session audit", "会话审计", "session list", "查看会话", "清除session", "delete session".

## Data sources

- `~/.claude/sessions/*.json` — active/running sessions
- `~/.claude/history.jsonl` — all historical sessions (one JSON object per user message)

## 1. Audit — list all sessions

```bash
python3 << 'PYEOF'
import json, os, glob
from datetime import datetime

# History
with open(os.path.expanduser("~/.claude/history.jsonl")) as f:
    lines = [json.loads(l) for l in f if l.strip()]

# Basic account
total = len(lines)
total_chars = sum(len(l.get("content","")) for l in lines)

# By session
from collections import Counter
sessions = Counter()
for l in lines:
    conv = l.get("conversation_id","") or "(single)"
    sessions[conv] += 1

# Session files
session_files = glob.glob(os.path.expanduser("~/.claude/sessions/*.json"))

# Print
print(f"history: {total} msgs, {total_chars:,} chars")
print(f"sessions: {len(sessions)} (IDs truncated):")
for sid, count in sessions.most_common(10):
    short = sid[:20] + "..." if len(sid) > 20 else sid
    print(f"  {short}: {count} msgs")
print(f"\nactive session files: {len(session_files)}")
for sf in sorted(session_files)[:5]:
    print(f"  {os.path.basename(sf)}")
PYEOF
```

## 2. Delete a session

```bash
# Replace with actual UUID
rm ~/.claude/sessions/<uuid>.json
```

## 3. View session details

```bash
python3 << 'PYEOF'
import json, os
sid = "<uuid>"
path = os.path.expanduser(f"~/.claude/sessions/{sid}.json")
with open(path) as f:
    s = json.load(f)
print(json.dumps(s, indent=2, default=str)[:2000])
PYEOF
```
