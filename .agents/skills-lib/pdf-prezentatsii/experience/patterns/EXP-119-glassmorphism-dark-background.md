# Glassmorphism на тёмном фоне -- работает с правильными параметрами
**Источник:** EXP-119 (Neural Grid v2, AI Models Comparison 2026, 2026-02-18)

## Проблема
backdrop-filter: blur() на однородном тёмном фоне даёт нулевой эффект (EXP-093 подтверждён). Нужен способ сделать glassmorphism видимым на тёмных палитрах.

## Решение
3-слойный фоновый паттерн создаёт достаточно "текстуры" под glass-элементами, чтобы blur был заметен:

```css
/* 1. Базовый фон + dot grid */
.slide::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 30px 30px;
}

/* 2. Горизонтальные линии */
.slide::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 99px,
        rgba(255,255,255,0.02) 99px,
        rgba(255,255,255,0.02) 100px
    );
}

/* 3. Radial-gradient accent для цветовой вариации */
body {
    background: #0A0E1A;
    background-image: radial-gradient(ellipse at 20% 50%, rgba(59,130,246,0.08) 0%, transparent 60%),
                       radial-gradient(ellipse at 80% 80%, rgba(16,185,129,0.06) 0%, transparent 50%);
}

/* Glass-элемент -- РАБОТАЕТ на текстурном фоне */
.glass-card {
    background: rgba(31, 41, 55, 0.55);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
}
```

### Ключевые параметры
| Параметр | Значение | Почему |
|----------|---------|--------|
| blur | 12px | Баланс видимости и производительности |
| background alpha | 0.55 | Достаточно прозрачности для blur + достаточно непрозрачности для читаемости |
| border alpha | 0.08 | Тонкий, не агрессивный |
| dot grid opacity | 0.03 | Едва заметный, но blur "видит" его |

## Когда использовать
- Тёмные sci-fi / tech темы с bg < #1A1A2E
- Множество карточек на странице (43 элемента с blur в Neural Grid -- всё работает)
- Когда нужен настоящий glassmorphism (не имитация через rgba)

## Ограничения
- Без текстурного фона (dot grid, lines, radial-gradient) blur невидим -- EXP-093 всё ещё актуален
- Apple Preview не поддерживает backdrop-filter -- для PDF всегда fallback через @media print
- На > 50 glass-элементах возможны тормоза на слабых устройствах
- НЕ использовать inset 0 1px 0 rgba(255,255,255,0.04) -- артефакты (EXP-112)

## Связанные
- EXP-061 -- Glassmorphism утилиты (базовые рецепты)
- EXP-071 -- Glassmorphism без backdrop-filter (альтернатива)
- EXP-093 -- backdrop-filter на однородном = 0 (почему нужна текстура)
- EXP-112 -- inset white highlight артефакты
