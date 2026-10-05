---
id: EXP-042
date: 2026-02-11
type: warning
severity: critical
category: colors
projects: []
related: [EXP-007, EXP-021, EXP-030]
tags: [css-variables, multi-theme, light-theme, important, invisible-text]
status: verified
---

# WARNING: CSS-переменные в multi-theme дизайнах

**Источник:** Каталог русских книг — animated HTML с dark/light темами
**Критичность:** ВЫСОКАЯ — приводит к невидимому тексту и нечитаемым элементам

---

## Проблема 1: Переменная меняет семантику между темами

```css
:root {
    --navy: #0a1128;      /* Тёмно-синий — используется как цвет текста */
}

body.light-theme {
    --navy: #f5f0e8;      /* Бежевый — теперь это ФОН, не текст! */
}
```

**Результат:** `color: var(--navy)` = тёмный текст в dark, БЕЖЕВЫЙ (невидимый) текст в light.

**Решение:** В `body.light-theme` секциях ХАРДКОДИТЬ цвета:
```css
body.light-theme .element {
    color: #1a1a2e;       /* Хардкод, НЕ var(--navy) */
}
```

---

## Проблема 2: var(--white) совпадает с фоном content-slide

```css
:root {
    --white: #f0f2f5;
}

/* content-slide ВСЕГДА имеет фон var(--white) */
.content-slide {
    background: var(--white); /* #f0f2f5 */
}

/* ЭТО ОШИБКА: */
.content-slide h2 {
    color: var(--white);  /* #f0f2f5 на фоне #f0f2f5 = НЕВИДИМО */
}
```

**Правило:** НИКОГДА не использовать `var(--white)` для текста на content-slide.

---

## Проблема 3: !important из glassmorphism перебивает вариации

```css
/* Glassmorphism (задан глобально) */
.stat-card {
    background: rgba(255,255,255,0.05) !important;
}

/* ЭТО НЕ СРАБОТАЕТ — !important выше побеждает */
.stat-card.highlight {
    background: linear-gradient(135deg, #0a1128, #1b2845);
    /* Без !important = проиграет glassmorphism */
}
```

**Решение:** Добавить `!important` ко ВСЕМ вариациям:
```css
.stat-card.highlight {
    background: linear-gradient(135deg, #0a1128, #1b2845) !important;
}
```

---

## Проблема 4: Каскад + специфичность — двойной конфликт

Даже `.set-card.featured` (специфичность 0,2,0) может проиграть `.set-card` (0,1,0) с `!important`.

**Правила приоритета CSS:**
1. `!important` побеждает специфичность
2. При одинаковом `!important` — специфичность решает
3. При одинаковой специфичности — порядок в файле решает

**Чек-лист для multi-theme:**
- [ ] `.featured`, `.highlight`, `.active` — ПОСЛЕ общих правил
- [ ] Если glassmorphism использует `!important` → вариации тоже с `!important`
- [ ] Тестировать переключение тем в обе стороны
- [ ] Проверять текст/фон в ОБЕИХ темах

---

## Проблема 5: Highlight карточки теряют тёмный фон в light-теме

Highlight карточки с белым текстом ОБЯЗАНЫ сохранять тёмный фон:
```css
body.light-theme .stat-card.highlight,
body.light-theme .set-card.featured {
    background: linear-gradient(135deg, #0a1128, #1b2845) !important;
    color: #ffffff !important;
}
```

---

## Золотые правила

1. **Если переменная меняет "семантику"** (из "цвет текста" в "цвет фона") — НЕ используй её для текста в обеих темах
2. **content-slide = всегда светлый фон** → текст всегда тёмный, хардкодом
3. **Glassmorphism + !important = проверяй ВСЕ вариации** (.highlight, .featured, .active)
4. **Бейджи (roi-badge, stat-badge)** — отдельные правила для light-теме с `!important`
5. **Тестируй ОБЕ темы** — переключай туда-обратно, проверяй каждый слайд
