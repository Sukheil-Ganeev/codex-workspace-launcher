---
id: EXP-106
date: 2026-02-13
type: pattern
severity: medium
category: layout
projects: [telegram-bot, whatsapp-bot, vk-bot]
related: [EXP-064, EXP-104]
tags: [timeline, before, pseudo-element, box-shadow, glow, display-none]
status: verified
---

# EXP-106: Timeline ::before линии -- пользователи часто просят убрать

## Проблема

Timeline и flow элементы часто имеют вертикальные/горизонтальные линии через `::before` или `::after` псевдо-элементы с box-shadow glow. Эти яркие размытые полосы -- часто первое что бросается в глаза как "лишнее" или "мешающее".

## Контекст

```css
/* Типичный timeline с glow-линией */
.timeline::before {
    content: '';
    position: absolute;
    left: 50%;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, #3B82F6, #8B5CF6);
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.4),
                0 0 30px rgba(59, 130, 246, 0.2);
}
```

## Решение

**Убирать через nth-child + display: none:**

```css
/* Убрать timeline линию на конкретном слайде */
.slide:nth-child(4) .timeline::before {
    display: none !important;
}

/* Или убрать glow, оставив линию */
.slide:nth-child(4) .timeline::before {
    box-shadow: none !important;
    opacity: 0.3;
}
```

## Когда убирать

1. Пользователь явно просит убрать "светящиеся линии"
2. Линия конкурирует с контентом за внимание
3. На слайде слишком много визуальных элементов
4. Линия не несёт смысловой нагрузки (декоративная)

## Когда оставить

1. Timeline реально показывает хронологию/последовательность
2. Flow-диаграмма -- линии связывают шаги
3. Линия тонкая и неяркая (opacity < 0.3, без glow)

## Урок

**Декоративные линии = первый кандидат на удаление при визуальной "шумности" слайда.** Проактивно делать их тонкими (1px) и тусклыми (opacity 0.2), или использовать только на слайдах с минимальным контентом.
