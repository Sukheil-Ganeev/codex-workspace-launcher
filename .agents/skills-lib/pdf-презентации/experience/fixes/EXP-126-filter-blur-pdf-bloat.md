---
id: EXP-126
date: 2026-02-18
type: fix
severity: critical
category: performance
projects: [Docker-справочник "Container Dock"]
related: [EXP-067, EXP-093, EXP-095, EXP-071]
tags: [filter-blur, pdf-size, optimization, bg-glow, glassmorphism, playwright, performance]
status: verified
---

## filter:blur() на bg-glow = 20x раздутие PDF

### Контекст

Docker-справочник "Container Dock" -- 18 слайдов, 7 stock photos (1880px), glassmorphism v3.0 дизайн. Тема: тёмная industrial (#0A0E1A), Docker blue #2496ED + navy #1B3A5C + yellow #FFC107.

### Проблема

PDF вышел 52 MB (ожидалось < 8 MB по нормам EXP-067). Это в 6.5x больше нормы и в 20x больше оптимального размера.

### Корневая причина

`filter: blur(150px)` на `.bg-glow` элементах. В презентации было 3 bg-glow на слайд (top, middle, bottom) x 18 слайдов = **54 blurred circles**.

Каждый `filter: blur()` заставляет Playwright PDF renderer создать **Gaussian composite bitmap layer** -- растровое изображение размером с область blur (circle 300-500px + blur radius 150px с каждой стороны = ~800px bitmap). 54 таких bitmap'а = основной источник раздутия.

### Что НЕ помогло

| Действие | Результат | Экономия |
|----------|-----------|----------|
| Убрать backdrop-filter с карточек | 52 -> 50.5 MB | ~3% |
| Убрать inset shadow с карточек | 50.5 -> 50.3 MB | ~0% |
| Уменьшить blur radius (150px -> 80px) | 52 -> ~40 MB | ~23% |
| Убрать только grid pattern | 52 -> ~48 MB | ~8% |

### Решение (поэтапно)

#### 1. Убрать filter:blur() с bg-glow (ГЛАВНЫЙ ЭФФЕКТ: -45 MB)

```css
/* БЫЛО (52 MB): */
.bg-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(150px);
    opacity: 0.08;
}

/* СТАЛО (2.5 MB): */
.bg-glow {
    position: absolute;
    border-radius: 50%;
    /* filter: blur() УБРАН */
    opacity: 0.06;
}
```

Без blur круги становятся solid-colored полупрозрачными, но при opacity 0.06 они создают мягкую подсветку без заметных краёв.

#### 2. Убрать grid pattern (.slide::after)

```css
/* БЫЛО: */
.slide::after {
    content: '';
    background: repeating-linear-gradient(
        0deg, transparent, transparent 39px,
        rgba(255,255,255,0.02) 39px, rgba(255,255,255,0.02) 40px
    ), repeating-linear-gradient(
        90deg, transparent, transparent 39px,
        rgba(255,255,255,0.02) 39px, rgba(255,255,255,0.02) 40px
    );
}

/* СТАЛО: полностью убран */
```

#### 3. Заменить backdrop-filter на solid backgrounds

```css
/* БЫЛО: */
.card {
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(24px) saturate(140%);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
}

/* СТАЛО: */
.card {
    background: var(--bg-card); /* solid rgba(15, 23, 42, 0.85) */
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
```

#### 4. Упростить box-shadow

```css
/* Убрать многослойные тени: */
box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);

/* Заменить на простую: */
box-shadow: 0 2px 8px rgba(0,0,0,0.2);
/* Или совсем убрать: */
box-shadow: none;
```

### Результат

| Этап | Размер | Дельта |
|------|--------|--------|
| Исходный (все эффекты) | 52 MB | -- |
| Без backdrop-filter | 50.5 MB | -3% |
| Без filter:blur на bg-glow | **2.5 MB** | **-95%** |
| С фото 1880px | 3.6 MB | +1.1 MB от фото |

**20x reduction (52 -> 2.5 MB).** filter:blur -- это 95% от раздутия.

### Обновлённая таблица факторов раздутия (для EXP-067)

| Фактор | Impact | Ранг |
|--------|--------|------|
| **filter: blur() на bg-glow (NEW)** | **x20 (2.5 -> 52 MB)** | **#1** |
| radial-gradient на ::after слайдов | x4 (3.5 -> 14.5 MB) | #2 |
| linear-gradient на карточках | x3 (3.7 -> 11 MB) | #3 |
| SVG feTurbulence | x2.5 (7 -> 17 MB) | #4 |
| Glow blobs (filter:blur, мало) | +3-6 MB | #5 |

### Правило

**Для static/PDF версий:**
1. ВСЕГДА удалять `filter: blur()` с декоративных элементов (bg-glow, deco-circles)
2. Использовать solid backgrounds вместо glassmorphism (backdrop-filter)
3. Упрощать box-shadow до одного слоя или убирать
4. Убирать repeating-linear-gradient grid patterns

**Для animated HTML версий:**
- filter:blur МОЖНО оставлять -- в браузере он рендерится через GPU без bitmap
- backdrop-filter МОЖНО оставлять -- в браузере работает нативно
- Все визуальные эффекты допустимы

**Workflow (два файла):**
1. `animated.html` -- полная версия с filter:blur, backdrop-filter, grid patterns, анимациями
2. `static.html` -- деанимированная + оптимизированная для PDF: без filter:blur, solid bg, простые тени

### Когда применять

- При КАЖДОЙ конвертации HTML -> PDF
- Если PDF > 8 MB -- ПЕРВЫМ ДЕЛОМ проверить `grep "filter.*blur" file.html`
- При создании static.html -- автоматически убирать filter:blur в процессе деанимации

### Связанные уроки

- **EXP-067** -- Оптимизация размера PDF (бенчмарки, стратегии). EXP-126 обновляет таблицу факторов -- filter:blur теперь #1
- **EXP-093** -- backdrop-filter на однородном фоне = нулевой эффект (отдельная проблема, но решается тем же способом)
- **EXP-095** -- bg-glow opacity 0.30+ для видимости (в PDF без blur нужно opacity 0.06, не больше)
- **EXP-071** -- Glassmorphism без backdrop-filter (рецепт для static/PDF)
- **EXP-023** -- Деанимация HTML для PDF (добавить шаг удаления filter:blur)
