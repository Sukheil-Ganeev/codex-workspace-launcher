---
id: EXP-063
date: 2026-02-11
type: pattern
severity: high
category: workflow
projects: [Skill_Presentations, Калькулятор-Документация]
related: [EXP-010, EXP-012, EXP-015, EXP-019]
tags: [html, pdf, конвертация, playwright, ограничения]
status: verified
---

## Контекст

За 23 справочника и 3 бизнес-презентации выработано понимание, когда оставлять HTML как финальный формат, а когда конвертировать в PDF. Каждый формат имеет свои сильные стороны и ограничения, и выбор формата определяет дизайн-решения с самого начала.

## Описание

### Сравнительная таблица HTML vs PDF

| Критерий | HTML | PDF |
|----------|------|-----|
| Интерактивность | Табы, аккордеоны, hover, клик | Только кликабельные ссылки (EXP-018) |
| Анимации | @keyframes, transition, transform | НЕ работают (статичный формат) |
| Шрифты | Google Fonts, CDN | Нужно встраивать base64 или системные |
| Размер файла | ~500 KB HTML + ресурсы | 3-10 MB (зависит от визуальных эффектов) |
| Распространение | Нужен веб-сервер или локальный файл | Универсальный, открывается везде |
| Печать | Непредсказуемо | Гарантированная верстка |
| Кросс-платформенность | Зависит от браузера | Одинаково на всех устройствах* |
| Редактирование | Легко -- текстовый редактор | Только через пересоздание из HTML |
| Навигация | Скролл, якоря, табы | Страницы, закладки |
| backdrop-filter | Работает в Chrome | Артефакты в Chrome PDF, белые квадраты в Apple Preview |
| conic-gradient | Работает | Серый круг в Apple Preview |
| filter: blur() | Работает | Работает (в отличие от backdrop-filter!) |
| vh/vw единицы | Работает | Непредсказуемо -- использовать px |
| position: fixed | Работает | Ломает page-break |

*Примечание: Apple Preview рендерит PDF иначе чем Chrome (EXP, SKILL.md Раздел 6)

### Конвертация HTML в PDF через Playwright

**Основной метод -- page.pdf():**

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f'file:///{html_path}')
    page.wait_for_load_state('networkidle')

    page.pdf(
        path='output.pdf',
        width='1920px',
        height='1080px',
        print_background=True,
        margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
    )
    browser.close()
```

**Альтернативный метод -- PDF из PNG скриншотов (EXP-015):**

Когда page.pdf() режет контент по границам страницы, используется метод через скриншоты:

```python
from PIL import Image

# Скриншот каждой секции -> объединение в PDF
images = [Image.open(f'slide_{i}.png').convert('RGB') for i in range(n)]
images[0].save('output.pdf', save_all=True, append_images=images[1:], resolution=96.0)
```

### Что нужно удалить/изменить перед конвертацией в PDF

```css
/* УДАЛИТЬ: */
animation: fadeIn 0.5s ease;       /* Не работает */
transition: all 0.3s ease;         /* Не работает */
@keyframes fadeIn { ... }          /* Не работает */
.button:hover { ... }              /* Нет интерактивности */
position: fixed;                   /* Ломает page-break */

/* ЗАМЕНИТЬ: */
height: 100vh;  -->  height: 1080px;   /* px вместо vh */
width: 100vw;   -->  width: 1920px;    /* px вместо vw */

/* ДОБАВИТЬ: */
.slide {
    page-break-after: always;
    page-break-inside: avoid;
}
```

### Деанимация HTML для PDF (EXP-010)

```javascript
await page.evaluate(() => {
    const style = document.createElement('style');
    style.textContent = `
        *, *::before, *::after {
            animation: none !important;
            transition: none !important;
        }
    `;
    document.head.appendChild(style);
});
await page.waitForTimeout(100);
```

### Zero-dependency подход (рекомендуемый)

Для максимальной надёжности конвертации -- 0 сетевых запросов:

| Вместо | Использовать |
|--------|-------------|
| Google Fonts | Системные: `'Segoe UI', 'Inter', Arial, sans-serif` |
| Font Awesome / CDN-иконки | Inline SVG (5-10 строк) |
| Фоновые изображения через URL | CSS gradients + `filter: blur()` |
| JS-библиотеки графиков | CSS-only (flexbox + width%) |

Результат: 0 проблем с загрузкой, конвертация ~3-15 сек, PDF 3-10 MB.

### Универсальный конвертер

**Путь:** `D:/Downloads/Skill_Presentations/_shared/convert_to_pdf.py`

Принимает путь к папке, ищет `presentation.html`, конвертирует с правильными параметрами (1920x1080, print_background, zero margins).

## Когда применять

- **Выбрать PDF** если: нужна рассылка, печать, единообразный вид на всех устройствах, отсутствие зависимости от интернета
- **Оставить HTML** если: нужна интерактивность (табы, фильтры, анимации), контент будет на веб-сервере, нужен минимальный размер файла
- **Оба формата** если: HTML для демо/просмотра, PDF для скачивания/рассылки

## Связанные уроки

- **EXP-010** -- Деанимация HTML для PDF рендеринга
- **EXP-012** -- Landscape PDF, НЕ использовать `landscape=True` с явными размерами
- **EXP-015** -- PDF из PNG скриншотов вместо page.pdf()
- **EXP-019** -- Zero-dependency презентация
