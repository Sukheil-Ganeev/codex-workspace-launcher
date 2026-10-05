# EXP-145: scrollLock vs TOC Interaction Bug

## Симптом
Пользователь нажимает стрелки для навигации, затем быстро открывает TOC (T) и кликает по пункту — слайд не переключается, TOC закрывается.

## Причина
```javascript
window.goToSlide = function(n) {
    if (scrollLock) return;  // ← Молча игнорирует вызов
    scrollLock = true;
    // ...navigation...
    setTimeout(function() { scrollLock = false; }, 800);
};
```
TOC onclick: `goToSlide(n); toggleTOC();` — если scrollLock=true, goToSlide молча выходит, но toggleTOC всё равно закрывает overlay.

## Решение
```javascript
window.toggleTOC = function() {
    var toc = document.querySelector('.toc-overlay');
    tocOpen = !tocOpen;
    if (tocOpen) scrollLock = false;  // ← Сброс при открытии TOC
    toc.classList.toggle('active');
};
```

## Правило
При любом модальном overlay (TOC, search, settings) — ВСЕГДА сбрасывать scrollLock при открытии. Пользователь явно хочет навигировать через overlay, lock не должен этому мешать.
