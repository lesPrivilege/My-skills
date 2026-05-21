---
name: project-audit
description: >
  Comprehensive project audit: architecture, modules, routes, storage,
  rendering, coupling, dead code, UI consistency. Read-only analysis,
  outputs structured markdown report.
  Trigger: "audit project", "review project", "项目审计", "审查项目",
  "全面审查", "项目评估", "check project", "project review".
  Even a bare "audit" or "审查" in the context of a codebase should trigger.
---

# Project Audit

Read-only comprehensive audit of a frontend project. Outputs a structured
assessment report covering architecture, module boundaries, routing, storage,
rendering, coupling, dead code, and UI consistency.

## Trigger

- "audit project", "review project", "项目审计", "审查项目"
- "全面审查", "项目评估", "check project", "project review"
- "audit", "审查" in the context of a codebase
- Any request to assess, evaluate, or review a project's current state

## Input

Project path (default: current working directory if not specified).
If user provides a path, use it. Otherwise, infer from working directory.

## Workflow

### Stage 1: Structure Scan

1. `read` project root → directory listing
2. `glob` all source files (`**/*.{ts,tsx,js,jsx,css,html,vue,svelte}`)
3. Count files per directory, identify module boundaries
4. `read` package.json → dependencies, scripts, version
5. `read` build configs (vite.config, webpack.config, tailwind.config, capacitor.config, etc.)
6. `read` project docs (README.md, ROADMAP.md, CLAUDE.md, PROJECT_PROMPT.md, etc.)

Record:
- Tech stack (framework, build tool, UI library, mobile wrapper)
- Project version and metadata
- Module boundaries (separate directories with own storage/logic)
- Shared infrastructure (components, utilities, styles)

### Stage 2: Architecture Map

1. `read` main entry (App.jsx, main.tsx, App.vue, etc.) → routing table
2. `read` each page's import lines → dependency graph per page
3. `read` all lib/util files → export function inventory
4. `read` storage layer → localStorage keys, data models, CRUD functions
5. `read` rendering pipeline → shared rendering functions

For each module, record:
- Storage namespace (localStorage keys)
- Data model (schema of stored objects)
- Key functions (CRUD, algorithms, parsers)
- External dependencies (what it imports from other modules)

### Stage 3: Issue Detection

Run these searches in parallel using `grep`:

1. **Unused imports** — imported but never referenced in the file
   Pattern: `import { X }` where X doesn't appear elsewhere in the file
2. **Unused exports** — exported but never imported elsewhere in the codebase
   Pattern: `export function X` where X is never imported
3. **Dead state** — `setState` called but state variable never read in JSX or logic
4. **Unreachable code** — branches after `return`, conditions that can never be true
5. **Inconsistent button text** — mixed languages (EN "Delete" vs ZH "删除")
   Pattern: `>ENGLISH<` or `'ENGLISH'` in button/text content
6. **Empty placeholders** — "即将推出", "TODO", "FIXME", "TBD", `cursor: not-allowed`
7. **Missing imports** — function called but not imported (runtime crash)
8. **Dead CSS classes** — defined in CSS but never used in any component

### Stage 4: Coupling Analysis

1. Build import graph: which pages import from which modules
   - Page A imports from `lib/storage` AND `quiz/lib/storage` → coupling
   - Page A imports only from `lib/storage` → clean
2. Identify cross-module dependencies
3. Map localStorage namespaces — find conflicts or overlaps
4. Identify shared components — which are used by multiple modules
5. Identify duplicated functionality — same logic reimplemented in multiple places

### Stage 5: Report Generation

Output structured markdown:

```markdown
# {Project Name} v{Version} — 完整评估报告

## 1. 架构总览

{Annotated directory tree}
{Tech stack summary}
{Module boundary description}

## 2. 模块解耦现状

{For each module: storage namespace, data model, key functions}
{Coupling points: which files bridge modules}

## 3. 路由表

| 路由 | 页面 | 模块 | 入口 |
|---|---|---|---|
| /path | PageName | module-name | how user reaches it |

## 4. 渲染管线

{Rendering flow diagram}
{Shared vs module-specific rendering}

## 5. localStorage 命名空间

| Key | 模块 | 内容 |
|---|---|---|
| key-name | module | data description |

## 6. 关键发现

{Categorized by severity:}
- **P0 (crash)**: missing imports, undefined references
- **P1 (UX)**: inconsistent text, empty states, dead routes
- **P2 (cleanup)**: unused code, dead CSS, redundant logic
- **P3 (architecture)**: coupling issues, naming inconsistencies

## 7. 改进建议

{Prioritized list with file:line references}
```

## Output Format

- Section headers in Chinese
- Technical terms in English
- Tables for structured data
- Code blocks for directory trees and code references
- File references as `file_path:line_number` for navigability
- Severity ratings: P0 > P1 > P2 > P3

## Constraints

- **Read-only** — never modify files during audit
- Use `explore` subagent for parallel file scanning when possible
- Adapt to any frontend framework (React/Vue/Svelte/Angular)
- Output to stdout; user decides whether to save
- If project has >100 source files, focus on:
  - Entry points and routing
  - Storage/data layer
  - Top-level pages
  - Shared components
  - Skip: generated files, node_modules, dist

## Report Save

Only save if user explicitly requests. When saving:
- Path: `~/Downloads/{project-name}-assessment.md`
- Confirm path to user after save

## Performance Tips

- Batch `read` calls where possible (parallel reads of independent files)
- Use `grep` instead of reading entire files for pattern searches
- Use `glob` for file discovery instead of manual directory traversal
- For large projects (>100 files), use `explore` subagent to parallelize Stage 1-3
- Cache analysis results within a session — don't re-scan files already analyzed

## Framework Adaptation

### React (default)
- Entry: `src/App.jsx` or `src/App.tsx`
- Routes: `react-router-dom` `<Route>` components
- State: `useState`, `useReducer`, Zustand, Redux
- Storage: localStorage, sessionStorage, IndexedDB

### Vue
- Entry: `src/App.vue`
- Routes: `src/router/index.js`
- State: Pinia, Vuex
- Storage: localStorage, sessionStorage

### Svelte
- Entry: `src/App.svelte`
- Routes: `src/routes/` (SvelteKit) or `App.svelte` switch
- State: Svelte stores
- Storage: localStorage, sessionStorage

### Angular
- Entry: `src/app/app.module.ts` or `app.component.ts`
- Routes: `src/app/app-routing.module.ts`
- State: NgRx, services
- Storage: localStorage, sessionStorage

Adjust grep patterns and file locations based on detected framework.

## Language

Output in Chinese with English technical terms preserved:
- Section headers in Chinese (架构总览, 模块解耦现状, 关键发现)
- Explanatory prose in Chinese
- Technical terms, file names, function names in English
- Code snippets in original form
