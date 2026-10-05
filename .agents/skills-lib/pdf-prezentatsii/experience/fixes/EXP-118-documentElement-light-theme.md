# EXP-118: Перенос fixed-элементов в documentElement + дублирование light-theme

**Дата:** 2026-02-18
**Проект:** AI Companies Engineering Research (presentation_animated.html)
**Связан с:** EXP-094 (transform:scale ломает fixed)

## Проблема

При использовании EXP-094 фикса (перенос fixed-элементов в documentElement для обхода transform:scale на body), элементы теряют стили light-theme, потому что CSS-селекторы привязаны к `body.light-theme .element`, а элементы теперь дети `html`, а не `body`.

Симптомы:
- TOC overlay затемняет фон, но содержание не видно (рендерится за пределами viewport из-за transform контекста)
- После фикса EXP-094 переключение темы (D) не влияет на перенесённые элементы

## Решение

### 1. JS: перенести fixed-элементы в documentElement

```javascript
var fixedIds = ['tocOverlay', 'helpOverlay', 'progressBar', 'prevBtn', 'nextBtn', 'slideCounter', 'themeFade'];
fixedIds.forEach(function(id) {
    var el = document.getElementById(id);
    if (el) document.documentElement.appendChild(el);
});
```

### 2. JS: переключать класс на ОБОИХ элементах

```javascript
window.toggleTheme = function() {
    var fade = document.getElementById('themeFade');
    fade.classList.add('active');
    setTimeout(function() {
        document.body.classList.toggle('light-theme');
        document.documentElement.classList.toggle('light-theme'); // ← ДОБАВИТЬ!
        setTimeout(function() {
            fade.classList.remove('active');
        }, 150);
    }, 200);
};
```

### 3. CSS: дублировать light-theme селекторы с html префиксом

```css
/* Для элементов перенесённых в html */
body.light-theme .toc-content, html.light-theme .toc-content { ... }
body.light-theme .toc-item:hover, html.light-theme .toc-item:hover { ... }
body.light-theme .slide-counter, html.light-theme .slide-counter { ... }
body.light-theme .progress-bar, html.light-theme .progress-bar { ... }
html.light-theme .nav-arrow { ... }
html.light-theme .help-content { ... }
html.light-theme .help-content .key { ... }
html.light-theme .theme-fade { background: #0A0F1E; }
```

## Правило

При использовании EXP-094 (перенос в documentElement) ВСЕГДА:
1. Переключать light-theme на `document.body` И `document.documentElement`
2. Дублировать ВСЕ `body.light-theme .element` CSS-селекторы с `html.light-theme .element`
3. Список элементов для переноса: overlays, progress bar, nav arrows, slide counter, theme fade

## Чеклист

- [ ] JS: fixedIds включает ВСЕ fixed-элементы
- [ ] JS: toggleTheme переключает класс на body И html
- [ ] CSS: каждый `body.light-theme .X` имеет пару `html.light-theme .X`

## Категория

FIX (дополнение к EXP-094)
