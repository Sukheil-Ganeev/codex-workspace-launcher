# Каталог операций PDF/PPTX

Полный каталог всех операций с готовыми сниппетами кода. Для детальной документации библиотек см. `library-guide.md`.

## Содержание
1. [Создание PDF](#создание)
2. [Извлечение данных](#извлечение)
3. [Манипуляция страницами](#манипуляция)
4. [Безопасность и подписи](#безопасность)
5. [OCR и распознавание](#ocr)
6. [Конвертация форматов](#конвертация)
7. [Оптимизация и ремонт](#оптимизация)
8. [Аннотации и водяные знаки](#аннотации)
9. [Формы](#формы)
10. [Метаданные](#метаданные)
11. [PPTX операции](#pptx)
12. [Штрих-коды и QR](#штрих-коды)

---

## Создание PDF {#создание}

### Инвойс с таблицей (ReportLab)
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Регистрация шрифта для русского
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'DejaVuSans-Bold.ttf'))

doc = SimpleDocTemplate("invoice.pdf", pagesize=A4)
styles = getSampleStyleSheet()
story = []

# Шапка
story.append(Paragraph("ИНВОЙС №2026-0316", styles['Title']))
story.append(Spacer(1, 20))

# Данные
data = [
    ['Услуга', 'Кол-во', 'Цена (AED)', 'Сумма (AED)'],
    ['Desert Safari Premium', '4', '350', '1,400'],
    ['Abu Dhabi City Tour', '4', '280', '1,120'],
    ['Dhow Cruise Marina', '2', '220', '440'],
    ['', '', 'ИТОГО:', '2,960'],
]
table = Table(data, colWidths=[7*cm, 2*cm, 3*cm, 3*cm])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
    ('FONTNAME', (0, 0), (-1, 0), 'DejaVu-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
    ('FONTNAME', (0, -1), (-1, -1), 'DejaVu-Bold'),
]))
story.append(table)
doc.build(story)
```

### Простой PDF с текстом и изображением (fpdf2)
```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', '', 14)

# Заголовок
pdf.cell(0, 10, text="Прайс-лист экскурсий", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(5)

# Логотип
pdf.image("logo.png", x=10, y=10, w=30)

# Таблица
pdf.set_font('DejaVu', '', 10)
items = [("Desert Safari", "250 AED"), ("Dhow Cruise", "180 AED")]
for name, price in items:
    pdf.cell(120, 8, text=name, border=1)
    pdf.cell(50, 8, text=price, border=1, new_x="LMARGIN", new_y="NEXT")

pdf.output("pricelist.pdf")
```

### HTML → PDF (WeasyPrint + Jinja2)
```python
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Шаблон invoice.html:
# <html><body>
#   <h1>Invoice #{{ number }}</h1>
#   <table>{% for item in items %}
#     <tr><td>{{ item.name }}</td><td>{{ item.price }} AED</td></tr>
#   {% endfor %}</table>
#   <p><strong>Total: {{ total }} AED</strong></p>
# </body></html>

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('invoice.html')
html = template.render(
    number="2026-0316",
    items=[{"name": "Desert Safari", "price": 350}],
    total=350
)
HTML(string=html).write_pdf('invoice.pdf')
```

**Fallback без WeasyPrint:** используй fpdf2 (см. выше)

---

## Извлечение данных {#извлечение}

### Текст из PDF (быстро)
```python
import fitz  # PyMuPDF — самый быстрый вариант

doc = fitz.open("input.pdf")
full_text = ""
for page in doc:
    full_text += page.get_text() + "\n"
doc.close()
```

### Таблицы из PDF
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("pricelist.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            df = pd.DataFrame(table[1:], columns=table[0])
            all_tables.append(df)

    if all_tables:
        combined = pd.concat(all_tables, ignore_index=True)
        combined.to_csv("extracted_tables.csv", index=False)
        combined.to_excel("extracted_tables.xlsx", index=False)
```

### Изображения из PDF (без потерь)
```python
import pikepdf
from pathlib import Path

pdf = pikepdf.Pdf.open("input.pdf")
output_dir = Path("extracted_images")
output_dir.mkdir(exist_ok=True)

for i, page in enumerate(pdf.pages):
    for name, image in page.images.items():
        pdfimage = pikepdf.PdfImage(image)
        pdfimage.extract_to(fileprefix=str(output_dir / f"page{i}_{name}"))

pdf.close()
```

### Markdown для LLM
```python
import pymupdf4llm
md = pymupdf4llm.to_markdown("input.pdf")
with open("output.md", "w", encoding="utf-8") as f:
    f.write(md)
```

---

## Манипуляция страницами {#манипуляция}

### Слияние нескольких PDF
```python
from pypdf import PdfMerger

merger = PdfMerger()
for pdf_file in ["part1.pdf", "part2.pdf", "part3.pdf"]:
    merger.append(pdf_file)
merger.write("merged.pdf")
merger.close()
```

### Разделение PDF на отдельные страницы
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    writer.write(f"page_{i+1}.pdf")
```

### Извлечение диапазона страниц
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages[2:7]:  # страницы 3-7
    writer.add_page(page)
writer.write("pages_3_to_7.pdf")
```

### Поворот страниц
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()
for page in reader.pages:
    page.rotate(90)  # 90, 180, 270 градусов
    writer.add_page(page)
writer.write("rotated.pdf")
```

---

## Безопасность {#безопасность}

### Шифрование AES-256
```python
import pikepdf

pdf = pikepdf.Pdf.open("input.pdf")
pdf.save("encrypted.pdf", encryption=pikepdf.Encryption(
    owner="strong_owner_pass",
    user="user_pass",
    aes=True, R=6
))
```

### Расшифровка
```python
import pikepdf
pdf = pikepdf.Pdf.open("encrypted.pdf", password="user_pass")
pdf.save("decrypted.pdf")
```

### Редактирование конфиденциальных данных
```python
import fitz

doc = fitz.open("input.pdf")
for page in doc:
    areas = page.search_for("конфиденциально")
    for area in areas:
        page.add_redact_annot(area, fill=(0, 0, 0))  # чёрный прямоугольник
    page.apply_redactions()
doc.save("redacted.pdf")
```

---

## OCR {#ocr}

### Полный OCR pipeline
```python
import ocrmypdf

ocrmypdf.ocr(
    "scan.pdf", "output_ocr.pdf",
    language="rus+eng",
    deskew=True,
    clean=True,
    rotate_pages=True,
    optimize=2,
    skip_text=True,  # не трогать уже текстовые страницы
)
```

### OCR без Ghostscript (fallback)
```python
import fitz
import subprocess

doc = fitz.open("scan.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=300)
    pix.save(f"temp_page_{i}.png")
    # Tesseract напрямую
    subprocess.run(["tesseract", f"temp_page_{i}.png", f"temp_page_{i}",
                    "-l", "rus+eng", "pdf"])
```

---

## Конвертация {#конвертация}

### PDF → изображения
```python
import fitz

doc = fitz.open("input.pdf")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=300)
    pix.save(f"page_{i+1}.png")
doc.close()
```

### Изображения → PDF (без потерь)
```python
import img2pdf
from pathlib import Path

images = sorted(Path(".").glob("*.jpg"))
with open("from_images.pdf", "wb") as f:
    f.write(img2pdf.convert([str(img) for img in images]))
```

### PDF → DOCX
```python
from pdf2docx import Converter

cv = Converter("input.pdf")
cv.convert("output.docx")
cv.close()
```

### PPTX → PDF (LibreOffice)
```python
import subprocess
subprocess.run([
    'libreoffice', '--headless', '--convert-to', 'pdf',
    '--outdir', 'D:/Downloads/', 'presentation.pptx'
], check=True)
```

---

## Оптимизация и ремонт {#оптимизация}

### Сжатие PDF
```python
# Вариант 1: pikepdf
import pikepdf
pdf = pikepdf.Pdf.open("large.pdf")
pdf.save("compressed.pdf",
         compress_streams=True,
         object_stream_mode=pikepdf.ObjectStreamMode.generate)

# Вариант 2: PyMuPDF
import fitz
doc = fitz.open("large.pdf")
doc.save("compressed.pdf", garbage=4, deflate=True)
doc.close()
```

### Каскадный ремонт повреждённого PDF
```python
import pikepdf
import subprocess
import shutil

def repair_pdf(input_path, output_path):
    """Каскадная стратегия ремонта: pikepdf → mutool → Ghostscript"""

    # Попытка 1: pikepdf (авто-ремонт через qpdf)
    try:
        pdf = pikepdf.Pdf.open(input_path)
        pdf.save(output_path)
        pdf.close()
        return "pikepdf"
    except Exception:
        pass

    # Попытка 2: mutool (если установлен)
    if shutil.which('mutool'):
        try:
            subprocess.run(['mutool', 'clean', '-d', input_path, output_path], check=True)
            return "mutool"
        except Exception:
            pass

    # Попытка 3: Ghostscript (если установлен)
    gs = shutil.which('gs') or shutil.which('gswin64c')
    if gs:
        try:
            subprocess.run([gs, '-sDEVICE=pdfwrite', '-dNOPAUSE', '-dQUIET',
                           '-dBATCH', f'-sOutputFile={output_path}', input_path], check=True)
            return "ghostscript"
        except Exception:
            pass

    raise RuntimeError(f"Не удалось восстановить {input_path}")
```

### Линеаризация (Fast Web View)
```python
import pikepdf
pdf = pikepdf.Pdf.open("input.pdf")
pdf.save("web_optimized.pdf", linearize=True)
```

---

## Аннотации и водяные знаки {#аннотации}

### Водяной знак (текст)
```python
import fitz

doc = fitz.open("input.pdf")
for page in doc:
    # Полупрозрачный текст по диагонали
    rect = page.rect
    text_point = fitz.Point(rect.width / 4, rect.height / 2)
    page.insert_text(text_point, "ОБРАЗЕЦ",
                     fontsize=72, color=(0.8, 0.8, 0.8),
                     rotate=45, overlay=True)
doc.save("watermarked.pdf")
```

### Нумерация страниц
```python
import fitz

doc = fitz.open("input.pdf")
for i, page in enumerate(doc):
    rect = page.rect
    page.insert_text(
        fitz.Point(rect.width / 2 - 20, rect.height - 30),
        f"— {i + 1} —",
        fontsize=10, color=(0.5, 0.5, 0.5)
    )
doc.save("numbered.pdf")
```

---

## Формы {#формы}

### Заполнение PDF-формы
```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("form_template.pdf").fill({
    "name": "Иванов Иван",
    "date": "16.03.2026",
    "email": "ivan@example.com",
    "amount": "2,960 AED",
    "checkbox_agree": True,
})

with open("filled_form.pdf", "wb") as f:
    f.write(filled.read())
```

### Чтение полей формы
```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_fields()
for name, field in fields.items():
    print(f"{name}: {field.get('/V', 'пусто')}")
```

---

## Метаданные {#метаданные}

### Чтение
```python
from pypdf import PdfReader

reader = PdfReader("input.pdf")
meta = reader.metadata
print(f"Автор: {meta.author}")
print(f"Создан: {meta.creation_date}")
print(f"Страниц: {len(reader.pages)}")
```

### Запись XMP-метаданных
```python
import pikepdf

pdf = pikepdf.Pdf.open("input.pdf")
with pdf.open_metadata() as meta:
    meta['dc:title'] = 'Инвойс VIP DXB RUS'
    meta['dc:creator'] = ['Сухейль']
    meta['dc:description'] = 'Инвойс за экскурсии'
pdf.save("with_metadata.pdf")
```

---

## PPTX операции {#pptx}

### Создание презентации
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation()

# Титульный слайд
slide = prs.slides.add_slide(prs.slide_layouts[0])
slide.shapes.title.text = "Туры по ОАЭ 2026"
slide.placeholders[1].text = "VIP DXB RUS — Лучшие цены"

# Контент
slide = prs.slides.add_slide(prs.slide_layouts[1])
slide.shapes.title.text = "Популярные экскурсии"
body = slide.placeholders[1].text_frame
body.text = "Desert Safari Premium — 350 AED"
p = body.add_paragraph()
p.text = "Abu Dhabi City Tour — 280 AED"

# Таблица на слайде
slide = prs.slides.add_slide(prs.slide_layouts[5])
table = slide.shapes.add_table(4, 3, Inches(1), Inches(1.5), Inches(8), Inches(3)).table
headers = ['Тур', 'Взрослый', 'Ребёнок']
for i, h in enumerate(headers):
    table.cell(0, i).text = h

prs.save("tours_2026.pptx")
```

### Извлечение текста из PPTX
```python
from pptx import Presentation

prs = Presentation("input.pptx")
all_text = []
for slide_num, slide in enumerate(prs.slides, 1):
    slide_text = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                slide_text.append(para.text)
    all_text.append(f"--- Слайд {slide_num} ---\n" + "\n".join(slide_text))

print("\n\n".join(all_text))
```

---

## Штрих-коды и QR {#штрих-коды}

### QR-код в PDF (ReportLab)
```python
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

qr = QrCodeWidget("https://vipdxbrus.com/tour/desert-safari")
d = Drawing(150, 150)
d.add(qr)
renderPDF.drawToFile(d, "qr.pdf")
```

### QR-код через python-qrcode
```python
import qrcode
qr = qrcode.make("https://vipdxbrus.com")
qr.save("qr.png")
# Затем вставить в PDF через fpdf2/ReportLab/PyMuPDF
```
