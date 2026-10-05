# Troubleshooting и FAQ

## Содержание
1. [Системные зависимости](#системные-зависимости)
2. [Типичные ошибки](#типичные-ошибки)
3. [Windows-специфика](#windows)
4. [Fallback-стратегии](#fallback)
5. [Производительность](#производительность)

---

## Системные зависимости {#системные-зависимости}

### Ghostscript не установлен

**Симптом:** `ocrmypdf` падает при создании PDF/A, `gs` not found

**Решение:**
1. Скачай с https://ghostscript.com/releases/gsdnld.html
2. Установи (запомни путь, напр. `C:\Program Files\gs\gs10.x\bin`)
3. Добавь в PATH: `C:\Program Files\gs\gs10.x\bin`
4. Проверь: `gswin64c --version`

**Fallback без Ghostscript:**
- Для ремонта PDF → используй `pikepdf` (работает без gs)
- Для OCR → используй Tesseract напрямую (без ocrmypdf)
- Для сжатия → используй `PyMuPDF` (`doc.save(garbage=4, deflate=True)`)

### GTK3/Cairo/Pango не установлены

**Симптом:** WeasyPrint падает с `OSError: cannot load library 'libgobject-2.0-0'`

**Решение (MSYS2):**
1. Установи MSYS2: https://www.msys2.org/
2. В MSYS2 терминале: `pacman -S mingw-w64-x86_64-gtk3`
3. Добавь `C:\msys64\mingw64\bin` в PATH

**Решение (standalone):**
1. Скачай GTK3 runtime: https://github.com/nickvdp/msys2-gtk-deps/releases
2. Распакуй и добавь `bin/` в PATH

**Fallback без WeasyPrint:**
- HTML → PDF: используй `fpdf2` (ручная вёрстка) или Playwright
- Для простых документов `fpdf2` — лучшая альтернатива

### Tesseract не найден

**Симптом:** `tesseract is not installed or it's not in your PATH`

**Статус:** ✅ Установлен (v5.4.0) на текущей системе

**Если пропал:**
1. Скачай: https://github.com/UB-Mannheim/tesseract/wiki
2. При установке выбери языки: Russian, English, Arabic
3. Добавь в PATH: `C:\Program Files\Tesseract-OCR`

---

## Типичные ошибки {#типичные-ошибки}

### `ModuleNotFoundError: No module named 'fitz'`
PyMuPDF импортируется как `fitz`, не как `pymupdf`:
```python
import fitz  # ✅ правильно
# import pymupdf  # ❌ неправильно
```

### `ModuleNotFoundError: No module named 'fpdf2'`
fpdf2 импортируется как `fpdf`:
```python
from fpdf import FPDF  # ✅ правильно
# from fpdf2 import FPDF  # ❌ неправильно
```

### `PdfReadError: EOF marker not found`
Повреждённый PDF. Используй каскадный ремонт:
```python
import pikepdf
pdf = pikepdf.Pdf.open("damaged.pdf")  # авто-ремонт
pdf.save("repaired.pdf")
```

### `UnicodeEncodeError` при создании PDF
Забыл зарегистрировать TTF-шрифт:
```python
# fpdf2
pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', '', 12)

# ReportLab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
```

### `RuntimeError: Tesseract failed. No text found`
Изображение слишком низкого качества или неправильный язык:
```python
ocrmypdf.ocr("scan.pdf", "output.pdf",
    language="rus+eng",  # указать все нужные языки
    deskew=True,          # выровнять
    clean=True,           # очистить от шума
    force_ocr=True,       # пере-OCR даже если есть текст
)
```

### `img2pdf: Only JPEG, PNG, TIFF supported`
img2pdf не поддерживает BMP, WebP, SVG. Конвертируй через Pillow:
```python
from PIL import Image
im = Image.open("photo.webp")
im.save("photo.jpg", "JPEG")
```

### Таблица не извлекается из PDF
pdfplumber не видит таблицу:
```python
# Попробуй другую стратегию
tables = page.extract_tables({
    "vertical_strategy": "text",      # вместо "lines"
    "horizontal_strategy": "text",
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
})

# Если не помогает — визуальная отладка
im = page.to_image(resolution=200)
im.debug_tablefinder()
im.save("debug_table.png")
# Посмотри PNG чтобы понять что pdfplumber видит
```

---

## Windows-специфика {#windows}

### Пути
```python
from pathlib import Path

# ВСЕГДА используй pathlib
output = Path("D:/Downloads/output.pdf")

# Или сырые строки
path = r"D:\Downloads\output.pdf"

# НИКОГДА не используй обратные слэши без r""
# path = "D:\Downloads\output.pdf"  # ❌ \D интерпретируется как escape
```

### Кодировка
```python
# При записи текста
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(text)

# При чтении CSV с русским текстом
import pandas as pd
df = pd.read_csv("data.csv", encoding="utf-8-sig")  # BOM-aware
```

### Блокировка файлов
Windows блокирует открытые PDF. Всегда закрывай файлы:
```python
doc = fitz.open("input.pdf")
# ... работа ...
doc.close()  # ОБЯЗАТЕЛЬНО

# Или используй context manager
with pdfplumber.open("input.pdf") as pdf:
    # ... работа ...
```

---

## Fallback-стратегии {#fallback}

| Задача | Основной | Если недоступен | Если и он недоступен |
|--------|---------|-----------------|---------------------|
| HTML → PDF | WeasyPrint | fpdf2 (ручная вёрстка) | Playwright |
| OCR | ocrmypdf | Tesseract напрямую | PyMuPDF + Tesseract |
| Ремонт PDF | pikepdf | PyMuPDF (open + save) | — |
| PDF/A | ocrmypdf | — | — |
| Сжатие | pikepdf | PyMuPDF (garbage=4) | Ghostscript CLI |
| PPTX → PDF | LibreOffice | python-pptx → img → pdf | — |

---

## Производительность {#производительность}

### Большие файлы (>100 MB)
```python
# PyMuPDF: инкрементальная запись
doc = fitz.open("huge.pdf")
# ... модификации ...
doc.save(doc.name, incremental=True)  # НЕ перезаписывает весь файл

# pikepdf: максимальное сжатие
pdf.save("output.pdf",
    compress_streams=True,
    object_stream_mode=pikepdf.ObjectStreamMode.generate)
```

### Много файлов — параллельная обработка
```python
from concurrent.futures import ProcessPoolExecutor

def process_pdf(path):
    # твоя обработка
    pass

with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_pdf, pdf_files))
```

### Память
```python
import gc

for pdf_path in large_pdf_list:
    doc = fitz.open(pdf_path)
    # ... обработка ...
    doc.close()
    gc.collect()  # явная сборка мусора для больших файлов
```
