# EXP-148: Минимальный паттерн навигации (стрелки + F)

**Дата:** 2026-03-04
**Проект:** GPU Buyer's Guide Dubai 2026 (15 слайдов)
**Категория:** improvement

## Проблема

EXP-138 описывает ПОЛНУЮ навигацию: стрелки + T=TOC + progress bar + slide counter + IntersectionObserver. Это ~120 строк JS. Для небольших презентаций без TOC — избыточно.

## Решение: Минимальный вариант (~55 строк)

```javascript
// ← → переключение слайдов + F = fullscreen
// Добавить HTML-подсказку (отображается поверх слайдов):
// <div id="nav-hint">◀ ▶ навигация · F — полный экран</div>

window.addEventListener('DOMContentLoaded', function() {
    var slides = document.querySelectorAll('.slide');
    var total = slides.length;
    var current = 0;
    var scrollLock = false;

    // Scale (zoom не ломает position:fixed — EXP-125)
    function scalePresentation() {
        document.body.style.zoom = window.innerWidth / 1920;
    }
    scalePresentation();
    window.addEventListener('resize', scalePresentation);

    function goTo(index) {
        if (index < 0 || index >= total || scrollLock) return;
        scrollLock = true;
        current = index;
        slides[current].scrollIntoView({ behavior: 'smooth', block: 'start' });
        setTimeout(function() { scrollLock = false; }, 800); // EXP-062
    }

    document.addEventListener('keydown', function(e) {
        if (e.code === 'ArrowRight' || e.code === 'ArrowDown') {
            e.preventDefault(); goTo(current + 1);
        } else if (e.code === 'ArrowLeft' || e.code === 'ArrowUp') {
            e.preventDefault(); goTo(current - 1);
        } else if (e.code === 'KeyF') {
            !document.fullscreenElement
                ? document.documentElement.requestFullscreen()
                : document.exitFullscreen();
        }
    });

    // Отслеживание текущего слайда при ручном скролле
    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting && !scrollLock)
                current = Array.from(slides).indexOf(entry.target);
        });
    }, { threshold: 0.5 });

    slides.forEach(function(slide) { observer.observe(slide); });
});
```

## Nav-hint UI

```html
<div id="nav-hint" style="position:fixed;bottom:24px;left:50%;
  transform:translateX(-50%);display:flex;gap:14px;align-items:center;
  z-index:9999;background:rgba(2,9,23,0.85);padding:9px 24px;
  border-radius:30px;border:1px solid rgba(255,255,255,0.10);
  font-size:13px;color:#94A3B8;pointer-events:none;white-space:nowrap;">
    <span style="color:#22D3EE;font-size:15px;">◀ ▶</span> навигация &nbsp;·&nbsp;
    <span style="color:#76B900;font-weight:700;">F</span> — полный экран
</div>
```

```css
/* Nav-hint не попадает в PDF */
@media print {
    #nav-hint { display: none !important; }
}
```

## Когда использовать минимальный vs полный (EXP-138)

| Критерий | Минимальный (EXP-148) | Полный (EXP-138) |
|---------|----------------------|-----------------|
| Слайдов | < 20 | Любое |
| TOC нужен | Нет | Да |
| Progress bar | Нет | Да |
| Slide counter | Только в HTML (статично) | Динамически |
| Строк JS | ~55 | ~120 |

## Правило

- **≤20 слайдов, без TOC** → EXP-148 (минимальный)
- **>20 слайдов ИЛИ нужен TOC** → EXP-138 (полный)
- **position:fixed nav-hint** — работает с `zoom` (не с `transform:scale`). EXP-125.
