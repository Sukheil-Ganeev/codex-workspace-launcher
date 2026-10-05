# Gradient text для hero заголовков
**Источник:** EXP-121 (Neural Grid v2, AI Models Comparison 2026, 2026-02-18)

## Проблема
Обычный белый заголовок на тёмном фоне выглядит плоско. Нужен визуально яркий hero-эффект без изображений.

## Решение

```css
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 64px;
    font-weight: 700;
    background: linear-gradient(135deg, #F9FAFB 0%, #3B82F6 50%, #10B981 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 8s linear infinite;
}

@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

/* PDF fallback */
@media print {
    .hero-title {
        -webkit-text-fill-color: #F9FAFB !important;
        background: none !important;
        animation: none !important;
    }
}
```

### Ключевые параметры
| Параметр | Значение | Почему |
|----------|---------|--------|
| gradient angle | 135deg | Диагональ = динамичнее горизонтали |
| background-size | 200% auto | Обязательно для shimmer (без этого анимация не работает) |
| shimmer duration | 8s | Спокойный, не мельтешит (EXP-103) |
| fallback color | #F9FAFB | Читаемый белый для PDF |

## Когда использовать
- Hero-слайд (первый слайд / титульный)
- Заголовки секций для визуального разделения
- Ключевые метрики / числа (в большом размере)

## Ограничения
- Не работает в Firefox < 90 (нужен -moz-background-clip: text)
- В PDF gradient text не печатается -- обязателен @media print fallback
- Не использовать на мелком тексте (< 24px) -- gradient нечитаем
- background-clip: text не наследуется -- задавать на каждый элемент отдельно
- Shimmer без background-size: 200% = статичный gradient (нет анимации)

## Связанные
- EXP-120 -- Анимации + PDF совместимость
- EXP-065 -- Типографика для 1920x1080
- EXP-124 -- Neural Grid дизайн-система
