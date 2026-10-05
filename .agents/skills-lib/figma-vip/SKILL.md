---
name: figma-vip
description: "Unified Figma super-skill for VIP-DXB-RUS design production. Single entry point for ALL Figma work. Integrates 6 Figma skills + bridge + console-mcp + CSS-to-Figma mapping + VIP system. Triggers - figma, фигма, html to figma, carousel to figma, plugin api, design system figma."
---
# Figma VIP — Unified Super-Skill

## MANDATORY: Lessons Protocol (КРИТИЧНО)

**ПЕРЕД ЛЮБОЙ операцией с Figma — ОБЯЗАТЕЛЬНО:**

1. Прочитать `references/lessons-learned.md` ПОЛНОСТЬЮ (все L-01 — L-35)
2. Прочитать `references/gotchas.md` ПОЛНОСТЬЮ (все 34 pitfalls)
3. Прочитать `docs/figma-data/font_weight_corrections.md`
4. Открыть `references/css_width_calculator.md` и выписать ширины для типа слайда
5. Подготовить SVG строки из HTML файла слайда
6. Пройти Checklist в конце lessons-learned.md — каждый пункт
7. **НИКОГДА не импровизировать в Figma.** Сначала подготовить скрипт на диск, проверить, затем выполнять (L-26, L-35)
8. **CSS = единственный source of truth** (L-28). Не доверять boilerplate, calculator — ВСЕГДА верифицировать по theme.css

**НЕ НАЧИНАТЬ создание слайдов пока все уроки не прочитаны и не применены.**

Если работа делегируется субагентам:
- Использовать `references/subagent_prompt_template.md` для формирования промпта
- ВСЕ данные (ширины, opacity, font corrections, boilerplate, SVG) должны быть ВСТРОЕНЫ в промпт
- Субагенты НЕ вызывают Skill tool (L-14) — они получают всё через промпт
- Перед запуском — зарезервировать Y-координату в `_progress.md`
- По умолчанию использовать **safe parallel mode**: субагент готовит другую карусель локально (`HTML -> unified scripts -> contracts -> preflight`), а live `use_figma`, live audit, ingest и shared tracking остаются у главного агента
- Не делегировать субагенту обновление `_progress.md`, `BUG_REGISTRY.md`, `GENERATOR_QA_CHANGELOG.md` или запуск `ingest_live_audit.py`

## Unified 1-Script Pipeline (L-27, replaces old 4-Pass)

Каждый слайд = **1 вызов `use_figma`** (~160 строк, ~27 нод, 2-5 сек). HTML структура sacred — НИКОГДА не упрощать.

**Почему заменили 4-pass:**
- 4 скрипта x ~135 строк = ~540 строк кода на слайд, node ID зависимости между вызовами
- 1 скрипт x ~160 строк = atomic, no ID dependencies, 4 font loads вместо 16
- 27 нод на слайд = 2-5 секунд (далеко от 30-сек таймаута)

**Структура unified скрипта:**
```
1. Page nav + font load (только нужные шрифты, ~4)
2. Colors + helpers (sf, rgba, nf, ap, tx, spc)
3. Root frame (1080x1350, gradient, inner border, watermark)
4. slide__content (padding 54/60) → meta → page (space-between)
5. top-section: chip with INLINE SVG → title → subtitle ("FIXED") → content
6. Footer strip (cream 0.85, radius 16, dark text)
7. validate() + return { rootId }
```

**Критические правила unified подхода:**
- SVG иконки инлайнить СРАЗУ (не placeholder → replace), НО: clear `frame.strokes=[]` на SVG frame, стилить только children vectors (L-30)
- Subtitle/text width: использовать `"FIXED"` sizing, НЕ `"HUG"` — Figma игнорирует resize() при HUG (L-29)
- Equal-height cards в grid: `"FILL","FILL"` на карточках (CSS grid stretch behavior) (L-31)
- Badge/icon containers: explicit `resize()` ПОСЛЕ `appendChild` SVG child (L-32)
- Mixed-weight text (Bold + Medium): два отдельных text node в горизонтальном frame (L-33)
- Feature panels = CREAM CARDS с DARK TEXT (opacity 0.92), не transparent с white text (L-34)
- **Сохранить скрипт на диск ПЕРЕД execute** — никогда не импровизировать в use_figma (L-35)

**HTML layout = Figma layout.** page-row → HORIZONTAL. cover-grid → HORIZONTAL. Точка.

## 1. Quick Decision Matrix

Before any Figma work, determine the right tool:

| I want to... | Invoke skill first | Then use |
|---|---|---|
| Create nodes via Plugin API | `figma:figma-use` | `use_figma` MCP tool |
| Convert Figma design → HTML/CSS code | `figma:figma-implement-design` | `get_design_context` |
| Build full screen from design system | `figma:figma-generate-design` | `use_figma` + `search_design_system` |
| Create design system (variables, tokens) | `figma:figma-generate-library` | `use_figma` |
| Generate project rules for Figma | `figma:figma-create-design-system-rules` | writes CLAUDE.md rules |
| Map Figma components to code | `figma:figma-code-connect-components` | Code Connect tools |
| Import HTML pixel-perfect (one-off) | This skill → html.to.design | Figma plugin (12/month free) |
| Import HTML programmatically (batch) | This skill → unified 1-script pipeline | `use_figma` per slide |
| Upload photos to Figma | This skill → bridge workflow | `createImageAsync` via bridge |
| Batch create carousels | This skill → unified 1-script pipeline | `use_figma` per slide |

## 2. Plugin API Critical Rules

These rules apply to EVERY `use_figma` call. Violations cause silent bugs or crashes.

| # | Rule | Why |
|---|------|-----|
| 1 | **blur radius = CSS / 2** | CSS `blur(20px)` = Figma `radius: 10`. Figma measures diameter, CSS measures radius. |
| 2 | **Colors 0-1 range** | `{r: 0.769, g: 0.537, b: 0.431}` not `{r: 196, g: 137, b: 110}`. Divide by 255. |
| 3 | **`loadFontAsync` BEFORE text ops** | Set `fontName` before `characters`. Always `await`. Use `Promise.all()` for parallel. |
| 4 | **`setCurrentPageAsync` at START** | Page resets between calls. ALWAYS navigate first. Use `await`. |
| 5 | **Fills/strokes read-only** | Clone, modify, reassign: `node.fills = [{...}]`. Never mutate in place. |
| 6 | **`FILL`/`HUG` AFTER `appendChild`** | `layoutSizingHorizontal = "FILL"` throws if node not yet in auto-layout parent. |
| 7 | **`resize()` BEFORE `textAutoResize`** | Set text width first, then `textAutoResize = "HEIGHT"`. Prevents garbled rendering. |
| 8 | **Gradient stops: alpha IN color** | Gradient: `{r, g, b, a}`. Solid fill: `{r, g, b}` + separate `opacity`. |
| 9 | **`DROP_SHADOW` needs full params** | Always include `blendMode: "NORMAL"`, `spread: 0`, `visible: true`. |
| 10 | **`return` is output** | No `figma.notify()`, no `console.log()`. Only `return {...}`. |
| 11 | **Return ALL created node IDs** | `return { createdNodeIds: [root.id] }` at minimum. |
| 12 | **No async IIFE wrapper** | Code auto-wrapped. Use top-level `await`. |
| 13 | **`createImageAsync`/`fetch` BLOCKED** | In MCP runtime only. Use noemuch/bridge for images. |
| 14 | **50KB code limit** | `use_figma` rejects scripts >50KB. Keep scripts lean. |
| 15 | **Absolute positioning > auto-layout** | For pixel-perfect reproduction of HTML designs, use `layoutMode: "NONE"` with manual x/y. |
| 16 | **Subtitle: "FIXED" not "HUG"** | `resize(w,h)` is IGNORED when `layoutSizing*="HUG"`. Use `"FIXED"` to enforce max-width on text (L-29). |
| 17 | **SVG frame: clear strokes** | `createNodeFromSvg()` returns a FRAME. Set `frame.strokes=[]`, style only children vectors. Setting fills on stroke-only icons makes white squares (L-30). |
| 18 | **Equal-height cards: FILL,FILL** | CSS grid stretches cards in a row. Figma needs `"FILL","FILL"` on cards, not `"FILL","HUG"` (L-31). |
| 19 | **Badge resize AFTER SVG append** | SVG icon collapses parent frame to icon size. Explicit `resize(w,h)` AFTER appendChild (L-32). |
| 20 | **Mixed-weight text: separate nodes** | HTML `<strong>` = two text nodes in HORIZONTAL frame (Bold 0.88 + Medium 0.62) (L-33). |

For full examples with WRONG/CORRECT patterns: read `references/plugin_api_rules.md`.

## 3. VIP Design System (InstaCovers)

### Canvas
- **1080 x 1350px** (Instagram 4:5) — strictly enforced

### Colors (CSS hex → Figma 0-1)

| Variable | Hex | Figma {r, g, b} |
|----------|-----|-----------------|
| `--copper` | #C4896E | `{r:0.769, g:0.537, b:0.431}` |
| `--copper-light` | #d4a088 | `{r:0.831, g:0.627, b:0.533}` |
| `--copper-dark` | #a06a50 | `{r:0.627, g:0.416, b:0.314}` |
| `--sand` | #DEB7A4 | `{r:0.871, g:0.718, b:0.643}` |
| `--warm-clay` | #C4956A | `{r:0.769, g:0.584, b:0.416}` |
| `--mist-blue` | #C7D8E6 | `{r:0.780, g:0.847, b:0.902}` |
| `--warm-gray` | #A89B90 | `{r:0.659, g:0.608, b:0.565}` |
| `--cream` | #F5EDE7 | `{r:0.961, g:0.929, b:0.906}` |
| `--black` | #1A1714 | `{r:0.102, g:0.090, b:0.078}` |
| `--white` | #FEFCFA | `{r:0.996, g:0.988, b:0.980}` |
| Dark text | #2e2825 | `{r:0.180, g:0.157, b:0.145}` |
| Dark blue | #1f2932 | `{r:0.122, g:0.161, b:0.196}` |

### Fonts (loadFontAsync calls)

```javascript
await Promise.all([
  figma.loadFontAsync({ family: "Tenor Sans", style: "Regular" }),    // Headings 82-86px
  figma.loadFontAsync({ family: "Montserrat", style: "Medium" }),     // Meta 18px
  figma.loadFontAsync({ family: "Montserrat", style: "Regular" }),    // Body 17-24px
  figma.loadFontAsync({ family: "Montserrat", style: "Bold" }),       // Chips, titles 14-22px
  figma.loadFontAsync({ family: "Montserrat", style: "SemiBold" }),   // Footer hints 16px
  figma.loadFontAsync({ family: "Cormorant SC", style: "Regular" })   // Eyebrows 22px
]);
```

### 5 Palette Etalons

| Palette | Base Fill | Text on BG | Layout | Unique Element |
|---------|-----------|-----------|--------|----------------|
| COPPER | Solid #C4896E | White | Badge + lead + guide-panel | Guide panel with backdrop-blur cards |
| MIST-BLUE | Solid #C7D8E6 | **Dark #1f2932** | Grid + route-panel | Metro route strip with colored line |
| WARM-CLAY | Gradient 180deg | White | Simple vertical stack | No panels (simplest) |
| WARM-GRAY | Gradient 168deg | White + dark on panels | Grid + feature-panel | Feature items without icons |
| SAND | Solid #C9C0B8 | White + dark on panels | Grid + feature-panel | Taller grid, 2-line value |

For full etalon layer structures: read `references/etalon_structures.md`.
For CSS-to-Figma property mapping: read `references/css_to_figma_mapping.md`.

## 4. MCP Servers

### Official use_figma (MCP)
- Built-in to Claude Code Figma plugin
- Creates/edits Figma nodes programmatically
- **Limitations:** No `fetch()`, no `createImageAsync()`, 50KB code limit, 30s timeout

### figma-console-mcp (87+ tools)
- WebSocket bridge to Figma Desktop Plugin API
- **Setup:** Already registered as MCP server `figma-console`
- **Plugin:** Import manifest from `C:\Users\londo\.figma-console-mcp\plugin\manifest.json`
- `fetch()` and `createImageAsync()` WORK through this bridge
- Needed for: uploading photos, loading images, heavy operations

For bridge setup and usage: read `references/bridge_guide.md`.

## 5. Workflows

### A) HTML → Figma (one-off)
1. Create standalone HTML (all CSS inlined, no local @font-face)
2. Open Figma → Plugins → html.to.design → Editor tab
3. Paste HTML, set viewport 1080px → Create
4. Result: pixel-perfect editable layers

### B) HTML → Figma (batch/programmatic — unified 1-script)
1. Read HTML slide FULLY + both CSS files (theme.css + style_v3.css)
2. Extract all values from CSS (L-28 — CSS is ONLY source of truth)
3. Write 1 unified script per slide (~160 lines, ~27 nodes)
4. Save script to disk FIRST (L-35)
5. Execute via `use_figma`, verify with `get_screenshot`
6. Pattern per script: page nav → fonts → colors → helpers → root → content → meta → page → top-section → footer → validate → return

### C) Photo Slides (Night Cinema)
1. Apply Night Cinema filter: `python photos/_figma_export/apply_night_cinema.py`
2. Upload via bridge (`createImageAsync`) or manual drag-drop
3. Add overlay layers: vignette (5 stops), gradient, color overlay, grain

For full workflows: read `references/workflows.md`.
For Night Cinema details: read `references/night_cinema.md`.

## 6. Figma File Organization

- **File:** `8B1Dfaq8XtBOXlJuS19UhK`
- **Slides page:** "Посты Инстаграм Финал" (id: 1796:2)
- **Photos page:** "фото постов инстаграм финал" (id: 1883:2)
- **Layout:** Each carousel = horizontal row, slides left→right, 80px gap, 200px between rows
- **Naming:** `PALETTE · carousel_name · Slide N` (e.g., "WARM-CLAY · arab_traditions_v1 · Cover")

## 7. References Index

Load on demand — only when the specific topic is needed:

| Reference | When to load |
|-----------|-------------|
| `references/plugin_api_rules.md` | Before writing ANY `use_figma` script |
| `references/css_to_figma_mapping.md` | When converting CSS properties to Figma API |
| `references/etalon_structures.md` | When recreating etalon layouts |
| `references/workflows.md` | When planning a Figma production workflow |
| `references/bridge_guide.md` | When using figma-console-mcp or uploading images |
| `references/night_cinema.md` | When processing photos for Figma |
| `references/gotchas.md` | When debugging Figma API issues |
| `references/lessons-learned.md` | **BEFORE writing any slide script** — checklist + 35 process lessons |
| `references/css_width_calculator.md` | **BEFORE every slide** — exact text widths from CSS |
| `references/verification_checklist.md` | **AFTER every slide** — automated + manual checks |
| `references/batch_production.md` | When creating multiple carousels |
| `references/palette_registry.md` | **EVERY script** — 5 palettes (copper, mist-blue, warm-clay, warm-gray, sand) as copy-paste PALETTES JS object |
| `references/boilerplate.md` | **EVERY script** — standard code blocks, helpers, naming convention |
| `references/subagent_prompt_template.md` | **BEFORE spawning sub-agents** — complete prompt with all data embedded |
| `references/parallel_production_protocol.md` | **BEFORE parallel work** — Y-registry, conflict prevention, quality gate |

## 8. Parallel Production

Для параллельной работы нескольких агентов — читать `references/parallel_production_protocol.md`.

Ключевые правила:
- **Max 2 агента** на один Figma файл
- **Y-координаты** резервируются в `_progress.md` ПЕРЕД началом
- **Промпт субагента** формируется из `references/subagent_prompt_template.md` (все данные встроены)
- **Boilerplate код** из `references/boilerplate.md` — не переписывать, копировать
- **Quality gate** — слайд "done" только когда validate()=0, все SVG заменены, ширины из калькулятора

## 9. Experience System

After each Figma session, check if new lessons were learned:
- New pitfalls → add to `references/gotchas.md`
- New patterns → add to `references/plugin_api_rules.md`
- New tool findings → update decision matrix

Experience log: `experience/_index.md`
