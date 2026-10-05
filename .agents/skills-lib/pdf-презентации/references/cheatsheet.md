# Шпаргалка PDF-презентаций

## Рабочий процесс

| Шаг | Действие | Скилл |
|-----|----------|-------|
| 1 | Планирование (если сложная) | `EnterPlanMode` |
| 2 | Создание HTML | `frontend-design` |
| 3 | Технические правила | `pdf-презентации` |
| 4 | Конвертация | Playwright |

---

## Размеры

| Формат | Пиксели | Playwright |
|--------|---------|------------|
| 16:9 HD | 1920x1080 | `width='1920px', height='1080px'` |
| 16:9 4K | 3840x2160 | `width='3840px', height='2160px'` |
| 4:3 | 1440x1080 | `width='1440px', height='1080px'` |
| A4 Landscape | 297mm × 210mm | `format='A4', landscape=True` |
| A4 Portrait | 210mm × 297mm | `format='A4', landscape=False` |

---

## CSS для слайдов (копируй)

```css
/* ⚠️ body БЕЗ height и overflow — иначе только 1 слайд виден! */
html, body {
    width: 1920px;
    margin: 0;
    padding: 0;
    /* НЕ указывать height и overflow: hidden! */
}

.slide {
    width: 1920px;
    height: 1080px;
    page-break-after: always;
    page-break-inside: avoid;
    overflow: hidden;
    box-sizing: border-box;
}

.slide:last-child {
    page-break-after: auto;
}
```

---

## Playwright (копируй)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('file:///D:/Downloads/presentation.html')
    page.wait_for_load_state('networkidle')
    page.pdf(
        path='D:/Downloads/presentation.pdf',
        width='1920px',
        height='1080px',
        print_background=True,
        margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
    )
    browser.close()
```

---

## Чек-лист

- [ ] body размеры = PDF размеры
- [ ] print_background: True
- [ ] margin: 0
- [ ] wait_for_load_state('networkidle')
- [ ] page-break-after: always
- [ ] Нет animation/transition/@keyframes

---

## Установка

```bash
pip install playwright
playwright install chromium
```

---

## Команда CLI

```bash
python scripts/convert-to-pdf.py input.html output.pdf --format 16:9
```

Форматы: `16:9`, `16:9-4k`, `4:3`, `a4`, `a4-portrait`

---

## ЗАПРЕЩЕНО

```css
/* ❌ Удалить перед конвертацией */
animation: ...;
transition: ...;
@keyframes { ... }
:hover { ... }
position: fixed;
/* Не использовать vh, vw — только px */
```

---

## Google Fonts

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
```

---

## Быстрый старт HTML

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        /* ⚠️ body БЕЗ height! */
        html, body {
            width: 1920px;
            margin: 0;
            padding: 0;
        }
        .slide {
            width: 1920px;
            height: 1080px;
            page-break-after: always;
            page-break-inside: avoid;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .slide:last-child { page-break-after: auto; }
    </style>
</head>
<body>
    <div class="slide">Слайд 1</div>
    <div class="slide">Слайд 2</div>
</body>
</html>
```
