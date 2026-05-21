---
name: system-audit
description: Scan macOS/Linux development environment and report installed software facts. No scoring, no inference, no recommendations. Trigger: "installed what tools", "system-audit", "brew / pip / npm breakdown", "系统软件画像".
---

# Skill: system-audit

Scan macOS/Linux development environment and report installed software facts. No scoring, no inference, no recommendations.

Trigger: "installed what tools", "system-audit", "brew / pip / npm breakdown", "系统软件画像".

## Execution steps

### 1. Homebrew layer (macOS)

```bash
brew list                       # all installed
brew leaves                     # explicitly installed (not dependencies)
brew list --versions            # version info
```

Report: package names, versions, count per list.

### 2. Python layer

```bash
pip list
```

Report: package names and versions.

### 3. Node.js layer

```bash
npm list -g --depth=0
```

Report: global package names and versions.

### 4. Ruby layer (if available)

```bash
gem list
```

### 5. System applications

```bash
ls /Applications
```

### 6. PATH

```bash
echo $PATH
```

### 7. Daemons / background services (macOS only)

```bash
launchctl list
```

## Output format

Organized by layer. Only facts: names, versions, counts. No analysis.
