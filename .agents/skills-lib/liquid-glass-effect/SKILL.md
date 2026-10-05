---
name: liquid-glass-effect
description: Use when the user asks for "liquid glass", "liquid-glass", "glass effect", "стекло эффект", "эффект стекла", "ликвид гласс", Apple-style glass UI, frosted/refractive glass controls, or wants Codex to choose/install/apply a reusable glass design pattern in React, Vue, vanilla web, or React Native UI. Prefer @samasante/liquid-glass for React web by default; compare alternatives in references/candidate-registry.md when the user asks to compare, install another implementation, or choose the best library for a specific stack.
---

# Liquid Glass Effect

## Purpose

Make "liquid glass" a repeatable global Codex workflow, not a one-off visual guess.

Primary upstream:

- GitHub: `https://github.com/samasante/liquid-glass`
- npm package: `@samasante/liquid-glass`
- License: MIT
- Peer deps: `react >=18`, `react-dom >=18`

Reference files:

- `references/candidate-registry.md` - compare samasante, shuding, PallavAg, rdev, h0rhay, zakisheriff, glinui, Vue, React Native and JS/WebGL candidates.
- `references/react-patterns.md` - small React/CSS patterns to adapt.

## First Decision

Before implementation, decide:

1. If the target is a React/Next/Vite app, prefer `@samasante/liquid-glass`.
2. If the user names another candidate, read `references/candidate-registry.md` and choose the matching provider.
3. If the target is static HTML/CSS or non-React, use `liquid-glass-component-kit` or a CSS/SVG fallback, and state that CSS-only fallback is not the same as live-DOM refractive glass.
4. If the user asks for global setup, do not add npm packages globally as the main solution. Project bundlers usually need dependencies installed inside each project. Use this skill globally, then install the npm package locally in the target project.

## Install Helper

Use the helper when available:

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\londo\.codex\skills\liquid-glass-effect\scripts\install-liquid-glass.ps1" -ProjectPath "C:\path\to\project" -Provider samasante
```

Provider choices:

- `samasante` - `@samasante/liquid-glass`, default React web.
- `pallavag` - `liquid-glass-web-react`, React live-DOM alternative.
- `rdev` - `liquid-glass-react`, React 19+ visual component route.
- `h0rhay` - `liquid-glass-component-kit`, vanilla JS first, optional React hook.
- `zakisheriff` - `@zakisheriff/liquid-glass`, ready-made React UI components.
- `aslanon-vue` - `@aslanonur/liquid-glass-vue`, Vue/Nuxt route.
- `callstack-rn` - `@callstack/liquid-glass`, React Native iOS route.

Manual default install:

```powershell
npm install @samasante/liquid-glass
```

For pnpm/yarn/bun projects, use the matching package manager:

```powershell
pnpm add @samasante/liquid-glass
yarn add @samasante/liquid-glass
bun add @samasante/liquid-glass
```

## Basic React Usage

```tsx
import { Glass } from "@samasante/liquid-glass";

export function GlassButton() {
  return (
    <Glass
      radius={16}
      style={{
        background: "rgba(255,255,255,0.22)",
        padding: "12px 22px",
        border: "1px solid rgba(255,255,255,0.38)",
      }}
      optics={{ frost: 6, dispersion: 0.35, bend: 0.55 }}
    >
      Сохранить
    </Glass>
  );
}
```

## Comparison Workflow

When asked to compare projects:

1. Read `references/candidate-registry.md`.
2. Verify current GitHub/npm facts if the decision affects spending time or production code.
3. Recommend one primary package and one fallback.
4. Do not install multiple candidates into the same production project unless the user explicitly asks for an isolated benchmark.
5. If testing alternatives, create isolated demo branches/folders and compare build result, browser screenshots, readability, clickability, mobile layout, and performance.

## Design Rules

- Keep readable contrast. Glass must not make text weak or blurry.
- Children/content must stay crisp; use glass for container/lens, not for text itself.
- Do not make the whole app a glass blur. Use it on focused controls: nav, floating toolbar, CTA, modal shell, media controls, compact cards.
- Add a non-glass fallback for low-performance or unsupported contexts.
- Respect existing brand UI. Liquid glass is an accent, not a redesign excuse.
- Test desktop and mobile screenshots before calling it done.

## Browser Reality

The upstream library supports Chrome/Edge, Safari/iOS, and Firefox, but the strongest live-page bending depends on browser capabilities. In Safari/Firefox, expect frosted/tinted glass and edge lighting; full live DOM bending may need copy/refract modes.

## QA Checklist

Run or create checks appropriate to the project:

- Build/typecheck passes.
- Browser screenshot proves the glass is visible and not blank.
- Text remains readable and selectable.
- Buttons/links remain clickable.
- No layout overlap on mobile.
- Reduced-motion or simple fallback is acceptable if animation is used.
- Visual effect does not hide business-critical content.

## When Not To Use

- Do not use for exact PDF-to-HTML catalog reproduction unless the original PDF actually has a glass effect.
- Do not use on dense operational dashboards where clarity is more important than atmosphere.
- Do not install new dependencies in a project without checking existing package manager and lockfile.
