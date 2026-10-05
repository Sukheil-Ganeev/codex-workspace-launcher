# Liquid Glass Candidate Registry

Snapshot checked: 2026-06-23.

Use this file when choosing a liquid-glass implementation. Do not install every candidate into one production project just to experiment. Pick one primary route, create a small isolated demo, then promote after browser QA.

## Short Ranking

1. `@samasante/liquid-glass` - default for React web.
2. `shuding/liquid-glass` - reference shader to understand the technique.
3. `liquid-glass-web-react` - React alternative to test when live-DOM refraction behavior matters.
4. `liquid-glass-component-kit` - best fallback when project is vanilla JS or mixed JS/React.
5. `@zakisheriff/liquid-glass` or `glinui` - when ready-made glass UI components matter more than low-level control.
6. `@aslanonur/liquid-glass-vue` - Vue/Nuxt route.
7. `@callstack/liquid-glass` - React Native iOS route only.

## Comparison Table

| Candidate | GitHub | npm/install | Best for | Current npm facts | Strength | Risk |
|---|---|---|---|---|---|---|
| samasante | `https://github.com/samasante/liquid-glass` | `@samasante/liquid-glass` | React web, headless live-DOM glass | `0.1.1`, MIT, peers `react >=18`, `react-dom >=18` | Crisp children, live DOM, flexible `Glass` API | New package, needs visual QA |
| shuding | `https://github.com/shuding/liquid-glass` | no normal npm route | Reference SVG shader / copy-paste prototype | MIT GitHub repo | Simple source for learning the SVG-filter idea | Not a maintained component package |
| PallavAg | `https://github.com/PallavAg/liquid-glass-web-react` | `liquid-glass-web-react` | React live-DOM lens alternative | `0.1.1`, MIT, peers `react >=18`, `react-dom >=18` | Similar philosophy to samasante, tiny/zero-deps claim | Very young repo/package |
| rdev | `https://github.com/rdev/liquid-glass-react` | `liquid-glass-react` | React visual demos, configurable refraction/elasticity | `1.1.1`, MIT, peers `react >=19`, `react-dom >=19` | Strong visual controls, hover/click effects | React 19 requirement; Safari/Firefox partial displacement |
| h0rhay | `https://github.com/h0rhay/liquid-glass-component-kit` | `liquid-glass-component-kit` | Vanilla JS first, optional React hook | `1.0.3`, MIT, peer `react >=16.8.0` | Works beyond React, simple apply/remove API | More effect-kit than headless React material |
| zakisheriff | `https://github.com/zakisheriff/Liquid-Glass` | `@zakisheriff/liquid-glass` | Ready-made React buttons/cards/inputs/nav/sheets | `0.1.3`, MIT, peers `react >=17`, `react-dom >=17` | Faster app UI assembly | Less design control; ships its own CSS |
| glinui | `https://github.com/glincker/glinui` | `glinui` CLI/package | Full glassmorphic React design system | `0.1.1`, MIT; CLI deps include `commander`, `prompts`, `zod` | Many production-style primitives | Heavy choice; not a single glass effect |
| aslanon Vue | `https://github.com/aslanon/liquid-glass-vue` | `@aslanonur/liquid-glass-vue` | Vue 3 / Nuxt 3 | `1.1.3`, MIT, peer `vue ^3.0.0` | Direct Vue component route | Not for React |
| callstack RN | `https://github.com/callstack/liquid-glass` | `@callstack/liquid-glass` | React Native iOS | `0.8.0`, MIT, peers `react`, `react-native` | Serious native/mobile route | Requires native build constraints; not Expo Go/web |
| dashersw | `https://github.com/dashersw/liquid-glass-js` | use source/demo, no primary npm route recorded here | WebGL experiment / pure JS research | GitHub MIT repo | Real-time WebGL refraction ideas | Heavier; page sampling can freeze or stale content |

## Decision Rules

- For a normal React/Next/Vite website, start with `samasante`.
- If `samasante` does not satisfy exact interaction or browser behavior, test `PallavAg` in an isolated demo.
- If project is React 19 and wants dramatic component-level visuals, test `rdev`.
- If project is static HTML or mixed vanilla JS, test `h0rhay`.
- If project needs a whole ready-made visual component set, test `zakisheriff` first, `glinui` second.
- If project is Vue/Nuxt, use `aslanon-vue`.
- If project is React Native iOS, use `callstack-rn`.
- Use `shuding` only as reference/source reading unless the task explicitly asks for copy-paste shader experimentation.

## Install Helper Examples

```powershell
# Default React route
powershell -ExecutionPolicy Bypass -File "C:\Users\londo\.codex\skills\liquid-glass-effect\scripts\install-liquid-glass.ps1" -ProjectPath "C:\path\to\app" -Provider samasante

# React alternative
powershell -ExecutionPolicy Bypass -File "C:\Users\londo\.codex\skills\liquid-glass-effect\scripts\install-liquid-glass.ps1" -ProjectPath "C:\path\to\app" -Provider pallavag

# Vanilla JS / optional React hook
powershell -ExecutionPolicy Bypass -File "C:\Users\londo\.codex\skills\liquid-glass-effect\scripts\install-liquid-glass.ps1" -ProjectPath "C:\path\to\app" -Provider h0rhay

# Vue/Nuxt
powershell -ExecutionPolicy Bypass -File "C:\Users\londo\.codex\skills\liquid-glass-effect\scripts\install-liquid-glass.ps1" -ProjectPath "C:\path\to\app" -Provider aslanon-vue
```

