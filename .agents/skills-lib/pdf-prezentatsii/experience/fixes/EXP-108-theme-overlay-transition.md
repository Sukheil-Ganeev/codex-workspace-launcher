# EXP-108: Overlay Fade техника для переключения тем

> Дата: 2026-02-14 | Категория: pattern | Проект: Taplink-презентация

## Проблема

CSS `transition: background-color 0.3s, color 0.3s` на всех элементах (`*`) создаёт "лоскутный" эффект при переключении темы:
- Разные элементы переключаются с разной скоростью
- Фон меняется раньше текста
- Карточки мерцают
- Таблицы "мигают"
- Общее ощущение -- дешёвый, непрофессиональный переход

```css
/* ❌ ПЛОХО -- лоскутный эффект */
* {
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}
```

## Решение: Overlay Fade

Полноэкранный div перекрывает страницу, затемняется, тема переключается мгновенно за overlay, overlay исчезает.

### HTML

```html
<!-- Добавить перед </body> -->
<div id="theme-overlay"></div>
```

### CSS

```css
#theme-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 99999;
    pointer-events: none;
    opacity: 0;
    transition: opacity 150ms ease;
}

#theme-overlay.active {
    opacity: 1;
}
```

### JavaScript -- полный код

```javascript
// === ИНИЦИАЛИЗАЦИЯ ТЕМЫ ===

function initTheme() {
    // Читаем сохранённую тему, по умолчанию light
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // Обновить иконку кнопки
    updateThemeIcon(savedTheme);
}

// Вызвать ДО DOMContentLoaded для предотвращения flash
initTheme();

// === ПЕРЕКЛЮЧЕНИЕ ТЕМЫ ===

function toggleTheme() {
    const html = document.documentElement;
    const overlay = document.getElementById('theme-overlay');
    const currentTheme = html.getAttribute('data-theme') || 'light';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';

    // 1. Установить цвет overlay = цвет НОВОЙ темы
    overlay.style.background = nextTheme === 'dark' ? '#1A1A2E' : '#FFFFFF';

    // 2. Fade in overlay (150ms)
    overlay.classList.add('active');

    // 3. Через 150ms (overlay полностью видим) -- переключить тему мгновенно
    setTimeout(() => {
        html.setAttribute('data-theme', nextTheme);
        localStorage.setItem('theme', nextTheme);
        updateThemeIcon(nextTheme);

        // 4. Через 30ms (дать браузеру отрисовать) -- fade out overlay (150ms)
        setTimeout(() => {
            overlay.classList.remove('active');
        }, 30);
    }, 150);
}

// === ОБНОВЛЕНИЕ ИКОНКИ ===

function updateThemeIcon(theme) {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;

    if (theme === 'dark') {
        // Солнце (для переключения на light)
        btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
        btn.title = 'Светлая тема (D)';
    } else {
        // Луна (для переключения на dark)
        btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
        btn.title = 'Тёмная тема (D)';
    }
}

// === ГОРЯЧАЯ КЛАВИША ===

document.addEventListener('keydown', (e) => {
    // Не перехватывать если фокус в input/textarea
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.key === 'd' || e.key === 'D' || e.key === 'в' || e.key === 'В') {
        toggleTheme();
    }
});
```

## Тайминги

| Фаза | Длительность | Описание |
|------|-------------|----------|
| Fade in | 150ms | Overlay появляется поверх страницы |
| Переключение | 0ms | `data-theme` меняется мгновенно за overlay |
| Отрисовка | 30ms | Браузер перерисовывает DOM |
| Fade out | 150ms | Overlay исчезает, показывая новую тему |
| **Итого** | **~330ms** | Чистый crossfade без артефактов |

## Критические правила

1. **НИКОГДА** не ставить `transition` на `*` для background/color при наличии dark mode
2. **overlay z-index: 99999** -- должен быть выше ВСЕХ элементов (навигации, модалок, тултипов)
3. **pointer-events: none** -- overlay не должен перехватывать клики
4. **initTheme() вызывать синхронно** в `<script>` в `<head>` или в начале `<body>` -- до рендеринга, чтобы не было flash of wrong theme
5. **localStorage** для сохранения выбора пользователя между сессиями
6. **Цвет overlay = цвет НОВОЙ темы** -- создаёт иллюзию плавного перехода в новый цвет

## Варианты overlay цветов по темам

| Переход | Overlay background |
|---------|-------------------|
| light -> dark | `#1A1A2E` (основной тёмный) |
| dark -> light | `#FFFFFF` (или #F8FAFC если warm) |
| light -> sepia | `#F5F0E8` |
| sepia -> dark | `#1A1A2E` |

## Связанные записи

- EXP-107: Dark Mode контраст (что должно измениться при переключении)
- EXP-042: CSS-переменные в multi-theme
- EXP-103: Профессиональные анимации (тайминги)
