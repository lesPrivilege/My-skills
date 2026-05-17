---
name: mini-srs-design
description: Design system for MiniSRS — a minimal spaced-repetition app (React + Tailwind + Capacitor). Use this skill whenever generating, modifying, or reviewing UI code (.jsx, .css, .html) for the mini-srs project. Also trigger when the user asks to style, redesign, or theme MiniSRS components, or references "MiniSRS design", "SRS UI", or "flashcard interface". Always read DESIGN.md before writing any UI code for this project.
---

# MiniSRS Design System

This skill provides the single-source-of-truth design specification for the MiniSRS app. Any agent (Claude Code, MiMo, DeepSeek) generating UI code for `<repo>/mini-srs/` MUST read `DESIGN.md` first.

## When to read DESIGN.md

- Before creating or modifying any `.jsx` component in `src/components/` or `src/pages/`
- Before touching `src/styles/index.css` or `tailwind.config.js`
- When the user asks for visual changes, theming, or layout adjustments

## How to use

1. Read `DESIGN.md` in this skill directory for the full spec
2. Apply the design tokens (colors, typography, spacing) via Tailwind config and CSS variables
3. Follow the component patterns for each page
4. Respect the anti-patterns list — violations are bugs

## File map

```
mini-srs-design/
├── SKILL.md          # This file — when/how to use the skill
└── DESIGN.md         # Full design specification (9 sections)
```

## Key constraints

- **Mobile-first**: Primary target is Android via Capacitor. All layouts must work at 360px width.
- **Tailwind only**: No component libraries (MUI, Chakra, etc.). All styling via Tailwind utility classes + CSS variables.
- **Dark mode default**: App opens in dark mode. Light mode is secondary.
- **Touch targets**: Minimum 44×44px for all interactive elements (review buttons, card taps, nav items).
- **No decorative animation**: Motion is functional only (card flip, page transition). No loading spinners, no bounce effects, no gratuitous micro-interactions.
