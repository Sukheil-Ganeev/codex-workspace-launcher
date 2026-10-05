---
id: EXP-006
date: 2026-02-11
type: fix
severity: critical
category: layout
projects: []
related: [EXP-034]
tags: [viewport, scaling, transform, desktop, 1920px]
status: verified
---

# EXP-006: Viewport Scaling для десктопных браузеров

**Дата:** 2026-02-11
**Проблема:** Контент обрезается справа при просмотре HTML-презентации (1920px) на экранах уже 1920px
**Серьёзность:** Критическая — пользователь видит обрезанную презентацию

## Корневая причина

`<meta name="viewport" content="width=1920">` **ИГНОРИРУЕТСЯ десктопными браузерами** (Chrome, Edge, Firefox). Viewport meta тег работает только на мобильных устройствах.

Слайды с `width: 1920px` на ноутбуке (1366-1536px viewport) просто выходят за правый край окна. Это НЕ overflow контента внутри слайдов — это проблема масштабирования.

## Что НЕ помогает
- `overflow: hidden` на карточках/таблицах — контент внутри уже правильный
- `box-sizing: border-box` — уже стоит, не в этом дело
- `max-width: 100%` на контейнерах — проблема не в контенте
- `table-layout: fixed` — таблицы не виноваты

## Решение: JavaScript transform: scale()

```javascript
function scaleSlides() {
    var screenWidth = window.innerWidth;
    var slides = document.querySelectorAll('.slide');
    var totalHeight = slides.length * 1080;
    if (screenWidth < 1920) {
        var scale = screenWidth / 1920;
        document.body.style.transformOrigin = 'top left';
        document.body.style.transform = 'scale(' + scale + ')';
        document.body.style.width = '1920px';
        // КРИТИЧНО: ограничить высоту прокрутки
        document.body.style.height = totalHeight + 'px';
        document.documentElement.style.height = (totalHeight * scale) + 'px';
        document.documentElement.style.overflowX = 'hidden';
    } else {
        document.body.style.transform = 'none';
        document.body.style.width = '';
        document.body.style.height = '';
        document.documentElement.style.height = '';
        document.documentElement.style.overflowX = '';
    }
}
scaleSlides();
window.addEventListener('resize', scaleSlides);
```

## Вторая ошибка: пустой фон после последнего слайда

`transform: scale()` уменьшает визуальный размер body, но scrollable area остаётся оригинальной (N×1080px). Пользователь может прокрутить далеко за последний слайд в пустой фон.

**Фикс:** Принудительно ставить `html.height = totalHeight × scale` — это ограничивает прокрутку ровно до конца последнего слайда.

## Когда применять

Добавлять в КАЖДУЮ HTML-презентацию с интерактивным просмотром (F + стрелки). Не нужно для PDF — Playwright рендерит при viewport 1920px.

## Связано с
- EXP-062: scrollLock 800ms для scroll-snap
- Навигация: F=fullscreen, стрелки=переключение слайдов, IntersectionObserver
