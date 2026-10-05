# EXP-134: Premium TOC overlay

> Дата: 2026-02-20
> Проект: Telegram Business + Connected Bot v2.0
> Категория: pattern

## Проблема

Стандартный TOC overlay (EXP-115) использует backdrop-filter для frosted glass. В тёмных темах нужна более премиальная реализация с категориями, цветовыми кодами и keyboard shortcuts.

## Решение: Premium TOC overlay

### Фон и контейнер

```css
.toc-overlay {
    position: fixed;
    inset: 0;
    background: rgba(8, 10, 25, 0.97);  /* НЕ backdrop-filter! Solid rgba */
    z-index: 10000;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
    overflow-y: auto;
    padding: 60px 80px;
}

.toc-overlay.active {
    opacity: 1;
    pointer-events: all;
}
```

**ВАЖНО:** НЕ использовать backdrop-filter — solid rgba(8, 10, 25, 0.97) на тёмном фоне даёт тот же визуальный эффект и не создаёт проблем (EXP-093). Скрыто в @media print через pointer-events + opacity, поэтому не влияет на PDF.

### 3-колоночная сетка карточек

```css
.toc-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    max-width: 1200px;
    margin: 0 auto;
}

.toc-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    gap: 16px;
    align-items: flex-start;
}

.toc-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(42, 171, 238, 0.3);
}

.toc-card.active {
    border-color: var(--accent-blue);
    background: rgba(42, 171, 238, 0.08);
}
```

### Нумерация badge

```css
.toc-num {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.6);
    flex-shrink: 0;
}
```

### Цветовая категоризация

```css
.toc-category {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
    margin-bottom: 4px;
}

/* Маппинг категорий к слайдам */
.cat-hero { color: #2AABEE; }
.cat-business { color: #10B981; }
.cat-solution { color: #7C5CFC; }
.cat-tech { color: #F59E0B; }
.cat-ai { color: #EC4899; }
.cat-metrics { color: #06B6D4; }
.cat-pricing { color: #F59E0B; }
.cat-cta { color: #EF4444; }
```

### Accent line на карточке

```css
.toc-accent {
    height: 2px;
    width: 40px;
    border-radius: 1px;
    margin-top: 8px;
}
/* Цвет accent line = цвет категории */
```

### Keyboard shortcuts pill bar

```css
.toc-shortcuts {
    display: flex;
    gap: 24px;
    justify-content: center;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.shortcut-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.4);
}

.shortcut-key {
    color: var(--accent-blue);
    font-weight: 600;
    font-family: monospace;
}
```

```html
<div class="toc-shortcuts">
    <span class="shortcut-pill"><span class="shortcut-key">&larr;&rarr;</span> Navigate</span>
    <span class="shortcut-pill"><span class="shortcut-key">F</span> Fullscreen</span>
    <span class="shortcut-pill"><span class="shortcut-key">T</span> Contents</span>
    <span class="shortcut-pill"><span class="shortcut-key">ESC</span> Close</span>
</div>
```

### Close button

```css
.toc-close {
    position: absolute;
    top: 24px;
    right: 24px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
}

.toc-close:hover {
    background: rgba(255, 255, 255, 0.12);
}

.toc-close svg {
    width: 18px;
    height: 18px;
    stroke: rgba(255, 255, 255, 0.6);
    stroke-width: 2;
    fill: none;
}
```

### Auto-scroll active card

```javascript
function openTOC() {
    tocOverlay.classList.add('active');
    // Scroll active card into view
    const activeCard = tocOverlay.querySelector('.toc-card.active');
    if (activeCard) {
        activeCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}
```

## Для русской версии

Заменить labels:
- "Table of Contents" -> "Содержание"
- "Navigate" -> "Навигация"
- "Fullscreen" -> "Полный экран"
- "Close" -> "Закрыть"
- Категории: ГЕРОЙ, БИЗНЕС, РЕШЕНИЕ, ТЕХНОЛОГИИ, ИИ, МЕТРИКИ, ЦЕНА, ПРИЗЫВ

## Связанные записи

- EXP-115 -- TOC frosted glass (предыдущая версия)
- EXP-114 -- Keyboard shortcuts стандарт
- EXP-125 -- TOC overlay реализация (zoom-совместимая)
