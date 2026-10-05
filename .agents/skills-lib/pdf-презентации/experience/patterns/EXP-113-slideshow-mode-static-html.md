---
id: EXP-113
date: 2026-02-18
type: pattern
severity: medium
category: layout
projects: [debit-cards-research]
related: [EXP-114, EXP-125]
tags: [slideshow, static-html, print, toc, fullscreen]
status: verified
---

# EXP-113: Slideshow mode для статических HTML-презентаций

## Паттерн
Статическую HTML-презентацию для PDF можно превратить в слайдшоу без изменения структуры.

## Базовая реализация
```css
body.slideshow-mode .slide {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
}
body.slideshow-mode .slide.active {
  display: flex;
}
```

## Совместимость с печатью
```css
@media print {
  .slide {
    display: flex !important;
    position: static !important;
    page-break-after: always;
  }
}
```

## Примечание
JS (IIFE, клавиатура, TOC, fullscreen) не должен ломать PDF-конвертацию.
