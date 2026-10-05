---
id: EXP-031
date: 2026-02-05
type: pattern
severity: high
category: conversion
projects: []
related: [EXP-028, EXP-029]
tags: [pdf, png, screenshots, pillow, page-break]
status: verified
---

# PDF из PNG скриншотов (без обрезки)

**ID:** EXP-031
**Дата:** 2026-02-05
**Контекст:** MCP Presentation — блоки выходили на другие страницы и обрезались

---

## Проблема

При использовании `page.pdf()` напрямую, Playwright:
1. Рендерит всю HTML страницу как один длинный документ
2. Режет его на страницы по высоте (1080px)
3. Контент, который пересекает границу страницы, **обрезается**

**Визуальные симптомы:**
- Карточки/блоки "разрезаны" между страницами
- Начало секции на одной странице, конец на другой
- Часть контента пропадает

**Исходная ошибка:**
```python
# ❌ НЕПРАВИЛЬНО — контент обрезается
page.pdf(
    path='presentation.pdf',
    width='1920px',
    height='1080px',
    print_background=True
)
```

---

## Решение

Создавать PDF из PNG скриншотов viewport через Pillow:

```python
from playwright.sync_api import sync_playwright
from PIL import Image

def html_to_pdf_via_screenshots(html_path, pdf_path, sections):
    """
    Создаёт PDF из скриншотов каждой секции.
    Каждый скриншот = отдельная страница PDF.
    """
    png_files = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto(f'file:///{html_path}')
        page.wait_for_load_state('networkidle')

        for i, section_id in enumerate(sections):
            # Скролл к секции
            page.evaluate(f'''() => {{
                document.getElementById('{section_id}')
                    .scrollIntoView({{behavior: 'auto', block: 'start'}});
            }}''')

            # Скриншот VIEWPORT (не секции!)
            png_path = f'slide_{i+1}.png'
            page.screenshot(path=png_path)  # Весь viewport!
            png_files.append(png_path)

        browser.close()

    # Объединяем PNG в PDF
    create_pdf_from_images(png_files, pdf_path)


def create_pdf_from_images(image_paths, output_pdf_path):
    """Создаёт PDF из списка PNG изображений."""
    images = []
    for path in image_paths:
        img = Image.open(path)
        # PDF не поддерживает RGBA
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)

    # Сохраняем PDF
    images[0].save(
        output_pdf_path,
        save_all=True,
        append_images=images[1:],
        resolution=96.0,
        quality=95
    )
```

---

## Критические детали

### 1. Скриншот VIEWPORT, не секции

```python
# ❌ НЕПРАВИЛЬНО — скриншот только секции (может обрезаться)
section = page.query_selector(f'#{section_id}')
section.screenshot(path=png_path)

# ✅ ПРАВИЛЬНО — скриншот всего viewport
page.screenshot(path=png_path)
```

Скриншот секции может обрезать контент, который выходит за её границы. Скриншот viewport гарантирует полный захват видимой области.

### 2. Конвертация RGBA → RGB

```python
if img.mode == 'RGBA':
    background = Image.new('RGB', img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[3])
    img = background
```

PNG может содержать альфа-канал (прозрачность), но PDF его не поддерживает. Pillow упадёт с ошибкой без конвертации.

### 3. Размер PDF = размер изображений

```python
# PNG 1920x1080 → PDF страница 1920x1080 (в points при 96 dpi)
images[0].save(output_pdf_path, ..., resolution=96.0)
```

При `resolution=96.0` размеры страницы PDF будут соответствовать пикселям PNG.

### 4. Качество JPEG в PDF

```python
images[0].save(output_pdf_path, ..., quality=95)
```

Pillow сохраняет изображения в PDF как JPEG. `quality=95` обеспечивает минимальные артефакты сжатия.

---

## Сравнение методов

| Метод | Плюсы | Минусы |
|-------|-------|--------|
| `page.pdf()` напрямую | Быстро, один вызов | Режет контент, обрезка |
| **PNG → PDF** | Без обрезки, контроль над страницами | Больше кода, больше файлов |

---

## Когда применять

**Используйте PNG → PDF когда:**
- Контент обрезается при `page.pdf()`
- Секции высотой > viewport
- Нужен контроль над каждой страницей
- Презентации с фиксированными "слайдами"

**Можно использовать `page.pdf()` когда:**
- Документ состоит из маленьких блоков
- Обрезка допустима (текстовые документы)
- Нужна быстрая генерация

---

## Полный пример (из MCP Presentation)

```python
from playwright.sync_api import sync_playwright
from PIL import Image
import time
import os

def convert_html_to_pdf_and_png(html_path, output_pdf_path, output_png_folder):
    """Конвертирует HTML презентацию в PDF через PNG скриншоты."""

    os.makedirs(output_png_folder, exist_ok=True)
    html_url = f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}"
    png_files = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto(html_url)
        page.wait_for_load_state('networkidle')
        page.evaluate('() => document.fonts.ready')
        time.sleep(2)

        # Получаем список секций
        sections = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('section[id]'))
                .map(s => s.id);
        }''')

        for i, section_id in enumerate(sections):
            # Скролл к секции
            page.evaluate(f'''() => {{
                document.getElementById('{section_id}')
                    .scrollIntoView({{behavior: 'auto', block: 'start'}});
            }}''')
            time.sleep(0.5)

            # Скриншот viewport
            png_path = os.path.join(output_png_folder, f'slide_{i+1:02d}_{section_id}.png')
            page.screenshot(path=png_path)
            png_files.append(png_path)

        browser.close()

    # Создание PDF из PNG
    create_pdf_from_images(png_files, output_pdf_path)
```

---

## Результат

**До (page.pdf):**
- 10 страниц
- Блоки обрезаются между страницами
- Контент теряется

**После (PNG → PDF):**
- 13 страниц
- Каждая секция = отдельная страница
- Без обрезки, полный контент

---

## Связанные паттерны

- `landscape-pdf-orientation.md` — правильная ориентация PDF
- `interactive-elements-coverage.md` — клик по интерактивным элементам
- `deanimate-html.md` — деанимация перед конвертацией
