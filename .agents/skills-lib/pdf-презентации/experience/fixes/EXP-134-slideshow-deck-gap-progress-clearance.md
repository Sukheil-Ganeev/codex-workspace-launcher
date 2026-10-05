---
id: EXP-134
date: 2026-02-20
type: fix
severity: high
category: layout
projects: [scraper-systems-2026-v2]
related: [EXP-113, EXP-114, EXP-125, EXP-133]
tags: [slideshow, deck-gap, progress-bar, viewport, geometry]
status: verified
---

# EXP-134: Несинхронизированная геометрия slideshow (верх/низ/прогресс)

## Проблема

В slideshow-режиме проявились три дефекта:

1. Над активным слайдом видно "хвост" соседнего слайда.
2. Нижний progress bar визуально упирается в карточку.
3. Верхний и нижний отступы ощущаются несбалансированно.

## Корневая причина

Вертикальная геометрия считалась разными формулами в CSS и JS:

- `#deck` и `.slide-frame` использовали одни значения (`padding`, `gap`, `scroll-margin-top`).
- `applySlideSize()` считал высоту по отдельной константе (`vh - 128`).

В результате scale и доступная высота слайда считались без общих safe-зон.

## Решение

Единый источник правды для вертикальных отступов: CSS-токены + чтение этих токенов в JS.

```css
:root {
  --deck-top-gap: 72px;
  --deck-bottom-gap: 104px;
}

#deck {
  gap: var(--deck-bottom-gap);
  padding: var(--deck-top-gap) 0 var(--deck-bottom-gap);
}

.slide-frame {
  scroll-margin-top: var(--deck-top-gap);
}

.progress {
  z-index: 90;
}
```

```js
const rootStyles = getComputedStyle(document.documentElement);
const deckTop = parseFloat(rootStyles.getPropertyValue("--deck-top-gap")) || 72;
const deckBottom = parseFloat(rootStyles.getPropertyValue("--deck-bottom-gap")) || 104;
const availH = Math.max(320, vh - deckTop - deckBottom);
```

## QA-критерии

- `visibleSecondPixels` на первом слайде = `0`.
- `gapToProgress` (верх progress до низа слайда) >= `48px` на 1366x768 и 1920x1080.
- На проблемных слайдах (01/07/22) нет "хвоста" соседних карточек сверху/снизу.

## Правило

Для slideshow нельзя держать отдельные числовые отступы в CSS и JS.
Геометрию viewport считать только из общих токенов (`--deck-top-gap`, `--deck-bottom-gap`).
