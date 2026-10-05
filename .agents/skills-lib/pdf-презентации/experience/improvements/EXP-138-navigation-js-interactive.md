# EXP-138: Navigation JS для интерактивного просмотра

> Дата: 2026-02-20
> Проект: Telegram Business + Connected Bot v2.0
> Категория: improvement

## Проблема

HTML-презентация без навигации — просто длинная страница. Нужен полноценный набор навигационных инструментов для комфортного просмотра.

## Решение: Комплексный навигационный JS

### 1. Arrow key navigation + scrollLock

```javascript
let scrollLock = false;
let currentSlide = 0;

document.addEventListener('keydown', (e) => {
    if (scrollLock) return;

    if (e.code === 'ArrowRight' || e.code === 'ArrowDown') {
        e.preventDefault();
        navigateTo(currentSlide + 1);
    }
    if (e.code === 'ArrowLeft' || e.code === 'ArrowUp') {
        e.preventDefault();
        navigateTo(currentSlide - 1);
    }
});

function navigateTo(index) {
    const slides = document.querySelectorAll('.slide');
    if (index < 0 || index >= slides.length) return;

    scrollLock = true;
    currentSlide = index;
    slides[index].scrollIntoView({ behavior: 'smooth' });
    updateUI();

    setTimeout(() => { scrollLock = false; }, 800);  // EXP-062: 800ms предотвращает bounce
}
```

### 2. Fullscreen toggle (клавиша F)

```javascript
if (e.code === 'KeyF') {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}
```

### 3. TOC overlay toggle (клавиша T)

```javascript
if (e.code === 'KeyT') {
    toggleTOC();
}
if (e.code === 'Escape') {
    closeTOC();
}
```

### 4. Progress bar

```css
.progress-bar {
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
    z-index: 9999;
    transition: width 0.3s ease;
}
```

```javascript
function updateUI() {
    const total = document.querySelectorAll('.slide').length;
    const progress = ((currentSlide + 1) / total) * 100;
    progressBar.style.width = progress + '%';
    slideCounter.textContent = `${currentSlide + 1} / ${total}`;
}
```

### 5. Slide counter

```css
.slide-counter {
    position: fixed;
    bottom: 24px;
    left: 24px;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.4);
    z-index: 9999;
    font-family: monospace;
}
```

### 6. IntersectionObserver scroll spy

```javascript
const observer = new IntersectionObserver((entries) => {
    if (scrollLock) return;
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            currentSlide = [...slides].indexOf(entry.target);
            updateUI();
        }
    });
}, { threshold: 0.5 });

slides.forEach(slide => observer.observe(slide));
```

### 7. Скрытие навигации в PDF

```css
@media print {
    .progress-bar,
    .slide-counter,
    .toc-overlay,
    .nav-arrows {
        display: none !important;
    }
}
```

## Важные правила

1. **scrollLock 800ms** — предотвращает bounce между слайдами (EXP-062, подтверждено повторно)
2. **zoom вместо transform:scale** — не ломает position:fixed элементы навигации (EXP-094, EXP-125)
3. **e.code** (не e.key) — для клавиш, работает на любой раскладке
4. **threshold: 0.5** — IntersectionObserver срабатывает когда слайд виден на 50%+
5. **ВСЕ fixed-элементы** скрывать в @media print { display: none !important }
6. **z-index: 9999** — progress bar и counter поверх всего контента

## Полный набор горячих клавиш

| Клавиша | Действие |
|---------|----------|
| `<-` `->` `Up` `Down` | Навигация по слайдам |
| `F` | Fullscreen toggle |
| `T` | Table of Contents toggle |
| `Esc` | Закрыть TOC / выйти из fullscreen |
| `Home` | Первый слайд |
| `End` | Последний слайд |

## Связанные записи

- EXP-062 -- scrollLock 800ms
- EXP-094 -- transform:scale ломает fixed
- EXP-113 -- Slideshow mode для статических HTML
- EXP-114 -- Keyboard shortcuts стандарт
- EXP-125 -- zoom вместо scale, e.code для клавиш
- EXP-134 -- Premium TOC overlay
