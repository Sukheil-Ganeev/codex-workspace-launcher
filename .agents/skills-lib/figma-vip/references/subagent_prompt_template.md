# Sub-Agent Prompt Template

Этот шаблон используется для создания промптов параллельных субагентов.
Заполнить переменные в `{{...}}` и отправить субагенту ЦЕЛИКОМ.

---

## Актуальный статус (2026-03-29)

- Ниже сохранён **legacy 4-pass prompt** для старых сессий и разборов, но это уже не основной production-путь.
- Текущий рекомендуемый режим для субагента: **safe parallel mode**.
- В safe parallel mode субагент делает только локальную подготовку другой карусели:
  - читает HTML/CSS
  - проверяет или регенерирует `unified.js`
  - запускает `build_slide_contracts.py`
  - запускает `figma_preflight_qa.py`
  - при необходимости готовит черновой production note по своей карусели
- В safe parallel mode субагент **не делает**:
  - live `use_figma` write
  - `generate_live_audit.py` + `ingest_live_audit.py`
  - обновление `_progress.md`, `BUG_REGISTRY.md`, `GENERATOR_QA_CHANGELOG.md`
- Если всё-таки делегируется live Figma write, legacy 4-pass блок ниже нельзя использовать как есть: его нужно заменить на текущий `unified 1-script + contract/live-audit` workflow, а финальный live audit, ingest и shared docs всё равно остаются у главного агента.

## Рекомендуемый safe prompt для субагента

````
FIGMA SOURCE PREP TASK — {{CAROUSEL_NAME}}

You are a sidecar worker. You are NOT the live Figma writer for this run.

Your job is limited to local prep on disjoint files for this carousel:
1. inspect HTML/CSS and existing unified scripts
2. regenerate or patch `docs/figma-analysis/scripts/{{CAROUSEL_SHORT}}/slide_*_unified.js` if needed
3. run `python scripts/build_slide_contracts.py templates/carousel/{{CAROUSEL_NAME}}`
4. run `python scripts/figma_preflight_qa.py templates/carousel/{{CAROUSEL_NAME}} --start {{START}} --end {{END}}`
5. summarize real fails/warns and list the exact files you changed

Do NOT:
- call `use_figma`
- run `generate_live_audit.py`
- run `ingest_live_audit.py`
- edit `_progress.md`, `BUG_REGISTRY.md`, `GENERATOR_QA_CHANGELOG.md`

Return:
- changed files
- preflight summary by slide
- unresolved risks that the main agent must verify live
````

---

## Шаблон промпта

````
FIGMA PRODUCTION TASK — {{CAROUSEL_NAME}} ({{TOTAL_SLIDES}} slides)

You will create slides in Figma using `use_figma` MCP tool.
Each slide = exactly 4 calls to use_figma (Pass 1, 2, 3, 4). NO exceptions.
HTML structure is SACRED — NEVER simplify layout to avoid timeouts.

═══════════════════════════════════════════════════
FIGMA CONNECTION
═══════════════════════════════════════════════════
File ID: 8B1Dfaq8XtBOXlJuS19UhK
Page: Посты Инстаграм Финал (node 1796:2)
Y position: {{Y_POSITION}}
X step: 1180 (slide width 1080 + gap 100)

═══════════════════════════════════════════════════
FONT WEIGHT CORRECTIONS (ОБЯЗАТЕЛЬНО)
═══════════════════════════════════════════════════
| Role | CSS weight | Figma weight | Montserrat style |
|------|-----------|-------------|-----------------|
| Meta (counter, handle) | 500 | **600** | SemiBold |
| Chip/button text | 700 | **800** | ExtraBold |
| Body (subtitle, copy) | 400 | **500** | Medium |
| Card title | 700 | **700** | Bold (no change) |
| Title (Tenor Sans) | 400 | **400** | Regular (no change) |
| Eyebrow (Cormorant SC) | 400 | **400** | Regular (no change) |

═══════════════════════════════════════════════════
OPACITY TABLE (ОБЯЗАТЕЛЬНО)
═══════════════════════════════════════════════════
| Element | Opacity |
|---------|---------|
| meta__counter, meta__handle | 0.84 |
| page__subtitle, content-page__subtitle | 0.86 |
| eyebrow (Cormorant SC) | 0.76 |
| place-card__text, tip-card__text | 0.66 |
| footer-banner__title | 0.95 |
| footer-banner__text, footer-note__text | 0.86 |
| footer-note__hint | 0.90 |
| watermark | 0.045 |
| service-line | 0.74 |
| cta-eyebrow | 0.78 |
| section-chip__text | 0.96 |
| page__title, content-page__title | 0.98 |

═══════════════════════════════════════════════════
CSS WIDTH TABLE (все ширины рассчитаны, НЕ угадывать)
═══════════════════════════════════════════════════
Content area: 952px (1080 - 64*2)

Full-width slides:
- content-page__title: 560px
- content-page__subtitle: 560px
- footer-banner__text: 718px
- footer-banner__title: 170px

Split layout (title + stat-card):
- Left column: 548px (924 * 1.05/1.77)
- content-page__subtitle in split: 520px
- Stat-card width: 376px
- Stat-card inner text: 320px (376 - 28*2)

Cover layout (title + pass-panel):
- page__title: 520px
- page__subtitle: 520px
- Pass-panel inner: 340px (400 - 28 - 32)
- Note-card text: 350px (474 - 56 - 68)
- footer-note__text: 328px

Place card text: 842px (FILL from parent)
Tip card text: 371px (half-width: 469 - 40 - 58)
CTA text: 620px
Service line: 720px

═══════════════════════════════════════════════════
BOILERPLATE CODE (копировать в каждый use_figma)
═══════════════════════════════════════════════════

--- Page navigation (FIRST LINE ALWAYS) ---
const pages = figma.root.children;
await figma.setCurrentPageAsync(pages.find(p => p.name === "Посты Инстаграм Финал") || pages[0]);

--- Font loading ---
const F = {
  tenor: { family: "Tenor Sans", style: "Regular" },
  corm: { family: "Cormorant SC", style: "Regular" },
  montM: { family: "Montserrat", style: "Medium" },
  montSB: { family: "Montserrat", style: "SemiBold" },
  montB: { family: "Montserrat", style: "Bold" },
  montEB: { family: "Montserrat", style: "ExtraBold" }
};
await Promise.all([
  figma.loadFontAsync(F.tenor), figma.loadFontAsync(F.corm),
  figma.loadFontAsync(F.montM), figma.loadFontAsync(F.montSB),
  figma.loadFontAsync(F.montB), figma.loadFontAsync(F.montEB)
]);

--- Colors (0-1 range) ---
const C = {
  white: { r: 0.996, g: 0.988, b: 0.980 },
  ink: { r: 0.102, g: 0.090, b: 0.078 },
  warmClay: { r: 0.769, g: 0.584, b: 0.416 },
  warmClayDeep: { r: 0.710, g: 0.541, b: 0.353 },
  cream: { r: 0.961, g: 0.929, b: 0.906 },
  copperDark: { r: 0.627, g: 0.416, b: 0.314 }
};

--- Helpers ---
function sf(c, o) { return [{ type: "SOLID", color: c, opacity: o ?? 1 }]; }
function rgba(c, a) { return { r: c.r, g: c.g, b: c.b, a }; }
function nf(name, mode) {
  const f = figma.createFrame(); f.name = name;
  f.layoutMode = mode || "VERTICAL"; f.fills = []; f.clipsContent = false;
  return f;
}
function ap(p, c, h, v) {
  p.appendChild(c);
  if (h) c.layoutSizingHorizontal = h;
  if (v) c.layoutSizingVertical = v;
  return c;
}
function tx(name, value, font, size, color, opacity, opts) {
  const t = figma.createText(); t.name = name; t.fontName = font;
  t.characters = value; t.fontSize = size; t.fills = sf(color, opacity ?? 1);
  if (opts) {
    if (opts.w) { t.resize(opts.w, 10); t.textAutoResize = "HEIGHT"; }
    else { t.textAutoResize = "WIDTH_AND_HEIGHT"; }
    if (opts.lh) t.lineHeight = { value: opts.lh, unit: "PIXELS" };
    if (opts.ls) t.letterSpacing = { value: opts.ls, unit: "PIXELS" };
    if (opts.tc) t.textCase = opts.tc;
    if (opts.al) t.textAlignHorizontal = opts.al;
  }
  return t;
}
function spc(h) { const s = nf("sp-" + h, "NONE"); s.resize(1, h); return s; }

--- Validate (ALWAYS at end of Pass 1 and Pass 3) ---
function validate(root) {
  const issues = [];
  function check(n) {
    if (n.type === "FRAME" && n.height === 100 && n.layoutMode !== "NONE" && !n.name.startsWith("sp")) {
      issues.push(n.name + ":h=100"); n.resize(n.width, 10); n.layoutSizingVertical = "HUG";
    }
    if (n.type === "FRAME" && n.width === 100 && n.clipsContent)
      issues.push(n.name + ":w=100+clip");
    if (n.type === "RECTANGLE" && n.name.includes("placeholder"))
      issues.push(n.name + ":placeholder");
    if ("children" in n) n.children.forEach(check);
  }
  check(root);
  return issues;
}

═══════════════════════════════════════════════════
NAMING CONVENTION (ОБЯЗАТЕЛЬНО — иначе Pass 3 не найдёт placeholder'ы)
═══════════════════════════════════════════════════
Root: {{carousel}}_slide_{{N}}
Content: slide__content
Meta: meta, meta__counter, meta__handle
Chip: section-chip, section-chip__text, chip-icon-placeholder
Title: page__title / content-page__title
Subtitle: page__subtitle / content-page__subtitle
Place card: place-card, place-card__copy, place-card__title, place-card__text
Card icon: card-icon-placeholder (rect 50x50 cornerRadius=16)
Tip card: tip-card, tip-card__copy, tip-card__title, tip-card__text
Tip icon: tip-icon-placeholder (rect 44x44 cornerRadius=14)
Footer: footer-banner, footer-banner__title, footer-banner__text
Stat card: stat-card, stat-card__eyebrow, stat-card__value, stat-card__text
Watermark: watermark
Border: inner-border
Spacer: sp-{height}

═══════════════════════════════════════════════════
4-PASS PIPELINE (СТРОГО)
═══════════════════════════════════════════════════

PASS 1 — Shell (~12 nodes, НИКОГДА не таймаутит):
- Root frame 1080x1350 + gradient fills
- Inner border + watermark
- slide__content container + meta bar + spacer
- Chip (с placeholder icon)
- Title + subtitle
- ПУСТЫЕ layout containers: page-row/cover-grid (HORIZONTAL) + left column + right column + footer
- validate(root)
- RETURN: { rootId: root.id, leftId: left.id, rightId: right.id, footerId: footer.id }

PASS 2 — Left Column (~10-15 nodes):
- getNodeByIdAsync(leftId)
- Fill depends on slide type: metrics, cards, stat-card, note-card, eyebrow, rule
- All icons as placeholder rectangles
- RETURN: { leftDone: true, itemCount: N }

PASS 3 — Right Column + Footer (~10-15 nodes):
- getNodeByIdAsync(rightId) → panels, feature-lists, info-cards
- getNodeByIdAsync(footerId) → footer-strip / footer-banner / save-chip + footer-note
- All icons as placeholder rectangles
- RETURN: { rightDone: true, footerDone: true }

PASS 4 — Polish (~5-10 nodes):
- Replace ALL placeholder icons with SVG (createNodeFromSvg)
  - card-icon-placeholder (rect 50x50, r=16) → Frame 50x50 + SVG 24x24 at (13,13)
  - tip-icon-placeholder (rect 44x44, r=14) → Frame 44x44 + SVG 22x22 at (11,11)
  - chip-icon-placeholder (rect 18x18, r=9) → SVG 18x18 (replace entirely)
- validate(root) — h=100, w=100+clip, text overflow, remaining placeholders
- Width audit — check all text widths vs css_width_calculator
- RETURN: { svgsReplaced: N, issues: [...], widthFixes: N }

RULE: HTML layout = Figma layout. NEVER simplify page-row to vertical stack.
RULE: If >15 nodes in a pass → split into 2 sub-passes. NEVER drop components.

═══════════════════════════════════════════════════
SLIDE DATA
═══════════════════════════════════════════════════

{{SLIDE_DATA_HERE — for each slide: type, num, chip text, chip SVG, title, subtitle, cards/tips data, footer text, card SVGs}}

═══════════════════════════════════════════════════
ERROR HANDLING
═══════════════════════════════════════════════════
- Timeout (fetch failed): retry once. If still fails, split Pass into 2 sub-passes.
- 502 Bad Gateway: wait 60 sec, retry. Max 3 retries.
- validate() finds issues: fix in same call (h=100 → resize+HUG). Don't create new call.
- NEVER skip SVG icons. NEVER skip validate(). NEVER guess widths.

═══════════════════════════════════════════════════
QUALITY GATE — slide is "done" when ALL true:
═══════════════════════════════════════════════════
- [ ] validate() returns 0 issues
- [ ] All text widths match CSS calculator (±5px)
- [ ] All SVG icons replaced (0 placeholders)
- [ ] Root = 1080x1350
- [ ] Content padding = 56/64
- [ ] Footer at bottom (SPACE_BETWEEN on page)
- [ ] Meta bar present
- [ ] Watermark present (opacity 0.045)
- [ ] Inner border present
````

---

## Как использовать шаблон

### Шаг 1: Извлечь данные из HTML

Для каждого слайда прочитать HTML и извлечь:
- Тип (cover / content / content-split / tips / cta)
- Номер ("01 / 08")
- Chip текст + SVG путь
- Title текст + font-size
- Subtitle текст
- Карточки: title + text + SVG путь для каждой
- Footer title + text
- Stat-card данные (если split)

### Шаг 2: Заполнить шаблон

Заменить все `{{...}}` переменные:
- `{{CAROUSEL_NAME}}` → `family_places_v1`
- `{{TOTAL_SLIDES}}` → `8`
- `{{Y_POSITION}}` → `28800`
- `{{SLIDE_DATA_HERE}}` → извлечённые данные

### Шаг 3: Запустить субагента

```javascript
Agent({
  prompt: ЗАПОЛНЕННЫЙ_ШАБЛОН,
  mode: "bypassPermissions",
  run_in_background: true,
  name: "figma-family-places"
})
```

### Шаг 4: Проверить результат

После завершения субагента:
1. get_screenshot для каждого слайда
2. Сверить с HTML оригиналом
3. Если проблемы → точечный fix (не пересоздание)

---

## Пример заполненного SLIDE_DATA

```
[slide_1]
type: cover
num: "01 / 08"
chip_text: "СЕМЕЙНЫЙ ГИД"
chip_svg: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26"/></svg>'
title: "ДУБАЙ\nС ДЕТЬМИ\n10 МЕСТ"
title_size: 84
subtitle: "Парки с кондиционером, аквапарки мирового уровня, бесплатные пляжи и фонтаны. Всё проверено на месте."
eyebrow: "СОХРАНИ ПЕРЕД ПОЕЗДКОЙ"
note_card_title: "Зачем этот гид"
note_card_text: "Показываем, куда реально стоит идти с детьми, что бесплатно и где не потеряться."
note_card_svg: '<svg viewBox="0 0 24 24" fill="none" stroke="#a06a50" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'
panel_label: "ЧТО ВНУТРИ"
panel_label_svg: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8"><path d="M3 12h18"/><path d="m13 5 8 7-8 7"/></svg>'
panel_value: "ПАРКИ\nПЛЯЖИ\nПРИРОДА"
panel_copy: "Крытые парки для лета, аквапарки с детскими зонами, бесплатные активности и лайфхаки для экономии."
save_chip_text: "СОХРАНИ ЭТОТ ГИД"
save_chip_svg: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8"><path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1Z"/></svg>'
footer_title: "СЛЕДОМ ПОКАЖЕМ"
footer_text: "куда идти в жару, что бесплатно\nи как сэкономить на парках"
footer_hint: "Листай →"

[slide_2]
type: content
num: "02 / 08"
chip_text: "КРЫТЫЕ ПАРКИ"
chip_svg: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8"><path d="M6 17 12 5l6 12"/><path d="M9.5 12.5h5"/></svg>'
title: "ПАРКИ\nРАЗВЛЕЧЕНИЙ"
title_size: 76
subtitle: "Все три крытые, с кондиционером. Идеальны для лета и на целый день."
cards:
  - title: "IMG Worlds of Adventure"
    text: "Крупнейший крытый парк в мире. Marvel, динозавры, Cartoon Network. Хватит на весь день."
    svg: '<svg viewBox="0 0 24 24" fill="none" stroke="#a06a50" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 3v18"/><path d="M15 3v18"/><path d="M3 9h18"/><path d="M3 15h18"/></svg>'
  - title: "Legoland Dubai"
    text: "Для детей 2-12 лет. 15 000+ моделей LEGO, дети водят машины и тушат пожары."
    svg: '<svg viewBox="0 0 24 24" fill="none" stroke="#a06a50" stroke-width="1.8"><rect x="4" y="14" width="4" height="6" rx="1"/><rect x="10" y="10" width="4" height="10" rx="1"/><rect x="16" y="6" width="4" height="14" rx="1"/></svg>'
  - title: "Motiongate Dubai"
    text: "Голливудский парк: Шрек, Мадагаскар, Кунг-фу Панда. Для детей от 5 лет."
    svg: '<svg viewBox="0 0 24 24" fill="none" stroke="#a06a50" stroke-width="1.8"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/></svg>'
footer_title: "ОБЩЕЕ ПРАВИЛО"
footer_text: "Все три парка крытые, поэтому жара не мешает. Один парк = один полный день. Не пытайтесь совместить два."
```
