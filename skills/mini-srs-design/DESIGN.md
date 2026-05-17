# MiniSRS — Design Specification (v0.x ARCHIVED)

> ⚠️ 此文件为 v0.x 设计规范。v1.0.0 已全面重设计（暖棕色板 + Inter/Instrument Serif 字体体系）。
> 当前设计系统以 `design/mnemos-v2.html` 和 `src/styles/index.css` 为准。

Visual direction: **Tech Utility** — clean, dense, tool-like. Think Linear meets terminal. No playfulness, no illustration, no rounded-everything. The app is a precision instrument for memory.

---

## 1. Color

OKLCh-based palette. Define as CSS variables, map to Tailwind via `tailwind.config.js`.

### Dark mode (default)

| Token | OKLCh | Hex (approx) | Usage |
|---|---|---|---|
| `--bg-primary` | oklch(0.15 0.01 260) | `#1a1a2e` | Page background |
| `--bg-surface` | oklch(0.20 0.01 260) | `#222240` | Card surface, panels |
| `--bg-elevated` | oklch(0.25 0.015 260) | `#2a2a4a` | Hover states, active items |
| `--border` | oklch(0.30 0.01 260) | `#3a3a55` | Dividers, card edges |
| `--text-primary` | oklch(0.93 0.01 260) | `#e8e8f0` | Body text |
| `--text-secondary` | oklch(0.65 0.01 260) | `#8888a0` | Labels, metadata |
| `--accent` | oklch(0.70 0.15 250) | `#5b8af5` | Primary actions, links |
| `--accent-muted` | oklch(0.35 0.08 250) | `#2a3a6a` | Accent backgrounds |
| `--success` | oklch(0.70 0.15 155) | `#4aba78` | Easy button, positive stats |
| `--warning` | oklch(0.75 0.12 85) | `#c4a643` | Hard button |
| `--danger` | oklch(0.65 0.15 25) | `#d45a5a` | Again button, destructive |

### Light mode

| Token | OKLCh | Hex (approx) | Usage |
|---|---|---|---|
| `--bg-primary` | oklch(0.97 0.005 260) | `#f5f5f8` | Page background |
| `--bg-surface` | oklch(1.0 0 0) | `#ffffff` | Card surface |
| `--bg-elevated` | oklch(0.95 0.005 260) | `#ededf2` | Hover states |
| `--border` | oklch(0.88 0.005 260) | `#d5d5dd` | Dividers |
| `--text-primary` | oklch(0.20 0.01 260) | `#1a1a2e` | Body text |
| `--text-secondary` | oklch(0.50 0.01 260) | `#6a6a80` | Labels |
| `--accent` | oklch(0.55 0.18 250) | `#3a6ae0` | Primary actions |

Accent/success/warning/danger stay the same across modes (already accessible on both backgrounds).

### Implementation

```css
/* src/styles/index.css */
:root { /* light */ }
:root.dark { /* dark values */ }
```

```js
// tailwind.config.js
colors: {
  bg: { primary: 'var(--bg-primary)', surface: 'var(--bg-surface)', elevated: 'var(--bg-elevated)' },
  border: 'var(--border)',
  text: { primary: 'var(--text-primary)', secondary: 'var(--text-secondary)' },
  accent: { DEFAULT: 'var(--accent)', muted: 'var(--accent-muted)' },
  success: 'var(--success)',
  warning: 'var(--warning)',
  danger: 'var(--danger)',
}
```

---

## 2. Typography

Two fonts. No more.

| Role | Font | Weight | Fallback |
|---|---|---|---|
| Display / heading | **JetBrains Mono** | 600, 700 | `monospace` |
| Body / UI | **IBM Plex Sans** | 400, 500, 600 | `system-ui, sans-serif` |

### Scale (mobile-first)

| Token | Size | Line height | Usage |
|---|---|---|---|
| `text-xs` | 11px | 1.4 | Metadata, timestamps |
| `text-sm` | 13px | 1.5 | Labels, secondary text |
| `text-base` | 15px | 1.6 | Body text, card content |
| `text-lg` | 18px | 1.4 | Section headers |
| `text-xl` | 22px | 1.3 | Page titles |
| `text-2xl` | 28px | 1.2 | Stats numbers |

Load via Google Fonts. Self-host if Capacitor offline support is needed later.

```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
```

---

## 3. Spacing

Base unit: **4px**. All spacing is a multiple of 4.

| Token | Value | Usage |
|---|---|---|
| `space-1` | 4px | Inline gaps, icon margins |
| `space-2` | 8px | Tight padding (buttons, tags) |
| `space-3` | 12px | Default inner padding |
| `space-4` | 16px | Card padding, list gaps |
| `space-6` | 24px | Section gaps |
| `space-8` | 32px | Page margins (mobile) |
| `space-12` | 48px | Major section separators |

Page horizontal padding: `space-4` (16px) on mobile.

---

## 4. Layout

### Screen structure

```
┌─────────────────────────┐
│  Header (48px fixed)    │  ← page title + back nav
├─────────────────────────┤
│                         │
│  Content (scrollable)   │  ← main content area
│                         │
├─────────────────────────┤
│  Bottom bar (optional)  │  ← review buttons only
└─────────────────────────┘
```

- **No bottom tab nav.** Three pages, accessed via list items and back buttons. Tab nav is overhead for 3 routes.
- **Header**: Fixed top, 48px height, `bg-surface`, bottom border `1px solid var(--border)`.
- **Content**: `overflow-y: auto`, padding `space-4`.
- **Safe areas**: Use `env(safe-area-inset-*)` for Capacitor/Android notch handling.

### Responsive

Single breakpoint: **640px**. Below = mobile (primary). Above = centered container, max-width 480px. This is a phone app that happens to work in a browser.

---

## 5. Components

### 5.1 Deck card (Home page)

```
┌──────────────────────────────┐
│  Deck Name              →    │
│  12 due · 48 total           │
└──────────────────────────────┘
```

- `bg-surface`, `border`, `rounded-lg` (8px)
- Padding `space-4`
- Tap target: entire card is clickable
- Right arrow: `text-secondary`, 16px

### 5.2 Review card (Review page)

```
┌──────────────────────────────┐
│                              │
│                              │
│      Front / Back text       │  ← centered, text-base
│                              │
│                              │
└──────────────────────────────┘
```

- `bg-surface`, full-width, min-height `240px`
- Text centered both axes
- Tap anywhere to flip
- Flip transition: `transform: rotateY(180deg)`, 300ms ease
- Front text: `text-primary`
- Back text: `text-accent`

### 5.3 Review buttons (bottom bar)

```
┌──────┬──────┬──────┬──────┐
│ Again│ Hard │ Good │ Easy │
│  1d  │  3d  │  7d  │ 14d  │  ← interval preview
└──────┴──────┴──────┴──────┘
```

- Fixed bottom, `bg-surface`, top border
- 4 equal-width buttons, `min-height: 56px`
- Colors: Again=`danger`, Hard=`warning`, Good=`accent`, Easy=`success`
- Show next interval as subtext (`text-xs`, `text-secondary`)
- Buttons use muted background of their color, solid color on press

### 5.4 Card editor (DeckDetail page)

- Two stacked text areas: "Front" and "Back"
- Monospace font (`JetBrains Mono`) for input
- Save/Cancel buttons right-aligned
- Inline editing — no modal, no separate page

### 5.5 Stats bar (Home page)

```
┌──────────────────────────────┐
│  Today: 12 reviewed · 5 due │
│  ▇▇▇▅▃▂▁  (7-day forecast)  │
└──────────────────────────────┘
```

- `bg-surface`, `rounded-lg`
- Bar chart: 7 columns, `accent` color, height proportional to count
- Labels: day abbreviation below each bar, `text-xs`

### 5.6 Progress bar (Review page)

- Top of review area, below header
- Thin (3px), full-width
- Fill color: `accent`
- Shows `current / total` count as right-aligned text

---

## 6. Animation

Minimal. Functional only.

| Element | Animation | Duration | Easing |
|---|---|---|---|
| Card flip | `rotateY(180deg)` | 300ms | `ease-in-out` |
| Page transition | Slide left/right | 200ms | `ease-out` |
| Button press | Scale to 0.97 | 100ms | `ease` |
| Progress bar | Width transition | 200ms | `ease` |

No: skeleton loaders, fade-ins on scroll, bounce effects, loading spinners, confetti, streak celebrations.

---

## 7. Tone / Copy

- **Terse.** "12 due" not "You have 12 cards due for review today!"
- **No emoji** in UI chrome. Card content is user's business.
- **Technical labels**: "Easiness", "Interval", "Repetitions" — SM-2 terminology, not dumbed-down synonyms.
- **Button labels**: Single word. "Again", "Hard", "Good", "Easy". Not "I didn't know this" / "I got it right".
- **Empty states**: One line. "No cards yet." not a friendly illustration with a paragraph.

---

## 8. Brand

There is no brand. This is a utility. No logo, no splash screen, no onboarding flow, no "about" page.

App name in header: "MiniSRS" in `JetBrains Mono 700`, `text-lg`.

Favicon: A simple `M` glyph in accent color on transparent background, rendered as SVG.

---

## 9. Anti-patterns

Violations of these are bugs, not style preferences.

- ❌ Rounded-everything (max border-radius: 8px, no `rounded-full` on containers)
- ❌ Gradient backgrounds
- ❌ Drop shadows (use borders instead)
- ❌ Component libraries (MUI, Chakra, Ant, shadcn)
- ❌ Icon libraries for core UI (use text labels; one exception: back arrow)
- ❌ Modals for card editing (inline only)
- ❌ Toast notifications
- ❌ Floating action buttons
- ❌ Bottom tab navigation
- ❌ Skeleton loading states
- ❌ Motivational text ("Great job!", "Keep going!", streak counters)
- ❌ Any element that exists only for decoration
