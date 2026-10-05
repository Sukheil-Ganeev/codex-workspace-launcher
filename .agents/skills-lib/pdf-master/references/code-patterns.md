# Готовые рецепты и шаблоны

Копируй и адаптируй эти рецепты для типовых задач.

## Содержание
1. [Инвойс для туристического бизнеса](#инвойс)
2. [Прайс-лист экскурсий](#прайс-лист)
3. [Сертификат/ваучер](#сертификат)
4. [Парсинг прайса поставщика](#парсинг-прайса)
5. [Пакетная обработка PDF](#пакетная-обработка)
6. [PDF-отчёт с графиками](#отчёт-с-графиками)
7. [Каталог продуктов](#каталог)
8. [Презентация туров (PPTX)](#презентация)
9. [OCR квитанции/чека](#ocr-чека)
10. [Слияние документов клиента](#слияние-документов)

---

## Инвойс для туристического бизнеса {#инвойс}

Полный инвойс с логотипом, реквизитами, таблицей услуг и QR-кодом.

```python
from fpdf import FPDF
from datetime import date

class TourismInvoice(FPDF):
    def header(self):
        # Логотип
        if hasattr(self, 'logo_path'):
            self.image(self.logo_path, 10, 8, 33)
        self.set_font('DejaVu', 'B', 20)
        self.cell(0, 10, 'INVOICE', align='R', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self):
        self.set_y(-30)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 5, 'VIP DXB RUS | Dubai, Tecom | +971-XX-XXX-XXXX', align='C', new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f'Page {self.page_no()}', align='C')

def create_invoice(invoice_data, output_path):
    pdf = TourismInvoice()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
    pdf.add_page()

    # Номер и дата
    pdf.set_font('DejaVu', '', 11)
    pdf.cell(0, 6, f"Invoice #: {invoice_data['number']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Date: {invoice_data['date']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Client: {invoice_data['client']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # Таблица
    pdf.set_font('DejaVu', 'B', 10)
    col_widths = [80, 25, 35, 40]
    headers = ['Service', 'Qty', 'Price (AED)', 'Total (AED)']
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, h, border=1, align='C')
    pdf.ln()

    pdf.set_font('DejaVu', '', 10)
    total = 0
    for item in invoice_data['items']:
        subtotal = item['qty'] * item['price']
        total += subtotal
        pdf.cell(col_widths[0], 8, item['name'], border=1)
        pdf.cell(col_widths[1], 8, str(item['qty']), border=1, align='C')
        pdf.cell(col_widths[2], 8, f"{item['price']:,.0f}", border=1, align='R')
        pdf.cell(col_widths[3], 8, f"{subtotal:,.0f}", border=1, align='R')
        pdf.ln()

    # Итого
    pdf.set_font('DejaVu', 'B', 11)
    pdf.cell(sum(col_widths[:3]), 10, 'TOTAL:', border=1, align='R')
    pdf.cell(col_widths[3], 10, f"{total:,.0f} AED", border=1, align='R')

    # Реквизиты
    pdf.ln(15)
    pdf.set_font('DejaVu', '', 9)
    pdf.multi_cell(0, 5, text=invoice_data.get('payment_details',
        "Payment: AED/USD cash, bank transfer (AED/KZT/RUB), crypto USDT"))

    pdf.output(output_path)
    return output_path

# Использование:
invoice = {
    "number": "2026-0316-001",
    "date": "16.03.2026",
    "client": "Иванов Иван Иванович",
    "items": [
        {"name": "Desert Safari Premium (4 pax)", "qty": 4, "price": 350},
        {"name": "Abu Dhabi City Tour (4 pax)", "qty": 4, "price": 280},
        {"name": "Dhow Cruise Dubai Marina (2 pax)", "qty": 2, "price": 220},
    ]
}
create_invoice(invoice, "D:/Downloads/invoice_2026-0316.pdf")
```

---

## Прайс-лист экскурсий {#прайс-лист}

```python
from fpdf import FPDF

def create_pricelist(tours, output_path, title="Прайс-лист экскурсий 2026"):
    pdf = FPDF()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
    pdf.add_page()

    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 10, title, align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Заголовок таблицы
    pdf.set_font('DejaVu', 'B', 9)
    pdf.set_fill_color(26, 35, 126)  # тёмно-синий
    pdf.set_text_color(255, 255, 255)
    cols = [('Название', 70), ('Описание', 50), ('Взрослый', 25),
            ('Ребёнок', 25), ('Длительность', 20)]
    for name, w in cols:
        pdf.cell(w, 8, name, border=1, fill=True, align='C')
    pdf.ln()

    # Данные
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('DejaVu', '', 8)
    for i, tour in enumerate(tours):
        fill = i % 2 == 0
        if fill:
            pdf.set_fill_color(232, 234, 246)
        pdf.cell(70, 7, tour['name'], border=1, fill=fill)
        pdf.cell(50, 7, tour.get('desc', ''), border=1, fill=fill)
        pdf.cell(25, 7, f"{tour['adult']} AED", border=1, align='C', fill=fill)
        pdf.cell(25, 7, f"{tour.get('child', 'N/A')} AED" if tour.get('child') else 'FREE',
                 border=1, align='C', fill=fill)
        pdf.cell(20, 7, tour.get('duration', ''), border=1, align='C', fill=fill)
        pdf.ln()

    pdf.output(output_path)

# Использование:
tours = [
    {"name": "Desert Safari Premium", "desc": "BBQ, shows, camel", "adult": 350, "child": 280, "duration": "6h"},
    {"name": "Abu Dhabi City Tour", "desc": "Mosque, Palace, Louvre", "adult": 280, "child": 220, "duration": "10h"},
    {"name": "Dubai City Tour", "desc": "Old & New Dubai", "adult": 180, "child": 140, "duration": "5h"},
]
create_pricelist(tours, "D:/Downloads/pricelist_2026.pdf")
```

---

## Парсинг прайса поставщика {#парсинг-прайса}

Извлечение таблиц из PDF-прайса поставщика в Excel.

```python
import pdfplumber
import pandas as pd
from pathlib import Path

def parse_supplier_price(pdf_path, output_path=None):
    """Извлекает все таблицы из PDF в Excel"""
    if output_path is None:
        output_path = Path(pdf_path).with_suffix('.xlsx')

    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables({
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "snap_tolerance": 5,
            })

            for table_idx, table in enumerate(tables):
                if len(table) < 2:
                    continue

                # Первая строка — заголовки
                headers = [str(h).strip() if h else f"col_{i}"
                          for i, h in enumerate(table[0])]
                df = pd.DataFrame(table[1:], columns=headers)
                df['_page'] = page_num
                df['_table'] = table_idx + 1
                all_tables.append(df)

    if all_tables:
        combined = pd.concat(all_tables, ignore_index=True)
        combined.to_excel(str(output_path), index=False)
        print(f"Извлечено {len(combined)} строк → {output_path}")
        return combined
    else:
        print("Таблицы не найдены")
        return None

# Использование:
df = parse_supplier_price("D:/Downloads/supplier_pricelist.pdf")
```

---

## Пакетная обработка PDF {#пакетная-обработка}

```python
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import fitz

def extract_text_from_pdf(pdf_path):
    """Извлекает текст из одного PDF"""
    try:
        doc = fitz.open(str(pdf_path))
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return str(pdf_path), text
    except Exception as e:
        return str(pdf_path), f"ОШИБКА: {e}"

def batch_extract(folder, pattern="*.pdf", max_workers=4):
    """Параллельное извлечение текста из всех PDF в папке"""
    pdfs = list(Path(folder).glob(pattern))
    print(f"Найдено {len(pdfs)} PDF файлов")

    results = {}
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for path, text in executor.map(extract_text_from_pdf, pdfs):
            results[path] = text

    return results

# Использование:
texts = batch_extract("D:/Downloads/pdfs/")
for path, text in texts.items():
    print(f"{path}: {len(text)} символов")
```

---

## Презентация туров (PPTX) {#презентация}

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_tour_presentation(tours, output_path, company="VIP DXB RUS"):
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    # Титульный слайд
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = f"Каталог туров {company}"
    slide.placeholders[1].text = "Лучшие цены на экскурсии по ОАЭ"

    # Слайды для каждого тура
    for tour in tours:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = tour['name']

        body = slide.placeholders[1].text_frame
        body.text = tour['description']

        p = body.add_paragraph()
        p.text = f"Цена: {tour['price']} AED / чел."
        p.font.bold = True
        p.font.size = Pt(18)

        p = body.add_paragraph()
        p.text = f"Длительность: {tour['duration']}"

        if tour.get('image'):
            slide.shapes.add_picture(tour['image'],
                                      Inches(7), Inches(1.5),
                                      width=Inches(5))

    prs.save(output_path)

# Использование:
tours = [
    {"name": "Desert Safari Premium", "description": "Незабываемое приключение в пустыне...",
     "price": 350, "duration": "6 часов", "image": None},
]
create_tour_presentation(tours, "D:/Downloads/tours_catalog.pptx")
```

---

## OCR квитанции/чека {#ocr-чека}

```python
import ocrmypdf
import fitz
import json

def ocr_receipt(input_path, output_path=None):
    """OCR квитанции с извлечением текста"""
    if output_path is None:
        output_path = input_path.replace('.pdf', '_ocr.pdf')

    # OCR
    ocrmypdf.ocr(input_path, output_path,
                  language="rus+eng",
                  deskew=True, clean=True)

    # Извлечение текста из OCR-результата
    doc = fitz.open(output_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    return text

# Если ocrmypdf недоступен (нет Ghostscript):
def ocr_receipt_fallback(image_path):
    """Fallback: Tesseract напрямую"""
    import subprocess
    result = subprocess.run(
        ['tesseract', image_path, 'stdout', '-l', 'rus+eng'],
        capture_output=True, text=True
    )
    return result.stdout
```

---

## Слияние документов клиента {#слияние-документов}

```python
from pypdf import PdfMerger
from pathlib import Path

def merge_client_docs(client_folder, output_path=None):
    """Собирает все PDF клиента в один файл"""
    folder = Path(client_folder)
    pdfs = sorted(folder.glob("*.pdf"))

    if not pdfs:
        print(f"PDF не найдены в {folder}")
        return None

    if output_path is None:
        output_path = folder / f"{folder.name}_combined.pdf"

    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(str(pdf))
        merger.add_outline_item(pdf.stem, len(merger.pages) - 1)

    merger.write(str(output_path))
    merger.close()
    print(f"Объединено {len(pdfs)} файлов → {output_path}")
    return output_path

# Использование:
merge_client_docs("D:/Downloads/client_docs/ivanov/")
```
