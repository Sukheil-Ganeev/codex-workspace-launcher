# EXP-141: Замена backdrop-filter для PDF конвертации

**Тип:** FIX
**Дата:** 2026-02-28
**Проект:** AI Models Comparison 2026
**Контекст:** Glassmorphism в интерактивной версии → solid backgrounds в PDF

## Проблема
Интерактивная HTML-презентация использует glassmorphism:
```css
.card {
    background: rgba(15, 23, 42, 0.55);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
```
В PDF `backdrop-filter` рендерится как **белый/серый квадрат** (Chromium print engine не поддерживает).

## Решение: Автоматическая замена при создании PDF-копии

1. Найти ВСЕ `backdrop-filter` в CSS и inline styles
2. Удалить `backdrop-filter` и `-webkit-backdrop-filter`
3. Увеличить opacity фона: `rgba(..., 0.55)` → `rgba(..., 0.85)`
4. Добавить глобальное правило:

```css
/* PDF-safe reset */
* {
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
}
```

## Таблица замены opacity

| Исходный opacity | PDF opacity | Визуальный эффект |
|-----------------|-------------|------------------|
| 0.15-0.25 | 0.60-0.70 | Лёгкая карточка |
| 0.30-0.55 | 0.75-0.85 | Стандартная карточка |
| 0.60-0.80 | 0.85-0.92 | Плотная карточка |
| 0.85-0.97 | 0.95-0.98 | TOC overlay / модал |

## Workflow
1. `cp presentation.html presentation_pdf.html`
2. В копии: regex replace `backdrop-filter: blur\([^)]+\);?` → удалить
3. В копии: увеличить opacity в rgba()
4. Конвертировать копию в PDF
5. НЕ трогать оригинал

## Урок
Всегда держать ДВЕ версии: интерактивную (с glassmorphism) и PDF-ready (с solid backgrounds). Конвертировать только PDF-ready копию.
