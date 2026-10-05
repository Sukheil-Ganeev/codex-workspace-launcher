#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор PDF инвойсов для туристического бизнеса в ОАЭ.

Функции:
- Автоматическая нумерация (INV-2026-0001)
- Шаблоны: стандартный, проформа, квитанция, кредит-нота
- Брендинг: логотип, цвета, QR-код
- Форматы: PDF, HTML, JSON
- Интеграции: операции.json, email, Bitrix24
"""

import os
import sys
import json
import argparse
import hashlib
import base64
import smtplib
from io import BytesIO
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, List, Optional, Any, Union

sys.stdout.reconfigure(encoding='utf-8')

# Попытка импорта reportlab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image, PageBreak, HRFlowable
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ПРЕДУПРЕЖДЕНИЕ: reportlab не установлен. PDF генерация недоступна.")
    print("Установите: pip install reportlab")

# Попытка импорта qrcode
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Пути
CHATS_DIR = Path("D:/Downloads/Chats")
INVOICES_DIR = CHATS_DIR / "_инвойсы"
REGISTRY_FILE = INVOICES_DIR / "invoice_registry.json"
OPERATIONS_FILE = CHATS_DIR / "_база" / "операции.json"
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Настройки email (из переменных окружения)
EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("SMTP_USERNAME", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
    "from_email": os.getenv("SMTP_FROM_EMAIL", ""),
    "from_name": os.getenv("SMTP_FROM_NAME", "Marsel Luxury Car Rental"),
}

# Bitrix24 (из config.py)
BITRIX24_CONFIG = {
    "domain": os.getenv("BITRIX24_DOMAIN", ""),
    "user_id": os.getenv("BITRIX24_USER_ID", ""),
    "webhook_key": os.getenv("BITRIX24_WEBHOOK_KEY", ""),
}


# ═══════════════════════════════════════════════════════════════
# ДАННЫЕ КОМПАНИИ
# ═══════════════════════════════════════════════════════════════

COMPANY_PROFILES = {
    "marsel": {
        "name": "Marsel Luxury Car Rental LLC",
        "name_short": "Marsel Luxury",
        "legal_name": "MARSEL LUXURY CAR RENTAL L.L.C",
        "address": [
            "Office 1205, The Metropolis Tower",
            "Business Bay, Dubai, UAE"
        ],
        "phone": "+971 50 770 5321",
        "email": "info@marselluxury.ae",
        "website": "www.marselluxury.ae",
        "trn": "123456789012345",  # Tax Registration Number
        "license": "CN-1234567",
        "bank": {
            "name": "Emirates NBD",
            "account": "AE12 0260 0010 1234 5678 901",
            "swift": "EABOREANXXX",
            "branch": "Business Bay Branch"
        },
        "colors": {
            "primary": "#1a1a2e",      # Тёмно-синий
            "secondary": "#c9a227",    # Золотой
            "accent": "#16213e",       # Синий
            "text": "#333333",
            "light": "#f5f5f5"
        },
        "logo_path": None,  # Путь к логотипу (если есть)
    },
    "sokol": {
        "name": "Sokol Car Rental LLC",
        "name_short": "Sokol Rental",
        "legal_name": "SOKOL CAR RENTAL L.L.C",
        "address": [
            "Office 502, Al Barsha Business Center",
            "Al Barsha 1, Dubai, UAE"
        ],
        "phone": "+971 55 123 4567",
        "email": "info@sokolrental.ae",
        "website": "www.sokolrental.ae",
        "trn": "987654321098765",
        "license": "CN-7654321",
        "bank": {
            "name": "Mashreq Bank",
            "account": "AE87 0330 0000 1234 5678 901",
            "swift": "BOMLAEAD",
            "branch": "Al Barsha Branch"
        },
        "colors": {
            "primary": "#2c3e50",
            "secondary": "#e74c3c",
            "accent": "#3498db",
            "text": "#333333",
            "light": "#ecf0f1"
        },
        "logo_path": None,
    }
}

# Компания по умолчанию
DEFAULT_COMPANY = "marsel"


# ═══════════════════════════════════════════════════════════════
# ШАБЛОНЫ ИНВОЙСОВ
# ═══════════════════════════════════════════════════════════════

INVOICE_TEMPLATES = {
    "invoice": {
        "title": "TAX INVOICE",
        "title_ru": "СЧЁТ-ФАКТУРА",
        "prefix": "INV",
        "description": "Стандартный счёт на оплату",
        "show_vat": True,
        "show_payment_info": True,
        "is_paid": False,
    },
    "proforma": {
        "title": "PROFORMA INVOICE",
        "title_ru": "ПРОФОРМА-ИНВОЙС",
        "prefix": "PRO",
        "description": "Предварительный счёт (не для оплаты налогов)",
        "show_vat": False,
        "show_payment_info": True,
        "is_paid": False,
        "watermark": "PROFORMA - NOT A TAX INVOICE",
    },
    "receipt": {
        "title": "PAYMENT RECEIPT",
        "title_ru": "КВИТАНЦИЯ ОБ ОПЛАТЕ",
        "prefix": "REC",
        "description": "Подтверждение получения оплаты",
        "show_vat": True,
        "show_payment_info": False,
        "is_paid": True,
        "paid_stamp": True,
    },
    "credit_note": {
        "title": "CREDIT NOTE",
        "title_ru": "КРЕДИТ-НОТА",
        "prefix": "CRN",
        "description": "Возврат средств / корректировка",
        "show_vat": True,
        "show_payment_info": False,
        "is_paid": False,
        "is_refund": True,
    }
}


# ═══════════════════════════════════════════════════════════════
# ТИПЫ УСЛУГ
# ═══════════════════════════════════════════════════════════════

SERVICE_TYPES = {
    "tour": {"name": "Tour / Excursion", "name_ru": "Тур / Экскурсия", "unit": "pax"},
    "transfer": {"name": "Transfer", "name_ru": "Трансфер", "unit": "trip"},
    "yacht": {"name": "Yacht Charter", "name_ru": "Аренда яхты", "unit": "hour"},
    "car_rental": {"name": "Car Rental", "name_ru": "Аренда авто", "unit": "day"},
    "tickets": {"name": "Tickets / Admission", "name_ru": "Билеты / Вход", "unit": "pax"},
    "catering": {"name": "Catering", "name_ru": "Кейтеринг", "unit": "pax"},
    "guide": {"name": "Guide Service", "name_ru": "Услуги гида", "unit": "hour"},
    "visa": {"name": "Visa Service", "name_ru": "Визовые услуги", "unit": "pax"},
    "hotel": {"name": "Hotel Accommodation", "name_ru": "Проживание в отеле", "unit": "night"},
    "other": {"name": "Other Services", "name_ru": "Прочие услуги", "unit": "pcs"},
}

# Ставка НДС в ОАЭ
UAE_VAT_RATE = Decimal("0.05")  # 5%


# ═══════════════════════════════════════════════════════════════
# КЛАСС ИНВОЙСА
# ═══════════════════════════════════════════════════════════════

class Invoice:
    """Класс для создания и управления инвойсами."""

    def __init__(
        self,
        template: str = "invoice",
        company: str = DEFAULT_COMPANY,
        client: Optional[Dict] = None,
        items: Optional[List[Dict]] = None,
        currency: str = "AED",
        include_vat: bool = True,
        notes: str = "",
        due_days: int = 7,
        language: str = "en",  # en или ru
    ):
        self.template = INVOICE_TEMPLATES.get(template, INVOICE_TEMPLATES["invoice"])
        self.template_key = template
        self.company = COMPANY_PROFILES.get(company, COMPANY_PROFILES[DEFAULT_COMPANY])
        self.company_key = company

        # Данные клиента
        self.client = client or {
            "name": "",
            "company": "",
            "address": "",
            "phone": "",
            "email": "",
            "trn": "",  # TRN клиента (если есть)
        }

        # Позиции инвойса
        self.items = items or []

        # Настройки
        self.currency = currency
        self.include_vat = include_vat and self.template.get("show_vat", True)
        self.notes = notes
        self.due_days = due_days
        self.language = language

        # Даты
        self.invoice_date = datetime.now()
        self.due_date = self.invoice_date + timedelta(days=due_days)

        # Номер инвойса (генерируется при сохранении)
        self.invoice_number = None

        # Расчётные поля
        self._calculate_totals()

    def _calculate_totals(self):
        """Расчёт итогов."""
        self.subtotal = Decimal("0")

        for item in self.items:
            qty = Decimal(str(item.get("quantity", 1)))
            price = Decimal(str(item.get("unit_price", 0)))
            item_total = (qty * price).quantize(Decimal("0.01"), ROUND_HALF_UP)
            item["total"] = float(item_total)
            self.subtotal += item_total

        # НДС
        if self.include_vat:
            self.vat_amount = (self.subtotal * UAE_VAT_RATE).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )
        else:
            self.vat_amount = Decimal("0")

        # Итого
        self.total = self.subtotal + self.vat_amount

        # Для кредит-ноты - отрицательные суммы
        if self.template.get("is_refund"):
            self.subtotal = -self.subtotal
            self.vat_amount = -self.vat_amount
            self.total = -self.total

    def add_item(
        self,
        description: str,
        quantity: float = 1,
        unit_price: float = 0,
        service_type: str = "other",
        date: Optional[str] = None,
        details: str = "",
    ):
        """Добавить позицию в инвойс."""
        service = SERVICE_TYPES.get(service_type, SERVICE_TYPES["other"])

        item = {
            "description": description,
            "quantity": quantity,
            "unit": service["unit"],
            "unit_price": unit_price,
            "service_type": service_type,
            "service_name": service["name"] if self.language == "en" else service["name_ru"],
            "date": date or self.invoice_date.strftime("%d.%m.%Y"),
            "details": details,
        }

        self.items.append(item)
        self._calculate_totals()

    def generate_number(self) -> str:
        """Генерация номера инвойса."""
        registry = load_registry()

        # Формат: PRE-YYYY-NNNN
        prefix = self.template["prefix"]
        year = self.invoice_date.year

        # Находим последний номер для этого префикса и года
        pattern = f"{prefix}-{year}-"
        existing = [
            inv["number"] for inv in registry.get("invoices", [])
            if inv["number"].startswith(pattern)
        ]

        if existing:
            last_num = max(int(n.split("-")[-1]) for n in existing)
            next_num = last_num + 1
        else:
            next_num = 1

        self.invoice_number = f"{prefix}-{year}-{next_num:04d}"
        return self.invoice_number

    def to_dict(self) -> Dict:
        """Конвертация в словарь."""
        return {
            "number": self.invoice_number,
            "template": self.template_key,
            "company": self.company_key,
            "company_name": self.company["name"],
            "client": self.client,
            "items": self.items,
            "currency": self.currency,
            "subtotal": float(self.subtotal),
            "vat_rate": float(UAE_VAT_RATE) if self.include_vat else 0,
            "vat_amount": float(self.vat_amount),
            "total": float(self.total),
            "include_vat": self.include_vat,
            "notes": self.notes,
            "invoice_date": self.invoice_date.isoformat(),
            "due_date": self.due_date.isoformat(),
            "language": self.language,
            "created_at": datetime.now().isoformat(),
        }

    def to_json(self) -> str:
        """Экспорт в JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_html(self) -> str:
        """Экспорт в HTML для email."""
        return generate_html_invoice(self)


# ═══════════════════════════════════════════════════════════════
# РЕЕСТР ИНВОЙСОВ
# ═══════════════════════════════════════════════════════════════

def ensure_directories():
    """Создание необходимых директорий."""
    INVOICES_DIR.mkdir(parents=True, exist_ok=True)
    (INVOICES_DIR / "pdf").mkdir(exist_ok=True)
    (INVOICES_DIR / "html").mkdir(exist_ok=True)
    (INVOICES_DIR / "json").mkdir(exist_ok=True)


def load_registry() -> Dict:
    """Загрузка реестра инвойсов."""
    ensure_directories()

    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "created_at": datetime.now().isoformat(),
        "invoices": [],
        "stats": {
            "total_count": 0,
            "total_amount_aed": 0,
            "total_amount_usd": 0,
            "by_template": {},
            "by_company": {},
        }
    }


def save_registry(registry: Dict):
    """Сохранение реестра инвойсов."""
    ensure_directories()

    registry["updated_at"] = datetime.now().isoformat()

    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)


def register_invoice(invoice: Invoice, pdf_path: str = "", html_path: str = ""):
    """Регистрация инвойса в реестре."""
    registry = load_registry()

    record = {
        **invoice.to_dict(),
        "pdf_path": pdf_path,
        "html_path": html_path,
        "status": "paid" if invoice.template.get("is_paid") else "pending",
    }

    registry["invoices"].append(record)

    # Обновление статистики
    stats = registry["stats"]
    stats["total_count"] += 1

    if invoice.currency == "AED":
        stats["total_amount_aed"] += float(invoice.total)
    elif invoice.currency == "USD":
        stats["total_amount_usd"] += float(invoice.total)

    # По шаблонам
    tpl = invoice.template_key
    stats["by_template"][tpl] = stats["by_template"].get(tpl, 0) + 1

    # По компаниям
    comp = invoice.company_key
    stats["by_company"][comp] = stats["by_company"].get(comp, 0) + 1

    save_registry(registry)

    return record


def get_invoice_by_number(number: str) -> Optional[Dict]:
    """Поиск инвойса по номеру."""
    registry = load_registry()

    for inv in registry.get("invoices", []):
        if inv["number"] == number:
            return inv

    return None


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ PDF (REPORTLAB)
# ═══════════════════════════════════════════════════════════════

def generate_pdf_invoice(invoice: Invoice, output_path: Optional[str] = None) -> str:
    """Генерация PDF инвойса с помощью reportlab."""

    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab не установлен. Установите: pip install reportlab")

    ensure_directories()

    # Генерируем номер если нет
    if not invoice.invoice_number:
        invoice.generate_number()

    # Путь к файлу
    if not output_path:
        filename = f"{invoice.invoice_number}.pdf"
        output_path = str(INVOICES_DIR / "pdf" / filename)

    # Создаём документ
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=20*mm,
    )

    # Стили
    styles = getSampleStyleSheet()
    company_colors = invoice.company["colors"]

    # Кастомные стили
    style_title = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(company_colors["primary"]),
        alignment=TA_CENTER,
        spaceAfter=10,
    )

    style_subtitle = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor(company_colors["text"]),
        alignment=TA_CENTER,
    )

    style_company = ParagraphStyle(
        'CompanyName',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(company_colors["primary"]),
        spaceAfter=5,
    )

    style_normal = ParagraphStyle(
        'InvoiceNormal',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor(company_colors["text"]),
    )

    style_bold = ParagraphStyle(
        'InvoiceBold',
        parent=style_normal,
        fontName='Helvetica-Bold',
    )

    style_small = ParagraphStyle(
        'InvoiceSmall',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
    )

    style_amount = ParagraphStyle(
        'InvoiceAmount',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor(company_colors["primary"]),
        alignment=TA_RIGHT,
    )

    # Элементы документа
    elements = []

    # === ШАПКА ===

    # Название компании
    elements.append(Paragraph(invoice.company["name"], style_company))
    elements.append(Spacer(1, 3*mm))

    # Адрес компании
    for line in invoice.company["address"]:
        elements.append(Paragraph(line, style_normal))

    elements.append(Paragraph(f"Tel: {invoice.company['phone']}", style_normal))
    elements.append(Paragraph(f"Email: {invoice.company['email']}", style_normal))
    elements.append(Paragraph(f"TRN: {invoice.company['trn']}", style_normal))

    elements.append(Spacer(1, 8*mm))

    # Заголовок инвойса
    title = invoice.template["title"]
    if invoice.language == "ru":
        title = f"{title} / {invoice.template['title_ru']}"

    elements.append(Paragraph(title, style_title))

    # Watermark для проформы
    if invoice.template.get("watermark"):
        elements.append(Paragraph(
            f"<i>{invoice.template['watermark']}</i>",
            style_subtitle
        ))

    elements.append(Spacer(1, 5*mm))

    # Линия-разделитель
    elements.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor(company_colors["secondary"]),
    ))

    elements.append(Spacer(1, 5*mm))

    # === ИНФОРМАЦИЯ ОБ ИНВОЙСЕ И КЛИЕНТЕ ===

    # Левая колонка: данные инвойса
    invoice_info = [
        [Paragraph("<b>Invoice No:</b>", style_normal),
         Paragraph(invoice.invoice_number, style_normal)],
        [Paragraph("<b>Date:</b>", style_normal),
         Paragraph(invoice.invoice_date.strftime("%d %B %Y"), style_normal)],
    ]

    if invoice.template.get("show_payment_info"):
        invoice_info.append([
            Paragraph("<b>Due Date:</b>", style_normal),
            Paragraph(invoice.due_date.strftime("%d %B %Y"), style_normal)
        ])

    # Правая колонка: данные клиента
    client_info = [
        [Paragraph("<b>Bill To:</b>", style_normal), Paragraph("", style_normal)],
    ]

    if invoice.client.get("company"):
        client_info.append([
            Paragraph(invoice.client["company"], style_bold),
            Paragraph("", style_normal)
        ])

    if invoice.client.get("name"):
        client_info.append([
            Paragraph(invoice.client["name"], style_normal),
            Paragraph("", style_normal)
        ])

    if invoice.client.get("address"):
        client_info.append([
            Paragraph(invoice.client["address"], style_normal),
            Paragraph("", style_normal)
        ])

    if invoice.client.get("phone"):
        client_info.append([
            Paragraph(f"Tel: {invoice.client['phone']}", style_normal),
            Paragraph("", style_normal)
        ])

    if invoice.client.get("email"):
        client_info.append([
            Paragraph(f"Email: {invoice.client['email']}", style_normal),
            Paragraph("", style_normal)
        ])

    if invoice.client.get("trn"):
        client_info.append([
            Paragraph(f"TRN: {invoice.client['trn']}", style_normal),
            Paragraph("", style_normal)
        ])

    # Объединяем в две колонки
    max_rows = max(len(invoice_info), len(client_info))
    while len(invoice_info) < max_rows:
        invoice_info.append(["", ""])
    while len(client_info) < max_rows:
        client_info.append(["", ""])

    header_data = []
    for i in range(max_rows):
        row = list(invoice_info[i]) + [""] + list(client_info[i])
        header_data.append(row)

    header_table = Table(header_data, colWidths=[30*mm, 40*mm, 15*mm, 30*mm, 60*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    # === ТАБЛИЦА УСЛУГ ===

    # Заголовок таблицы
    table_header = [
        Paragraph("<b>#</b>", style_normal),
        Paragraph("<b>Description</b>", style_normal),
        Paragraph("<b>Date</b>", style_normal),
        Paragraph("<b>Qty</b>", style_normal),
        Paragraph("<b>Unit Price</b>", style_normal),
        Paragraph("<b>Total</b>", style_normal),
    ]

    table_data = [table_header]

    # Позиции
    for idx, item in enumerate(invoice.items, 1):
        row = [
            Paragraph(str(idx), style_normal),
            Paragraph(f"{item['description']}<br/><font size=7 color='gray'>{item.get('details', '')}</font>", style_normal),
            Paragraph(item.get("date", ""), style_normal),
            Paragraph(f"{item['quantity']} {item['unit']}", style_normal),
            Paragraph(f"{item['unit_price']:,.2f} {invoice.currency}", style_normal),
            Paragraph(f"{item['total']:,.2f} {invoice.currency}", style_normal),
        ]
        table_data.append(row)

    items_table = Table(
        table_data,
        colWidths=[10*mm, 75*mm, 25*mm, 20*mm, 25*mm, 25*mm]
    )

    items_table.setStyle(TableStyle([
        # Заголовок
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(company_colors["primary"])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),

        # Данные
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),

        # Выравнивание
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Границы
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),

        # Чередование цвета строк
        *[('BACKGROUND', (0, i), (-1, i), colors.HexColor("#f9f9f9"))
          for i in range(2, len(table_data), 2)],
    ]))

    elements.append(items_table)
    elements.append(Spacer(1, 5*mm))

    # === ИТОГИ ===

    totals_data = [
        [
            Paragraph("<b>Subtotal:</b>", style_normal),
            Paragraph(f"{abs(float(invoice.subtotal)):,.2f} {invoice.currency}", style_amount)
        ],
    ]

    if invoice.include_vat:
        totals_data.append([
            Paragraph(f"<b>VAT ({float(UAE_VAT_RATE)*100:.0f}%):</b>", style_normal),
            Paragraph(f"{abs(float(invoice.vat_amount)):,.2f} {invoice.currency}", style_amount)
        ])

    totals_data.append([
        Paragraph("<b>TOTAL:</b>", style_bold),
        Paragraph(f"<b>{abs(float(invoice.total)):,.2f} {invoice.currency}</b>", style_amount)
    ])

    # Если это возврат
    if invoice.template.get("is_refund"):
        totals_data.append([
            Paragraph("<font color='red'><b>CREDIT AMOUNT:</b></font>", style_normal),
            Paragraph(f"<font color='red'><b>({abs(float(invoice.total)):,.2f}) {invoice.currency}</b></font>", style_amount)
        ])

    totals_table = Table(totals_data, colWidths=[130*mm, 50*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor(company_colors["secondary"])),
    ]))

    elements.append(totals_table)
    elements.append(Spacer(1, 8*mm))

    # === ШТАМП "ОПЛАЧЕНО" ===

    if invoice.template.get("paid_stamp"):
        paid_style = ParagraphStyle(
            'PaidStamp',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=colors.HexColor("#28a745"),
            alignment=TA_CENTER,
        )
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("PAID", paid_style))
        elements.append(Paragraph(
            f"Payment received on {invoice.invoice_date.strftime('%d %B %Y')}",
            style_subtitle
        ))
        elements.append(Spacer(1, 5*mm))

    # === ПЛАТЁЖНАЯ ИНФОРМАЦИЯ ===

    if invoice.template.get("show_payment_info"):
        elements.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#dddddd"),
        ))
        elements.append(Spacer(1, 5*mm))

        elements.append(Paragraph("<b>Payment Information:</b>", style_bold))
        elements.append(Spacer(1, 3*mm))

        bank = invoice.company["bank"]
        bank_info = f"""
        Bank: {bank['name']}<br/>
        Account: {bank['account']}<br/>
        SWIFT: {bank['swift']}<br/>
        Branch: {bank['branch']}<br/>
        Beneficiary: {invoice.company['legal_name']}
        """
        elements.append(Paragraph(bank_info, style_normal))

        elements.append(Spacer(1, 5*mm))

        # QR-код для оплаты
        if QRCODE_AVAILABLE:
            qr_data = f"Payment for {invoice.invoice_number}\nAmount: {invoice.total} {invoice.currency}\nBank: {bank['name']}\nAccount: {bank['account']}"

            qr = qrcode.QRCode(version=1, box_size=4, border=2)
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Конвертируем в байты
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)

            # Добавляем на страницу
            qr_image = Image(qr_buffer, width=25*mm, height=25*mm)

            qr_table = Table([
                [qr_image, Paragraph("<font size=8>Scan QR code for payment details</font>", style_small)]
            ], colWidths=[30*mm, 100*mm])

            qr_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(qr_table)

    # === ПРИМЕЧАНИЯ ===

    if invoice.notes:
        elements.append(Spacer(1, 5*mm))
        elements.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#dddddd"),
        ))
        elements.append(Spacer(1, 3*mm))
        elements.append(Paragraph("<b>Notes:</b>", style_bold))
        elements.append(Paragraph(invoice.notes, style_normal))

    # === ФУТЕР ===

    elements.append(Spacer(1, 10*mm))
    elements.append(HRFlowable(
        width="100%",
        thickness=0.5,
        color=colors.HexColor("#dddddd"),
    ))
    elements.append(Spacer(1, 3*mm))

    footer_text = f"""
    Thank you for your business!<br/>
    {invoice.company['name']} | {invoice.company['phone']} | {invoice.company['email']} | {invoice.company['website']}
    """
    elements.append(Paragraph(footer_text, style_small))

    # Собираем PDF
    doc.build(elements)

    return output_path


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ HTML
# ═══════════════════════════════════════════════════════════════

def generate_html_invoice(invoice: Invoice) -> str:
    """Генерация HTML версии инвойса для email."""

    company = invoice.company
    colors = company["colors"]
    template = invoice.template

    # Заголовок
    title = template["title"]
    if invoice.language == "ru":
        title = f"{title} / {template['title_ru']}"

    # Позиции таблицы
    items_html = ""
    for idx, item in enumerate(invoice.items, 1):
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{idx}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">
                {item['description']}
                {f'<br><small style="color: #888;">{item.get("details", "")}</small>' if item.get("details") else ""}
            </td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item.get("date", "")}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']} {item['unit']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">{item['unit_price']:,.2f} {invoice.currency}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">{item['total']:,.2f} {invoice.currency}</td>
        </tr>
        """

    # Штамп оплаты
    paid_stamp = ""
    if template.get("paid_stamp"):
        paid_stamp = f"""
        <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 48px; color: #28a745; font-weight: bold; border: 3px solid #28a745; padding: 10px 30px; border-radius: 10px;">
                PAID
            </span>
            <p style="color: #28a745; margin-top: 10px;">
                Payment received on {invoice.invoice_date.strftime('%d %B %Y')}
            </p>
        </div>
        """

    # Платёжная информация
    payment_info = ""
    if template.get("show_payment_info"):
        bank = company["bank"]
        payment_info = f"""
        <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <h3 style="margin: 0 0 10px 0; color: {colors['primary']};">Payment Information</h3>
            <table style="font-size: 14px;">
                <tr><td style="padding: 3px 10px 3px 0;"><strong>Bank:</strong></td><td>{bank['name']}</td></tr>
                <tr><td style="padding: 3px 10px 3px 0;"><strong>Account:</strong></td><td>{bank['account']}</td></tr>
                <tr><td style="padding: 3px 10px 3px 0;"><strong>SWIFT:</strong></td><td>{bank['swift']}</td></tr>
                <tr><td style="padding: 3px 10px 3px 0;"><strong>Beneficiary:</strong></td><td>{company['legal_name']}</td></tr>
            </table>
        </div>
        """

    # VAT строка
    vat_row = ""
    if invoice.include_vat:
        vat_row = f"""
        <tr>
            <td style="padding: 8px; text-align: right;"><strong>VAT ({float(UAE_VAT_RATE)*100:.0f}%):</strong></td>
            <td style="padding: 8px; text-align: right;">{abs(float(invoice.vat_amount)):,.2f} {invoice.currency}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title} - {invoice.invoice_number}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: {colors['text']};
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            border-bottom: 2px solid {colors['secondary']};
            padding-bottom: 20px;
            margin-bottom: 20px;
        }}
        .company-name {{
            font-size: 24px;
            font-weight: bold;
            color: {colors['primary']};
            margin-bottom: 5px;
        }}
        .invoice-title {{
            font-size: 28px;
            color: {colors['primary']};
            text-align: center;
            margin: 20px 0;
        }}
        .watermark {{
            text-align: center;
            color: #888;
            font-style: italic;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        .items-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .items-table th {{
            background: {colors['primary']};
            color: white;
            padding: 12px;
            text-align: left;
        }}
        .items-table th:nth-child(4),
        .items-table th:nth-child(5),
        .items-table th:nth-child(6) {{
            text-align: right;
        }}
        .totals {{
            margin-top: 20px;
            text-align: right;
        }}
        .totals table {{
            margin-left: auto;
        }}
        .total-row {{
            font-size: 18px;
            color: {colors['primary']};
            border-top: 2px solid {colors['secondary']};
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #888;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="company-name">{company['name']}</div>
        <div>{', '.join(company['address'])}</div>
        <div>Tel: {company['phone']} | Email: {company['email']}</div>
        <div>TRN: {company['trn']}</div>
    </div>

    <h1 class="invoice-title">{title}</h1>
    {f'<p class="watermark">{template["watermark"]}</p>' if template.get("watermark") else ""}

    <div class="info-grid">
        <div>
            <p><strong>Invoice No:</strong> {invoice.invoice_number}</p>
            <p><strong>Date:</strong> {invoice.invoice_date.strftime('%d %B %Y')}</p>
            {f'<p><strong>Due Date:</strong> {invoice.due_date.strftime("%d %B %Y")}</p>' if template.get("show_payment_info") else ""}
        </div>
        <div>
            <p><strong>Bill To:</strong></p>
            {f'<p><strong>{invoice.client.get("company", "")}</strong></p>' if invoice.client.get("company") else ""}
            <p>{invoice.client.get("name", "")}</p>
            <p>{invoice.client.get("address", "")}</p>
            {f'<p>Tel: {invoice.client.get("phone", "")}</p>' if invoice.client.get("phone") else ""}
            {f'<p>Email: {invoice.client.get("email", "")}</p>' if invoice.client.get("email") else ""}
            {f'<p>TRN: {invoice.client.get("trn", "")}</p>' if invoice.client.get("trn") else ""}
        </div>
    </div>

    <table class="items-table">
        <thead>
            <tr>
                <th>#</th>
                <th>Description</th>
                <th>Date</th>
                <th style="text-align: center;">Qty</th>
                <th style="text-align: right;">Unit Price</th>
                <th style="text-align: right;">Total</th>
            </tr>
        </thead>
        <tbody>
            {items_html}
        </tbody>
    </table>

    <div class="totals">
        <table>
            <tr>
                <td style="padding: 8px; text-align: right;"><strong>Subtotal:</strong></td>
                <td style="padding: 8px; text-align: right;">{abs(float(invoice.subtotal)):,.2f} {invoice.currency}</td>
            </tr>
            {vat_row}
            <tr class="total-row">
                <td style="padding: 8px; text-align: right;"><strong>TOTAL:</strong></td>
                <td style="padding: 8px; text-align: right;"><strong>{abs(float(invoice.total)):,.2f} {invoice.currency}</strong></td>
            </tr>
        </table>
    </div>

    {paid_stamp}

    {payment_info}

    {f'<div style="margin-top: 20px;"><strong>Notes:</strong><br>{invoice.notes}</div>' if invoice.notes else ""}

    <div class="footer">
        <p>Thank you for your business!</p>
        <p>{company['name']} | {company['phone']} | {company['email']} | {company['website']}</p>
    </div>
</body>
</html>
    """

    return html


def save_html_invoice(invoice: Invoice, output_path: Optional[str] = None) -> str:
    """Сохранение HTML инвойса в файл."""

    ensure_directories()

    if not invoice.invoice_number:
        invoice.generate_number()

    if not output_path:
        filename = f"{invoice.invoice_number}.html"
        output_path = str(INVOICES_DIR / "html" / filename)

    html = generate_html_invoice(invoice)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


# ═══════════════════════════════════════════════════════════════
# ИНТЕГРАЦИИ
# ═══════════════════════════════════════════════════════════════

def create_invoice_from_operation(operation: Dict, **kwargs) -> Invoice:
    """Создание инвойса из данных операции (из операции.json)."""

    # Определяем тип услуги
    op_type = operation.get("type", "other")
    service_mapping = {
        "tour": "tour",
        "transfer": "transfer",
        "yacht": "yacht",
        "car_rental": "car_rental",
        "tickets": "tickets",
        "catering": "catering",
        "exchange": "other",
    }
    service_type = service_mapping.get(op_type, "other")

    # Данные клиента
    client = {
        "name": operation.get("contact_name", ""),
        "phone": operation.get("recipient_phone", ""),
        "email": operation.get("email", ""),
    }

    # Создаём инвойс
    invoice = Invoice(
        template=kwargs.get("template", "invoice"),
        company=kwargs.get("company", DEFAULT_COMPANY),
        client=client,
        currency=operation.get("currency", "AED"),
        **{k: v for k, v in kwargs.items() if k not in ["template", "company"]}
    )

    # Добавляем позицию
    amount = float(operation.get("amount", 0))
    description = operation.get("raw_text", operation.get("type", "Service"))[:100]

    invoice.add_item(
        description=description,
        quantity=1,
        unit_price=amount,
        service_type=service_type,
        date=operation.get("date", ""),
    )

    return invoice


def send_invoice_email(
    invoice: Invoice,
    to_email: str,
    subject: Optional[str] = None,
    message: Optional[str] = None,
    attach_pdf: bool = True,
) -> bool:
    """Отправка инвойса на email."""

    if not EMAIL_CONFIG.get("username") or not EMAIL_CONFIG.get("password"):
        print("Ошибка: Email не настроен. Установите SMTP_USERNAME и SMTP_PASSWORD.")
        return False

    if not invoice.invoice_number:
        invoice.generate_number()

    # Тема письма
    if not subject:
        subject = f"{invoice.template['title']} {invoice.invoice_number} from {invoice.company['name']}"

    # Текст письма
    if not message:
        message = f"""
Dear {invoice.client.get('name', 'Customer')},

Please find attached {invoice.template['title'].lower()} {invoice.invoice_number}.

Total Amount: {abs(float(invoice.total)):,.2f} {invoice.currency}
Due Date: {invoice.due_date.strftime('%d %B %Y')}

Thank you for your business!

Best regards,
{invoice.company['name']}
{invoice.company['phone']}
{invoice.company['email']}
        """

    try:
        # Создаём письмо
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['from_email'] or EMAIL_CONFIG['username']}>"
        msg['To'] = to_email

        # Текстовая версия
        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        # HTML версия
        html_content = generate_html_invoice(invoice)
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # PDF вложение
        if attach_pdf and REPORTLAB_AVAILABLE:
            pdf_path = generate_pdf_invoice(invoice)
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attachment.add_header(
                    'Content-Disposition', 'attachment',
                    filename=f"{invoice.invoice_number}.pdf"
                )
                msg.attach(pdf_attachment)

        # Отправляем
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
            server.send_message(msg)

        print(f"Email отправлен на {to_email}")
        return True

    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False


def save_to_bitrix24(invoice: Invoice) -> Optional[str]:
    """Сохранение инвойса в Bitrix24 как сделку."""

    if not BITRIX24_CONFIG.get("domain") or not BITRIX24_CONFIG.get("webhook_key"):
        print("Ошибка: Bitrix24 не настроен.")
        return None

    try:
        import requests

        webhook_url = (
            f"https://{BITRIX24_CONFIG['domain']}.bitrix24.ru/rest/"
            f"{BITRIX24_CONFIG['user_id']}/{BITRIX24_CONFIG['webhook_key']}/"
        )

        # Создаём сделку
        deal_data = {
            "fields": {
                "TITLE": f"{invoice.template['title']} {invoice.invoice_number}",
                "OPPORTUNITY": float(invoice.total),
                "CURRENCY_ID": invoice.currency,
                "COMMENTS": invoice.notes,
                "UF_CRM_INVOICE_NUMBER": invoice.invoice_number,
            }
        }

        response = requests.post(
            f"{webhook_url}crm.deal.add",
            json=deal_data,
            timeout=30
        )

        result = response.json()

        if result.get("result"):
            deal_id = result["result"]
            print(f"Сделка создана в Bitrix24: ID {deal_id}")
            return str(deal_id)
        else:
            print(f"Ошибка Bitrix24: {result.get('error_description', 'Unknown error')}")
            return None

    except Exception as e:
        print(f"Ошибка сохранения в Bitrix24: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# CLI ИНТЕРФЕЙС
# ═══════════════════════════════════════════════════════════════

def create_sample_invoice() -> Invoice:
    """Создание примера инвойса для демонстрации."""

    invoice = Invoice(
        template="invoice",
        company="marsel",
        client={
            "name": "John Smith",
            "company": "ABC Travel Agency",
            "address": "123 Main Street, Moscow, Russia",
            "phone": "+7 999 123 4567",
            "email": "john@abctravel.com",
        },
        currency="AED",
        include_vat=True,
        notes="Thank you for choosing our services. Payment due within 7 days.",
        language="en",
    )

    # Добавляем услуги
    invoice.add_item(
        description="Dubai City Tour - Full Day",
        quantity=2,
        unit_price=450,
        service_type="tour",
        date="25.01.2026",
        details="Includes Burj Khalifa, Dubai Mall, Palm Jumeirah"
    )

    invoice.add_item(
        description="Airport Transfer - DXB to Hotel",
        quantity=1,
        unit_price=150,
        service_type="transfer",
        date="24.01.2026",
        details="Mercedes V-Class, Meet & Greet"
    )

    invoice.add_item(
        description="Desert Safari with BBQ Dinner",
        quantity=2,
        unit_price=350,
        service_type="tour",
        date="26.01.2026",
        details="Dune bashing, camel ride, entertainment"
    )

    return invoice


def main():
    """Основная функция CLI."""

    parser = argparse.ArgumentParser(
        description="Генератор PDF инвойсов для туристического бизнеса"
    )

    subparsers = parser.add_subparsers(dest="command", help="Команды")

    # Команда: create
    create_parser = subparsers.add_parser("create", help="Создать новый инвойс")
    create_parser.add_argument(
        "--template", "-t",
        choices=list(INVOICE_TEMPLATES.keys()),
        default="invoice",
        help="Шаблон инвойса"
    )
    create_parser.add_argument(
        "--company", "-c",
        choices=list(COMPANY_PROFILES.keys()),
        default=DEFAULT_COMPANY,
        help="Компания"
    )
    create_parser.add_argument("--client-name", help="Имя клиента")
    create_parser.add_argument("--client-email", help="Email клиента")
    create_parser.add_argument("--client-phone", help="Телефон клиента")
    create_parser.add_argument(
        "--currency",
        choices=["AED", "USD", "EUR"],
        default="AED",
        help="Валюта"
    )
    create_parser.add_argument("--notes", help="Примечания")
    create_parser.add_argument(
        "--output", "-o",
        help="Путь для сохранения PDF"
    )
    create_parser.add_argument(
        "--sample",
        action="store_true",
        help="Создать пример инвойса"
    )

    # Команда: from-operation
    op_parser = subparsers.add_parser(
        "from-operation",
        help="Создать инвойс из операции"
    )
    op_parser.add_argument("operation_id", help="ID операции")
    op_parser.add_argument(
        "--operations-file",
        default=str(OPERATIONS_FILE),
        help="Путь к файлу операций"
    )

    # Команда: list
    list_parser = subparsers.add_parser("list", help="Список инвойсов")
    list_parser.add_argument(
        "--limit", "-n",
        type=int,
        default=20,
        help="Количество записей"
    )

    # Команда: send
    send_parser = subparsers.add_parser("send", help="Отправить инвойс на email")
    send_parser.add_argument("invoice_number", help="Номер инвойса")
    send_parser.add_argument("email", help="Email получателя")

    # Команда: stats
    stats_parser = subparsers.add_parser("stats", help="Статистика инвойсов")

    args = parser.parse_args()

    if args.command == "create":
        if args.sample:
            invoice = create_sample_invoice()
        else:
            invoice = Invoice(
                template=args.template,
                company=args.company,
                client={
                    "name": args.client_name or "",
                    "email": args.client_email or "",
                    "phone": args.client_phone or "",
                },
                currency=args.currency,
                notes=args.notes or "",
            )

            # Интерактивное добавление позиций
            print("\nДобавление позиций (введите 'done' для завершения):")
            while True:
                desc = input("Описание услуги: ").strip()
                if desc.lower() == "done" or not desc:
                    break

                qty = input("Количество [1]: ").strip()
                qty = float(qty) if qty else 1

                price = input("Цена за единицу: ").strip()
                price = float(price) if price else 0

                print("Типы услуг:", ", ".join(SERVICE_TYPES.keys()))
                stype = input("Тип услуги [other]: ").strip()
                stype = stype if stype in SERVICE_TYPES else "other"

                invoice.add_item(
                    description=desc,
                    quantity=qty,
                    unit_price=price,
                    service_type=stype,
                )

        if not invoice.items:
            print("Ошибка: Инвойс не содержит позиций.")
            return

        # Генерируем номер
        invoice.generate_number()

        # Сохраняем PDF
        if REPORTLAB_AVAILABLE:
            pdf_path = generate_pdf_invoice(invoice, args.output)
            print(f"\nPDF создан: {pdf_path}")
        else:
            pdf_path = ""
            print("\nPDF не создан (reportlab не установлен)")

        # Сохраняем HTML
        html_path = save_html_invoice(invoice)
        print(f"HTML создан: {html_path}")

        # Сохраняем JSON
        json_path = str(INVOICES_DIR / "json" / f"{invoice.invoice_number}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(invoice.to_json())
        print(f"JSON создан: {json_path}")

        # Регистрируем
        register_invoice(invoice, pdf_path, html_path)
        print(f"\nИнвойс зарегистрирован: {invoice.invoice_number}")

        # Итоги
        print(f"\n{'='*50}")
        print(f"Номер: {invoice.invoice_number}")
        print(f"Клиент: {invoice.client.get('name', 'N/A')}")
        print(f"Сумма: {float(invoice.subtotal):,.2f} {invoice.currency}")
        if invoice.include_vat:
            print(f"НДС (5%): {float(invoice.vat_amount):,.2f} {invoice.currency}")
        print(f"ИТОГО: {float(invoice.total):,.2f} {invoice.currency}")
        print(f"{'='*50}")

    elif args.command == "list":
        registry = load_registry()
        invoices = registry.get("invoices", [])[-args.limit:]

        print(f"\nПоследние {len(invoices)} инвойсов:")
        print("-" * 80)

        for inv in reversed(invoices):
            status = "PAID" if inv.get("status") == "paid" else "PENDING"
            print(
                f"{inv['number']:15} | "
                f"{inv.get('client', {}).get('name', 'N/A'):20} | "
                f"{inv['total']:>10,.2f} {inv['currency']} | "
                f"{status}"
            )

    elif args.command == "send":
        inv_data = get_invoice_by_number(args.invoice_number)
        if not inv_data:
            print(f"Инвойс {args.invoice_number} не найден.")
            return

        # Восстанавливаем инвойс
        invoice = Invoice(
            template=inv_data.get("template", "invoice"),
            company=inv_data.get("company", DEFAULT_COMPANY),
            client=inv_data.get("client", {}),
            items=inv_data.get("items", []),
            currency=inv_data.get("currency", "AED"),
            include_vat=inv_data.get("include_vat", True),
            notes=inv_data.get("notes", ""),
        )
        invoice.invoice_number = inv_data["number"]
        invoice.invoice_date = datetime.fromisoformat(inv_data["invoice_date"])
        invoice.due_date = datetime.fromisoformat(inv_data["due_date"])

        send_invoice_email(invoice, args.email)

    elif args.command == "stats":
        registry = load_registry()
        stats = registry.get("stats", {})

        print("\n=== Статистика инвойсов ===\n")
        print(f"Всего инвойсов: {stats.get('total_count', 0)}")
        print(f"Сумма AED: {stats.get('total_amount_aed', 0):,.2f}")
        print(f"Сумма USD: {stats.get('total_amount_usd', 0):,.2f}")

        print("\nПо шаблонам:")
        for tpl, count in stats.get("by_template", {}).items():
            print(f"  {tpl}: {count}")

        print("\nПо компаниям:")
        for comp, count in stats.get("by_company", {}).items():
            print(f"  {comp}: {count}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
