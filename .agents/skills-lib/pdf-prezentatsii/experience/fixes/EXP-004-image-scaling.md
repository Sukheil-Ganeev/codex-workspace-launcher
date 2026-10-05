---
id: EXP-004
date: 2026-02-04
type: fix
severity: high
category: images
projects: []
related: [EXP-026, EXP-027, EXP-043]
tags: [images, object-fit, масштабирование, min-width]
status: verified
---

# EXP-004: Проблема масштабирования изображений в PDF

**Дата:** 2026-02-04
**Проект:** Каталог книг Дубай

## Проблема
Маленькие изображения обложек (179x281px) не масштабировались до нужного размера. Квадратные изображения (1200x1200) выглядели маленькими.

## Что НЕ работало
```css
/* min-width не масштабирует img вверх! */
.book-cover {
    min-width: 320px;
    max-width: 460px;
    object-fit: contain;
}
```

## Решение
```css
.book-cover {
    width: 420px;
    height: 600px;
    object-fit: cover;        /* заполняет, обрезает края */
    object-position: center top;
}
```

## Источники
- [MDN object-fit](https://developer.mozilla.org/en-US/docs/Web/CSS/object-fit)
- [DigitalOcean CSS cropping](https://www.digitalocean.com/community/tutorials/css-cropping-images-object-fit)

## Урок
`min-width` на `<img>` задаёт минимальный размер ЭЛЕМЕНТА, но не масштабирует ИЗОБРАЖЕНИЕ. Для масштабирования нужны фиксированные `width`/`height` + `object-fit`.
