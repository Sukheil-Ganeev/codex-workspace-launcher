---
id: EXP-099
date: 2026-02-13
type: fix
severity: high
category: images
projects: [telegram-bot, whatsapp-bot, vk-bot]
related: [EXP-041, EXP-093]
tags: [backdrop-filter, blur, images, glassmorphism, quality, crisp-edges]
status: verified
---

# EXP-099: backdrop-filter blur на контейнере изображений убивает качество

## Проблема

Glassmorphism модуль добавляет `backdrop-filter: blur(4px)` на `.product-img` и другие контейнеры с изображениями. Это создаёт "дымку" поверх картинок -- изображения выглядят размытыми и нечёткими.

## Контекст

- Glassmorphism утилиты применяются глобально ко всем карточкам
- `.product-img`, `.card img`, `.feature-img` попадают под общие правила
- Особенно заметно на мелких иконках и скриншотах интерфейсов

## Решение

**Явно отключить backdrop-filter на контейнерах с img + добавить crisp-edges:**

```css
/* Контейнеры с изображениями -- без blur */
.product-img,
.card img,
.feature-img,
[class*="img"] img {
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    image-rendering: crisp-edges;
    image-rendering: -webkit-optimize-contrast;
}
```

## Урок

**Glassmorphism blur предназначен для фоновых элементов и панелей, НЕ для контейнеров с изображениями.** Всегда исключать img-контейнеры из общих glassmorphism правил.

## Связь с другими записями

- EXP-041 -- backdrop-filter артефакты (НЕ ЧИНИТЬ в общем случае)
- EXP-093 -- backdrop-filter на однородном фоне = 0 эффект
- Текущий урок: backdrop-filter на img = деградация качества
