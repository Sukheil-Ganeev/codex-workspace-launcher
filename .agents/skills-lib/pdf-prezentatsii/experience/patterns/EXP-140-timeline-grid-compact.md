# EXP-140: Timeline Grid — компактная сетка событий на одном слайде

**Тип:** PATTERN
**Дата:** 2026-02-28
**Проект:** AI Models Comparison 2026
**Контекст:** Слайд "Горячие релизы" — с 2 событий вырос до 10

## Ситуация
Слайд 12 изначально показывал 2 события (split layout: Sonnet 4.6 vs Grok 4.20). После обновления нужно было показать 10 событий за весь февраль.

## Решение: Compact 5x2 grid
Вместо добавления второго слайда — компактная сетка карточек:

```css
.releases-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
}

.release-card {
    padding: 16px;
    border-left: 3px solid var(--provider-color);
    /* Компактный формат: дата + заголовок + 1 строка описания */
}

.release-date {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-secondary);
}

.release-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--provider-color);
}

.release-desc {
    font-size: 12px;
    color: var(--text-secondary);
}
```

## Структура карточки
```
┌─────────────────┐
│ 5 фев           │  ← дата (mono, muted)
│ Claude Opus 4.6  │  ← заголовок (provider color)
│ 500+ zero-day    │  ← описание (1 строка)
└─────────────────┘
```

## Правила
- Максимум 10 карточек (5x2) на 1920x1080 слайде
- При >10 событиях — приоритизировать, НЕ добавлять второй слайд
- Provider-colored left border для визуальной группировки
- Хронологический порядок (слева направо, сверху вниз)
- Summary callout внизу слайда

## Урок
5x2 grid с компактными карточками вмещает до 10 событий без потери читаемости. Лучше чем split layout (макс 2-3) или list (теряется визуальная иерархия).
