---
id: EXP-001
date: 2026-02-03
type: fix
severity: critical
category: layout
projects: []
related: [EXP-022]
tags: [body, height, overflow, многостраничный, первый-слайд]
status: verified
---

## Проблема

При конвертации HTML в PDF видно только первый слайд. Остальные слайды обрезаются или не попадают в PDF.

## Контекст

Происходит когда в CSS для body указаны:
- `height: 1080px` (или другая фиксированная высота)
- `overflow: hidden`

Эти свойства ограничивают body размером одного слайда, и все последующие слайды не рендерятся в PDF.

## Решение

**Убрать height и overflow с body. Фиксировать размеры только на слайдах:**

```css
/* ✅ ПРАВИЛЬНО */
html, body {
    width: 1920px;
    margin: 0;
    padding: 0;
    /* БЕЗ height и overflow! */
}

.slide {
    width: 1920px;
    height: 1080px;  /* Высота ТОЛЬКО здесь */
    page-break-after: always;
    page-break-inside: avoid;
}
```

```css
/* ❌ НЕПРАВИЛЬНО */
body {
    height: 1080px;    /* ← Удалить! */
    overflow: hidden;  /* ← Удалить! */
}
```

## Урок

**Body должен растягиваться под все слайды.** Фиксировать высоту нужно только на отдельных слайдах. Playwright использует page-break-after для разбивки на страницы PDF.

---

## Пример использования

Проверка перед конвертацией:
1. Открыть CSS
2. Найти `body {`
3. Убедиться что НЕТ `height:` и `overflow: hidden`
4. Убедиться что `.slide` имеет `page-break-after: always`
