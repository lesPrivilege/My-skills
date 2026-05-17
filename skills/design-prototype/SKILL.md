---
name: design-prototype
description: 打包前端專案成單檔 HTML 視覺原型。Trigger: 打包、build、package、打包HTML、打包產出、生成預覽HTML、建置成單頁、vite build + singlefile、合併成一個HTML。任何將 React/Vue 專案壓成一份開箱即用 .html 的請求。
---

# Skill: design-prototype

Package a frontend project into a single-file HTML visual spec for Claude Design redelivery.

**Goal:** Capture every screen's UI appearance — not working logic. One HTML file opens in browser showing all screens side-by-side in phone frames. Claude Design redraws each screen from this visual reference; the code is disposable.

**Scope:**
- ALL screens: list, detail, empty, error, settings, modals, every route
- Visual-only: layout, spacing, colors, typography, icons
- Minimal interaction: tab switch, flip, expand/collapse — enough to reveal hidden UI states, nothing more
- Static mock data: 4-6 items per list, realistic names/values, varied lengths

**Target time: ~5 minutes.** One agent, sequential reads, Write tool directly.

## Pipeline

```
Phase 0 — Explore agent: scan project → structured spec (~30s)
Phase 1 — Main agent: read sources + templates → generate CSS + JSX (~3min)
Phase 2 — Main agent: Write tool to target file (~30s)
Phase 3 — Main agent: validate (~30s)
```

### Phase 0 — Analyze (Explore agent, quick)

Scan project and output a structured spec (be framework-agnostic):

- **CSS vars**: `:root` / `:root.dark` / `[data-theme]` variable names
- **Screens**: all route/page components — scan `src/pages/`, `src/views/`, `src/screens/`, or `src/routes/`
- **Icons**: extract all SVG paths from icon component files
- **Fonts**: check `package.json` for `@fontsource/*`, or `index.html` for Google Fonts links
- **Storage**: identify localStorage/API wrapper functions to replace with mock data
- **Dependencies**: framework (React/Vue/Svelte), router, UI library versions

### Phase 1 — Generate (main agent)

**Read source files:**
- Project CSS → extract `:root`, `:root.dark`, component styles (strip `@tailwind`, unwrap `@layer`, replace `env(safe-area-*)` with `0px`)
- Skill templates: `templates/stage-base.css` + `templates/phone-frame.css` (or `browser-frame.css`)
- Icon source file → extract SVG paths (usually in `components/Icons.jsx` or similar)
- All distinct page/route files → extract JSX structure, className usage, component hierarchy
- Storage layer → infer mock data shapes

**Generate and Write to file:**

Compose the complete HTML, then write it in ONE Write tool call to `{project}-prototype.html`:

```
<head>
  Font CDN (Google Fonts — most widely accessible)
  React 18 + ReactDOM + Babel standalone (cdnjs — most widely accessible)
  <style>
    Stage canvas CSS (from skill templates)
    Phone frame CSS (from skill templates)
    Project :root + :root.dark CSS variables
    Project component CSS (all component classes)
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    Icons: Icon component + icon map
    Mock data: 4-6 items per array
    Phone wrapper component (frame + screen area)
    Screen components — one per distinct route/state:
      - Main list / dashboard (the primary screen users see)
      - Detail page (expandable sections, tabs, filters)
      - Data interaction (card flip, item selection, expand/collapse)
      - Settings / configuration
      - Utility pages (search, bookmarks, history, notifications)
      - Empty states, error states, modals if present
    App (Stage) component: renders all screens in Phone frames on a grid
    ReactDOM.createRoot().render(<App/>)
  </script>
</body>
```

**Key rules for script:**
- Use JSX (Babel transforms it). No `import`/`export`.
- `useState` only for display state (tab, flip, expand). No `useEffect`, localStorage, API calls.
- `.map()` → iterate over 4-6 mock items
- `Link`/`navigate` → `onNav(screenName)` or simply render all screens simultaneously (no router needed)
- **Never output content as agent response** — always use Write tool directly to file

### Phase 2 — Validate (main agent)

```bash
# No import/export
grep -c "^import \|^export " prototype.html          # must be 0

# Bracket balance in script block
node -e '
const f=require("fs").readFileSync("prototype.html","utf8");
const m=f.match(/<script type="text\/babel">([\s\S]+?)<\/script>/);
if(!m)process.exit(1);
const j=m[1];let p=0,b=0;
for(let i=0;i<j.length;i++){const c=j[i];if(c==="(")p++;else if(c===")")p--;else if(c==="{")b++;else if(c==="}")b--;if(p<0||b<0){console.log("UNBALANCED");process.exit(1)}}
console.log("OK",{p,b})
'

# CSS variables
node -e '
const f=require("fs").readFileSync("prototype.html","utf8");
console.log("Vars:",(f.match(/--[\w-]+/g)||[]).length,"Light:",!!f.match(/:root\s*\{/),"Dark:",!!f.match(/:root\.dark/))
'
```

Fix failures and re-validate before reporting done.

## Constraints

| Rule | Why |
|------|-----|
| Use JSX (Babel handles it) | 5x more compact, avoids output limits |
| No `import`/`export` in script | Plain script, not ESM |
| All data hardcoded | No server, no storage |
| Fonts via Google Fonts CDN | Widest accessibility (vs unpkg) |
| React/Babel via cdnjs | Widest accessibility (vs unpkg) |
| CSS vars from project, not hardcoded | Design fidelity |
| `useState` only for display state | No side effects |
| Write tool directly, never response output | Avoids max_tokens truncation |

## Extraction boundaries

| Keep | Strip |
|------|-------|
| JSX structure, className, style | API calls, data fetching |
| Display state (tab, flip, expand) | Route transitions, form submit |
| CSS transitions, transforms | JS animation, `useEffect` |
| `.map()` over mock arrays | `useEffect` data loading |
| Inline SVG icons | localStorage (mock instead) |
| Component CSS | `@tailwind`, `@layer` wrappers |

## Template files

| File | Content |
|------|--------|
| `templates/stage-base.css` | Stage canvas (neutral, grid layout) |
| `templates/phone-frame.css` | Phone bezel 360×740 + notch + status bar |
| `templates/browser-frame.css` | Browser window 1200×800 |

## Known pitfalls

| Issue | Symptom | Fix |
|-------|---------|-----|
| Agent uses `React.createElement` instead of JSX | Bracket imbalance (b ≠ 0, p ≠ 0) across deep nesting — unfixable without full rewrite | **Forbid `React.createElement`.** JSX only. If the agent starts writing `React.createElement`, it has already lost. Kill and restart. |
| `overflow:hidden` on body | Stage grid doesn't scroll, phones below fold invisible | Use `overflow-y:auto` on body. The stage shows all screens, it MUST scroll |
| `crossorigin` on script tags | CDN scripts silently fail from `file://` | Remove `crossorigin`. Scripts load fine without it. |
| unpkg CDN blocked | Blank page, CDN scripts never load | Use cdnjs (wide access) + Google Fonts |
| Nested JSX `{map(...)}` with complex ternaries | Brace imbalance (b != 0) | Keep map expressions shallow. Avoid deeply nested `{condition && <div>{items.map(...)}</div>}` — extract into variables or flatten. |
| Agent outputs JSX as response text | Hits max_tokens, content truncated mid-Write | Always use Write tool directly. Never let JSX content appear in agent response. |
| Deep `style={{...}}` objects | Minified CSS + JSX in same file, hard to debug braces | Validate bracket balance immediately after writing. Fix before reporting done. |
| Subagents read source files independently | Duplicate reads, wasted tokens, slower | Single agent does all reads. Phase 0 spec is sufficient context for generation. |
| Agent skips post-write validation | Broken file reported as done | **Validation is mandatory.** Phase 2 must run the 3 validation commands. If any fail, fix and re-validate before reporting done. Do not report success with validation failures. |
| Deep JSX nesting (>6 levels) | Same bracket issues as React.createElement, just harder to debug | **Enforce max 4 levels of nesting.** Extract repeated patterns into helper components. If a component is indented more than 4 levels deep in JSX, split it. |

## Hard constraints (DO NOT BREAK)

1. **JSX only** — if you type `React.createElement`, stop and restart
2. **Validation gate** — `node -e '...'` must print `OK {p:0, b:0}` before reporting done
3. **Max 4 nesting levels** — if a JSX tree goes deeper than 4 indent levels, extract a sub-component
4. **No `crossorigin`** on `<script>` tags
5. **`overflow-y: auto`** on body
6. **Write tool only** — never let prototype HTML content appear in agent response
