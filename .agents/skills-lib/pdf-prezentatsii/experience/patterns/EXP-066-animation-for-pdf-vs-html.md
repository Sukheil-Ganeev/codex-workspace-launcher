---
id: EXP-066
date: 2026-02-11
type: pattern
severity: high
category: animation
projects: [Skill_Presentations, Калькулятор-Документация]
related: [EXP-010, EXP-063, EXP-019]
tags: [анимации, transition, keyframes, деанимация, pdf, html]
status: verified
---

## Контекст

CSS анимации и transitions -- одна из основных причин артефактов при генерации PDF. Элементы "застревают" в промежуточных состояниях, hover-эффекты не работают. При этом для HTML-варианта презентации анимации существенно улучшают восприятие. Этот паттерн описывает, как управлять анимациями в обоих форматах.

## Описание

### Что НЕ работает в PDF

| CSS-свойство | Поведение в PDF | Замена |
|-------------|-----------------|--------|
| `animation` / `@keyframes` | Элемент застывает в случайном кадре | Статичное конечное состояние |
| `transition` | Не применяется | Убрать, оставить конечный стиль |
| `:hover` | Нет интерактивности | Убрать или оставить как fallback |
| `:focus` | Нет интерактивности | Убрать |
| `transform` (анимированный) | Застывает | Статичный transform OK |
| `opacity` (анимированный) | Случайное значение | Фиксированный opacity |
| `will-change` | Может вызывать артефакты | Убрать |

### Что РАБОТАЕТ в PDF

| CSS-свойство | Результат |
|-------------|-----------|
| Статичный `transform: rotate(45deg)` | Работает корректно |
| Статичный `opacity: 0.5` | Работает корректно |
| `filter: blur(120px)` | Работает (ambient glow!) |
| `linear-gradient` | Работает (но раздувает размер, EXP-038) |
| `radial-gradient` | Работает (но раздувает ещё сильнее, EXP-043) |
| `box-shadow` | Работает (но "грязь" на тёмных темах, EXP-033) |
| CSS `clip-path` | Работает |
| SVG inline | Работает |
| `-webkit-mask` / `mask-composite` | Работает (gradient borders, EXP-031) |
| `-webkit-background-clip: text` | Работает (gradient text) |

### Деанимация HTML перед генерацией PDF (EXP-010)

**Обязательный шаг** при конвертации HTML с анимациями:

```javascript
// Внутри Playwright перед page.pdf()
await page.evaluate(() => {
    const style = document.createElement('style');
    style.textContent = `
        *, *::before, *::after {
            animation: none !important;
            animation-delay: 0s !important;
            animation-duration: 0s !important;
            transition: none !important;
            transition-delay: 0s !important;
            transition-duration: 0s !important;
        }
    `;
    document.head.appendChild(style);
});
await page.waitForTimeout(100);  // Дать время применить стили
```

### Паттерн: "Двойной CSS" для HTML + PDF

Если нужны оба формата из одного HTML, используйте медиа-запрос `@media print`:

```css
/* Анимации для HTML-просмотра */
.card {
    animation: fadeInUp 0.5s ease forwards;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Отключить для PDF/печати */
@media print {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
    .card {
        opacity: 1 !important;
        transform: none !important;
    }
    .card:hover {
        transform: none;
        box-shadow: none;
    }
}
```

### Интерактивные элементы в HTML (не переносятся в PDF)

Для HTML-версии можно использовать:

```css
/* Табы */
.tab-btn.active { border-bottom: 3px solid var(--accent-1); }
.tab-content { display: none; }
.tab-content.active { display: block; }

/* Аккордеоны */
.accordion-content { max-height: 0; overflow: hidden; transition: max-height 0.3s ease; }
.accordion.open .accordion-content { max-height: 500px; }

/* Tooltip на hover */
.tooltip-trigger:hover .tooltip { opacity: 1; visibility: visible; }
```

**Для PDF:** Все табы/аккордеоны нужно "раскрыть" программно перед конвертацией (EXP-013 -- клик по интерактивным элементам) или показать все состояния одновременно.

### "Замораживание" конкретных анимаций

Иногда нужно оставить элемент в определённом кадре анимации:

```javascript
// Установить animation на конечное состояние
await page.evaluate(() => {
    document.querySelectorAll('.animated-element').forEach(el => {
        const computed = getComputedStyle(el);
        // Скопировать конечные стили
        el.style.opacity = '1';
        el.style.transform = 'translateY(0)';
        el.style.animation = 'none';
    });
});
```

### Рекомендация для серии справочников

В серии из 23 справочников НЕ используются анимации вообще -- zero-dependency подход (EXP-019). Все визуальные эффекты статичные:
- `filter: blur(120-160px)` на `.bg-glow` div'ах -- ambient свечение
- Gradient text через `-webkit-background-clip: text`
- `mask-composite` для gradient borders
- SVG inline для декораций

Это обеспечивает:
- Одинаковый вид HTML и PDF
- 0 артефактов при конвертации
- Быстрая конвертация (~3-15 сек)

## Когда применять

- При создании HTML, который будет конвертирован в PDF -- не добавлять анимации изначально
- При конвертации существующего HTML с анимациями -- обязательная деанимация
- При запросе "HTML + PDF из одного файла" -- паттерн "@media print"
- При интерактивных элементах (табы, фильтры) -- программный клик по всем состояниям перед PDF

## Связанные уроки

- **EXP-010** -- Деанимация HTML для PDF рендеринга
- **EXP-013** -- Клик по интерактивным элементам для полного покрытия
- **EXP-019** -- Zero-dependency презентация
- **EXP-063** -- HTML vs PDF tradeoffs
