# Шпаргалка PDF/PPTX

Быстрый справочник: задача → одна строка кода.

## Извлечение

```python
# Текст (быстро)
text = fitz.open("f.pdf")[0].get_text()

# Все таблицы → pandas
import pdfplumber; tables = pdfplumber.open("f.pdf").pages[0].extract_tables()

# Изображения (без потерь)
pikepdf.PdfImage(pikepdf.Pdf.open("f.pdf").pages[0].images[img_name]).extract_to("img")

# Метаданные
meta = pypdf.PdfReader("f.pdf").metadata

# Markdown для LLM
md = pymupdf4llm.to_markdown("f.pdf")

# Кол-во страниц
n = len(fitz.open("f.pdf"))

# Поля формы
fields = pypdf.PdfReader("f.pdf").get_fields()
```

## Создание

```python
# Простой PDF (fpdf2)
from fpdf import FPDF; pdf = FPDF(); pdf.add_page(); pdf.set_font("Helvetica", size=12)
pdf.cell(text="Hello"); pdf.output("out.pdf")

# HTML → PDF (WeasyPrint)
from weasyprint import HTML; HTML(string="<h1>Hi</h1>").write_pdf("out.pdf")

# С русским текстом (fpdf2)
pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True); pdf.set_font('DejaVu')

# Из изображений (без потерь)
import img2pdf; open("out.pdf","wb").write(img2pdf.convert(["1.jpg","2.jpg"]))
```

## Манипуляция

```python
# Слияние
from pypdf import PdfMerger; m = PdfMerger(); m.append("1.pdf"); m.append("2.pdf"); m.write("merged.pdf")

# Разделение (каждая страница)
r = pypdf.PdfReader("f.pdf")
for i, p in enumerate(r.pages): w = pypdf.PdfWriter(); w.add_page(p); w.write(f"p{i}.pdf")

# Поворот на 90°
for p in pypdf.PdfReader("f.pdf").pages: p.rotate(90)

# Водяной знак
page = fitz.open("f.pdf")[0]
page.insert_text(fitz.Point(200, 400), "DRAFT", fontsize=60, color=(0.8,0.8,0.8), rotate=45)
```

## Безопасность

```python
# Шифрование AES-256
pikepdf.Pdf.open("f.pdf").save("enc.pdf", encryption=pikepdf.Encryption(owner="o", user="u", aes=True, R=6))

# Расшифровка
pikepdf.Pdf.open("enc.pdf", password="u").save("dec.pdf")

# Редактирование (удаление текста)
for a in fitz.open("f.pdf")[0].search_for("secret"): page.add_redact_annot(a); page.apply_redactions()
```

## OCR

```python
# Полный pipeline
ocrmypdf.ocr("scan.pdf", "out.pdf", language="rus+eng", deskew=True, clean=True)

# Tesseract напрямую (fallback)
import subprocess; subprocess.run(["tesseract", "scan.png", "out", "-l", "rus+eng", "pdf"])
```

## Конвертация

```python
# PDF → PNG (каждая страница)
for i, p in enumerate(fitz.open("f.pdf")): p.get_pixmap(dpi=300).save(f"p{i}.png")

# PDF → DOCX
from pdf2docx import Converter; c = Converter("f.pdf"); c.convert("f.docx"); c.close()

# PPTX → PDF (LibreOffice)
subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "f.pptx"])
```

## Оптимизация

```python
# Сжатие (pikepdf)
pikepdf.Pdf.open("big.pdf").save("small.pdf", compress_streams=True,
    object_stream_mode=pikepdf.ObjectStreamMode.generate)

# Сжатие (PyMuPDF)
fitz.open("big.pdf").save("small.pdf", garbage=4, deflate=True)

# Ремонт
pikepdf.Pdf.open("broken.pdf").save("fixed.pdf")

# Линеаризация (web)
pikepdf.Pdf.open("f.pdf").save("web.pdf", linearize=True)
```

## PPTX

```python
# Создание
from pptx import Presentation; prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Title"; prs.save("out.pptx")

# Чтение текста
for s in Presentation("f.pptx").slides:
    for sh in s.shapes:
        if sh.has_text_frame: print(sh.text_frame.text)
```

## Проверка окружения

```bash
# Python пакеты
python -c "import fitz; print(fitz.__doc__)"
python -c "import pypdf; print(pypdf.__version__)"

# Системные
tesseract --version
gswin64c --version  # Ghostscript на Windows
```
