---
id: EXP-103
date: 2026-02-13
type: pattern
severity: high
category: animation
projects: [telegram-bot, whatsapp-bot, vk-bot]
related: [EXP-064, EXP-066, EXP-021]
tags: [animation, transition, hover, cubic-bezier, scale, performance, will-change]
status: verified
---

# EXP-103: Профессиональные анимации -- принципы плавности

## Принципы

Анимации должны быть **едва заметными** -- пользователь чувствует отзывчивость, но не отвлекается.

## Параметры

### Длительность
| Элемент | Правильно | Неправильно |
|---------|-----------|-------------|
| Hover карточки | 0.4-0.55s | 0.2-0.3s (слишком резко) |
| Hover кнопки | 0.3-0.4s | 0.15s (дёрганье) |
| Пульсации (glow) | 4-5s | 2-3s (слишком быстро, раздражает) |
| Shimmer эффекты | 8-10s | 4-6s (мельтешит) |

### Easing
```css
/* Профессиональный мягкий ease-out */
transition-timing-function: cubic-bezier(0.25, 0.46, 0.45, 0.94);

/* Альтернатива для быстрого отклика */
transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
```

### Scale и TranslateY
```css
/* ПРАВИЛЬНО -- едва заметный подъём */
.card:hover {
    transform: translateY(-3px) scale(1.015);
}

/* НЕПРАВИЛЬНО -- слишком агрессивно */
.card:hover {
    transform: translateY(-8px) scale(1.05); /* Прыгающие карточки */
}
```

| Свойство | Макс. значение | Типичная ошибка |
|----------|---------------|-----------------|
| scale | 1.015 | 1.02-1.08 (дрожание layout) |
| translateY | -3px | -5px..-10px (элементы "выпрыгивают") |

### Transition -- раздельные свойства

```css
/* ПРАВИЛЬНО */
.card {
    transition: transform 0.45s cubic-bezier(0.25, 0.46, 0.45, 0.94),
                box-shadow 0.45s cubic-bezier(0.25, 0.46, 0.45, 0.94),
                border-color 0.45s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* НЕПРАВИЛЬНО */
.card {
    transition: all 0.3s ease; /* Анимирует ВСЁ включая width, height, padding */
}
```

### GPU-ускорение

```css
.card {
    will-change: transform; /* Подсказка браузеру для GPU-ускорения */
}
```

## Анти-паттерны

1. `transition: all` -- анимирует неожиданные свойства, тормозит рендер
2. `scale(1.05)` и выше -- карточки "прыгают", layout дрожит
3. `duration < 0.3s` -- слишком резко, нет ощущения плавности
4. `pulse 2s infinite` -- раздражает через 10 секунд просмотра
5. Отсутствие `will-change` -- браузер не оптимизирует анимацию

## Урок

**Правило "едва заметно":** если анимацию видно с первого взгляда -- она слишком агрессивная. Профессиональные анимации создают ощущение, а не привлекают внимание.
