# Etalon Structures -- 5 Palette Layer Trees

> Layer structure reference for all 5 InstaCovers solid-color palette etalons.
> Source: html.to.design plugin imports analyzed via get_design_context.
> Figma file: `8B1Dfaq8XtBOXlJuS19UhK`, page: "Посты Инстаграм Финал"

---

## COPPER -- "Нелегальное такси в Дубае" (1902:38, 95 nodes)

```
div.slide (1080x1350, bg: solid #C4896E, clipsContent: true)
├── ::before .............. overlay: radial gradient (warm white 8%) + linear gradient (white 4%)
├── ::after ............... inner border: inset 24px, 1px rgba(254,252,250,0.08), radius 42px
└── div.slide__content .... padding: 56px 64px 58px, gap: 54px, VERTICAL
    ├── div.meta .......... HORIZONTAL, space-between
    │   ├── counter ....... "01 / 09" Montserrat Medium 18px, white 84%
    │   └── handle ........ "@vip_dxb_rus" Montserrat Medium 18px, white 84%
    ├── div.cover ......... main content, VERTICAL
    │   ├── div.cover__lead  left column: badge + title + subtitle + note
    │   └── div.guide-panel  UNIQUE: right panel with backdrop-blur cards
    └── div.cover__footer . save-chip + footer-note
```

**Unique:** Guide panel with glassmorphism cards (backdrop-blur + copper gradient). No grid overlay. White text throughout.

---

## MIST-BLUE -- "8 фактов о метро Дубая" (1902:135, 81 nodes)

```
div.slide (1080x1350, bg: 4 layers -- solid #C7D8E6 + linear + 2 radial blobs)
├── ::before .............. grid overlay: opacity 55%, DARK lines + copper/green radial blobs
├── ::after ............... inner border: inset 22px, 1px rgba(31,41,50,0.08), radius 42px
└── div.slide__content .... padding: 54px 60px, gap: 34px, VERTICAL
    ├── div.meta .......... counter + handle (Montserrat Medium 18px, dark #1f2932)
    ├── div.page .......... space-between, height: 1206px
    │   ├── section-chip .. cream bg, dark text, copper icon
    │   ├── cover-grid .... 2-column layout
    │   │   ├── left ...... title (Tenor Sans 60-82px DARK) + subtitle + rule + eyebrow
    │   │   └── right ..... route-panel OR feature-panel (cream bg, shadows)
    │   └── note-card ..... cream bg, dark text
    └── footer ............ tagline (Cormorant SC) + handle
```

**Unique:** DARK text (#1f2932) on light background. Dark borders. Copper accents on dividers/labels. Green radial blob (metro theme). Grid overlay with colored blobs at 55% opacity.

---

## WARM-CLAY -- "5 ошибок при покупке билетов" (1902:218, 43 nodes)

```
div.slide (1080x1350, bg: 3 layers -- linear #C4956A->#A87D54 + 2 radial accents)
├── ::before .............. grid overlay: opacity 18%, warm-white lines
├── ::after ............... inner border: inset 24px, 1px rgba(254,252,250,0.08), radius 42px
└── div.slide__content .... padding: 50px 55px 80px, VERTICAL
    ├── div.meta .......... counter + handle (white 84%)
    ├── section-chip ...... pill badge, semi-transparent white bg
    ├── title ............. Tenor Sans 84px, white 98%, letter-spacing 6px
    ├── subtitle .......... Montserrat 22px, white 85%
    ├── rule .............. copper gradient divider
    ├── eyebrow ........... Cormorant SC, sand color
    └── footer ............ tagline + handle + footer-note (max-width 328px)
```

**Unique:** SIMPLEST etalon. No grid layout, no panels. Pure vertical text stack. Title 84px (largest). White text on warm background. Padding 50px 55px 80px (unique).

---

## WARM-GRAY -- "Солнце в Дубае" (1902:263, 86 nodes)

```
div.slide (1080x1350, bg: 4 layers -- linear 168deg #A89B90->#8F8378 + linear + 2 radial)
├── ::before .............. grid overlay: opacity 18%, warm-white lines (same as warm-clay)
├── ::after ............... inner border: inset 22px, 1px rgba(254,252,250,0.2), radius 42px
└── div.slide__content .... padding: 54px 60px, gap: 34px, VERTICAL
    ├── div.meta .......... counter + handle (white 82%)
    ├── div.page .......... space-between
    │   ├── section-chip .. pill, semi-transparent white bg, dark text #2e2825
    │   ├── cover-grid .... 2-column (1.04fr / 0.84fr), gap 28px, height 609.23px
    │   │   ├── left ...... title + subtitle + rule + eyebrow + note-card
    │   │   └── right ..... feature-panel (NO route-strip, simple list, NO icons)
    │   └── note-card
    └── footer
```

**Unique:** 2-column grid like sand but SHORTER (609px vs 726px). Feature panel WITHOUT icons or route-strip. Border opacity 0.2 (brighter than others). Base gradient 168deg (angled, not straight 180deg).

---

## SAND -- "Когда лететь в Дубай?" (1902:351, 79 nodes)

```
div.slide (1080x1350, bg: 4 layers -- solid #C9C0B8 + linear + 2 radial)
├── ::before .............. grid overlay: opacity 18%, warm-white lines
├── ::after ............... inner border: inset 22px, 1px rgba(254,252,250,0.2), radius 42px
└── div.slide__content .... padding: 54px 60px, gap: 34px, VERTICAL
    ├── div.meta .......... counter + handle (white 82%)
    ├── div.page .......... space-between, height: 1206px
    │   ├── section-chip .. pill, semi-transparent white bg, dark text #2e2825, Montserrat Bold 14px
    │   ├── cover-grid .... 2-column (1.04fr / 0.84fr), gap 28px, height 726.61px
    │   │   ├── left ...... title (Tenor Sans 82px white) + subtitle + rule + eyebrow + note-card (490px wide)
    │   │   └── right ..... feature-panel (label + large value + text + feature-list WITH icons)
    │   └── note-card
    └── footer
```

**Unique:** Solid base color (not gradient). TALLEST grid (726px) and feature panel (685px). Wider note card (490px). Feature list items WITH icons. Very similar to warm-gray but taller proportions.

---

## Key Differences Between Palettes

| Property | COPPER | MIST-BLUE | WARM-CLAY | WARM-GRAY | SAND |
|----------|--------|-----------|-----------|-----------|------|
| Base bg | Solid #C4896E | 4 layers, #C7D8E6 | 3-layer gradient | 4-layer gradient 168deg | 4 layers, solid #C9C0B8 |
| Text color | White | **Dark #1f2932** | White | White (outer), dark (cards) | White (outer), dark (cards) |
| Border color | White 8% | **Dark 8%** | White 8% | White 20% | White 20% |
| Grid overlay | None | 55%, dark + color blobs | 18%, white | 18%, white | 18%, white |
| Layout | Guide panel | 2-col grid + route | **Simple vertical** | 2-col grid | 2-col grid |
| Grid height | N/A | ~700px | N/A | 609px | **726px** |
| Title size | Varies | 60-82px | **84px** | 82px | 82px |
| Content padding | 56/64/58 | 54/60 | **50/55/80** | 54/60 | 54/60 |
| Inner border inset | 24px | 22px | 24px | 22px | 22px |
| Feature panel | Glass cards | Route + features | None | Simple list | List WITH icons |
| Node count | 95 | 81 | **43** (simplest) | 86 | 79 |

---

## Common Layer Pattern (All Palettes)

Every solid-color etalon shares this base structure:

1. **Root frame** (1080x1350, clipsContent: true, background fills)
2. **::before** -- Grid/texture overlay (opacity varies)
3. **::after** -- Inner decorative border (inset 22-24px, radius 42px)
4. **slide__content** -- Main content container (flex column, padded)
   - **meta** -- Slide counter + @vip_dxb_rus handle
   - **page/cover** -- Main content area (layout varies by palette)
   - **footer** -- Tagline (Cormorant SC) + handle
