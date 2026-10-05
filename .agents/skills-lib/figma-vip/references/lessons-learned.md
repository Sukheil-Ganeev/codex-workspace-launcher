# Lessons Learned — HTML→Figma Production

Процессные уроки из реального создания карусельных слайдов в Figma.
Каждый урок: Problem → Root Cause → Rule.

---

## 1. Source of Truth

### L-01: CSS — источник, не эталон

**Problem:** Базовый цвет фона был неправильным (149 вместо 137 в green-канале).
**Root Cause:** Скопировали gradient из эталона (Figma import), а не из CSS оригинала.
**Rule:** Всегда брать значения из `theme.css` + `style_v3.css`. Эталоны — только для проверки структуры, НЕ для цветов/размеров.

### L-02: Дочитывай HTML до конца

**Problem:** Не увидели footer structure, пропустили SVG-пути иконок.
**Root Cause:** Читали только первые 80 строк HTML.
**Rule:** Всегда читать HTML файл ПОЛНОСТЬЮ. Каждый элемент = нода в Figma.

### L-03: style_v3.css содержит глобальные стили

**Problem:** Не проверили базовые стили (color, font-family наследование).
**Root Cause:** theme.css импортирует style_v3.css, но мы его не читали.
**Rule:** При первом слайде новой карусели — прочитать ОБА CSS файла.

---

## 2. Font Weights

### L-04: CSS weights тоньше на цветном фоне

**Problem:** Текст в Figma выглядел тоньше чем в HTML.
**Root Cause:** Figma и браузер рендерят шрифты по-разному. На цветном фоне CSS weight 400 выглядит как 300.
**Rule:** Применять коррекцию жирностей:

| Роль | CSS | Figma | Montserrat style |
|------|-----|-------|-----------------|
| Meta (counter, handle) | 500 | **600** | SemiBold |
| Chip/button text | 700 | **800** | ExtraBold |
| Body (subtitle, copy, footer text) | 400 | **500** | Medium |
| Card title | 700 | **700** | Bold (без изменений) |
| Title (Tenor Sans) | 400 | **400** | Regular (без изменений) |
| Eyebrow (Cormorant SC) | 400 | **400** | Regular (без изменений) |

**Файл коррекций:** `D:/Downloads/InstaCovers/docs/figma-data/font_weight_corrections.md`

---

## 3. Figma API Traps

### L-05: FILL/HUG только ПОСЛЕ appendChild

**Problem:** `Error: FILL can only be set on children of auto-layout frames`
**Root Cause:** Устанавливали `layoutSizingHorizontal = "FILL"` до добавления в родитель.
**Rule:** Паттерн: `parent.appendChild(child); child.layoutSizingHorizontal = "FILL";` — ВСЕГДА в этом порядке.

### L-06: Wrapper-фреймы дефолтят в 100px + clipsContent

**Problem:** Chip/кнопки стали 100px высотой, eyebrow текст обрезался.
**Root Cause:** Figma создаёт фрейм 100x100 по умолчанию. `clipsContent = true` по умолчанию. Если не установить HUG после append — фрейм остаётся 100px и обрезает содержимое.
**Rule:** Хелпер `mkW()` НЕ должен ставить sizing. Ставить ПОСЛЕ append. Отключать `clipsContent` на wrapper-фреймах.

**Безопасный паттерн:**
```javascript
function mkW(pt) {
  const f = figma.createFrame();
  f.fills = [];
  f.layoutMode = "VERTICAL";
  f.paddingTop = pt;
  f.clipsContent = false; // ВАЖНО
  return f;
}
// Использование:
const w = mkW(24);
w.appendChild(child);
parent.appendChild(w);
w.layoutSizingHorizontal = "FILL"; // ПОСЛЕ append
w.layoutSizingVertical = "HUG";   // ПОСЛЕ append
```

### L-07: paddingTop нельзя ставить на Text-ноды

**Problem:** `TypeError: object is not extensible`
**Root Cause:** Text-ноды не имеют свойства `paddingTop`. Padding — свойство auto-layout фреймов.
**Rule:** Для spacing между текстами — wrapper-фрейм с paddingTop, никогда на самом тексте.

### L-08: createNodeFromSvg() работает — используй его

**Problem:** Иконки были заменены серыми прямоугольниками.
**Root Cause:** Предположили что SVG нельзя вставить через Plugin API.
**Rule:** `figma.createNodeFromSvg(svgString)` создаёт полноценную векторную ноду. SVG-пути брать прямо из HTML. Формат:
```javascript
const icon = figma.createNodeFromSvg('<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8"><path d="..."/></svg>');
icon.resize(18, 18);
```

---

## 4. Process

### L-09: Автопроверка в конце каждого скрипта

**Problem:** Баги обнаруживались только визуально после создания.
**Root Cause:** Нет валидации внутри скрипта.
**Rule:** Добавлять в конец скрипта проверку:
```javascript
// VALIDATION
const issues = [];
function validate(n) {
  if (n.type === "FRAME") {
    if (n.height === 100 && n.layoutSizingVertical !== "FIXED")
      issues.push(`${n.name}: height stuck at 100`);
    if (n.width === 100 && n.clipsContent && n.layoutSizingHorizontal === "FIXED")
      issues.push(`${n.name}: width 100 + clipping`);
  }
  if ("children" in n) n.children.forEach(validate);
}
validate(root);
return { createdNodeIds: [root.id], issues };
```

### L-10: Grid overlay — ограничение Figma

**Problem:** CSS `background-size: 64px 64px` создаёт повторяющуюся сетку. Figma не поддерживает tiling gradients.
**Root Cause:** Figma gradients не повторяются.
**Rule:** Принять как допустимое расхождение. Визуально малозаметно (opacity 0.18 * 0.03 alpha). Если нужна точность — экспортировать grid как PNG tile и использовать image fill.

### L-11: Negative margins не поддерживаются в auto-layout

**Problem:** CSS `margin-left: -8px` на pass-panel нельзя воспроизвести.
**Root Cause:** Figma auto-layout не поддерживает отрицательные margins.
**Rule:** Принять как допустимое расхождение или использовать absolute positioning для элемента с offset.

---

## 5. Script Organization

### L-12: sf() хелпер экономит код

**Problem:** `[{type:"SOLID",color:{...W},opacity:0.14}]` повторяется 15+ раз.
**Root Cause:** Нет хелпера для создания fills.
**Rule:** Использовать:
```javascript
function sf(c, o) { return [{type: "SOLID", color: c, opacity: o || 1}]; }
// Использование: node.fills = sf(W, 0.14);
```

### L-13: Spread не нужен для цветов

**Problem:** `{...W}` создаёт лишние объекты.
**Root Cause:** Figma API не мутирует переданные цвета.
**Rule:** Использовать `W` напрямую вместо `{...W}`. Экономит ~80 байт и GC pressure.

---

## 6. Subagent Production

### L-14: Субагенты НЕ читают скиллы автоматически

**Problem:** Субагенты не загрузили figma-vip skill несмотря на инструкцию в промпте.
**Root Cause:** Субагенты не умеют вызывать Skill tool. Инструкция "загрузи скилл" для них бессмысленна.
**Rule:** Включать СОДЕРЖИМОЕ скилла (ключевые правила, коррекции, checklist) прямо в промпт субагента. Не надеяться что они сами прочитают файлы.

### L-15: Scan → Save → Fix → Verify

**Problem:** Данные скана теряются при сжатии контекста. Повторные обращения к Figma API.
**Root Cause:** Результаты не сохраняются на диск.
**Rule:** Всегда сохранять результат скана в `production-log/{carousel}_scan.md` ПЕРЕД началом исправлений. Один scan → файл → все фиксы по файлу → один verify.

### L-16: Flat layout — системная проблема субагентов

**Problem:** Субагенты создают все элементы напрямую в root через абсолютное позиционирование (x/y). Нет вложенного auto-layout дерева.
**Root Cause:** Flat layout проще генерировать — не нужно думать о FILL/HUG/appendChild порядке.
**Rule:** В промпте для субагентов ЯВНО требовать nested structure: root → decorations + content(VERTICAL) → meta(HORIZONTAL) → page(VERTICAL,FILL) → hero + cards + footer.

### L-17: Opacity 1.0 — системная проблема субагентов

**Problem:** ВСЕ тексты субагентов имеют opacity 1.0. CSS требует разные значения.
**Root Cause:** Субагенты не знают про CSS opacity значения.
**Rule:** Включать таблицу opacity В промпт субагента:
- meta: 0.82
- subtitle/body: 0.86
- card meta: 0.66
- footer title: 0.95
- footer text: 0.86
- watermark: 0.045
- service line: 0.74
- CTA eyebrow: 0.78

### L-18: Batch fix — проверенный подход

**Problem:** Как чинить 7 слайдов с 10+ проблемами на каждом?
**Root Cause:** Нужен системный подход.
**Rule:** Один скрипт на слайд через `use_figma`:
1. Загрузить нужные шрифты (SemiBold, ExtraBold, Medium, Bold)
2. `getNodeByIdAsync` конкретной ноды
3. Рекурсивный обход: чинить fonts → opacities → h=100 → w=100 → clipping
4. Verify после фикса
5. Return count fixes + remaining issues

### L-19: Один слайд = один use_figma вызов
**Problem:** Batch-скрипт на 8 слайдов (26KB) вызывает таймаут Figma API (30 сек).
**Root Cause:** Каждый createFrame, createText, createNodeFromSvg занимает время. 8 слайдов x 20+ нод = timeout.
**Rule:** Создавать СТРОГО один слайд за один вызов `use_figma`. Для карусели из 8 слайдов = 8 отдельных вызовов. Никогда не пытаться создать всю карусель за раз.

### L-20: createNodeFromSvg() добавляет время — выносить в отдельный pass
**Problem:** Скрипт с 4 SVG-иконками (star, arrow, clock, bookmark) + полная структура слайда = timeout.
**Root Cause:** SVG parsing дорогая операция. 4 SVG + 30+ нод = превышает 30 сек.
**Rule:** УСТАРЕЛО с L-27. При unified подходе (~27 нод) SVG инлайнятся сразу — не нужен отдельный pass. Но если слайд имеет >6 SVG иконок и >35 нод — разбить на 2 вызова.

### L-21: validate() ловит реальные баги — НЕ пропускать
**Problem:** cover-footer и footer-note застряли на h=100, визуально footer провалился вниз.
**Root Cause:** Фреймы создаются 100x100 по умолчанию. Без validate() баг остался бы незамеченным.
**Rule:** ВСЕГДА включать validate() в конец КАЖДОГО скрипта. Паттерн:
```javascript
const issues=[];
function validate(n){
  if(n.type==="FRAME"&&n.height===100&&n.layoutMode!=="NONE"&&!n.name.startsWith("sp"))
    issues.push(n.name+":h=100");
  if(n.type==="FRAME"&&n.width===100&&n.clipsContent)
    issues.push(n.name+":w=100+clip");
  if("children" in n)n.children.forEach(validate);
}
validate(root);
return{createdNodeIds:[root.id],issues};
```
Если issues не пустой — сразу второй вызов для фикса.

### L-22: Ширина текста должна учитывать padding родителя
**Problem:** Subtitle и pass-panel__copy обрезались справа — текст выходил за границы панели.
**Root Cause:** Текст имел width:520px но находился внутри panel с padding 28+32=60px и шириной 380px. Доступная ширина = 380-60 = 320px, а не 520.
**Rule:** Формула ширины текста: `parent.width - parent.paddingLeft - parent.paddingRight - extra_margins`. Для cover-grid левая колонка: ~520px (60% от 960). Для pass-panel: 380 - 28 - 32 = 320px max для текста внутри.

### L-23: Spacer-фреймы для CSS margin-top
**Problem:** CSS margin-top нельзя напрямую перенести в Figma auto-layout.
**Root Cause:** Figma auto-layout использует itemSpacing (одинаковый для всех детей). CSS margin-top разный у каждого элемента.
**Rule:** Использовать spacer-фреймы с itemSpacing=0 на родителе:
```javascript
function spc(h){const s=fr("sp","NONE");s.resize(1,h);s.fills=[];return s}
// В родителе: itemSpacing=0, затем spc(36) между meta и page, spc(40) перед grid, и т.д.
```
Это точнее чем единый itemSpacing и позволяет 1:1 маппинг CSS margin-top.

### L-24: Стандартный 4-pass pipeline — УСТАРЕЛ, заменён L-27

**Problem:** 4-pass pipeline работал но был over-engineered: ~540 строк на слайд, node ID зависимости между вызовами, 16 font loads вместо 4.
**Root Cause:** Предполагали что 27 нод = таймаут. На практике 27 нод = 2-5 секунд (далеко от 30-сек лимита).
**Rule:** Заменён на **Unified 1-Script Pipeline** (L-27). 4-pass оправдан ТОЛЬКО для слайдов с >40 нодами или >6 SVG иконок.

### L-25: HTML структура — sacred, таймаут ≠ упрощение

**Problem:** При таймауте я "упрощал" структуру — убирал page-row split, клал всё в одну колонку, терял компоненты. Slide 3 и 4 fountains_dubai потеряли двухколоночный layout.
**Root Cause:** Рефлекс "сделать проще чтобы влезло в лимит" вместо "разбить на больше pass'ов".
**Rule:**
1. HTML layout = Figma layout. НИКОГДА не менять page-row на vertical stack, не убирать split columns, не выкидывать компоненты
2. Если таймаут — увеличить количество pass'ов (2-3), НЕ уменьшать количество компонентов
3. Каждый компонент из HTML ОБЯЗАН быть в Figma. Пропуск = баг
4. Перед каждым pass — пересчитать: сколько нод создаю? Если >15 — разбить на 2 pass'а

### L-26: Подготовь всё ПЕРЕД Figma — никогда не импровизируй

**Problem:** Скрипты писались на ходу прямо в use_figma вызове. Каждый раз — новая импровизация, новые ошибки, забытые компоненты, неправильные ширины.
**Root Cause:** Нет этапа подготовки. Сразу прыгаю в Figma API без готовых скриптов.
**Rule:**
1. НИКОГДА не писать код прямо в use_figma. Сначала подготовить скрипт на диск
2. Pipeline: read HTML + CSS → write unified script → save to disk → review → execute in Figma
3. Аналогия: подготовь всю почву перед тем как сажать семя

---

## 7. Unified Pipeline (Session 5)

### L-27: Unified script > 4-pass pipeline

**Problem:** 4-pass pipeline = ~540 строк на слайд, node ID зависимости, 16 font loads, сложная координация между pass'ами.
**Root Cause:** Переоценили количество нод и время выполнения. На практике ~27 нод = 2-5 секунд (далеко от 30-сек таймаута).
**Rule:** 1 unified script per slide (~160 строк):
1. Page nav + font load (только нужные, ~4)
2. Colors + helpers (sf, rgba, nf, ap, tx, spc)
3. Root frame (1080x1350, gradient, inner border, watermark)
4. slide__content (padding 54/60) → meta → page (space-between)
5. top-section: chip with INLINE SVG → title → subtitle ("FIXED") → content
6. Footer strip (cream 0.85, radius 16, dark text)
7. validate() + return { rootId }

**Преимущества:** atomic (all-or-nothing), no ID dependencies, 4 font loads вместо 16, проще отлаживать.

### L-28: CSS — ЕДИНСТВЕННЫЙ source of truth (не boilerplate, не calculator)

**Problem:** Boilerplate говорил padding 64px, calculator считал content area 952px — а CSS говорит padding 60px, content area 960px. Все ширины были смещены на 8px.
**Root Cause:** Boilerplate и calculator были написаны по памяти/приблизительно, не сверены с CSS.
**Rule:** ВСЕГДА верифицировать КАЖДОЕ значение по theme.css и style_v3.css. Boilerplate и calculator — удобные shortcuts, но могут врать. При расхождении — CSS побеждает.

### L-29: Subtitle/text width: "FIXED" sizing, не "HUG"

**Problem:** `resize(560, 10)` на subtitle игнорировалось — текст растягивался на всю ширину.
**Root Cause:** При `layoutSizingHorizontal = "HUG"` Figma игнорирует `resize()`. Width определяется содержимым.
**Rule:** Для ограничения ширины текста: использовать `"FIXED"` sizing, затем `resize(maxWidth, h)`, затем `textAutoResize = "HEIGHT"`. НЕ `"HUG"`.

### L-30: SVG frame: clear strokes, style only children vectors

**Problem:** Иконки превращались в белые квадраты после стилизации.
**Root Cause:** `createNodeFromSvg()` возвращает FRAME. Установка fills на frame (а не на child vector) закрашивает весь frame белым. Stroke-only иконки имеют fills=[] на vectors — добавление fills делает их solid white.
**Rule:**
1. `createNodeFromSvg()` возвращает frame — НЕ стилить frame напрямую
2. `frame.strokes = []` — убрать дефолтную обводку frame
3. Итерировать `frame.children` → найти Vector/Line ноды → стилить их
4. Для stroke-only иконок: менять `strokes`, НЕ `fills`
5. Для fill-only иконок: менять `fills`

### L-31: Equal-height cards: "FILL","FILL" в grid rows

**Problem:** Карточки в одном ряду имели разную высоту — одна выше, другая ниже.
**Root Cause:** CSS grid автоматически растягивает карточки до высоты ряда. Figma с `"FILL","HUG"` не делает этого — каждая карточка имеет свою высоту.
**Rule:** Для карточек в горизонтальном ряду: `ap(row, card, "FILL", "FILL")`. Это аналог CSS `align-items: stretch` в grid.

### L-32: Badge/icon containers: explicit resize() ПОСЛЕ SVG append

**Problem:** Badge frame (64x64) коллапсировал до размера SVG иконки (24x24) после appendChild.
**Root Cause:** SVG child определяет размер parent frame при HUG sizing. Frame "схлопывается" до размера содержимого.
**Rule:** После `badgeFrame.appendChild(svgIcon)` — ВСЕГДА вызвать `badgeFrame.resize(64, 64)` явно. Не полагаться на то что предыдущий resize сохранится.

### L-33: Mixed-weight text: split into separate text nodes

**Problem:** Строка "Сервис: круглосуточно" — "Сервис:" должен быть Bold, "круглосуточно" Regular.
**Root Cause:** Figma Plugin API не поддерживает mixed fontName в одном text node через simple API (нужен setRangeFontName).
**Rule:** Создать HORIZONTAL frame с 2 text nodes:
- Text 1: "Сервис: " — Bold, opacity 0.88
- Text 2: "круглосуточно" — Medium, opacity 0.62
- Frame: itemSpacing=0, fills=[], counterAxisAlignItems="CENTER"

### L-34: Feature panels = CREAM CARDS с DARK TEXT

**Problem:** Boilerplate описывал feature panels как transparent (cream 0.17) с white text. На самом деле это solid cream cards.
**Root Cause:** Boilerplate был написан по памяти, не сверен с CSS.
**Rule:** Feature panels в warm-clay palette:
- Background: cream 0.92 (NOT 0.17)
- Text: dark ink (NOT white)
- Border: ink 0.06
- Box-shadow: есть (DROP_SHADOW)
- Footer strip: cream 0.85, ink 0.06 border, radius 16px, dark text

### L-35: Всегда сохраняй скрипт на диск ПЕРЕД execute

**Problem:** Импровизированные скрипты прямо в use_figma содержали ошибки (забытые SVG, неправильные ширины, пропущенные компоненты).
**Root Cause:** Нет review-этапа. Код пишется и выполняется одновременно.
**Rule:**
1. Написать скрипт → сохранить в `docs/figma-analysis/scripts/{carousel}/slide_N.js`
2. Проверить: все SVG есть? Ширины из CSS? Все компоненты из HTML?
3. ТОЛЬКО ПОТОМ → `use_figma` с содержимым файла
4. Если нужен fix — новый файл `slide_N_fix.js`, не редактирование на ходу

---

## Checklist: Перед запуском скрипта

- [ ] Прочитан HTML ПОЛНОСТЬЮ (не только первые N строк)
- [ ] Прочитаны ОБА CSS файла (theme.css + style_v3.css)
- [ ] Цвета из CSS, не из эталона
- [ ] Жирности скорректированы (L-04 таблица)
- [ ] SVG иконки через createNodeFromSvg() с правильной стилизацией (L-30)
- [ ] Watermark добавлен
- [ ] ВСЕ layoutSizing="FILL" стоят ПОСЛЕ appendChild
- [ ] Wrapper-фреймы: clipsContent=false
- [ ] Wrapper-фреймы: sizing установлен ПОСЛЕ append
- [ ] Нет paddingTop на Text-нодах
- [ ] Автопроверка в конце скрипта (L-09)
- [ ] `return { createdNodeIds: [...], issues: [...] }`
- [ ] Один слайд = один use_figma вызов (L-19)
- [ ] validate() в конце скрипта (L-21)
- [ ] Ширина текста = parent.width - paddings (L-22)
- [ ] Скрипт использует unified подход ~160 строк (L-27)
- [ ] Все значения из CSS, не из boilerplate/calculator (L-28)
- [ ] Subtitle/text max-width: "FIXED" sizing (L-29)
- [ ] SVG: frame.strokes=[], style only children (L-30)
- [ ] Cards в grid row: "FILL","FILL" (L-31)
- [ ] Badge containers: resize() ПОСЛЕ SVG append (L-32)
- [ ] Mixed-weight text: separate nodes (L-33)
- [ ] Feature panels: cream 0.92 + dark text (L-34)
- [ ] Скрипт сохранён на диск ПЕРЕД execute (L-35)
- [ ] HTML структура = Figma структура, ничего не упрощено (L-25)
