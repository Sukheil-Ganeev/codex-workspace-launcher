---
id: EXP-002
date: 2026-02-03
type: fix
severity: high
category: conversion
projects: []
related: []
tags: [фон, белый, print_background, playwright]
status: verified
---

## Проблема

PDF получается с белым фоном вместо заданного в CSS.

## Контекст

По умолчанию браузер не печатает фоновые цвета и изображения для экономии чернил. Playwright наследует это поведение.

## Решение

Указать `print_background=True` в page.pdf():

```python
page.pdf(
    path='output.pdf',
    width='1920px',
    height='1080px',
    print_background=True,  # ← КРИТИЧНО!
    margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
)
```

## Урок

**Всегда добавлять `print_background=True`** — это не опционально для презентаций с цветным фоном.

---

## Чек-лист

- [ ] `print_background=True` в page.pdf()
- [ ] CSS background-color указан
- [ ] Для градиентов — тоже работает
