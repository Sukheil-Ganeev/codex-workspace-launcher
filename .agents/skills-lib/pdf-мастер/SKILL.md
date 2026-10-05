---
name: pdf-мастер
description: "Универсальный навык для ВСЕХ операций с PDF и PPTX. Создание, парсинг, извлечение данных, слияние, разделение, конвертация, OCR, формы, подписи, водяные знаки, сжатие. Триггеры - PDF, пдф, документ, инвойс, счёт, прайс, каталог."
---
# PDF-мастер: Универсальный PDF/PPTX навык

## Установленный стек (22 пакета)

| Пакет | Импорт | Роль |
|-------|--------|------|
| pypdf | `import pypdf` | Слияние, разделение, формы, метаданные |
| PyMuPDF | `import fitz` | Быстрое извлечение, аннотации, рендеринг, редактирование |
| ReportLab | `from reportlab.lib...` | Создание сложных PDF с нуля |
| fpdf2 | `from fpdf import FPDF` | Быстрое создание простых PDF |
| pdfplumber | `import pdfplumber` | Извлечение таблиц |
| pikepdf | `import pikepdf` | Ремонт, шифрование, линеаризация |
| WeasyPrint | `from weasyprint import HTML` | HTML/CSS → PDF (нужен GTK3) |
| ocrmypdf | `import ocrmypdf` | OCR → текстовый слой (нужен Tesseract) |
| pyHanko | `from pyhanko...` | Цифровые подписи |
| img2pdf | `import img2pdf` | Изображения → PDF без потерь |
| PyPDFForm | `from PyPDFForm import PdfWrapper` | Заполнение AcroForms |
| fpdf2 | `from fpdf import FPDF` | Лёгкие PDF, Unicode |
| pypdfium2 | `import pypdfium2` | Быстрое извлечение текста |
| pdfplumber | `import pdfplumber` | Таблицы с координатами |
| pdfminer.six | `from pdfminer...` | Глубокий анализ шрифтов/позиций |
| python-pptx | `from pptx import Presentation` | Создание/чтение PPTX |
| python-docx | `from docx import Document` | Создание/чтение DOCX |
| pdf2docx | `from pdf2docx import Converter` | PDF → DOCX |
| Pillow | `from PIL import Image` | Обработка изображений |
| Jinja2 | `from jinja2 import ...` | Шаблоны для HTML→PDF |
| svglib | `from svglib.svglib import svg2rlg` | SVG → ReportLab |
| openpyxl | `import openpyxl` | Excel чтение/запись |

## Системные зависимости

| Зависимость | Статус | Нужна для |
|-------------|--------|-----------|
| Tesseract OCR 5.4 | ✅ Установлен | ocrmypdf, pytesseract |
| Ghostscript 10.04 | ✅ Установлен | ocrmypdf PDF/A, сжатие |
| GTK3 (Cairo/Pango) | ✅ Работает (встроен в WeasyPrint 67+) | WeasyPrint |
| LibreOffice 26.2 | ✅ Установлен | PPTX→PDF, DOCX→PDF |

> **Все зависимости установлены.** Полный стек работает без fallback-ограничений.

## Алгоритм выбора инструмента

Перед выполнением любой PDF-задачи определи категорию и используй рекомендованный инструмент:

### Создание PDF

| Задача | Первый выбор | Fallback |
|--------|-------------|----------|
| Сложный макет (инвойс, отчёт с таблицами и графиками) | **ReportLab** | fpdf2 |
| Простой PDF (текст, таблица, картинка) | **fpdf2** | ReportLab |
| Из HTML/CSS шаблона | **WeasyPrint** + Jinja2 | fpdf2 |
| Из HTML с JavaScript | **Playwright** | — |
| Сертификат, визитка, билет | **fpdf2** (быстро) | ReportLab |
| С QR-кодом / штрих-кодом | **ReportLab** (встроенные) | fpdf2 + qrcode |
| Из изображений (без потерь) | **img2pdf** | PyMuPDF |

### Извлечение данных

| Задача | Первый выбор | Fallback |
|--------|-------------|----------|
| Быстрое извлечение текста | **PyMuPDF** | pypdfium2, pypdf |
| Таблицы | **pdfplumber** | PyMuPDF |
| Изображения (без потерь) | **pikepdf** | PyMuPDF |
| Текст с позициями и шрифтами | **pdfminer.six** | pdfplumber |
| Метаданные | **pypdf** | pikepdf |
| Данные форм | **pypdf** | PyMuPDF |
| Markdown для LLM/RAG | **PyMuPDF** (pymupdf4llm) | — |

### Манипуляция страницами

| Задача | Первый выбор | Fallback |
|--------|-------------|----------|
| Слияние | **pypdf** | pikepdf, PyMuPDF |
| Разделение | **pypdf** | pikepdf |
| Поворот | **pypdf** | pikepdf |
| Обрезка | **pypdf** | pikepdf |
| Удаление страниц | **pypdf** | pikepdf |
| Наложение текста/штампа | **PyMuPDF** | pypdf + ReportLab |
| Водяные знаки | **PyMuPDF** | pypdf + ReportLab |
| Нумерация страниц | **PyMuPDF** | ReportLab (при создании) |

### Безопасность

| Задача | Первый выбор | Fallback |
|--------|-------------|----------|
| Шифрование AES-256 | **pikepdf** | pypdf |
| Расшифровка | **pikepdf** | pypdf |
| Цифровая подпись | **pyHanko** | — |
| Редактирование (удаление) контента | **PyMuPDF** | — |
| Установка прав доступа | **pikepdf** | pypdf |

### OCR и конвертация

| Задача | Первый выбор | Fallback |
|--------|-------------|----------|
| OCR сканированного PDF | **ocrmypdf** | PyMuPDF + Tesseract |
| PDF → изображения | **PyMuPDF** | pypdfium2 |
| PDF → DOCX | **pdf2docx** | — |
| DOCX → PDF | **LibreOffice headless** | WeasyPrint (из HTML) |
| PPTX → PDF | **LibreOffice headless** | python-pptx → img → pdf |
| PDF/A конвертация | **ocrmypdf** | — |

### Оптимизация

| Задача | Первый выбор | Fallback |
|--------|-------------|----------|
| Сжатие | **pikepdf** (compress_streams) | PyMuPDF (garbage=4) |
| Линеаризация (web) | **pikepdf** | — (уникальная возможность) |
| Удаление мусора | **PyMuPDF** (garbage=4) | pikepdf |
| Ремонт повреждённого PDF | **pikepdf** → mutool → Ghostscript | каскадная стратегия |

### PPTX операции

| Задача | Инструмент |
|--------|-----------|
| Создание презентации | **python-pptx** |
| Чтение/извлечение из PPTX | **python-pptx** |
| Модификация слайдов | **python-pptx** |
| PPTX → PDF | **LibreOffice headless** или python-pptx → изображения → img2pdf |
| PPTX → изображения | python-pptx + Pillow |

## Workflow: пошаговый процесс

### 1. Определи задачу
Классифицируй запрос пользователя:
- **CREATE** — создать PDF/PPTX с нуля
- **EXTRACT** — извлечь данные из существующего PDF
- **MANIPULATE** — слить, разделить, повернуть, обрезать
- **CONVERT** — конвертировать между форматами
- **SECURE** — зашифровать, подписать, редактировать
- **OPTIMIZE** — сжать, починить, оптимизировать
- **OCR** — распознать текст в скане
- **PPTX** — работа с презентациями

### 2. Проверь зависимости
Перед использованием библиотеки проверь доступность:
```python
try:
    import fitz  # PyMuPDF
except ImportError:
    # fallback к pypdf
    import pypdf
```

Для системных зависимостей:
```python
import shutil
has_tesseract = shutil.which('tesseract') is not None
has_gs = shutil.which('gs') or shutil.which('gswin64c')
```

### 3. Выполни задачу
Используй таблицы выше для выбора инструмента. При ошибке — переходи к fallback.

### 4. Верифицируй результат
После создания/модификации PDF:
```python
import fitz
doc = fitz.open("output.pdf")
print(f"Страниц: {doc.page_count}, Размер: {os.path.getsize('output.pdf')/1024:.0f} KB")
doc.close()
```

## Каскадная стратегия ремонта

При повреждённом PDF пробуй последовательно:
1. `pikepdf.Pdf.open('damaged.pdf')` — авто-ремонт
2. `mutool clean -d damaged.pdf repaired.pdf` — если есть MuPDF tools
3. Ghostscript `gs -sDEVICE=pdfwrite -o repaired.pdf damaged.pdf`
4. Если ничего не помогло — сообщи пользователю

## Паттерн Jinja2 + WeasyPrint (стандарт индустрии)

Для генерации PDF из HTML-шаблонов:
```python
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('invoice.html')
html = template.render(data=context)
HTML(string=html).write_pdf('output.pdf')
```

**Если WeasyPrint недоступен** (нет GTK3), используй fpdf2:
```python
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', size=12)
pdf.cell(text="Текст на русском")
pdf.output('output.pdf')
```

## Рекомендуемые шрифты для Unicode

- **Noto Sans/Serif** — покрывает все мировые письменности
- **DejaVu Sans** — 200+ языков, хорош для RU/EN/AR
- **Roboto** — современный, чистый
- **Liberation** — метрически эквивалентны Arial/Times/Courier

## Справочные материалы

Для детальной информации — читай файлы из `references/`:

| Файл | Когда читать |
|------|-------------|
| `references/library-guide.md` | Нужны детали API конкретной библиотеки |
| `references/operations-catalog.md` | Полный каталог ВСЕХ операций с примерами кода |
| `references/code-patterns.md` | Готовые рецепты для типовых задач (инвойсы, отчёты, OCR) |
| `references/troubleshooting.md` | Ошибки, Windows-специфика, fallback-стратегии |
| `references/cheatsheet.md` | Быстрая шпаргалка: команда → результат |

## Важные правила

1. **Всегда проверяй fallback** — если основная библиотека не работает, переходи к альтернативе
2. **Unicode** — для русского/арабского текста ОБЯЗАТЕЛЬНО регистрируй TTF-шрифт (DejaVu или Noto)
3. **Большие файлы (>100MB)** — используй инкрементальную запись и чанковую обработку
4. **Пути на Windows** — используй `pathlib.Path` или сырые строки `r"D:\path"`
5. **Сохраняй на D:** — все выходные файлы сохраняй в `D:/Downloads/` или указанную пользователем папку
6. **Логируй** — при ошибке показывай что пошло не так и какой fallback использован
7. **XFA-формы** — НЕ поддерживаются в open-source. Только AcroForms
8. **Лицензии** — PyMuPDF = AGPL (ок для личного использования). ReportLab Community = BSD. pikepdf = MPL-2.0
