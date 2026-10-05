---
id: EXP-007
date: 2026-02-11
type: fix
severity: high
category: colors
projects: []
related: [EXP-021, EXP-042]
tags: [animated-html, multi-theme, glassmorphism, click-zones, light-theme]
status: verified
---

# Фиксы: Каталог русских книг — Animated HTML презентация

**Проект:** `D:/Downloads/Каталог_книг/05_презентация/`
**Тип:** Интерактивная animated HTML (НЕ PDF), 52-56 слайдов, навигация, поиск, темы
**Версии:** клиентская (52 слайда, без цен) + полная (56 слайдов, с аналитикой)
**Бэкапы:** `animated_backup_v2.html`
**Скриншоты:** `screenshots/` (52 PNG, render_slides.py)

---

## FIX-1: content-slide текст невидим на светлом фоне

**Проблема:** Текст на content-slide был белым/светлым, но content-slide ВСЕГДА имеет светлый фон (`var(--white)` = `#f0f2f5`) даже в "тёмной" теме. Тёмная тема меняет только title-slide и book-slide.

**Симптом:** Белый текст на светло-сером фоне = невидимый контент.

**Решение:** Текст на content-slide всегда ТЁМНЫЙ:
```css
/* Цвета для content-slide (не зависят от темы) */
.content-slide h2 { color: #0a1128; }
.content-slide p, .content-slide li { color: #34495e; }
```

**Правило:** НИКОГДА не использовать `var(--white)` или белые/светлые цвета для текста на content-slide.

---

## FIX-2: Glassmorphism !important перебивает highlight/featured

**Проблема:** Правило `.stat-card { background: rgba(255,255,255,0.05) !important }` из glassmorphism перебивало `.stat-card.highlight` с более тёмным фоном.

**Симптом:** Все stat-card выглядели одинаково, featured/highlight не выделялись.

**Решение:** Добавить `!important` к highlight/featured элементам:
```css
.stat-card.highlight {
    background: linear-gradient(135deg, #0a1128, #1b2845) !important;
    color: #ffffff !important;
}
```

**Правило:** Если glassmorphism использует `!important`, все вариации (highlight, featured, active) тоже должны иметь `!important`.

---

## FIX-3: var(--navy) невидим в light-теме

**Проблема:** `var(--navy)` в light-теме переопределяется в бежевый (`#f5f0e8`). Элемент с `color: var(--navy)` становится невидимым на бежевом фоне.

**Симптом:** Текст, рамки, иконки исчезают при переключении в light-тему.

**Решение:** В `body.light-theme` секциях использовать хардкодные цвета:
```css
body.light-theme .some-element {
    color: #1a1a2e;  /* НЕ var(--navy) */
    border-color: #2d2d4a;  /* НЕ var(--navy) */
}
```

**Правило:** В multi-theme дизайнах НЕ полагаться на CSS-переменные для цвета текста/рамок, если переменная меняет семантику между темами.

---

## FIX-4: CSS каскад — порядок + специфичность + !important

**Проблема:** `.set-card.featured` правила стояли ДО общих `.set-card` правил. Даже с более высокой специфичностью, `!important` из glassmorphism побеждал обычные правила.

**Решение:**
1. `.set-card.featured` правила ПОСЛЕ общих `.set-card`
2. Добавить `!important` к featured правилам
3. Проверять: glassmorphism `!important` + каскад = двойная проблема

---

## FIX-5: Navigation click zones перехватывают UI клики

**Проблема:** Click zones навигации (left 15%, right 15%) перехватывали клики по кнопкам, dropdown, поиску.

**Симптом:** Кнопки UI не реагируют на клик, вместо этого переключается слайд.

**Решение:** Трёхуровневая защита:
```javascript
// Layer 1: Проверка через closest() в navigation handler
if (e.target.closest('.toolbar, .search-overlay, .category-nav, button, select, input')) return;

// Layer 2: Координатная проверка (failsafe)
const rect = toolbar.getBoundingClientRect();
if (e.clientX >= rect.left && e.clientX <= rect.right && e.clientY >= rect.top && e.clientY <= rect.bottom) return;

// Layer 3: capture-phase флаг
document.addEventListener('click', (e) => {
    if (e.target.closest('.toolbar')) e._skipSlideNav = true;
}, true);
// В navigation handler:
if (e._skipSlideNav) return;
```

**Правило:** Slide navigation click handlers ВСЕГДА должны проверять, что клик не по UI элементу. Минимум 2 уровня защиты.

---

## FIX-6: Wheel event при открытом search overlay

**Проблема:** Wheel handler для переключения слайдов вызывал `e.preventDefault()` даже при открытом search overlay, блокируя прокрутку результатов поиска.

**Решение:**
```javascript
document.addEventListener('wheel', (e) => {
    if (searchOverlay.style.display !== 'none') return; // Пропускаем, если поиск открыт
    e.preventDefault();
    // ... логика переключения слайдов
}, { passive: false });
```

---

## FIX-7: Хаотичные UI кнопки → toolbar-ы

**Проблема:** Разбросанные кнопки (тема, категории, TOC, счётчик, подсказки) создавали хаотичный UI.

**Решение:** Группировка в toolbar-ы:
- **Top-right toolbar:** тема + категории (pill-панель с glassmorphism)
- **Bottom-center toolbar:** TOC + hints + счётчик (единая полоса с разделителями)
- Cat-nav toggle (выступающий tab) → скрыть, заменить кнопкой в toolbar

---

## FIX-8: Highlight карточки в light-теме

**Проблема:** Highlight/featured карточки теряли тёмный фон в light-теме, белый текст становился нечитаемым.

**Решение:**
```css
body.light-theme .set-card.highlight,
body.light-theme .stat-card.highlight {
    background: linear-gradient(135deg, #0a1128, #1b2845) !important;
    color: #ffffff !important;
}
```

**Правило:** Highlight карточки с белым текстом ВСЕГДА сохраняют тёмный фон, независимо от темы.

---

## FIX-9: roi-badge прозрачный в light-теме

**Проблема:** roi-badge получал прозрачный фон из glassmorphism, текст сливался с фоном.

**Решение:**
```css
body.light-theme .roi-badge {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: #ffffff !important;
}
```

---

## FIX-10: var(--white) для текста на content-slide = невидимый

**Проблема:** `var(--white)` = `#f0f2f5`, что совпадает с фоном content-slide. Текст исчезает.

**Правило:** НИКОГДА не использовать `var(--white)` для цвета текста на content-slide. Использовать тёмные хардкодные цвета.

---

## Рендер и отладка

### Скриншоты слайдов (PNG)
**Скрипт:** `screenshots/render_slides.py`
```python
# Python + Playwright
# viewport 1920x1080
# goToSlide(i) + wait 300ms + screenshot
```

### Chrome DevTools MCP для визуальной отладки
**Подход:**
1. Запустить `python -m http.server` (обход ограничения file:// URL)
2. `evaluate_script` для переключения тем/слайдов
3. `take_screenshot` для проверки результата
