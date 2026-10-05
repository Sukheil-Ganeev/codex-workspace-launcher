---
id: EXP-061
date: 2026-02-11
type: pattern
severity: medium
category: visual-effects
projects: [Калькулятор-Документация/06-Презентация-Владелец, Threads-справочник]
related: [EXP-033, EXP-038, EXP-043]
tags: [glassmorphism, backdrop-filter, css-utilities, visual-upgrade]
status: verified
---

## Контекст

Когда пользователь просит "улучши" или "сделай красивее" презентацию, один из самых эффективных визуальных приёмов -- glassmorphism. Он добавляет глубину и слоистость через полупрозрачные фоны, размытие и цветные бейджи. Паттерн был отработан на презентации "Vault Command Center" (06-Презентация-Владелец) и Threads "Neon Wire".

## Описание

### Утилит-классы glassmorphism

```css
/* Базовый glass-value */
.glass-value {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.10);
    font-size: 18px;
    font-weight: 600;
}

/* Цветные варианты */
.glass-value-green {
    background: rgba(0, 200, 83, 0.12);
    border-color: rgba(0, 200, 83, 0.20);
    color: #00c853;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05),
                inset 0 -1px 0 rgba(0,0,0,0.10);
}

.glass-value-amber {
    background: rgba(255, 160, 0, 0.12);
    border-color: rgba(255, 160, 0, 0.20);
    color: #ffa000;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05),
                inset 0 -1px 0 rgba(0,0,0,0.10);
}

.glass-value-red {
    background: rgba(239, 83, 80, 0.12);
    border-color: rgba(239, 83, 80, 0.20);
    color: #ef5350;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05),
                inset 0 -1px 0 rgba(0,0,0,0.10);
}
```

### Inset shadows для глубины

Ключевая техника glassmorphism -- двойные inset shadows (верхний светлый + нижний тёмный), создающие иллюзию стеклянной поверхности:

```css
.glass-card {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 16px;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.06),   /* верхний блик */
        inset 0 -1px 0 rgba(0, 0, 0, 0.12);         /* нижняя тень */
}
```

### КРИТИЧНОЕ ПРЕДУПРЕЖДЕНИЕ: backdrop-filter артефакты

**НЕ ИСПОЛЬЗОВАТЬ `backdrop-filter: blur()` + полупрозрачные border-ы на тёмном фоне если возможны артефакты!**

Проблема: светящиеся линии появляются на стыке `backdrop-filter: blur()` и полупрозрачных border-ов. Это баг рендеринга Chrome, который НЕЛЬЗЯ исправить через CSS. На проекте Калькулятор-Документация потрачено 6 итераций на попытки убрать эти артефакты -- не помогло, только ухудшило.

**Решение для тёмных тем:** Заменить `backdrop-filter` на увеличенный `opacity` фона:

```css
/* Вместо glassmorphism */
.card {
    background: rgba(255, 255, 255, 0.25);
    /* backdrop-filter: blur(10px);  <-- УБРАТЬ */
}
```

**Решение для Apple Preview:** `backdrop-filter` вообще не работает -- показывает белые квадраты. Всегда тестировать на Mac если аудитория использует Apple.

### Безопасная альтернатива (без backdrop-filter)

```css
.safe-glass {
    background: rgba(22, 27, 34, 0.92);  /* почти непрозрачный */
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.04),
        inset 0 -1px 0 rgba(0, 0, 0, 0.15);
    /* Нет backdrop-filter = нет артефактов */
}
```

## Когда применять

- Пользователь просит "улучши", "красивее", "премиальнее"
- Презентации с числовыми метриками (выручка, конверсии, KPI) -- glass-value-green/amber/red
- Тёмные темы с акцентными карточками
- Слайды-дашборды, аналитика

### Когда НЕ применять

- На светлых темах (glassmorphism теряет эффект на белом фоне)
- Если аудитория на Apple устройствах -- backdrop-filter не работает в Preview
- После 3+ итераций правок связанных с артефактами -- пересобирать с нуля (EXP из Калькулятор-Документации)
- На слайдах с большим количеством карточек -- gradient/blur на каждой раздувает PDF (EXP-038, EXP-043)

## Связанные уроки

- **EXP-033** -- Тени на тёмном фоне = "грязь", убирать box-shadow
- **EXP-038** -- CSS gradients на карточках раздувают PDF в 3x
- **EXP-043** -- radial-gradient на ::after раздувает PDF в 4x
- **SKILL.md Раздел 6** -- Совместимость с Apple, backdrop-filter не работает в Preview
