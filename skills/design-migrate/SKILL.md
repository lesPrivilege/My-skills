# Skill: design-migrate

Migrate visual changes from a redesigned prototype HTML back to the source code.

Trigger: "migrate design", "sync视觉", "回遷", "apply design", "遷移設計".

## Workflow

```
design-prototype (package) → huashu-design (redesign) → design-migrate (this)
```

1. Read the redesigned HTML and the source project
2. List diffs by page/component — user confirms before any write
3. Write only visual layer back to source code

## What to migrate

| Migrate | Do NOT touch |
|---------|-------------|
| CSS variable values | `useState` / `useEffect` logic |
| Layout (flex/grid/position) | `onClick` / `onChange` handlers |
| Spacing (margin/padding/gap) | Route config (App.jsx, router) |
| Fonts and typography | Data layer, storage |
| Animation (transition/@keyframes) | Import statements |
| New visual components (JSX structure only, no logic) | Deleted elements (annotate, don't remove) |

## Diff classification

For each page or component, determine one of:

| Status | Meaning | Action |
|--------|---------|--------|
| style change | className / style / CSS variables differ | Update styles |
| layout change | flex / grid / position structure differs | Update layout |
| animation change | transition / @keyframes differ | Update animation |
| added | exists in design but not in source | Create new file or component |
| removed | exists in source but not in design | Annotate, don't delete |
| unchanged | both match | Skip |

## Migration rules

### CSS variables
Replace values directly. Keep the source's file structure.

### Layout changes
Update className and style only. Do not rewrite JSX structure between Tailwind and inline style — keep the source's convention.

### Animation changes
Update CSS transition durations, easing curves, and @keyframes.

### New components
Create new files containing only JSX structure and style references:
```jsx
// src/components/NewThing.jsx
export default function NewThing() {
  return (
    <div className="new-thing">
      {/* JSX structure from design */}
    </div>
  );
}
```
No useState, useEffect, or onClick — those belong to the business layer.

### Removed elements
Do not delete. Annotate in the source:
```jsx
{/* design-migrate: removed in redesign, kept for reference */}
<div className="old-section">...</div>
```

## Validation

Before reporting completion:
- All import paths are correct
- CSS variable names match between design output and source
- Business logic (`useState`, `useEffect`, `onClick`, data layer) has zero changes
- Every diff item was either actioned or explicitly skipped with user's acknowledgement

## References

None. This skill is self-contained — the design HTML and source code are provided at invocation time.
