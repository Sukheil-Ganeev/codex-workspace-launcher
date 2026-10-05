# EXP-144: Enhanced Glassmorphism Values for PDF

## Контекст
Базовые значения glassmorphism (rgba 0.04 bg, 0.08 border) были слишком тонкие — стеклянный эффект почти невидим.

## Оптимальные значения

### Base .glass-card
| Свойство | Было | Стало |
|----------|------|-------|
| background | rgba(255,255,255, **0.04**) | rgba(255,255,255, **0.06**) |
| border | rgba(255,255,255, **0.08**) | rgba(255,255,255, **0.10**) |
| border-top | — | rgba(255,255,255, **0.15**) NEW |
| inset shadow | rgba(255,255,255, **0.06**) | rgba(255,255,255, **0.08**) |

### Brand variants (.nvidia, .amd, .intel, .warn)
| Свойство | Было | Стало |
|----------|------|-------|
| background | rgba(COLOR, **0.04**) | rgba(COLOR, **0.06**) |
| border | rgba(COLOR, **0.12**) | rgba(COLOR, **0.15**) |
| border-top | — | rgba(COLOR, **0.25**) NEW |

### Section-slide glass panel
```css
.section-slide::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 700px; height: 300px;
    background: rgba(255,255,255, 0.03);
    border: 1px solid rgba(255,255,255, 0.06);
    border-top: 1px solid rgba(255,255,255, 0.10);
    border-radius: 32px;
    box-shadow: inset 0 1px 0 rgba(255,255,255, 0.06);
    z-index: 1;
}
```

### Стеклянные таблицы
```css
.styled-table {
    background: rgba(255,255,255, 0.02);  /* НЕ rgba(0,0,0, 0.15) */
    box-shadow: inset 0 1px 0 rgba(255,255,255, 0.04);
}
.styled-table thead th {
    box-shadow: inset 0 1px 0 rgba(255,255,255, 0.08);
}
```

## Ключевой приём
**border-top ярче остальных borders** — имитирует блик света на верхней грани стекла. Это основной визуальный сигнал glassmorphism без backdrop-filter.

## PDF Impact
Размер PDF НЕ увеличился (10.1 MB) — solid rgba + border + box-shadow inset минимальны по весу.

## Декоративные micro-details (PDF-safe)

### Dot-pattern
```css
.dot-pattern {
    position: absolute;
    width: 120px; height: 120px;
    background-image: radial-gradient(rgba(255,255,255,0.12) 1px, transparent 1px);
    background-size: 12px 12px;
    opacity: 0.5;
    z-index: 1;
}
```
Размещать на 3-4 слайдах (не на всех). 120x120 = 100 точек — минимальный PDF impact.

### Glass-separator
```css
.glass-separator {
    width: 100%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.10), transparent);
    margin: 16px 0;
}
```
Использовать между логическими секциями внутри слайда.
