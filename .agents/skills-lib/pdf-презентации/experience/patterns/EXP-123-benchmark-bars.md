# Бенчмарк-бары -- лучшие практики
**Источник:** EXP-123 (Neural Grid v2, AI Models Comparison 2026, 2026-02-18)

## Проблема
Числовые бенчмарки (score, %, рейтинги) в таблицах нечитаемы. Нужна визуальная репрезентация с моментальным пониманием "кто лидер".

## Решение

### HTML-структура
```html
<div class="benchmark-row">
    <div class="benchmark-label">Claude Opus 4</div>
    <div class="benchmark-track">
        <div class="benchmark-bar" style="--width: 94%; --color: #D97706;">
            <span class="benchmark-value-inner">94.2</span>
        </div>
        <span class="benchmark-value-outer">94.2%</span>
    </div>
</div>
```

### CSS
```css
.benchmark-track {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 12px;
    height: 32px;
}

.benchmark-bar {
    height: 100%;
    width: var(--width);
    border-radius: 6px;
    background: linear-gradient(90deg,
        var(--color) 0%,
        color-mix(in srgb, var(--color), white 15%) 80%,
        color-mix(in srgb, var(--color), white 25%) 100%
    );
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 10px;
    transition: width 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.benchmark-value-inner {
    color: white;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.benchmark-value-outer {
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 500;
    min-width: 50px;
}
```

### Анимация при scroll (growBar)
```javascript
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const bars = entry.target.querySelectorAll('.benchmark-bar');
            bars.forEach((bar, i) => {
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = bar.style.getPropertyValue('--width');
                }, i * 100); // Stagger 100ms
            });
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.2 });
```

### PDF fallback
```css
@media print {
    .benchmark-bar {
        transition: none !important;
        width: var(--width) !important;
    }
}
```

## Ключевые правила
1. **Сортировка по убыванию** -- лидер сверху, отстающий снизу
2. **Число ВНУТРИ бара** (белый + text-shadow) + число СПРАВА (для узких баров)
3. **Provider-colored gradient** -- 3 точки: base 0%, lighten 15% at 80%, lighten 25% at 100%
4. **Stagger анимация** -- 100ms между барами для каскадного эффекта
5. **Моноширинный шрифт** для чисел (JetBrains Mono) -- цифры выравниваются

## Когда использовать
- AI benchmarks (MMLU, HumanEval, GPQA, etc.)
- Сравнение провайдеров / продуктов по метрикам
- Любые числовые рейтинги (1-100, проценты)

## Ограничения
- `color-mix()` не поддерживается в Safari < 16.4 -- fallback через rgb() с ручным осветлением
- При > 10 барах stagger 100ms = 1 сек ожидания -- уменьшить до 50ms
- Узкие бары (< 20%) -- число внутри не влезает, показывать только снаружи
- growBar анимация не работает в PDF -- @media print обязателен

## Связанные
- EXP-073 -- Bar chart multi-color (nth-child) -- альтернативный способ
- EXP-124 -- Neural Grid дизайн-система
- EXP-120 -- Анимации + PDF совместимость
