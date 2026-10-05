---
id: EXP-136
date: 2026-02-20
type: pattern
severity: medium
category: motion
projects: [scraper-systems-2026-v2]
related: [EXP-103, EXP-120, EXP-135]
tags: [animation, infographic, scoped-css, readability, slideshow]
status: verified
---

# EXP-136: Scoped-деанимация инфографики без деградации UI

## Контекст

Пользователь попросил убрать неуместную анимацию внутри инфографик (zoom/pulse), но сохранить живость интерфейса (hover, переходы, навигация).

## Паттерн

Отключать motion точечно, только для SVG/инфографических слоев, а не глобально по всему слайду.

```css
.infographic-svg .pulse-dot,
.infographic-svg [data-anim="pulse"],
.infographic-svg [data-anim="zoom"],
.infographic-svg [data-anim="float"] {
  animation: none !important;
  transform: none !important;
}

.nav-btn,
.toc-btn,
.card,
.tag {
  transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}
```

## Почему это работает

- Убирается визуальный шум именно там, где он мешает чтению данных.
- Навигация и интерактивные элементы сохраняют тактильность.
- PDF-режим и HTML-режим остаются предсказуемыми.

## QA-критерии

- Инфографика статична и читаема на всех ключевых слайдах.
- UI элементы реагируют на hover/focus.
- Нет глобального `animation: none` на `*`.

## Правило

Деанимация для презентаций делается scoped-подходом: только целевые слои, никогда не "рубить" весь интерфейс целиком.
