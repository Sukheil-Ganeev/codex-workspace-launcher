---
id: EXP-021
date: 2026-02-11
type: pattern
severity: high
category: layout
projects: []
related: [EXP-007, EXP-042, EXP-023]
tags: [animated-html, navigation, multi-theme, interactive, scroll]
status: verified
---

# Паттерн: Animated HTML презентация (интерактивная, НЕ PDF)

**Первый проект:** Каталог русских книг (52-56 слайдов)
**Путь:** `D:/Downloads/Каталог_книг/05_презентация/`

---

## Отличия от PDF презентации

| Аспект | PDF презентация | Animated HTML |
|--------|----------------|---------------|
| Анимации | Запрещены | Обязательны (transition, @keyframes) |
| Навигация | page-break | JavaScript goToSlide() |
| Интерактивность | Нет | Поиск, темы, фильтры, клик |
| Wheel/keyboard | Нет | Обработчики событий |
| Темы | Одна | Переключаемые (dark/light) |
| body height | Без фиксации | Фиксированная (100vh) |
| Формат | Статичный файл | Открывается в браузере |

---

## Архитектура слайдов

### Типы слайдов
```
title-slide      — титульный, с полноэкранным фоном/градиентом
content-slide    — контентный (ВСЕГДА светлый фон, даже в тёмной теме!)
book-slide       — карточка книги (с обложкой, описанием, данными)
```

### Навигация
```javascript
function goToSlide(index) {
    slides[currentSlide].classList.remove('active');
    slides[index].classList.add('active');
    currentSlide = index;
    updateCounter();
}

// Click zones: left 15% = назад, right 15% = вперёд
// Keyboard: ArrowLeft/ArrowRight, Space
// Wheel: deltaY > 0 = вперёд
```

### Защита UI от перехвата навигацией (КРИТИЧНО!)
```javascript
// Трёхуровневая защита:
// 1. e.target.closest() — проверка DOM-дерева
// 2. getBoundingClientRect() — координатная проверка
// 3. e._skipSlideNav — capture-phase флаг
```

---

## Multi-theme система

### Принцип
```css
:root {
    --navy: #0a1128;      /* В dark = тёмно-синий */
    --white: #f0f2f5;     /* В dark = светло-серый */
    --cream: #f5f0e8;     /* Бежевый */
}

body.light-theme {
    --navy: #f5f0e8;      /* ВНИМАНИЕ: navy стал бежевым! */
    --white: #f0f2f5;     /* Не меняется */
}
```

### Правила для multi-theme
1. **content-slide ВСЕГДА светлый** — текст всегда тёмный (#0a1128, #34495e)
2. **НЕ использовать var() для текста на content-slide** — переменные меняют семантику
3. **Highlight карточки** — всегда тёмный navy фон + `!important`
4. **Glassmorphism + !important** — все вариации (highlight, featured) тоже с `!important`
5. **body.light-theme** — хардкодные цвета, не CSS-переменные

---

## Поиск

### Search overlay
```html
<div class="search-overlay" style="display: none;">
    <input type="text" placeholder="Поиск книг...">
    <div class="search-results"><!-- Динамически --></div>
</div>
```

### Wheel handler при поиске
```javascript
// КРИТИЧНО: пропускать wheel event если поиск открыт
if (searchOverlay.style.display !== 'none') return;
```

---

## UI организация — toolbar-ы

### Top-right toolbar
```
[Тема] [Категории]
```
Glassmorphism панель, pill-кнопки.

### Bottom-center toolbar
```
[TOC] | [Hints] | [1/52]
```
Единая полоса с разделителями.

---

## Рендер слайдов в PNG

### Скрипт: render_slides.py
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    page.goto('http://localhost:8000/animated.html')
    page.wait_for_load_state('networkidle')

    total = page.evaluate('slides.length')
    for i in range(total):
        page.evaluate(f'goToSlide({i})')
        page.wait_for_timeout(300)
        page.screenshot(path=f'screenshots/slide_{i+1:02d}.png')

    browser.close()
```

### Chrome DevTools MCP отладка
1. `python -m http.server` — обход file:// ограничения
2. `evaluate_script('goToSlide(5)')` — переключить слайд
3. `evaluate_script('document.body.classList.toggle("light-theme")')` — сменить тему
4. `take_screenshot` — проверить результат

---

## Две версии из одного файла

| Версия | Слайды | Содержание |
|--------|--------|------------|
| Клиентская | 52 | Книги, описания, рекомендации. БЕЗ цен и аналитики |
| Полная | 56 | Всё + ценообразование + аналитика + ROI |

**Подход:** Создать полную версию, затем удалить 4 аналитических слайда для клиентской.
**Файлы:**
- `клиентская_версия/animated.html`
- `полная_версия/animated.html`

---

## Чек-лист для animated HTML

- [ ] content-slide текст тёмный (НЕ белый)
- [ ] Glassmorphism !important сбалансирован с highlight/featured
- [ ] var() переменные проверены в обеих темах
- [ ] Navigation click zones не перехватывают UI
- [ ] Wheel event не блокирует scroll при поиске
- [ ] UI элементы сгруппированы в toolbar-ы
- [ ] Highlight карточки сохраняют тёмный фон в light-теме
- [ ] roi-badge/бейджи видимы в обеих темах
- [ ] Скриншоты всех слайдов в PNG (render_slides.py)
