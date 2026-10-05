# Figma Boilerplate — Стандартные блоки кода

Копировать в КАЖДЫЙ `use_figma` скрипт. Не переписывать, не сокращать, не "оптимизировать".

**ВАЖНО (L-28):** Все значения здесь взяты из CSS (theme.css + style_v3.css). При сомнениях — ВСЕГДА сверяй с CSS.

---

## 1. Page Navigation (ВСЕГДА первая строка)

```javascript
const pages = figma.root.children;
await figma.setCurrentPageAsync(pages.find(p => p.name === "Посты Инстаграм Финал") || pages[0]);
```

---

## 2. Font Loading (ВСЕГДА перед любым текстом)

```javascript
const F = {
  tenor:  { family: "Tenor Sans",   style: "Regular" },
  corm:   { family: "Cormorant SC", style: "Regular" },
  montM:  { family: "Montserrat",   style: "Medium" },
  montSB: { family: "Montserrat",   style: "SemiBold" },
  montB:  { family: "Montserrat",   style: "Bold" },
  montEB: { family: "Montserrat",   style: "ExtraBold" }
};
await Promise.all([
  figma.loadFontAsync(F.tenor),
  figma.loadFontAsync(F.corm),
  figma.loadFontAsync(F.montM),
  figma.loadFontAsync(F.montSB),
  figma.loadFontAsync(F.montB),
  figma.loadFontAsync(F.montEB)
]);
```

**Когда Cormorant SC не нужен** (content slides без eyebrow): убрать `F.corm` и его loadFontAsync для экономии времени.

---

## 3. Color Constants (из style_v3.css + theme.css)

```javascript
// Brand colors (0-1 range, NOT 0-255)
const C = {
  white:       { r: 0.996, g: 0.988, b: 0.980 },  // #FEFCFA
  ink:         { r: 0.102, g: 0.090, b: 0.078 },  // #1A1714
  warmClay:    { r: 0.769, g: 0.584, b: 0.416 },  // #C4956A
  warmClayDeep:{ r: 0.710, g: 0.541, b: 0.353 },  // #b58a5a
  cream:       { r: 0.961, g: 0.929, b: 0.906 },  // #F5EDE7
  copperDark:  { r: 0.627, g: 0.416, b: 0.314 },  // #a06a50
  copper:      { r: 0.769, g: 0.537, b: 0.431 },  // #C4896E
  sand:        { r: 0.871, g: 0.718, b: 0.643 },  // #DEB7A4
  mistBlue:    { r: 0.780, g: 0.847, b: 0.902 },  // #C7D8E6
  warmGray:    { r: 0.659, g: 0.608, b: 0.565 },  // #A89B90
};
```

---

## 4. Helper Functions (стандартный набор)

```javascript
// Solid fill (L-12: helper saves code)
function sf(c, o) { return [{ type: "SOLID", color: c, opacity: o ?? 1 }]; }

// RGBA for gradients (L-08: alpha IN color for gradients)
function rgba(c, a) { return { r: c.r, g: c.g, b: c.b, a }; }

// Frame with auto-layout (L-06: clipsContent=false)
function nf(name, mode) {
  const f = figma.createFrame();
  f.name = name;
  f.layoutMode = mode || "VERTICAL";
  f.fills = [];
  f.clipsContent = false;  // КРИТИЧНО — иначе h=100 trap
  return f;
}

// Append + set sizing (L-05: FILL/HUG AFTER appendChild)
function ap(parent, child, h, v) {
  parent.appendChild(child);
  if (h) child.layoutSizingHorizontal = h;
  if (v) child.layoutSizingVertical = v;
  return child;
}

// Text node (L-07: no padding on text)
function tx(name, value, font, size, color, opacity, opts) {
  const t = figma.createText();
  t.name = name;
  t.fontName = font;
  t.characters = value;
  t.fontSize = size;
  t.fills = sf(color, opacity ?? 1);
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

// Spacer frame for CSS margin-top (L-23)
function spc(h) {
  const s = nf("sp-" + h, "NONE");
  s.resize(1, h);
  return s;
}
```

---

## 5. Root Frame (warm-clay palette)

```javascript
function createRoot(name, x, y) {
  const root = figma.createFrame();
  root.name = name;
  root.resize(1080, 1350);
  root.x = x;
  root.y = y;
  root.clipsContent = true;
  root.layoutMode = "NONE";
  root.fills = [
    { type: "GRADIENT_LINEAR", gradientTransform: [[0,1,0],[-1,0,1]],
      gradientStops: [
        { position: 0, color: rgba(C.warmClay, 1) },
        { position: 1, color: rgba(C.warmClayDeep, 1) }
      ]},
    { type: "GRADIENT_RADIAL", gradientTransform: [[0.26,0,0.14],[0,0.26,0.18]],
      gradientStops: [
        { position: 0, color: rgba(C.white, 0.09) },
        { position: 1, color: rgba(C.white, 0) }
      ]}
  ];

  // Inner border (CSS .slide::after)
  const bdr = figma.createRectangle();
  bdr.name = "inner-border";
  bdr.resize(1032, 1302);
  bdr.x = 24; bdr.y = 24;
  bdr.cornerRadius = 42;
  bdr.fills = [];
  bdr.strokes = sf(C.white, 0.16);
  bdr.strokeWeight = 1;
  bdr.strokeAlign = "INSIDE";
  root.appendChild(bdr);

  // Watermark (L-17: opacity 0.045)
  const wm = figma.createText();
  wm.name = "watermark";
  wm.fontName = F.montSB;
  wm.characters = "@vip_dxb_rus";
  wm.fontSize = 16;
  wm.fills = sf(C.white, 0.045);
  wm.textAutoResize = "WIDTH_AND_HEIGHT";
  wm.x = 902; wm.y = 1298;
  root.appendChild(wm);

  return root;
}
```

---

## 6. Content Container + Meta Bar

```javascript
function createContentAndMeta(root, slideNum) {
  const ct = nf("slide__content", "VERTICAL");
  ct.resize(1080, 1350);
  ct.paddingTop = 54; ct.paddingBottom = 54;
  ct.paddingLeft = 60; ct.paddingRight = 60;
  ct.itemSpacing = 0;
  ct.layoutSizingHorizontal = "FIXED";
  ct.layoutSizingVertical = "FIXED";
  root.appendChild(ct);

  // Meta bar (L-04: SemiBold, opacity 0.82 from CSS)
  const meta = nf("meta", "HORIZONTAL");
  meta.primaryAxisAlignItems = "SPACE_BETWEEN";
  meta.counterAxisAlignItems = "CENTER";
  meta.itemSpacing = 16;
  ap(meta, tx("meta__counter", slideNum, F.montSB, 18, C.white, 0.82, { ls: 1 }), "HUG", "HUG");
  ap(meta, tx("meta__handle", "@vip_dxb_rus", F.montSB, 18, C.white, 0.82, { ls: 1 }), "HUG", "HUG");
  ap(ct, meta, "FILL", "HUG");

  // Spacer (CSS .content-page margin-top: 34px / .page margin-top: 36px)
  ap(ct, spc(34), "FILL", "FIXED");

  // Page container (space-between for footer pinning)
  const page = nf("page", "VERTICAL");
  page.primaryAxisAlignItems = "SPACE_BETWEEN";
  page.itemSpacing = 0;
  ap(ct, page, "FILL", "FILL");

  return { ct, page };
}
```

---

## 7. Component Builders

### Section Chip
```javascript
function createChip(text, placeholderIcon) {
  const chip = nf("section-chip", "HORIZONTAL");
  chip.itemSpacing = 8;
  chip.paddingTop = 10; chip.paddingBottom = 10;
  chip.paddingLeft = 18; chip.paddingRight = 18;
  chip.cornerRadius = 999;
  chip.fills = sf(C.cream, 0.3);
  chip.strokes = sf(C.white, 0.2);
  chip.strokeWeight = 1;
  // Placeholder icon (replaced with SVG in Pass 3)
  const dot = figma.createRectangle();
  dot.name = "chip-icon-placeholder";
  dot.resize(18, 18); dot.cornerRadius = 9;
  dot.fills = sf(C.white, 0.7);
  ap(chip, dot, "FIXED", "FIXED");
  // L-04: chip text weight → ExtraBold
  ap(chip, tx("section-chip__text", text.toUpperCase(), F.montEB, 14, C.white, 0.96, { ls: 1, tc: "UPPER" }));
  return chip;
}
```

### Place Card
```javascript
// Width 854 from css_width_calculator (960 - 44padding - 62icon)
function createPlaceCard(title, text) {
  const card = nf("place-card", "HORIZONTAL");
  card.itemSpacing = 16;
  card.paddingTop = 20; card.paddingBottom = 20;
  card.paddingLeft = 22; card.paddingRight = 22;
  card.cornerRadius = 24;
  card.fills = sf(C.cream, 0.94);
  card.strokes = [{ type: "SOLID", color: C.warmClay, opacity: 0.1 }];
  card.strokeWeight = 1;
  // Icon placeholder (replaced in Pass 3)
  const ico = figma.createRectangle();
  ico.name = "card-icon-placeholder";
  ico.resize(50, 50); ico.cornerRadius = 16;
  ico.fills = [{ type: "SOLID", color: C.warmClay, opacity: 0.14 }];
  ap(card, ico, "FIXED", "FIXED");
  // Text column
  const col = nf("place-card__copy", "VERTICAL");
  col.itemSpacing = 6;
  ap(card, col, "FILL", "HUG");
  // L-04: title weight 800 = ExtraBold (no correction needed)
  ap(col, tx("place-card__title", title, F.montEB, 20, C.ink, 0.92, { w: 854, lh: 23 }), "FILL", "HUG");
  // L-17: card text opacity 0.66
  ap(col, tx("place-card__text", text, F.montM, 16, C.ink, 0.66, { w: 854, lh: 23 }), "FILL", "HUG");
  return card;
}
```

### Tip Card (2-column)
```javascript
// Width 378 from css_width_calculator (473 - 40padding - 55icon)
function createTipCard(title, text) {
  const card = nf("tip-card", "HORIZONTAL");
  card.itemSpacing = 14;
  card.paddingTop = 18; card.paddingBottom = 18;
  card.paddingLeft = 20; card.paddingRight = 20;
  card.cornerRadius = 22;
  card.fills = sf(C.cream, 0.94);
  card.strokes = [{ type: "SOLID", color: C.warmClay, opacity: 0.1 }];
  card.strokeWeight = 1;
  const ico = figma.createRectangle();
  ico.name = "tip-icon-placeholder";
  ico.resize(44, 44); ico.cornerRadius = 14;
  ico.fills = [{ type: "SOLID", color: C.warmClay, opacity: 0.14 }];
  ap(card, ico, "FIXED", "FIXED");
  const col = nf("tip-card__copy", "VERTICAL");
  col.itemSpacing = 5;
  ap(card, col, "FILL", "HUG");
  ap(col, tx("tip-card__title", title, F.montEB, 17, C.ink, 0.92, { w: 378, lh: 20 }), "FILL", "HUG");
  ap(col, tx("tip-card__text", text, F.montM, 14, C.ink, 0.66, { w: 378, lh: 20 }), "FILL", "HUG");
  return card;
}
```

### Footer Banner
```javascript
// Width 730/170 from css_width_calculator
function createFooterBanner(title, text) {
  const fb = nf("footer-banner", "HORIZONTAL");
  fb.itemSpacing = 20;
  fb.counterAxisAlignItems = "MIN";
  fb.paddingTop = 18; fb.paddingBottom = 18;
  fb.paddingLeft = 22; fb.paddingRight = 22;
  fb.cornerRadius = 24;
  fb.fills = [{ type: "SOLID", color: C.cream, opacity: 0.12 }];
  fb.strokes = sf(C.white, 0.1);
  fb.strokeWeight = 1;
  // L-04: title ExtraBold, L-17: opacity 0.95
  ap(fb, tx("footer-banner__title", title.toUpperCase(), F.montEB, 14, C.white, 0.95,
    { w: 170, ls: 1, tc: "UPPER", lh: 17 }), "FIXED", "HUG");
  // L-17: text opacity 0.86
  ap(fb, tx("footer-banner__text", text, F.montM, 16, C.white, 0.86,
    { w: 730, lh: 23 }), "FILL", "HUG");
  return fb;
}
```

### Stat Card
```javascript
// Width 376, inner 320 from css_width_calculator
function createStatCard(eyebrowText, value, bodyText) {
  const sc = nf("stat-card", "VERTICAL");
  sc.itemSpacing = 0;
  sc.paddingTop = 26; sc.paddingBottom = 26;
  sc.paddingLeft = 28; sc.paddingRight = 28;
  sc.cornerRadius = 34;
  sc.fills = [{ type: "SOLID", color: C.cream, opacity: 0.18 }];
  sc.strokes = sf(C.white, 0.14);
  sc.strokeWeight = 1;
  sc.resize(376, 10);
  // Eyebrow chip
  const ey = nf("stat-card__eyebrow", "HORIZONTAL");
  ey.paddingTop = 8; ey.paddingBottom = 8;
  ey.paddingLeft = 12; ey.paddingRight = 12;
  ey.cornerRadius = 999;
  ey.fills = sf(C.white, 0.12);
  ap(ey, tx("stat-card__eyebrow-text", eyebrowText.toUpperCase(), F.montEB, 12, C.white, 0.92, { ls: 1, tc: "UPPER" }));
  ap(sc, ey, "HUG", "HUG");
  ap(sc, spc(18), "FILL", "FIXED");
  // Value: Tenor Sans 74px (inner width = 320)
  ap(sc, tx("stat-card__value", value, F.tenor, 74, C.white, 1, { w: 320, lh: 67, ls: 1.4 }), "HUG", "HUG");
  ap(sc, spc(14), "FILL", "FIXED");
  // Body text (inner width = 320)
  ap(sc, tx("stat-card__text", bodyText, F.montM, 18, C.white, 0.86, { w: 320, lh: 26 }), "HUG", "HUG");
  return sc;
}
```

---

## 8. Validate (L-09 + L-21)

```javascript
function validate(root) {
  const issues = [];
  function check(n) {
    if (n.type === "FRAME" && n.height === 100 && n.layoutMode !== "NONE" && !n.name.startsWith("sp")) {
      issues.push({ node: n.name, issue: "h=100" });
      n.resize(n.width, 10);
      n.layoutSizingVertical = "HUG";
    }
    if (n.type === "FRAME" && n.width === 100 && n.clipsContent) {
      issues.push({ node: n.name, issue: "w=100+clip" });
    }
    if (n.type === "TEXT" && n.parent && n.parent.type === "FRAME" && n.parent.layoutMode !== "NONE") {
      const inner = n.parent.width - (n.parent.paddingLeft || 0) - (n.parent.paddingRight || 0);
      if (n.width > inner + 5) {
        issues.push({ node: n.name, issue: "text overflow", w: Math.round(n.width), max: Math.round(inner) });
      }
    }
    if (n.type === "RECTANGLE" && n.name.includes("placeholder")) {
      issues.push({ node: n.name, issue: "placeholder not replaced" });
    }
    if ("children" in n) n.children.forEach(check);
  }
  check(root);
  return issues;
}
```

---

## 9. Naming Convention

| Элемент | Имя | Пример |
|---------|-----|--------|
| Root frame | `{carousel}_slide_{N}` | `family_places_v1_slide_3` |
| Content wrapper | `slide__content` | — |
| Meta bar | `meta` | — |
| Counter | `meta__counter` | "03 / 08" |
| Handle | `meta__handle` | "@vip_dxb_rus" |
| Chip | `section-chip` | — |
| Chip text | `section-chip__text` | "КРЫТЫЕ ПАРКИ" |
| Chip icon placeholder | `chip-icon-placeholder` | — |
| Page title | `page__title` или `content-page__title` | — |
| Subtitle | `page__subtitle` или `content-page__subtitle` | — |
| Place card | `place-card` | — |
| Card icon placeholder | `card-icon-placeholder` | — |
| Card title | `place-card__title` | — |
| Card text | `place-card__text` | — |
| Tip card | `tip-card` | — |
| Tip icon placeholder | `tip-icon-placeholder` | — |
| Footer banner | `footer-banner` | — |
| Footer title | `footer-banner__title` | — |
| Footer text | `footer-banner__text` | — |
| Stat card | `stat-card` | — |
| Stat value | `stat-card__value` | — |
| Stat text | `stat-card__text` | — |
| Watermark | `watermark` | — |
| Inner border | `inner-border` | — |
| Spacer | `sp-{height}` | `sp-34` |

**Правило:** BEM-подобная нотация. Никогда однобуквенные имена ("c", "h", "t"). Субагенты ОБЯЗАНЫ использовать эти имена — иначе Pass 3 не найдёт placeholder'ы для замены.
