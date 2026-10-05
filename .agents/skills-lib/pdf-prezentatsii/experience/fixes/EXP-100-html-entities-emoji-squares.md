---
id: EXP-100
date: 2026-02-13
type: fix
severity: high
category: typography
projects: [telegram-bot, whatsapp-bot, vk-bot]
related: [EXP-035]
tags: [emoji, html-entities, unicode, font-family, squares, rendering]
status: verified
---

# EXP-100: HTML entities для эмодзи показывают квадратики

## Проблема

HTML entities типа `&#x2610;` (BALLOT BOX), `&#x1F3DC;`, `&#x1F3D9;` и подобные на многих системах отображаются как пустые квадраты или прямоугольники вместо эмодзи.

## Контекст

- Не все шрифты содержат глифы для Unicode Emoji блоков
- Windows, Linux и macOS имеют разные шрифты с поддержкой эмодзи
- Особенно проблематичны символы из блока Miscellaneous Symbols (U+2600..U+26FF) и Supplemental Symbols (U+1F300..U+1F9FF)
- В PDF проблема усугубляется -- Playwright рендерит через Chromium с системными шрифтами

## Решение

**1. Заменить HTML entities на реальные UTF-8 эмодзи:**

```html
<!-- НЕПРАВИЛЬНО -->
<span>&#x1F3DC;</span>
<span>&#x2610;</span>

<!-- ПРАВИЛЬНО -->
<span>&#127964;</span>  <!-- или просто вставить эмодзи напрямую -->
```

**2. Добавить emoji-шрифты в body font-family:**

```css
body {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system,
                 'Segoe UI Emoji', 'Apple Color Emoji',
                 'Noto Color Emoji', 'Twemoji Mozilla',
                 sans-serif;
}
```

**3. Лучший вариант -- вставлять эмодзи напрямую как UTF-8 символы:**

```html
<span>&#x1F3DC;&#xFE0F;</span>  <!-- С variation selector для цветного рендера -->
```

## Урок

**Всегда использовать реальные UTF-8 эмодзи вместо HTML entity кодов.** Обязательно добавлять emoji-фолбэк шрифты (Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji) в font-family цепочку.
