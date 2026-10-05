---
id: EXP-068
date: 2026-02-11
type: pattern
severity: high
category: design-system
projects: [Skill_Presentations (все 23 справочника)]
related: [EXP-026, EXP-062, EXP-065, EXP-025]
tags: [компоненты, дизайн-система, css, карточки, таблицы, code-block]
status: verified
---

## Контекст

За 23 справочника выработана библиотека CSS-компонентов, которые копируются из проекта в проект. Базовые компоненты одинаковы во всех темах, а тема-специфичные добавляют уникальную визуальную метафору. Этот файл описывает каждый базовый компонент, его CSS-структуру и когда использовать.

## Описание

### 1. `.slide` -- Слайд (контейнер страницы)

**Когда:** Каждая "страница" PDF. Обязательный корневой элемент.

```css
.slide {
    width: 1920px;
    height: 1080px;
    padding: 70px 100px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    background: var(--bg-slide);
    page-break-after: always;
    page-break-inside: avoid;
}
.slide:last-child { page-break-after: auto; }
```

**Структура HTML:**
```html
<div class="slide" id="slide-1">
    <div class="gradient-top"></div>     <!-- 4px полоска сверху -->
    <div class="bg-glow g-1"></div>      <!-- Ambient свечение -->
    <div class="section-label">01 ВВЕДЕНИЕ</div>
    <h2>Заголовок слайда</h2>
    <div class="content two-columns">    <!-- Лейаут -->
        <!-- Контент -->
    </div>
    <div class="highlight-box">Акцент</div>
    <div class="slide-num">01 / 18</div>
</div>
```

---

### 2. `.card` -- Карточка

**Когда:** Основной контейнер для контента -- факты, описания, списки, код.

```css
.card {
    background: var(--bg-card);
    border-radius: 16px;
    padding: 32px;           /* 28px для плотных, 22px для очень плотных */
    position: relative;
    border: 1px solid var(--border-subtle);  /* rgba(255,255,255,0.06) */
}

/* Размерные варианты */
.card-sm { padding: 22px; }
.card-lg { padding: 40px; }

/* Цветовые варианты (left-border) */
.card-green { border-left: 3px solid var(--accent-1); }
.card-blue { border-left: 3px solid var(--accent-2); }
.card-warn { border-left: 3px solid var(--accent-3); }

/* Акцентный вариант (gradient border через mask-composite) */
.card-glow::before {
    content: ''; position: absolute; inset: 0;
    border-radius: 16px; padding: 1px;
    background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.02));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude;
}

/* Top shine */
.card::after {
    content: ''; position: absolute; top: 0; left: 20px; right: 20px; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}
```

---

### 3. `.styled-table` -- Таблица

**Когда:** Сравнения, списки параметров, прайс-листы, характеристики.

```css
.styled-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 15px;         /* 13px для шпаргалок */
}
.styled-table th {
    text-align: left;
    padding: 12px 16px;
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-secondary);
    border-bottom: 2px solid var(--border-light);
    background: rgba(var(--accent-1-rgb), 0.08);  /* Тинтованный заголовок */
}
.styled-table td {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-primary);
}
.styled-table tr:last-child td { border-bottom: none; }
```

**Таблица в карточке:**
```html
<div class="card card-sm" style="padding:0; overflow:hidden;">
    <table class="styled-table" style="margin:0;">...</table>
</div>
```

---

### 4. `.code-block` -- Блок кода

**Когда:** Примеры кода, CLI-команды, конфиги, API-запросы.

```css
.code-block {
    background: var(--code-bg);  /* Тонированный под тему, НЕ #010409 (EXP-040) */
    border-radius: 12px;
    padding: 20px 24px;
    font-family: 'Consolas', 'SF Mono', 'Fira Code', monospace;
    font-size: 13px;             /* 12-12.5px для плотных */
    line-height: 1.5;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(var(--accent-1-rgb), 0.10);
}

/* Terminal dots */
.code-dots {
    display: flex; gap: 6px; margin-bottom: 12px;
}
.code-dots span {
    width: 7px; height: 7px;    /* НЕ 10px -- слишком крупно */
    border-radius: 50%;
    opacity: 0.5;                /* Приглушённые, EXP-046 */
}
.code-dots .d-r { background: #e8655f; }  /* Смягчённые цвета */
.code-dots .d-y { background: #d9a83a; }
.code-dots .d-g { background: #32b54a; }

/* Syntax highlighting (базовые классы) */
.code-block .cm { color: #6e7681; }   /* comment */
.code-block .kw { color: var(--syntax-keyword, #e8756e); }
.code-block .st { color: var(--syntax-string, #a5d6ff); }
.code-block .fn { color: var(--syntax-function, #c49ef0); }
.code-block .num { color: var(--syntax-number, #6db3e8); }
.code-block .prop { color: var(--syntax-property, #d9944e); }

/* Language badge */
.code-lang {
    position: absolute; top: 0; right: 0;
    font-size: 10px; padding: 2px 10px;
    border-radius: 0 10px 0 8px;
    background: rgba(var(--accent-1-rgb), 0.15);
    color: var(--accent-1);
}
```

**Описание перед code-block (EXP-039):**
```css
.code-note {
    font-size: 14px;
    color: var(--text-muted);
    padding-left: 12px;
    border-left: 2px solid rgba(var(--accent-1-rgb), 0.2);
    margin-bottom: 8px;
}
```

---

### 5. `.timeline` -- Горизонтальная цепочка шагов

**Когда:** Последовательности, roadmaps, этапы процесса (3-5 шагов).

```css
.timeline {
    display: flex;
    align-items: stretch;
    gap: 0;                      /* Шаги вплотную, стрелки через ::after */
}
.timeline-step {
    flex: 1;
    padding: 20px;
    background: var(--bg-card);
    border-radius: 12px;
    text-align: center;
    position: relative;
    margin-right: 32px;          /* Место для стрелки */
}
.timeline-step::after {
    content: '';
    position: absolute;
    right: -20px;
    top: 50%;
    transform: translateY(-50%);
    border-left: 8px solid var(--accent-1);
    border-top: 6px solid transparent;
    border-bottom: 6px solid transparent;
}
.timeline-step:last-child::after { display: none; }
.timeline-step:last-child { margin-right: 0; }
```

---

### 6. `.flow-container` -- Блоки со стрелками

**Когда:** Pipeline, workflow, цепочки обработки данных.

```css
.flow-container {
    display: flex;
    align-items: center;
    gap: 12px;
}
.flow-step {
    flex: 1;
    padding: 16px 20px;
    background: var(--bg-card);
    border-radius: 12px;
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid var(--border-subtle);
}
.flow-arrow {
    font-size: 20px;
    color: var(--accent-1);
    flex-shrink: 0;
}
```

HTML: `<div class="flow-step">Шаг 1</div><div class="flow-arrow">--></div><div class="flow-step">Шаг 2</div>`

---

### 7. `.bar-chart` -- Горизонтальная диаграмма

**Когда:** Метрики, рейтинги, прогресс, сравнения значений.

```css
.bar-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}
.bar-label {
    width: 80px;              /* НЕ 110px -- выпирает (EXP-034) */
    font-size: 13px;
    color: var(--text-secondary);
    text-align: right;
    flex-shrink: 0;
}
.bar-track {
    flex: 1;
    height: 24px;
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 12px;
    background: var(--accent-1);
    /* width через inline style: width: 85% */
}
.bar-value {
    width: 48px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    flex-shrink: 0;
}
```

---

### 8. `.chat-mockup` -- Имитация чата

**Когда:** Мессенджеры (Telegram, WhatsApp, Max), боты, UI переписки.

```css
.chat-mockup {
    background: var(--bg-card);
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--border-subtle);
}
.chat-header {
    padding: 12px 20px;
    background: var(--bg-card-elevated);
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--border-subtle);
}
.chat-body {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.chat-msg {
    max-width: 75%;
    padding: 10px 16px;
    border-radius: 14px;
    font-size: 15px;
    line-height: 1.4;
}
.chat-msg.out {
    align-self: flex-end;
    background: var(--accent-1);       /* или wa-out для WhatsApp */
    border-radius: 14px 14px 2px 14px;
}
.chat-msg.in {
    align-self: flex-start;
    background: var(--bg-card-elevated);
    border-radius: 14px 14px 14px 2px;
}
```

**Важно:** Chat mockup занимает много места -- при нехватке уменьшать padding (20 -> 14px) и font-size (15 -> 13px).

---

### 9. `.highlight-box` -- Акцентная плашка

**Когда:** Вывод, совет, результат -- прижимается к низу слайда через `margin-top: auto` или фиксированный `margin-top: 20px`.

```css
.highlight-box {
    padding: 20px 28px;
    background: rgba(var(--accent-1-rgb), 0.06);
    border-left: 4px solid var(--accent-1);
    border-radius: 0 12px 12px 0;
    font-size: 15px;
    line-height: 1.5;
    color: var(--text-primary);
    margin-top: 20px;           /* Гарантированный отступ (EXP-053) */
    flex-shrink: 0;              /* Не сжимается (EXP-053) */
}
```

**Правило:** НЕ ставить `flex: 1` на grid-контейнер если на том же уровне есть highlight-box (EXP-053).

---

### 10. `.bg-glow` -- Ambient свечение

**Когда:** Добавление глубины и атмосферы. 1-2 штуки на слайд с разными позициями.

```css
.bg-glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(150px);        /* Работает в PDF! */
    z-index: 0;
    pointer-events: none;
}
.g-1 {
    width: 500px; height: 500px;
    background: var(--accent-1);
    opacity: 0.06;
    top: -100px; left: -100px;
}
.g-2 {
    width: 400px; height: 400px;
    background: var(--accent-2);
    opacity: 0.04;
    bottom: -80px; right: -80px;
}
```

---

### 11. Лейауты

```css
.two-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
}
.three-columns {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 24px;
}
.four-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;  /* 2x2 grid */
    gap: 20px;
}
.split-40-60 {
    display: grid;
    grid-template-columns: 2fr 3fr;
    gap: 32px;
}
.split-50-50 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
}
/* align-items: stretch по умолчанию -- НЕ ставить start (EXP-035) */
```

---

### 12. `.vs-layout` -- Сравнение двух вариантов

**Когда:** "До / После", "Правильно / Неправильно", сравнение подходов.

```css
.vs-layout {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 24px;
    align-items: stretch;
}
.vs-label {
    writing-mode: vertical-lr;
    text-orientation: mixed;
    font-size: 28px;
    font-weight: 700;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    justify-content: center;
}
```

---

### 13. Вспомогательные элементы

```css
/* gradient-top -- полоска сверху слайда */
.gradient-top {
    position: absolute; top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--gradient-top);
}

/* section-label -- метка секции */
.section-label {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: var(--accent-1);
    margin-bottom: 8px;
}

/* slide-num -- номер слайда */
.slide-num {
    position: absolute;
    bottom: 30px; right: 100px;
    font-size: 15px;
    color: var(--text-muted);
}

/* tags */
.tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid rgba(var(--tag-color-rgb), 0.25);
}
.tag-blue { background: rgba(88,166,255,0.10); color: #58a6ff; }
.tag-green { background: rgba(63,185,80,0.10); color: #3fb950; }
.tag-yellow { background: rgba(210,153,34,0.10); color: #d29922; }
.tag-red { background: rgba(248,81,73,0.10); color: #f85149; }

/* feature-list */
.feature-list {
    list-style: none; padding: 0;
}
.feature-list li {
    padding: 8px 0 8px 28px;
    position: relative;
    font-size: 17px;
    line-height: 1.5;
}
.feature-list li::before {
    content: '';
    position: absolute; left: 0; top: 16px;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent-1);
}
```

## Когда применять

- При создании нового справочника -- копировать базовые компоненты из любого готового
- При добавлении нового слайда -- выбирать компонент по типу контента (см. "Когда" для каждого)
- При адаптации темы -- менять ТОЛЬКО `:root` переменные, компоненты остаются
- При добавлении уникальных компонентов -- строить поверх базовых (`.card` как основа)

## Связанные уроки

- **EXP-026** -- Серия справочников, единая дизайн-система с переключаемыми темами
- **EXP-062** -- Выбор цветовой палитры
- **EXP-065** -- Типографика для 1920x1080
- **EXP-025** -- Масштабирование шрифтов
