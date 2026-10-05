# Анимации + PDF совместимость -- @media print решает всё
**Источник:** EXP-120 (Neural Grid v2, AI Models Comparison 2026, 2026-02-18)

## Проблема
Анимации делают HTML-презентацию живой и интерактивной, но при конвертации в PDF через Playwright:
- @keyframes анимации "замораживаются" в случайном кадре
- CSS transition на .slide ломает PDF-рендеринг
- IntersectionObserver не срабатывает в headless-браузере

## Решение

### 1. Определить @keyframes для браузера
```css
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

@keyframes pulseDot {
    0%, 100% { opacity: 0.4; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.2); }
}
```

### 2. IntersectionObserver для scroll-triggered
```javascript
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.animate-on-scroll').forEach(el => {
    observer.observe(el);
});
```

### 3. @media print -- КЛЮЧ
```css
@media print {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
        animation-delay: 0s !important;
        animation-duration: 0s !important;
    }

    .animate-on-scroll {
        opacity: 1 !important;
        transform: none !important;
    }

    /* Gradient text fallback */
    .gradient-text {
        -webkit-text-fill-color: #F9FAFB !important;
        background: none !important;
    }
}
```

### 4. Gradient text для hero заголовков
```css
.hero-title {
    background: linear-gradient(135deg, #F9FAFB 0%, #3B82F6 50%, #10B981 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 8s linear infinite;
}
```

## Когда использовать
- Любая HTML-презентация, которая конвертируется в PDF
- Когда нужны эффекты в браузере, но чистый статичный PDF
- fadeSlideUp для карточек, shimmer для заголовков, pulseDot для индикаторов
- growBar анимация для benchmark-баров (IntersectionObserver + width transition)

## Ограничения
- НЕ использовать CSS transition на .slide -- ломает PDF рендеринг
- Только @keyframes (не transition) для декоративных анимаций
- IntersectionObserver НЕ работает в headless Playwright -- всё видимо через @media print fallback
- Shimmer длительность 8-10s (не 4s -- мельтешит, EXP-103)
- Gradient text + shimmer: background-size: 200% обязателен

## Связанные
- EXP-066 -- Анимации: PDF vs HTML (базовые правила)
- EXP-023 -- Деанимация HTML для PDF
- EXP-103 -- Профессиональные анимации: принципы плавности
- EXP-121 -- Gradient text для hero (детали)
