# Gradient border через ::before + mask-composite
**Источник:** EXP-122 (Neural Grid v2, AI Models Comparison 2026, 2026-02-18)

## Проблема
`border-image` с gradient не работает вместе с `border-radius` -- углы становятся прямыми. Нужен gradient border, совместимый с rounded corners.

## Решение

```css
.card {
    position: relative;
    border-radius: 16px;
    /* НЕ использовать border -- вместо него ::before */
}

.card::before {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: inherit;
    background: linear-gradient(180deg,
        rgba(255, 255, 255, 0.1),
        rgba(255, 255, 255, 0.02)
    );
    /* Маска: показать только "рамку" (разница между content-box и padding-box) */
    mask: linear-gradient(#fff 0 0) content-box,
          linear-gradient(#fff 0 0);
    mask-composite: exclude;
    -webkit-mask-composite: xor;
    padding: 1px; /* Толщина "бордера" */
    pointer-events: none;
    z-index: 0;
}

.card > * {
    position: relative;
    z-index: 1;
}
```

### Как это работает
1. `::before` создаёт полноразмерный overlay с gradient
2. `mask` с двумя слоями: первый покрывает content-box, второй -- весь элемент
3. `mask-composite: exclude` вычитает внутреннюю часть -- остаётся только рамка
4. `padding: 1px` определяет толщину рамки
5. `inset: -1px` компенсирует padding, чтобы рамка была вокруг элемента

### Варианты gradient
```css
/* Тонкий top-fade */
background: linear-gradient(180deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02));

/* Provider-colored */
background: linear-gradient(180deg, var(--provider-color), transparent);

/* Rainbow */
background: linear-gradient(135deg, #3B82F6, #10B981, #D97706);
```

## Когда использовать
- Карточки на тёмном фоне с border-radius
- Замена border-image (который не работает с border-radius)
- Когда нужен gradient border, исчезающий снизу (top-to-bottom fade)

## Ограничения
- `mask-composite` не поддерживается в IE11 (но для PDF-презентаций неактуально)
- Webkit требует `-webkit-mask-composite: xor` (не `exclude`)
- `pointer-events: none` обязателен -- иначе ::before перехватывает клики
- z-index: контент карточки должен быть выше ::before
- Если карточка имеет overflow: hidden -- ::before с inset: -1px обрезается, использовать inset: 0

## Связанные
- EXP-012 -- Gradient border (старый способ через border-image)
- EXP-124 -- Neural Grid дизайн-система
- EXP-119 -- Glassmorphism на тёмном фоне
