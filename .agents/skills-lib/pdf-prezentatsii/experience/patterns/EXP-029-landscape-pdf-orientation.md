---
id: EXP-029
date: 2026-02-05
type: pattern
severity: critical
category: conversion
projects: []
related: [EXP-002, EXP-031]
tags: [landscape, orientation, pdf, viewport, playwright]
status: verified
---

# Landscape PDF ориентация для горизонтальных презентаций

**ID:** EXP-029
**Дата:** 2026-02-05
**Контекст:** MCP Presentation — PDF создавался вертикальным вместо горизонтального

---

## Проблема

PDF презентации создаётся в формате A4 (portrait), хотя исходный HTML имеет горизонтальную ориентацию 1920x1080.

**Визуальные симптомы:**
- Контент обрезается по бокам
- Презентация выглядит "сжатой"
- Много пустого пространства сверху и снизу
- Пропорции элементов нарушены

**Исходная ошибка:**
```python
# НЕПРАВИЛЬНО — создаёт вертикальный PDF
page.pdf(
    path='presentation.pdf',
    format='A4',
    print_background=True
)
```

---

## Решение

Явно указать размеры в пикселях **БЕЗ `landscape=True`**:

```python
page.pdf(
    path='presentation.pdf',
    width='1920px',   # Ширина > высота = автоматически landscape
    height='1080px',  #
    print_background=True,
    margin={
        'top': '0',
        'right': '0',
        'bottom': '0',
        'left': '0'
    }
)
```

⚠️ **КРИТИЧНО:** НЕ используйте `landscape=True` вместе с явными размерами!
Playwright интерпретирует это неправильно и создаёт portrait PDF.
```

---

## Критические детали

### 1. Почему `landscape=True` недостаточно без размеров?

```python
# НЕ РАБОТАЕТ как ожидается
page.pdf(landscape=True)  # Просто переворачивает A4

# РАБОТАЕТ
page.pdf(width='1920px', height='1080px', landscape=True)
```

`landscape=True` без явных размеров просто меняет ориентацию стандартного A4 (297x210mm), но не меняет его размер.

### 2. Размеры должны соответствовать viewport HTML

```python
# Установить viewport браузера
page.set_viewport_size({'width': 1920, 'height': 1080})

# PDF должен соответствовать
page.pdf(width='1920px', height='1080px', ...)
```

### 3. Нулевые margins важны

```python
margin={
    'top': '0',
    'right': '0',
    'bottom': '0',
    'left': '0'
}
```

Если не указать нулевые margins, Playwright добавит стандартные отступы (~10mm), что сдвинет контент.

---

## Полный рабочий код

```python
from playwright.sync_api import sync_playwright

def html_to_landscape_pdf(html_path: str, pdf_path: str, width=1920, height=1080):
    """Конвертирует HTML в landscape PDF с правильными размерами."""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Viewport соответствует размерам презентации
        page.set_viewport_size({'width': width, 'height': height})

        # Загрузить HTML
        page.goto(f'file:///{html_path}')
        page.wait_for_load_state('networkidle')

        # PDF с правильной ориентацией
        page.pdf(
            path=pdf_path,
            width=f'{width}px',
            height=f'{height}px',
            landscape=True,
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )

        browser.close()

# Использование
html_to_landscape_pdf('presentation.html', 'presentation.pdf')
```

---

## Диагностика

**Если PDF выглядит неправильно, проверьте:**

1. Размеры viewport в браузере == размеры PDF?
2. `landscape=True` указан?
3. Margins нулевые?
4. HTML ширина фиксирована (`width: 1920px`) или резиновая?

**Быстрая проверка:**
```python
# В Playwright DevTools
print(f"Viewport: {page.viewport_size}")
# Должно быть {'width': 1920, 'height': 1080}
```

---

## Когда применять

- Wide-screen презентации (16:9, 1920x1080)
- Лендинги с горизонтальной прокруткой
- Инфографика в горизонтальном формате
- Dashboards и отчёты

---

## Связанные паттерны

- `deanimate-html.md` — деанимация перед конвертацией
- `interactive-elements-coverage.md` — покрытие интерактивных элементов
