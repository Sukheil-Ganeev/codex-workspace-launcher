# CSS Width Calculator -- Точные формулы для Figma

Эти формулы ОБЯЗАТЕЛЬНЫ перед созданием любого слайда. Не угадывать ширины -- считать.

**ВАЖНО (L-28):** Все значения ниже основаны на CSS. ВСЕГДА верифицируй конкретные значения по theme.css -- этот файл может быть outdated.

## Base Values (from style_v3.css + theme.css)

- Canvas: 1080px
- Content padding: 60px * 2 = 120px
- **Content area: 1080 - 120 = 960px**

## Layout Types

### Full Width (slides без split)
- `.content-page__title`: width = 560px (CSS max-width)
- `.content-page__subtitle`: width = 560px (CSS max-width)
- `.page__title` (cover): width = 520px (CSS max-width)
- `.page__title--md` (medium title): CSS class = **68px** font-size (NOT 84px)
- `.page__subtitle` (cover): width = 520px (CSS max-width)
- `.eyebrow`: width = 420px
- `.footer-banner__text`: 960 - 22*2(padding) - 170(title col) - 20(gap) = **726px**
- `.footer-banner__title`: **170px** (CSS grid-template-columns: 170px 1fr)
- `.footer-note__text`: **328px** (CSS max-width)

### Split Layout (hero--split: title left + stat-card right)
CSS: `grid-template-columns: minmax(0, 1.05fr) minmax(300px, 0.72fr)`, gap: 28px
- Available: 960 - 28 = **932px**
- Left column: 932 * 1.05 / (1.05+0.72) = 932 * 1.05/1.77 = **553px**
- Right column (stat-card): 932 * 0.72/1.77 = **379px**, min 300px
- `.content-page__lead` inside left: max-width = **560px** (but column is 553, so effectively 553)
- `.content-page__subtitle` in split: **520px** (CSS max-width on lead)

### Stat Card (inside right column of split)
- Card width: **379px** (from grid calc above)
- Card padding: 26px top/bottom, 28px left/right
- Inner text width: 379 - 28*2 = **323px**
- `.stat-card__value`: **323px**
- `.stat-card__text`: **323px**
- `.stat-card__eyebrow` text: auto-width (HUG)

### Cover Grid (slide 1 type)
CSS: `grid-template-columns: 1.02fr 0.84fr`, gap: 32px
- Available: 960 - 32 = **928px**
- Left column: 928 * 1.02 / (1.02+0.84) = 928 * 1.02/1.86 = **509px**
- Right column (pass-panel): 928 * 0.84/1.86 = **419px**

### Pass Panel (cover right column)
- Panel max-width: **400px** (CSS)
- Panel padding: 28px left, 32px right = 60px total
- Inner text width: 400 - 60 = **340px**
- `.pass-panel__value`: **340px**
- `.pass-panel__copy`: **340px**

### Note Card (inside cover left column)
- Card width: **474px** (CSS)
- Card padding: 28px * 2 = 56px
- Icon: 52px + gap 16px = 68px
- Text width: 474 - 56 - 68 = **350px**

### Place Card (full width cards)
- Card fills parent (960px)
- Card padding: 22px * 2 = 44px
- Icon: 50px + gap 16px = 66px
- Text width: 960 - 44 - 66 = **850px**

### Tip Card (2-column grid)
- Grid: 2 columns with gap 14px
- Card width: (960 - 14) / 2 = **473px**
- Card padding: 20px * 2 = 40px
- Icon: 44px + gap 14px = 58px
- Text width: 473 - 40 - 58 = **375px**

### Feature Panel (cream card -- L-34)
- Panel fills parent (960px or column width)
- Panel padding: 22px * 2 = 44px
- Inner text width: parent_width - 44
- Text color: DARK (ink), NOT white

### Footer Strip (cream 0.85 -- L-34)
- Strip fills parent (960px)
- Strip padding: 20px * 2 = 40px
- Title column: **210px** fixed
- Gap: 12px
- Text width: 960 - 40 - 210 - 12 = **698px**
- Text color: DARK (ink), NOT white

### CTA Shell
- `.cta-shell__title`: **auto-width** (centered)
- `.cta-shell__text`: **620px** (CSS max-width)
- `.service-line`: **720px**
- `.action-pill` text: **auto-width** (HUG)

## How to Use

BEFORE writing any use_figma script:
1. Identify slide type (cover / content / content-split / tips / cta)
2. Look up ALL text widths from this calculator
3. Write them as constants at top of script
4. NEVER use a width not from this table
5. **ALWAYS verify against theme.css -- this file may be outdated (L-28)**
