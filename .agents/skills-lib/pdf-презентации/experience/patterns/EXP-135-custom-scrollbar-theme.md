# EXP-135 + EXP-147: Custom Scrollbar Matching Theme

> Дата: 2026-02-20 (EXP-135), обновлено 2026-03-02 (EXP-147)
> Проект: Telegram Business + Connected Bot v2.0 / GPU-презентация
> Категория: pattern

## Проблема
Системный скроллбар ломает визуальное единство тёмной презентации.

## Решение

### WebKit (Chrome, Edge, Safari)
```css
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-dark); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #76B900, #0071C5);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #8BD400, #0088EE);
}
```

### Firefox
Мержить В СУЩЕСТВУЮЩИЙ `html {}` блок:
```css
html {
    scrollbar-width: thin;
    scrollbar-color: #76B900 var(--bg-dark);
}
```

### TOC Overlay (отдельный скроллбар)
```css
.toc-overlay::-webkit-scrollbar { width: 6px; }
.toc-overlay::-webkit-scrollbar-track { background: rgba(10, 14, 23, 0.97); }
.toc-overlay::-webkit-scrollbar-thumb {
    background: rgba(118, 185, 0, 0.4);
    border-radius: 3px;
}
```

## Правила
1. Firefox props ВСЕГДА мержить в existing html{} — отдельный блок переопределит другие свойства
2. Gradient thumb: использовать 2 основных акцент-цвета темы (180deg vertical)
3. Hover на scrollbar-thumb — OK для HTML, игнорируется в PDF
4. Per-element scrollbar (overlay, sidebar) — отдельные ::-webkit-scrollbar правила
5. Track background = основной bg темы для полного слияния

## Адаптация под разные темы

| Тема | Thumb gradient | Firefox thumb | Hover gradient |
|------|---------------|---------------|----------------|
| AI Product Launch | #2AABEE -> #7C5CFC | #2AABEE | #3BBCFF -> #8D6DFF |
| Neural Grid | #4285F4 -> #10A37F | #4285F4 | — |
| Container Dock | #2496ED -> #1B3A5C | #2496ED | — |
| GitHub Dark | #58a6ff -> #3fb950 | #58a6ff | — |
| GPU Comparison | #76B900 -> #0071C5 | #76B900 | #8BD400 -> #0088EE |

## Связанные записи

- EXP-109 -- Кастомный scrollbar обязателен
- EXP-118 -- Scrollbar стилизация (webkit + Firefox)
- EXP-147 -- Gradient scrollbar + TOC overlay scrollbar (GPU-презентация)
