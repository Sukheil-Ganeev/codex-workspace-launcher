---
id: EXP-101
date: 2026-02-13
type: warning
severity: critical
category: css
projects: [telegram-bot, whatsapp-bot, vk-bot]
related: [EXP-091, EXP-061, EXP-093, EXP-097]
tags: [glassmorphism, gradient-text, border-left, border-collapse, not-selector, overrides]
status: verified
---

# EXP-101: Glassmorphism модуль ломает специфические элементы

## Проблема

Глобальный glassmorphism модуль перезаписывает стили специфических элементов, которые полагаются на:
1. **Gradient text** (`-webkit-background-clip: text`) -- glassmorphism ставит solid background поверх градиента, текст становится невидимым
2. **Цветные border-left** на карточках (`.card-blue`, `.card-indigo`, `.card-green`, `.card-amber`) -- перезаписываются общим border
3. **Цветные бордеры тегов** (`.tag-b`, `.tag-i`, `.tag-g`) -- аналогично перезаписываются
4. **border-collapse: collapse** на `.tbl` таблицах -- конфликтует с `border-collapse: separate` от glassmorphism

## Что НЕ работает

- Простое добавление `!important` на оригинальные стили -- glassmorphism тоже использует `!important`
- Порядок CSS -- glassmorphism загружается позже и перезаписывает

## Решение

**Исключения через :not() селекторы в glassmorphism модуле:**

```css
/* Glassmorphism НЕ трогает эти элементы */
.card:not(.card-blue):not(.card-indigo):not(.card-green):not(.card-amber) {
    /* glassmorphism стили */
}

.section-label {
    /* Восстановить gradient text */
    background: linear-gradient(...) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
}

.tbl {
    border-collapse: collapse !important; /* Перебить separate */
}
```

**Или отдельные правила восстановления после glassmorphism:**

```css
/* Восстановление после glassmorphism */
.card-blue { border-left: 4px solid #3B82F6 !important; }
.card-indigo { border-left: 4px solid #6366F1 !important; }
.tag-b { border-color: #3B82F6 !important; }
```

## Критическое правило

**При добавлении glassmorphism модуля ВСЕГДА проверять:**
1. Gradient text элементы (section-label, accent-text)
2. Цветные border-left карточки
3. Цветные теги/бейджи
4. Таблицы с border-collapse: collapse
5. Любые элементы с кастомными background/border

## Контекст

- Это расширение уроков EXP-091 (`.slide > *` ломает absolute) и EXP-097 (декор-классы)
- Glassmorphism -- мощный визуальный инструмент, но требует аккуратных исключений
