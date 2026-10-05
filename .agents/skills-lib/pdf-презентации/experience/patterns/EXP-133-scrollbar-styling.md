---
id: EXP-133
date: 2026-02-18
type: pattern
severity: low
category: layout
projects: [debit-cards-research]
related: [EXP-109]
tags: [scrollbar, webkit, firefox, toc, dual-theme]
status: verified
---

# EXP-133: Стилизация скроллбара

> Новый ID для блока скроллбара, вынесенного из агрегата, чтобы не конфликтовать с `EXP-118-documentElement-light-theme`.

## WebKit
```css
::-webkit-scrollbar { height: 4px; width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-color); }
::-webkit-scrollbar-thumb { background: rgba(accent, 0.25); border-radius: 2px; }
```

## Firefox
```css
* { scrollbar-width: thin; scrollbar-color: rgba(accent, 0.25) var(--bg-color); }
```

## Нюансы
Для TOC-панели задавать отдельные правила вертикального скролла. Для dual-theme допустим градиентный thumb (emerald -> cyan).
