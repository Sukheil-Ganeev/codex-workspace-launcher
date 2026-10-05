---
id: EXP-043
date: 2026-02-04
type: warning
severity: high
category: images
projects: []
related: [EXP-004, EXP-026, EXP-027]
tags: [min-width, images, object-fit, масштабирование]
status: verified
---

# НЕ используй min-width для масштабирования изображений!

## Неправильно
```css
.book-cover {
    min-width: 320px;  /* НЕ РАБОТАЕТ для масштабирования вверх! */
    object-fit: contain;
}
```

## Правильно
```css
.book-cover {
    width: 420px;
    height: 600px;
    object-fit: cover;  /* или contain */
}
```

## Почему
CSS `min-width` задаёт минимальный размер HTML-элемента `<img>`, но НЕ заставляет браузер масштабировать само изображение внутри этого элемента.

Для масштабирования изображений используй:
1. Фиксированные `width` и `height`
2. `object-fit: contain` (сохраняет пропорции) или `cover` (заполняет, обрезает)
