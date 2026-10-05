# Справочник библиотек PDF/PPTX стека

## Содержание
1. [pypdf — слияние, разделение, формы](#pypdf)
2. [PyMuPDF (fitz) — быстрое извлечение и редактирование](#pymupdf)
3. [ReportLab — создание сложных PDF](#reportlab)
4. [fpdf2 — быстрое создание простых PDF](#fpdf2)
5. [pdfplumber — извлечение таблиц](#pdfplumber)
6. [pikepdf — ремонт и шифрование](#pikepdf)
7. [WeasyPrint — HTML/CSS → PDF](#weasyprint)
8. [ocrmypdf — OCR pipeline](#ocrmypdf)
9. [pyHanko — цифровые подписи](#pyhanko)
10. [img2pdf — изображения → PDF](#img2pdf)
11. [PyPDFForm — заполнение форм](#pypdfform)
12. [pdfminer.six — глубокий анализ](#pdfminer)
13. [pypdfium2 — быстрый текст](#pypdfium2)
14. [python-pptx — презентации](#python-pptx)
15. [python-docx — документы Word](#python-docx)
16. [pdf2docx — конвертация PDF→DOCX](#pdf2docx)
17. [svglib — SVG → ReportLab](#svglib)
18. [Pillow — изображения](#pillow)
19. [Jinja2 — шаблоны](#jinja2)

---

## pypdf
**Версия:** 6.9.0 | **Лицензия:** BSD-3 | **GitHub:** ~9,500 ⭐
**Роль:** Слияние, разделение, поворот, обрезка, формы, метаданные, шифрование

### Ключевые операции

```python
from pypdf import PdfReader, PdfWriter, PdfMerger

# Чтение
reader = PdfReader("input.pdf")
print(f"Страниц: {len(reader.pages)}")
text = reader.pages[0].extract_text()

# Метаданные
meta = reader.metadata
print(f"Автор: {meta.author}, Создан: {meta.creation_date}")

# Слияние
merger = PdfMerger()
merger.append("file1.pdf")
merger.append("file2.pdf", pages=(0, 3))  # только стр. 1-3
merger.write("merged.pdf")
merger.close()

# Разделение — каждая страница отдельно
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    writer.write(f"page_{i+1}.pdf")

# Поворот
writer = PdfWriter()
for page in reader.pages:
    page.rotate(90)  # 90, 180, 270
    writer.add_page(page)
writer.write("rotated.pdf")

# Шифрование
writer = PdfWriter()
writer.append_pages_from_reader(reader)
writer.encrypt(user_password="user123", owner_password="owner456",
               use_128bit=False)  # AES-256 с pypdf[crypto]
writer.write("encrypted.pdf")

# Расшифровка
reader = PdfReader("encrypted.pdf")
reader.decrypt("user123")

# Заполнение форм
reader = PdfReader("form.pdf")
writer = PdfWriter()
writer.append(reader)
writer.update_page_form_field_values(
    writer.pages[0],
    {"field_name": "value", "date_field": "2026-03-16"}
)
writer.write("filled.pdf")

# Flatten форм (сглаживание)
reader = PdfReader("filled.pdf")
writer = PdfWriter()
writer.append(reader)
for page in writer.pages:
    for annot in page.get("/Annots", []):
        annot.update({pypdf.generic.NameObject("/Ff"): pypdf.generic.NumberObject(1)})
writer.write("flattened.pdf")

# Закладки
writer.add_outline_item("Глава 1", 0)  # страница 0
writer.add_outline_item("Глава 2", 5)
```

### Когда использовать pypdf
- Слияние/разделение PDF — основной инструмент
- Простое извлечение текста (если скорость не критична)
- Заполнение AcroForms
- Чтение/запись метаданных
- Базовое шифрование

### Когда НЕ использовать
- Скорость критична → PyMuPDF
- Таблицы → pdfplumber
- Создание PDF с нуля → ReportLab или fpdf2
- Ремонт повреждённых → pikepdf
- Аннотации/водяные знаки → PyMuPDF

---

## PyMuPDF (fitz) {#pymupdf}
**Версия:** 1.27.2 | **Лицензия:** AGPL-3.0 | **GitHub:** ~9,000 ⭐
**Роль:** Самая быстрая библиотека. Извлечение, рендеринг, аннотации, редактирование.

### Ключевые операции

```python
import fitz  # PyMuPDF

# Открытие и информация
doc = fitz.open("input.pdf")
print(f"Страниц: {doc.page_count}")
print(f"Метаданные: {doc.metadata}")

# Извлечение текста (несколько режимов)
page = doc[0]
text = page.get_text()           # простой текст
text_blocks = page.get_text("blocks")  # блоки с координатами
text_dict = page.get_text("dict")      # полная структура (шрифты, размеры)
text_html = page.get_text("html")      # HTML с форматированием

# Извлечение таблиц (с v1.23)
tables = page.find_tables()
for table in tables:
    df = table.to_pandas()  # → pandas DataFrame
    print(df)

# Извлечение изображений
for img_index, img in enumerate(page.get_images(full=True)):
    xref = img[0]
    base_image = doc.extract_image(xref)
    image_bytes = base_image["image"]
    ext = base_image["ext"]
    with open(f"image_{img_index}.{ext}", "wb") as f:
        f.write(image_bytes)

# Рендеринг страницы в изображение
pix = page.get_pixmap(dpi=300)
pix.save("page1.png")

# Добавление текста (водяной знак, штамп)
page = doc[0]
text_point = fitz.Point(50, 50)
page.insert_text(text_point, "КОНФИДЕНЦИАЛЬНО",
                 fontsize=48, color=(1, 0, 0), rotate=45)

# Выделение текста (highlight)
areas = page.search_for("важный текст")
for area in areas:
    page.add_highlight_annot(area)

# Добавление изображения
rect = fitz.Rect(100, 100, 300, 200)
page.insert_image(rect, filename="logo.png")

# Удаление контента (redaction)
areas = page.search_for("секретные данные")
for area in areas:
    page.add_redact_annot(area, fill=(0, 0, 0))
page.apply_redactions()

# Оглавление
toc = doc.get_toc()  # [[level, title, page], ...]
doc.set_toc([
    [1, "Введение", 1],
    [1, "Глава 1", 3],
    [2, "Раздел 1.1", 5],
])

# Сохранение с оптимизацией
doc.save("output.pdf", garbage=4, deflate=True)
# garbage=4 — максимальная очистка неиспользуемых объектов
doc.close()

# Markdown для LLM (pymupdf4llm)
import pymupdf4llm
md_text = pymupdf4llm.to_markdown("input.pdf")
```

### Производительность
- Извлечение текста: ~0.01 с/страница (в 5-10× быстрее pypdf)
- Рендеринг: ~0.05 с/страница при 150 DPI
- Оптимально для больших файлов (100+ стр.)

### Когда использовать PyMuPDF
- Извлечение текста с максимальной скоростью
- Рендеринг PDF → изображения
- Аннотации, водяные знаки, штампы
- Редактирование (удаление) конфиденциальных данных
- Работа с оглавлением

---

## ReportLab {#reportlab}
**Версия:** 4.4.10 | **Лицензия:** BSD | **GitHub:** ~4,600 ⭐
**Роль:** Создание сложных PDF с нуля. Промышленный стандарт.

### Два уровня API

**Canvas (низкий уровень)** — прямое рисование:
```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

c = canvas.Canvas("output.pdf", pagesize=A4)
width, height = A4

# Текст
c.setFont("Helvetica-Bold", 24)
c.drawString(100, height - 100, "Заголовок")

# Линия
c.setStrokeColorRGB(0.2, 0.2, 0.8)
c.setLineWidth(2)
c.line(50, height - 120, width - 50, height - 120)

# Прямоугольник
c.setFillColorRGB(0.9, 0.9, 1.0)
c.rect(50, height - 300, width - 100, 150, fill=True, stroke=True)

# Изображение
c.drawImage("logo.png", 50, height - 80, width=100, height=50)

c.showPage()
c.save()
```

**PLATYPUS (высокий уровень)** — потоковые элементы с автоматическим разбиением:
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, Image, PageBreak
)

doc = SimpleDocTemplate("report.pdf", pagesize=A4,
                        topMargin=2*cm, bottomMargin=2*cm)
styles = getSampleStyleSheet()
story = []

# Заголовок
story.append(Paragraph("Отчёт за март 2026", styles['Title']))
story.append(Spacer(1, 12))

# Параграф
story.append(Paragraph("Текст отчёта с <b>жирным</b> и <i>курсивом</i>.",
                        styles['Normal']))

# Таблица
data = [
    ['Услуга', 'Кол-во', 'Цена (AED)', 'Сумма'],
    ['Desert Safari', '4', '250', '1,000'],
    ['Dhow Cruise', '2', '180', '360'],
    ['Ferrari World', '4', '295', '1,180'],
    ['', '', 'ИТОГО:', '2,540'],
]
table = Table(data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E3F2FD')),
    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
]))
story.append(table)

# Встроенные штрих-коды
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
qr = QrCodeWidget("https://vipdxbrus.com")
d = Drawing(100, 100)
d.add(qr)
story.append(d)

doc.build(story)
```

### Регистрация TTF-шрифтов (для русского/арабского)
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'DejaVuSans-Bold.ttf'))
```

### Диаграммы
```python
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing

d = Drawing(400, 200)
chart = VerticalBarChart()
chart.x, chart.y = 50, 50
chart.width, chart.height = 300, 125
chart.data = [[10, 20, 30, 40], [15, 25, 35, 45]]
chart.categoryAxis.categoryNames = ['Q1', 'Q2', 'Q3', 'Q4']
d.add(chart)
```

---

## fpdf2 {#fpdf2}
**Версия:** 2.8.5 | **Лицензия:** LGPL-3.0 | **GitHub:** ~1,200 ⭐
**Роль:** Быстрое создание простых PDF. Полная поддержка Unicode.

```python
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()

# Unicode шрифт (ОБЯЗАТЕЛЬНО для русского)
pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
pdf.set_font('DejaVu', 'B', 24)
pdf.cell(text="Инвойс №1234", new_x="LMARGIN", new_y="NEXT")

pdf.set_font('DejaVu', '', 12)
pdf.cell(text="Клиент: Иванов Иван")

# Таблица
pdf.set_font('DejaVu', 'B', 10)
headers = ['Услуга', 'Цена']
for h in headers:
    pdf.cell(w=90, h=8, text=h, border=1)
pdf.ln()

pdf.set_font('DejaVu', '', 10)
data = [['Desert Safari', '250 AED'], ['Dhow Cruise', '180 AED']]
for row in data:
    for cell in row:
        pdf.cell(w=90, h=8, text=cell, border=1)
    pdf.ln()

# Изображение
pdf.image("logo.png", x=10, y=10, w=30)

# Оглавление
pdf.add_page()
pdf.start_section("Глава 1")
pdf.cell(text="Содержание главы 1")
pdf.add_page()
pdf.start_section("Глава 2")
pdf.insert_toc_placeholder(render_toc)  # auto TOC

pdf.output("output.pdf")
```

### Преимущества fpdf2
- Чисто Python, нулевые системные зависимости
- Очень быстрая генерация
- Полный Unicode с подмножествами шрифтов
- Встроенные штрих-коды (Code39, I2of5)
- JSON-шаблоны для повторяющихся форматов

---

## pdfplumber {#pdfplumber}
**Версия:** 0.11.7 | **Лицензия:** MIT | **GitHub:** ~9,000 ⭐
**Роль:** Лучшее извлечение таблиц из PDF.

```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    page = pdf.pages[0]

    # Извлечение текста
    text = page.extract_text()

    # Извлечение таблиц
    tables = page.extract_tables()
    for table in tables:
        for row in table:
            print(row)  # ['col1', 'col2', 'col3']

    # Таблица → pandas DataFrame
    import pandas as pd
    table = tables[0]
    df = pd.DataFrame(table[1:], columns=table[0])

    # Настройки извлечения таблиц
    table_settings = {
        "vertical_strategy": "lines",    # "lines", "text", "explicit"
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "join_tolerance": 3,
    }
    tables = page.extract_tables(table_settings)

    # Визуальная отладка
    im = page.to_image(resolution=150)
    im.debug_tablefinder()
    im.save("debug.png")

    # Доступ к отдельным символам
    chars = page.chars  # список словарей с x0, y0, text, fontname, size
    words = page.extract_words()
```

---

## pikepdf {#pikepdf}
**Версия:** 10.5.0 | **Лицензия:** MPL-2.0 | **GitHub:** ~2,600 ⭐
**Роль:** Ремонт, шифрование, линеаризация, низкоуровневые операции.

```python
import pikepdf

# Ремонт повреждённого PDF (автоматически при открытии)
pdf = pikepdf.Pdf.open("damaged.pdf")
pdf.save("repaired.pdf")

# Шифрование AES-256
pdf = pikepdf.Pdf.open("input.pdf")
pdf.save("encrypted.pdf",
         encryption=pikepdf.Encryption(
             owner="owner_pass",
             user="user_pass",
             aes=True,
             R=6  # AES-256
         ))

# Расшифровка
pdf = pikepdf.Pdf.open("encrypted.pdf", password="user_pass")
pdf.save("decrypted.pdf")

# Линеаризация (оптимизация для веба)
pdf = pikepdf.Pdf.open("input.pdf")
pdf.save("linearized.pdf", linearize=True)

# Сжатие
pdf = pikepdf.Pdf.open("input.pdf")
pdf.save("compressed.pdf",
         compress_streams=True,
         object_stream_mode=pikepdf.ObjectStreamMode.generate)

# XMP-метаданные
with pdf.open_metadata() as meta:
    meta['dc:title'] = 'Мой документ'
    meta['dc:creator'] = ['Автор']

# Извлечение изображений (без потерь)
for page in pdf.pages:
    for name, image in page.images.items():
        pdfimage = pikepdf.PdfImage(image)
        pdfimage.extract_to(fileprefix=f"img_{name}")
```

---

## WeasyPrint {#weasyprint}
**Версия:** 67.0 | **Лицензия:** BSD-3 | **GitHub:** ~7,200 ⭐
**Роль:** HTML/CSS → PDF. Требует GTK3 (Cairo, Pango).

⚠️ **На текущей системе GTK3 НЕ установлен.** Используй fpdf2 как fallback.

```python
from weasyprint import HTML, CSS

# Из строки HTML
HTML(string='<h1>Привет</h1><p>Текст</p>').write_pdf('output.pdf')

# Из файла
HTML(filename='report.html').write_pdf('output.pdf')

# С CSS
HTML(string=html_content).write_pdf('output.pdf',
    stylesheets=[CSS(string='@page { size: A4; margin: 2cm; }')])

# Паттерн Jinja2 + WeasyPrint
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('invoice.html')
html = template.render(
    company="VIP DXB RUS",
    items=[{"name": "Desert Safari", "price": 250}],
    total=250
)
HTML(string=html).write_pdf('invoice.pdf')
```

### CSS Paged Media
```css
@page {
    size: A4;
    margin: 2cm;
    @bottom-center {
        content: "Стр. " counter(page) " из " counter(pages);
    }
}
h1 { page-break-before: always; }
table { page-break-inside: avoid; }
```

---

## ocrmypdf {#ocrmypdf}
**Версия:** 17.3.0 | **Лицензия:** MPL-2.0
**Роль:** OCR pipeline: deskew → clean → Tesseract → PDF/A

⚠️ **Требует Tesseract (✅ установлен) и Ghostscript (⚠️ НЕ установлен)**

```python
import ocrmypdf

# Базовый OCR
ocrmypdf.ocr("scan.pdf", "output.pdf", language="rus+eng")

# С оптимизацией
ocrmypdf.ocr("scan.pdf", "output.pdf",
    language="rus+eng",
    deskew=True,           # выровнять
    clean=True,            # убрать шум
    rotate_pages=True,     # автоповорот
    optimize=2,            # уровень сжатия (0-3)
    output_type="pdfa-2",  # стандарт PDF/A
    skip_text=True,        # не трогать страницы с текстом
)

# CLI
# ocrmypdf --language rus+eng --deskew --clean input.pdf output.pdf
```

---

## pyHanko {#pyhanko}
**Версия:** 0.34.1 | **Лицензия:** MIT
**Роль:** Цифровые подписи PDF (PAdES).

```python
from pyhanko.sign import signers, fields
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

# Создание подписи с PKCS#12
signer = signers.SimpleSigner.load_pkcs12(
    pfx_file='certificate.p12',
    passphrase=b'password'
)

with open('input.pdf', 'rb') as f:
    w = IncrementalPdfFileWriter(f)
    fields.append_signature_field(w, sig_field_spec=fields.SigFieldSpec(
        sig_field_name='Signature1',
        box=(100, 100, 300, 200)
    ))
    out = signers.sign_pdf(w, signers.PdfSignatureMetadata(
        field_name='Signature1'
    ), signer=signer)
    with open('signed.pdf', 'wb') as out_f:
        out_f.write(out.getvalue())
```

---

## python-pptx {#python-pptx}
**Версия:** 1.0.2 | **Лицензия:** MIT
**Роль:** Создание, чтение, модификация PowerPoint PPTX.

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# Создание презентации
prs = Presentation()
prs.slide_width = Inches(13.33)  # 16:9
prs.slide_height = Inches(7.5)

# Титульный слайд
slide_layout = prs.slide_layouts[0]  # Title Slide
slide = prs.slides.add_slide(slide_layout)
slide.shapes.title.text = "Туры по ОАЭ 2026"
slide.placeholders[1].text = "VIP DXB RUS"

# Контентный слайд
slide_layout = prs.slide_layouts[1]  # Title and Content
slide = prs.slides.add_slide(slide_layout)
slide.shapes.title.text = "Наши услуги"
body = slide.placeholders[1]
tf = body.text_frame
tf.text = "Desert Safari — от 250 AED"
p = tf.add_paragraph()
p.text = "Dhow Cruise — от 180 AED"
p.level = 1

# Таблица
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank
table = slide.shapes.add_table(3, 4, Inches(1), Inches(1.5),
                                Inches(8), Inches(3)).table
table.cell(0, 0).text = "Услуга"
table.cell(0, 1).text = "Взрослый"
table.cell(0, 2).text = "Ребёнок"
table.cell(0, 3).text = "Группа"

# Изображение
slide.shapes.add_picture("photo.jpg", Inches(1), Inches(1),
                          width=Inches(4))

# Чтение существующего PPTX
prs = Presentation("existing.pptx")
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            print(shape.text_frame.text)

prs.save("output.pptx")
```

### PPTX → PDF конвертация
```python
# Вариант 1: LibreOffice headless (лучшее качество)
import subprocess
subprocess.run([
    'libreoffice', '--headless', '--convert-to', 'pdf',
    '--outdir', 'D:/Downloads/', 'presentation.pptx'
])

# Вариант 2: python-pptx → изображения → img2pdf
from pptx import Presentation
from PIL import Image
import img2pdf, io

# Нужен LibreOffice или другой рендерер для точного результата
```

---

## pdf2docx {#pdf2docx}
**Версия:** 0.5.12 | **Лицензия:** GPL-3.0

```python
from pdf2docx import Converter

cv = Converter("input.pdf")
cv.convert("output.docx")  # весь документ
cv.close()

# Выборочные страницы
cv = Converter("input.pdf")
cv.convert("output.docx", start=0, end=5)
cv.close()
```

---

## img2pdf {#img2pdf}
**Версия:** 0.6.3 | **Лицензия:** LGPL-3.0
**Роль:** Конвертация изображений в PDF БЕЗ перекодировки (lossless).

```python
import img2pdf
from pathlib import Path

# Одно изображение
with open("output.pdf", "wb") as f:
    f.write(img2pdf.convert("photo.jpg"))

# Несколько изображений
images = sorted(Path("scans/").glob("*.jpg"))
with open("combined.pdf", "wb") as f:
    f.write(img2pdf.convert([str(img) for img in images]))

# С настройками размера страницы
a4 = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
layout = img2pdf.get_layout_fun(a4)
with open("output.pdf", "wb") as f:
    f.write(img2pdf.convert("photo.jpg", layout_fun=layout))
```

---

## Бенчмарки производительности

### Извлечение текста (14 тестовых PDF)

| Библиотека | Среднее время | Относительно |
|---|---|---|
| **PyMuPDF** | ~0.1 с | 1× (базовая линия) |
| **pypdfium2** | ~0.1 с | ~1× |
| **pypdf** | ~0.5 с | ~5× медленнее |
| **pdfminer.six** | ~0.8 с | ~8× медленнее |
| **pdfplumber** | ~1.0 с | ~10× медленнее |

### Рекомендации по производительности
- <50 страниц: любая библиотека подходит
- 50-500 страниц: PyMuPDF или pypdfium2
- 500+ страниц: только PyMuPDF с инкрементальной обработкой
- Пакетная обработка: multiprocessing.Pool по ядрам CPU
