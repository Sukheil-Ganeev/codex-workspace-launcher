# Тема "Neural Grid" -- дизайн-система
**Источник:** EXP-124 (Neural Grid v2, AI Models Comparison 2026, 2026-02-18)

## Проблема
Нужна визуально сильная тема для tech comparisons, AI benchmarks и pricing tables -- sci-fi эстетика, которая выделяет данные, а не декор.

## Решение

### Палитра
```css
:root {
    /* Фон */
    --bg-primary: #0A0E1A;
    --bg-card: rgba(31, 41, 55, 0.55);
    --bg-card-hover: rgba(31, 41, 55, 0.7);

    /* Текст */
    --text-primary: #F9FAFB;
    --text-secondary: #9CA3AF;
    --text-muted: #6B7280;

    /* Провайдеры (акцентные) */
    --color-google: #4285F4;
    --color-openai: #10A37F;
    --color-anthropic: #D97706;
    --color-xai: #1DA1F2;

    /* Границы */
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-hover: rgba(255, 255, 255, 0.15);
}
```

### Шрифты
```css
/* Headings -- геометрический, tech-feel */
font-family: 'Space Grotesk', sans-serif;

/* Body -- нейтральный, высокая читаемость */
font-family: 'Inter', sans-serif;

/* Data / code -- моноширинный для чисел и кода */
font-family: 'JetBrains Mono', monospace;
```

### Фоновый паттерн (3 слоя)
```css
/* Слой 1: Dot grid */
background-image: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
background-size: 30px 30px;

/* Слой 2: Горизонтальные линии */
background-image: repeating-linear-gradient(
    0deg, transparent, transparent 99px,
    rgba(255,255,255,0.02) 99px, rgba(255,255,255,0.02) 100px
);

/* Слой 3: Цветные radial-gradient акценты */
background-image:
    radial-gradient(ellipse at 20% 50%, rgba(59,130,246,0.08) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 80%, rgba(16,185,129,0.06) 0%, transparent 50%);
```

### Gradient border через mask-composite
```css
.card::before {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: inherit;
    background: linear-gradient(180deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02));
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    -webkit-mask-composite: xor;
    padding: 1px;
    pointer-events: none;
}
```

### Benchmark бары
```css
.benchmark-bar {
    height: 32px;
    border-radius: 6px;
    background: linear-gradient(90deg,
        var(--provider-color) 0%,
        color-mix(in srgb, var(--provider-color), white 15%) 80%,
        color-mix(in srgb, var(--provider-color), white 25%) 100%
    );
    transition: width 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.benchmark-value {
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
}
```

## Когда использовать
- Tech comparisons (AI модели, облачные сервисы, фреймворки)
- Benchmark презентации с числовыми данными
- Pricing tables с несколькими провайдерами
- Любые sci-fi / dark-tech темы

## Ограничения
- Не подходит для "тёплых" или "human" тематик (туризм, еда, lifestyle)
- Провайдерские цвета (#4285F4, #10A37F, #D97706, #1DA1F2) -- заменять под конкретных вендоров
- Space Grotesk + Inter + JetBrains Mono -- 3 шрифта = 3 CDN-запроса, для standalone использовать font-display: swap
- Dot grid 30px + horizontal lines 100px -- значения подобраны для 1920x1080, для других разрешений масштабировать

## Связанные
- EXP-062 -- Палитра: 21 тема (добавить Neural Grid как 22-ю)
- EXP-065 -- Типографика для 1920x1080
- EXP-068 -- 13 компонентов дизайн-системы
- EXP-119 -- Glassmorphism на тёмном фоне (рецепт текстуры)
- EXP-122 -- Gradient border через mask-composite (детали)
- EXP-123 -- Benchmark бары (детали)
