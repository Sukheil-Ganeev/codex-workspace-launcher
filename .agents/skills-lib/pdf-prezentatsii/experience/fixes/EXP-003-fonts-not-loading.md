---
id: EXP-003
date: 2026-02-03
type: fix
severity: high
category: typography
projects: []
related: [EXP-036]
tags: [шрифты, google-fonts, networkidle, wait]
status: verified
---

## Проблема

В PDF отображаются системные шрифты вместо Google Fonts или кастомных шрифтов.

## Контекст

Playwright конвертирует страницу в PDF до того как браузер успел загрузить внешние шрифты. Особенно часто происходит с Google Fonts.

## Решение

1. **Добавить preconnect для ускорения:**

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

2. **Ждать загрузки через networkidle:**

```python
page.goto(f'file:///{html_path}')
page.wait_for_load_state('networkidle')  # ← КРИТИЧНО!
page.pdf(...)
```

## Урок

**Всегда использовать `wait_for_load_state('networkidle')`** перед конвертацией. Это даёт время на загрузку шрифтов, изображений и других ресурсов.

---

## Альтернатива — встроить шрифты

Если networkidle не помогает, можно встроить шрифт в base64:

```css
@font-face {
    font-family: 'MyFont';
    src: url('data:font/woff2;base64,...') format('woff2');
}
```
