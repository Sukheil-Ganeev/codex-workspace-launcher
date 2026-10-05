---
id: EXP-104
date: 2026-02-13
type: pattern
severity: medium
category: css
projects: [telegram-bot, whatsapp-bot, vk-bot]
related: [EXP-091, EXP-033]
tags: [nth-child, isolation, per-slide, specificity, important]
status: verified
---

# EXP-104: Изоляция CSS-фиксов через .slide:nth-child(N)

## Принцип

Все per-slide фиксы должны быть привязаны к конкретному слайду через `:nth-child`, а не через глобальные селекторы.

## Реализация

```css
/* ПРАВИЛЬНО -- фикс только для слайда 3 */
.slide:nth-child(3) .card-grid {
    grid-template-columns: 1fr 1fr !important;
    gap: 20px !important;
}

.slide:nth-child(5) .section-label {
    font-size: 18px !important;
    color: #60A5FA !important;
}

/* НЕПРАВИЛЬНО -- глобальный фикс для единичной проблемы */
.card-grid {
    grid-template-columns: 1fr 1fr !important; /* Ломает ВСЕ слайды */
}
```

## Правила

1. **Единичные правки** -- всегда через `:nth-child(N)`
2. **!important** -- для переопределения inline стилей и glassmorphism
3. **Не использовать ID** -- слайды обычно не имеют ID, nth-child надёжнее
4. **Обратный порядок** -- при массовых фиксах начинать с последнего слайда (см. EXP-033)
5. **Комментарии** -- подписывать какой слайд и зачем

```css
/* === SLIDE 7: Webhooks — уменьшить padding таблицы === */
.slide:nth-child(7) .tbl td {
    padding: 8px 12px !important;
    font-size: 15px !important;
}
```

## Когда использовать глобальные селекторы

- Проблема воспроизводится на 3+ слайдах одинаково
- Это системный баг (glassmorphism, dekoration, навигация)
- Фикс не имеет побочных эффектов на других слайдах

## Урок

**Изоляция = безопасность.** nth-child гарантирует что фикс одного слайда не сломает остальные. Глобальные правки -- только для системных проблем.
