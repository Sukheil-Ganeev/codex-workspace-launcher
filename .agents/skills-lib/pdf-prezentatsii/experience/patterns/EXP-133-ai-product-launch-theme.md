# EXP-133: "AI Product Launch" тёмная тема

> Дата: 2026-02-20
> Проект: Telegram Business + Connected Bot v2.0
> Категория: pattern

## Проблема

Нужна премиальная тёмная тема для презентации AI/tech продукта (Telegram Bot). Стандартные палитры не передают "AI-launch" ощущение.

## Решение: AI Product Launch палитра

```css
:root {
    --bg-dark: #0a0c1a;
    --bg-slide: #0a0c1a;
    --bg-card: rgba(255, 255, 255, 0.04);
    --accent-blue: #2AABEE;      /* Telegram blue */
    --accent-purple: #7C5CFC;    /* AI/tech purple */
    --accent-green: #10B981;     /* success/growth */
    --accent-red: #EF4444;       /* alerts/danger */
    --accent-gold: #F59E0B;      /* premium/highlights */
    --text-primary: rgba(255, 255, 255, 0.92);
    --text-secondary: rgba(255, 255, 255, 0.65);
    --text-muted: rgba(255, 255, 255, 0.40);
}
```

### Gradient text комбинации

```css
/* Hero заголовки — основной акцент */
.gradient-text-hero {
    background: linear-gradient(135deg, #2AABEE, #7C5CFC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Зелёно-фиолетовый акцент — для подзаголовков, цитат */
.gradient-text-alt {
    background: linear-gradient(135deg, #7C5CFC, #10B981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

## Когда использовать

- Презентации AI/ML продуктов
- Запуск Telegram-ботов
- Tech product launch
- SaaS pitch decks

## Сочетаемые компоненты

- Glassmorphism карточки (EXP-128)
- Mesh gradients на .slide (EXP-127)
- Gradient text + shimmer (EXP-129)
- Premium TOC overlay (EXP-134)
- CSS ambient glow (overflow-x: hidden обязателен, EXP-137)

## Правила

1. `#0a0c1a` чуть темнее стандартного `#0A0E1A` — более глубокий "космический" фон
2. Telegram blue `#2AABEE` как главный акцент — привязка к бренду
3. Фиолетовый `#7C5CFC` — "AI" ощущение, хорошо дополняет голубой
4. Золотой `#F59E0B` — только для premium выделений (pill tags, KPI, бейджи)
5. Не использовать все 5 акцентов на одном слайде — максимум 3
