#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Генератор ваучеров для туристических услуг.

Типы ваучеров:
- Туристический ваучер (экскурсии, туры)
- Трансфер ваучер
- Ваучер на билеты (парки, аттракционы)
- Подарочный сертификат

Выход:
- PDF файлы (A4 и мобильная версия)
- voucher_codes.json (база кодов)
"""

import json
import hashlib
import secrets
import qrcode
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Literal
from dataclasses import dataclass, field, asdict
from io import BytesIO
import base64

# PDF генерация
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A6
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.barcode import qr

try:
    from config import CHATS_DIR, ensure_directories
except ImportError:
    CHATS_DIR = Path("D:/Downloads/Chats")
    def ensure_directories():
        pass

# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ И НАСТРОЙКИ
# ═══════════════════════════════════════════════════════════════

VOUCHERS_DIR = CHATS_DIR / "_ваучеры"
VOUCHER_CODES_FILE = VOUCHERS_DIR / "voucher_codes.json"

# Брендинг
BRAND = {
    "company_name": "Marsel Luxury Travel",
    "tagline": "Premium Travel Experiences in UAE",
    "phone": "+971 50 770 5321",
    "email": "info@marselluxury.com",
    "website": "www.marselluxury.com",
    "address": "Dubai, UAE",
    "logo_color": colors.HexColor("#1a5f7a"),  # Тёмно-бирюзовый
    "accent_color": colors.HexColor("#c9a227"),  # Золотой
    "text_color": colors.HexColor("#2c3e50"),
    "light_bg": colors.HexColor("#f8f9fa"),
}

# Типы ваучеров
VoucherType = Literal["tour", "transfer", "tickets", "gift"]

# ═══════════════════════════════════════════════════════════════
# МОДЕЛИ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class TourVoucher:
    """Ваучер на экскурсию/тур."""
    voucher_type: str = "tour"
    booking_number: str = ""
    guest_name: str = ""  # Как в паспорте
    tour_name: str = ""
    tour_name_en: str = ""
    date: str = ""  # DD.MM.YYYY
    time: str = ""  # HH:MM
    duration: str = ""  # "8 часов", "Full day"
    meeting_point: str = ""
    meeting_coordinates: str = ""  # "25.2048,55.2708"
    guide_name: str = ""
    guide_phone: str = ""
    driver_name: str = ""
    driver_phone: str = ""
    car_model: str = ""
    car_number: str = ""
    pax: int = 1
    included: List[str] = field(default_factory=list)
    not_included: List[str] = field(default_factory=list)
    notes: str = ""
    language: str = "RU"  # RU, EN, AR

@dataclass
class TransferVoucher:
    """Ваучер на трансфер."""
    voucher_type: str = "transfer"
    booking_number: str = ""
    guest_name: str = ""
    pickup_location: str = ""
    pickup_address: str = ""
    pickup_coordinates: str = ""
    dropoff_location: str = ""
    dropoff_address: str = ""
    dropoff_coordinates: str = ""
    date: str = ""
    pickup_time: str = ""
    flight_number: str = ""  # Если аэропорт
    flight_time: str = ""  # Время прилёта/вылета
    terminal: str = ""
    driver_name: str = ""
    driver_phone: str = ""
    car_model: str = ""
    car_number: str = ""
    car_color: str = ""
    pax: int = 1
    luggage: str = ""  # "2 чемодана"
    child_seat: bool = False
    meet_and_greet: bool = False  # Встреча с табличкой
    notes: str = ""

@dataclass
class TicketVoucher:
    """Ваучер на билеты."""
    voucher_type: str = "tickets"
    booking_number: str = ""
    guest_name: str = ""
    attraction_name: str = ""
    attraction_name_en: str = ""
    ticket_type: str = ""  # "General Admission", "VIP", "Fast Track"
    quantity: int = 1
    adults: int = 1
    children: int = 0
    date: str = ""
    valid_until: str = ""  # Если билет открытый
    time_slot: str = ""  # Если есть тайм-слот
    address: str = ""
    coordinates: str = ""
    barcode: str = ""  # Штрих-код
    qr_data: str = ""  # Данные для QR
    original_booking_ref: str = ""  # Референс от поставщика
    notes: str = ""

@dataclass
class GiftVoucher:
    """Подарочный сертификат."""
    voucher_type: str = "gift"
    certificate_number: str = ""
    amount: float = 0
    currency: str = "AED"
    recipient_name: str = ""
    purchaser_name: str = ""
    issue_date: str = ""
    valid_until: str = ""
    message: str = ""  # Персональное сообщение
    redeemable_for: List[str] = field(default_factory=list)  # На что можно использовать
    terms: List[str] = field(default_factory=list)
    is_redeemed: bool = False
    redeemed_date: str = ""
    redeemed_for: str = ""

# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ КОДОВ И QR
# ═══════════════════════════════════════════════════════════════

class VoucherCodeGenerator:
    """Генератор уникальных кодов ваучеров."""

    def __init__(self, codes_file: Path = VOUCHER_CODES_FILE):
        self.codes_file = codes_file
        self.codes_db = self._load_codes()

    def _load_codes(self) -> Dict[str, Any]:
        """Загрузить базу кодов."""
        if self.codes_file.exists():
            with open(self.codes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"codes": {}, "stats": {"total": 0, "by_type": {}}}

    def _save_codes(self):
        """Сохранить базу кодов."""
        self.codes_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.codes_file, 'w', encoding='utf-8') as f:
            json.dump(self.codes_db, f, ensure_ascii=False, indent=2)

    def generate_booking_number(self, voucher_type: str, date: str = None) -> str:
        """
        Генерировать номер бронирования.
        Формат: MLT-{TYPE}-{DATE}-{SEQ}
        Пример: MLT-TOR-260126-001
        """
        type_codes = {
            "tour": "TOR",
            "transfer": "TRF",
            "tickets": "TKT",
            "gift": "GFT"
        }

        type_code = type_codes.get(voucher_type, "XXX")

        if date:
            try:
                dt = datetime.strptime(date, "%d.%m.%Y")
            except:
                dt = datetime.now()
        else:
            dt = datetime.now()

        date_code = dt.strftime("%d%m%y")

        # Найти следующий порядковый номер для этой даты
        prefix = f"MLT-{type_code}-{date_code}"
        existing = [k for k in self.codes_db["codes"].keys() if k.startswith(prefix)]
        seq = len(existing) + 1

        booking_number = f"{prefix}-{seq:03d}"
        return booking_number

    def generate_gift_code(self, amount: float) -> str:
        """
        Генерировать код подарочного сертификата.
        Формат: GIFT-{RANDOM}-{CHECKSUM}
        """
        random_part = secrets.token_hex(4).upper()

        # Контрольная сумма для проверки
        data = f"{random_part}{amount}"
        checksum = hashlib.md5(data.encode()).hexdigest()[:4].upper()

        return f"GIFT-{random_part}-{checksum}"

    def generate_qr_data(self, voucher: Any) -> str:
        """Генерировать данные для QR кода."""
        if isinstance(voucher, TourVoucher):
            data = {
                "type": "tour",
                "booking": voucher.booking_number,
                "guest": voucher.guest_name,
                "tour": voucher.tour_name_en or voucher.tour_name,
                "date": voucher.date,
                "time": voucher.time,
                "verify": f"https://marselluxury.com/verify/{voucher.booking_number}"
            }
        elif isinstance(voucher, TransferVoucher):
            data = {
                "type": "transfer",
                "booking": voucher.booking_number,
                "guest": voucher.guest_name,
                "from": voucher.pickup_location,
                "to": voucher.dropoff_location,
                "date": voucher.date,
                "time": voucher.pickup_time,
                "verify": f"https://marselluxury.com/verify/{voucher.booking_number}"
            }
        elif isinstance(voucher, TicketVoucher):
            data = {
                "type": "tickets",
                "booking": voucher.booking_number,
                "attraction": voucher.attraction_name_en or voucher.attraction_name,
                "date": voucher.date,
                "pax": voucher.quantity,
                "ref": voucher.original_booking_ref,
                "verify": f"https://marselluxury.com/verify/{voucher.booking_number}"
            }
        elif isinstance(voucher, GiftVoucher):
            data = {
                "type": "gift",
                "code": voucher.certificate_number,
                "amount": voucher.amount,
                "currency": voucher.currency,
                "valid_until": voucher.valid_until,
                "verify": f"https://marselluxury.com/gift/{voucher.certificate_number}"
            }
        else:
            data = {"error": "unknown voucher type"}

        return json.dumps(data, ensure_ascii=False)

    def register_voucher(self, voucher: Any) -> str:
        """Зарегистрировать ваучер в базе."""
        if hasattr(voucher, 'booking_number'):
            code = voucher.booking_number
        elif hasattr(voucher, 'certificate_number'):
            code = voucher.certificate_number
        else:
            code = secrets.token_hex(8).upper()

        voucher_type = getattr(voucher, 'voucher_type', 'unknown')

        self.codes_db["codes"][code] = {
            "type": voucher_type,
            "created": datetime.now().isoformat(),
            "data": asdict(voucher) if hasattr(voucher, '__dataclass_fields__') else {},
            "status": "active"
        }

        self.codes_db["stats"]["total"] += 1
        self.codes_db["stats"]["by_type"][voucher_type] = \
            self.codes_db["stats"]["by_type"].get(voucher_type, 0) + 1

        self._save_codes()
        return code

    def verify_code(self, code: str) -> Optional[Dict]:
        """Проверить код ваучера."""
        return self.codes_db["codes"].get(code)

    def redeem_gift(self, code: str, redeemed_for: str) -> bool:
        """Погасить подарочный сертификат."""
        if code in self.codes_db["codes"]:
            entry = self.codes_db["codes"][code]
            if entry["type"] == "gift" and entry["status"] == "active":
                entry["status"] = "redeemed"
                entry["redeemed_date"] = datetime.now().isoformat()
                entry["redeemed_for"] = redeemed_for
                self._save_codes()
                return True
        return False

# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАЦИЯ QR КОДОВ
# ═══════════════════════════════════════════════════════════════

def generate_qr_image(data: str, size: int = 150) -> Image:
    """Создать QR код как Image для ReportLab."""
    qr_obj = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr_obj.add_data(data)
    qr_obj.make(fit=True)

    img = qr_obj.make_image(fill_color="black", back_color="white")

    # Конвертировать в байты
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return Image(buffer, width=size, height=size)

def generate_qr_drawing(data: str, size: int = 50*mm) -> Drawing:
    """Создать QR код как Drawing для ReportLab."""
    qr_code = qr.QrCodeWidget(data)
    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    d = Drawing(size, size, transform=[size/width, 0, 0, size/height, 0, 0])
    d.add(qr_code)
    return d

# ═══════════════════════════════════════════════════════════════
# PDF ГЕНЕРАЦИЯ
# ═══════════════════════════════════════════════════════════════

class VoucherPDFGenerator:
    """Генератор PDF ваучеров."""

    def __init__(self, output_dir: Path = VOUCHERS_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.code_generator = VoucherCodeGenerator()
        self._setup_fonts()
        self._setup_styles()

    def _setup_fonts(self):
        """Настроить шрифты."""
        # Попытка загрузить кириллические шрифты
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/timesbd.ttf",
        ]

        try:
            pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
            self.font_regular = 'Arial'
            self.font_bold = 'Arial-Bold'
        except:
            self.font_regular = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'

    def _setup_styles(self):
        """Настроить стили текста."""
        self.styles = getSampleStyleSheet()

        # Заголовок компании
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            fontName=self.font_bold,
            fontSize=18,
            textColor=BRAND["logo_color"],
            alignment=TA_CENTER,
            spaceAfter=2*mm
        ))

        # Подзаголовок
        self.styles.add(ParagraphStyle(
            name='Tagline',
            fontName=self.font_regular,
            fontSize=9,
            textColor=BRAND["accent_color"],
            alignment=TA_CENTER,
            spaceAfter=5*mm
        ))

        # Заголовок ваучера
        self.styles.add(ParagraphStyle(
            name='VoucherTitle',
            fontName=self.font_bold,
            fontSize=16,
            textColor=BRAND["text_color"],
            alignment=TA_CENTER,
            spaceAfter=5*mm,
            spaceBefore=5*mm
        ))

        # Номер бронирования
        self.styles.add(ParagraphStyle(
            name='BookingNumber',
            fontName=self.font_bold,
            fontSize=12,
            textColor=BRAND["accent_color"],
            alignment=TA_CENTER,
            spaceAfter=3*mm
        ))

        # Обычный текст
        self.styles.add(ParagraphStyle(
            name='VoucherText',
            fontName=self.font_regular,
            fontSize=10,
            textColor=BRAND["text_color"],
            alignment=TA_LEFT,
            spaceAfter=2*mm
        ))

        # Жирный текст
        self.styles.add(ParagraphStyle(
            name='VoucherBold',
            fontName=self.font_bold,
            fontSize=10,
            textColor=BRAND["text_color"],
            alignment=TA_LEFT,
            spaceAfter=2*mm
        ))

        # Мелкий текст
        self.styles.add(ParagraphStyle(
            name='SmallText',
            fontName=self.font_regular,
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=1*mm
        ))

        # Контактная информация
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            fontName=self.font_regular,
            fontSize=9,
            textColor=BRAND["text_color"],
            alignment=TA_CENTER,
            spaceAfter=1*mm
        ))

    def _create_header(self) -> List:
        """Создать шапку ваучера с брендингом."""
        elements = []

        # Линия сверху
        elements.append(HRFlowable(
            width="100%",
            thickness=3,
            color=BRAND["logo_color"],
            spaceAfter=5*mm
        ))

        # Название компании
        elements.append(Paragraph(BRAND["company_name"], self.styles['CompanyName']))
        elements.append(Paragraph(BRAND["tagline"], self.styles['Tagline']))

        return elements

    def _create_footer(self) -> List:
        """Создать подвал ваучера."""
        elements = []

        elements.append(Spacer(1, 10*mm))
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=BRAND["accent_color"],
            spaceBefore=5*mm,
            spaceAfter=3*mm
        ))

        # Контакты
        contact_text = f"{BRAND['phone']} | {BRAND['email']} | {BRAND['website']}"
        elements.append(Paragraph(contact_text, self.styles['ContactInfo']))

        # Дисклеймер
        disclaimer = "This voucher is valid only for the specified service and date. " \
                    "Please present this voucher (printed or digital) upon arrival."
        elements.append(Paragraph(disclaimer, self.styles['SmallText']))

        return elements

    def _create_info_table(self, data: List[tuple], col_widths: List = None) -> Table:
        """Создать информационную таблицу."""
        table_data = []
        for label, value in data:
            table_data.append([
                Paragraph(f"<b>{label}:</b>", self.styles['VoucherText']),
                Paragraph(str(value), self.styles['VoucherText'])
            ])

        if not col_widths:
            col_widths = [50*mm, 100*mm]

        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('BACKGROUND', (0, 0), (0, -1), BRAND["light_bg"]),
        ]))

        return table

    def generate_tour_voucher(self, voucher: TourVoucher, mobile: bool = False) -> Path:
        """Генерировать ваучер на тур."""
        # Генерировать номер бронирования если нет
        if not voucher.booking_number:
            voucher.booking_number = self.code_generator.generate_booking_number(
                "tour", voucher.date
            )

        # Зарегистрировать
        self.code_generator.register_voucher(voucher)

        # Определить размер страницы
        page_size = A6 if mobile else A4
        suffix = "_mobile" if mobile else ""

        filename = f"tour_{voucher.booking_number}{suffix}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=page_size,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )

        elements = []

        # Шапка
        elements.extend(self._create_header())

        # Заголовок ваучера
        elements.append(Paragraph("TOUR VOUCHER", self.styles['VoucherTitle']))
        elements.append(Paragraph(
            f"Booking: {voucher.booking_number}",
            self.styles['BookingNumber']
        ))

        # QR код
        qr_data = self.code_generator.generate_qr_data(voucher)
        qr_size = 30*mm if mobile else 50*mm
        qr_drawing = generate_qr_drawing(qr_data, qr_size)

        # Таблица с QR кодом справа
        info_data = [
            ("Guest Name", voucher.guest_name),
            ("Tour", voucher.tour_name),
            ("Date", voucher.date),
            ("Time", voucher.time),
            ("Duration", voucher.duration),
            ("Passengers", str(voucher.pax)),
        ]

        if voucher.language:
            info_data.append(("Language", voucher.language))

        info_table = self._create_info_table(info_data)

        # Основная таблица с информацией и QR
        main_table = Table(
            [[info_table, qr_drawing]],
            colWidths=[120*mm if not mobile else 60*mm, qr_size + 10*mm]
        )
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(main_table)

        elements.append(Spacer(1, 5*mm))

        # Место встречи
        elements.append(Paragraph("<b>MEETING POINT</b>", self.styles['VoucherBold']))
        elements.append(Paragraph(voucher.meeting_point, self.styles['VoucherText']))

        if voucher.meeting_coordinates:
            maps_link = f"https://maps.google.com/?q={voucher.meeting_coordinates}"
            elements.append(Paragraph(
                f"<link href='{maps_link}'><u>Open in Google Maps</u></link>",
                self.styles['SmallText']
            ))

        elements.append(Spacer(1, 3*mm))

        # Контакты гида/водителя
        if voucher.guide_name or voucher.driver_name:
            elements.append(Paragraph("<b>YOUR CONTACTS</b>", self.styles['VoucherBold']))

            contact_data = []
            if voucher.guide_name:
                contact_data.append(("Guide", f"{voucher.guide_name} {voucher.guide_phone}"))
            if voucher.driver_name:
                contact_data.append(("Driver", f"{voucher.driver_name} {voucher.driver_phone}"))
            if voucher.car_model:
                contact_data.append(("Vehicle", f"{voucher.car_model} {voucher.car_number}"))

            elements.append(self._create_info_table(contact_data))

        # Включено/не включено
        if voucher.included:
            elements.append(Spacer(1, 3*mm))
            elements.append(Paragraph("<b>INCLUDED</b>", self.styles['VoucherBold']))
            for item in voucher.included:
                elements.append(Paragraph(f"  * {item}", self.styles['VoucherText']))

        if voucher.not_included:
            elements.append(Spacer(1, 2*mm))
            elements.append(Paragraph("<b>NOT INCLUDED</b>", self.styles['VoucherBold']))
            for item in voucher.not_included:
                elements.append(Paragraph(f"  - {item}", self.styles['VoucherText']))

        # Примечания
        if voucher.notes:
            elements.append(Spacer(1, 3*mm))
            elements.append(Paragraph("<b>NOTES</b>", self.styles['VoucherBold']))
            elements.append(Paragraph(voucher.notes, self.styles['VoucherText']))

        # Подвал
        elements.extend(self._create_footer())

        doc.build(elements)
        return filepath

    def generate_transfer_voucher(self, voucher: TransferVoucher, mobile: bool = False) -> Path:
        """Генерировать ваучер на трансфер."""
        if not voucher.booking_number:
            voucher.booking_number = self.code_generator.generate_booking_number(
                "transfer", voucher.date
            )

        self.code_generator.register_voucher(voucher)

        page_size = A6 if mobile else A4
        suffix = "_mobile" if mobile else ""

        filename = f"transfer_{voucher.booking_number}{suffix}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=page_size,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )

        elements = []
        elements.extend(self._create_header())

        elements.append(Paragraph("TRANSFER VOUCHER", self.styles['VoucherTitle']))
        elements.append(Paragraph(
            f"Booking: {voucher.booking_number}",
            self.styles['BookingNumber']
        ))

        # QR код
        qr_data = self.code_generator.generate_qr_data(voucher)
        qr_size = 30*mm if mobile else 50*mm
        qr_drawing = generate_qr_drawing(qr_data, qr_size)

        # Информация о госте
        info_data = [
            ("Guest Name", voucher.guest_name),
            ("Date", voucher.date),
            ("Pickup Time", voucher.pickup_time),
            ("Passengers", str(voucher.pax)),
        ]

        if voucher.luggage:
            info_data.append(("Luggage", voucher.luggage))

        info_table = self._create_info_table(info_data)

        main_table = Table(
            [[info_table, qr_drawing]],
            colWidths=[120*mm if not mobile else 60*mm, qr_size + 10*mm]
        )
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(main_table)

        elements.append(Spacer(1, 5*mm))

        # Маршрут
        elements.append(Paragraph("<b>ROUTE</b>", self.styles['VoucherBold']))

        route_data = [
            ["FROM", "TO"],
            [
                Paragraph(f"<b>{voucher.pickup_location}</b><br/>{voucher.pickup_address}",
                         self.styles['VoucherText']),
                Paragraph(f"<b>{voucher.dropoff_location}</b><br/>{voucher.dropoff_address}",
                         self.styles['VoucherText'])
            ]
        ]

        route_table = Table(route_data, colWidths=[80*mm, 80*mm])
        route_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND["logo_color"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('GRID', (0, 0), (-1, -1), 1, BRAND["logo_color"]),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ]))
        elements.append(route_table)

        # Информация о рейсе (если аэропорт)
        if voucher.flight_number:
            elements.append(Spacer(1, 5*mm))
            elements.append(Paragraph("<b>FLIGHT INFORMATION</b>", self.styles['VoucherBold']))

            flight_data = [
                ("Flight", voucher.flight_number),
                ("Flight Time", voucher.flight_time),
            ]
            if voucher.terminal:
                flight_data.append(("Terminal", voucher.terminal))

            elements.append(self._create_info_table(flight_data))

        # Водитель и машина
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("<b>DRIVER & VEHICLE</b>", self.styles['VoucherBold']))

        driver_data = [
            ("Driver", f"{voucher.driver_name}"),
            ("Phone", voucher.driver_phone),
            ("Vehicle", f"{voucher.car_model} ({voucher.car_color})"),
            ("Plate", voucher.car_number),
        ]
        elements.append(self._create_info_table(driver_data))

        # Дополнительные услуги
        extras = []
        if voucher.child_seat:
            extras.append("Child seat included")
        if voucher.meet_and_greet:
            extras.append("Meet & Greet with name board")

        if extras:
            elements.append(Spacer(1, 3*mm))
            elements.append(Paragraph("<b>EXTRAS</b>", self.styles['VoucherBold']))
            for extra in extras:
                elements.append(Paragraph(f"  * {extra}", self.styles['VoucherText']))

        if voucher.notes:
            elements.append(Spacer(1, 3*mm))
            elements.append(Paragraph("<b>NOTES</b>", self.styles['VoucherBold']))
            elements.append(Paragraph(voucher.notes, self.styles['VoucherText']))

        elements.extend(self._create_footer())
        doc.build(elements)
        return filepath

    def generate_ticket_voucher(self, voucher: TicketVoucher, mobile: bool = False) -> Path:
        """Генерировать ваучер на билеты."""
        if not voucher.booking_number:
            voucher.booking_number = self.code_generator.generate_booking_number(
                "tickets", voucher.date
            )

        self.code_generator.register_voucher(voucher)

        page_size = A6 if mobile else A4
        suffix = "_mobile" if mobile else ""

        filename = f"tickets_{voucher.booking_number}{suffix}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=page_size,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )

        elements = []
        elements.extend(self._create_header())

        elements.append(Paragraph("TICKET VOUCHER", self.styles['VoucherTitle']))
        elements.append(Paragraph(
            f"Booking: {voucher.booking_number}",
            self.styles['BookingNumber']
        ))

        # Название аттракциона крупно
        elements.append(Paragraph(
            f"<b>{voucher.attraction_name}</b>",
            self.styles['VoucherTitle']
        ))
        if voucher.attraction_name_en and voucher.attraction_name_en != voucher.attraction_name:
            elements.append(Paragraph(
                voucher.attraction_name_en,
                self.styles['SmallText']
            ))

        elements.append(Spacer(1, 5*mm))

        # QR код (большой для билетов)
        qr_data = voucher.qr_data or self.code_generator.generate_qr_data(voucher)
        qr_size = 40*mm if mobile else 70*mm
        qr_drawing = generate_qr_drawing(qr_data, qr_size)

        # Центрировать QR
        qr_table = Table([[qr_drawing]], colWidths=[qr_size])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))

        # Обёртка для центрирования
        wrapper = Table([[qr_table]], colWidths=[page_size[0] - 30*mm])
        wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))
        elements.append(wrapper)

        # Референс поставщика
        if voucher.original_booking_ref:
            elements.append(Paragraph(
                f"Reference: {voucher.original_booking_ref}",
                self.styles['BookingNumber']
            ))

        elements.append(Spacer(1, 5*mm))

        # Информация о билетах
        info_data = [
            ("Guest Name", voucher.guest_name),
            ("Ticket Type", voucher.ticket_type),
            ("Date", voucher.date),
        ]

        if voucher.time_slot:
            info_data.append(("Time Slot", voucher.time_slot))

        if voucher.valid_until:
            info_data.append(("Valid Until", voucher.valid_until))

        # Количество
        pax_str = f"Adults: {voucher.adults}"
        if voucher.children > 0:
            pax_str += f", Children: {voucher.children}"
        info_data.append(("Guests", pax_str))

        elements.append(self._create_info_table(info_data))

        # Адрес
        if voucher.address:
            elements.append(Spacer(1, 5*mm))
            elements.append(Paragraph("<b>LOCATION</b>", self.styles['VoucherBold']))
            elements.append(Paragraph(voucher.address, self.styles['VoucherText']))

            if voucher.coordinates:
                maps_link = f"https://maps.google.com/?q={voucher.coordinates}"
                elements.append(Paragraph(
                    f"<link href='{maps_link}'><u>Open in Google Maps</u></link>",
                    self.styles['SmallText']
                ))

        if voucher.notes:
            elements.append(Spacer(1, 3*mm))
            elements.append(Paragraph("<b>IMPORTANT</b>", self.styles['VoucherBold']))
            elements.append(Paragraph(voucher.notes, self.styles['VoucherText']))

        elements.extend(self._create_footer())
        doc.build(elements)
        return filepath

    def generate_gift_voucher(self, voucher: GiftVoucher, mobile: bool = False) -> Path:
        """Генерировать подарочный сертификат."""
        if not voucher.certificate_number:
            voucher.certificate_number = self.code_generator.generate_gift_code(voucher.amount)

        if not voucher.issue_date:
            voucher.issue_date = datetime.now().strftime("%d.%m.%Y")

        if not voucher.valid_until:
            valid_date = datetime.now() + timedelta(days=365)
            voucher.valid_until = valid_date.strftime("%d.%m.%Y")

        self.code_generator.register_voucher(voucher)

        page_size = A6 if mobile else A4
        suffix = "_mobile" if mobile else ""

        filename = f"gift_{voucher.certificate_number}{suffix}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=page_size,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        elements = []

        # Декоративная рамка сверху
        elements.append(HRFlowable(
            width="100%",
            thickness=5,
            color=BRAND["accent_color"],
            spaceAfter=10*mm
        ))

        # Шапка
        elements.append(Paragraph(BRAND["company_name"], self.styles['CompanyName']))
        elements.append(Paragraph(BRAND["tagline"], self.styles['Tagline']))

        elements.append(Spacer(1, 10*mm))

        # Заголовок
        gift_title_style = ParagraphStyle(
            name='GiftTitle',
            fontName=self.font_bold,
            fontSize=24,
            textColor=BRAND["accent_color"],
            alignment=TA_CENTER,
            spaceAfter=5*mm
        )
        elements.append(Paragraph("GIFT CERTIFICATE", gift_title_style))

        # Номер сертификата
        elements.append(Paragraph(
            voucher.certificate_number,
            self.styles['BookingNumber']
        ))

        elements.append(Spacer(1, 10*mm))

        # Сумма крупно
        amount_style = ParagraphStyle(
            name='Amount',
            fontName=self.font_bold,
            fontSize=36,
            textColor=BRAND["logo_color"],
            alignment=TA_CENTER,
            spaceAfter=5*mm
        )
        elements.append(Paragraph(
            f"{voucher.amount:,.0f} {voucher.currency}",
            amount_style
        ))

        elements.append(Spacer(1, 5*mm))

        # Получатель
        if voucher.recipient_name:
            elements.append(Paragraph(
                f"Presented to: <b>{voucher.recipient_name}</b>",
                self.styles['VoucherText']
            ))

        # Персональное сообщение
        if voucher.message:
            elements.append(Spacer(1, 5*mm))
            message_style = ParagraphStyle(
                name='Message',
                fontName=self.font_regular,
                fontSize=11,
                textColor=BRAND["text_color"],
                alignment=TA_CENTER,
                spaceAfter=5*mm,
                leading=14
            )
            elements.append(Paragraph(f'"{voucher.message}"', message_style))

        elements.append(Spacer(1, 10*mm))

        # QR код
        qr_data = self.code_generator.generate_qr_data(voucher)
        qr_size = 35*mm if mobile else 50*mm
        qr_drawing = generate_qr_drawing(qr_data, qr_size)

        qr_table = Table([[qr_drawing]], colWidths=[qr_size])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))
        wrapper = Table([[qr_table]], colWidths=[page_size[0] - 40*mm])
        wrapper.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))
        elements.append(wrapper)

        elements.append(Spacer(1, 5*mm))

        # Срок действия
        elements.append(Paragraph(
            f"Valid until: {voucher.valid_until}",
            self.styles['VoucherBold']
        ))

        # На что можно использовать
        if voucher.redeemable_for:
            elements.append(Spacer(1, 5*mm))
            elements.append(Paragraph("<b>Redeemable for:</b>", self.styles['VoucherText']))
            for item in voucher.redeemable_for:
                elements.append(Paragraph(f"  * {item}", self.styles['VoucherText']))

        # Условия
        if voucher.terms:
            elements.append(Spacer(1, 5*mm))
            elements.append(Paragraph("<b>Terms & Conditions:</b>", self.styles['SmallText']))
            for term in voucher.terms:
                elements.append(Paragraph(f"- {term}", self.styles['SmallText']))

        # Подвал
        elements.append(Spacer(1, 10*mm))
        elements.append(HRFlowable(
            width="100%",
            thickness=2,
            color=BRAND["accent_color"],
            spaceBefore=5*mm,
            spaceAfter=3*mm
        ))

        contact_text = f"{BRAND['phone']} | {BRAND['email']}"
        elements.append(Paragraph(contact_text, self.styles['ContactInfo']))

        doc.build(elements)
        return filepath

    def generate_voucher(self, voucher: Any, mobile: bool = False) -> Path:
        """Универсальный метод генерации ваучера."""
        if isinstance(voucher, TourVoucher):
            return self.generate_tour_voucher(voucher, mobile)
        elif isinstance(voucher, TransferVoucher):
            return self.generate_transfer_voucher(voucher, mobile)
        elif isinstance(voucher, TicketVoucher):
            return self.generate_ticket_voucher(voucher, mobile)
        elif isinstance(voucher, GiftVoucher):
            return self.generate_gift_voucher(voucher, mobile)
        else:
            raise ValueError(f"Unknown voucher type: {type(voucher)}")

    def generate_both_versions(self, voucher: Any) -> tuple[Path, Path]:
        """Генерировать обе версии (A4 и мобильную)."""
        a4_path = self.generate_voucher(voucher, mobile=False)
        mobile_path = self.generate_voucher(voucher, mobile=True)
        return a4_path, mobile_path

# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def create_tour_voucher_from_dict(data: Dict) -> TourVoucher:
    """Создать ваучер на тур из словаря."""
    return TourVoucher(
        booking_number=data.get("booking_number", ""),
        guest_name=data.get("guest_name", ""),
        tour_name=data.get("tour_name", ""),
        tour_name_en=data.get("tour_name_en", ""),
        date=data.get("date", ""),
        time=data.get("time", ""),
        duration=data.get("duration", ""),
        meeting_point=data.get("meeting_point", ""),
        meeting_coordinates=data.get("meeting_coordinates", ""),
        guide_name=data.get("guide_name", ""),
        guide_phone=data.get("guide_phone", ""),
        driver_name=data.get("driver_name", ""),
        driver_phone=data.get("driver_phone", ""),
        car_model=data.get("car_model", ""),
        car_number=data.get("car_number", ""),
        pax=data.get("pax", 1),
        included=data.get("included", []),
        not_included=data.get("not_included", []),
        notes=data.get("notes", ""),
        language=data.get("language", "RU"),
    )

def create_transfer_voucher_from_dict(data: Dict) -> TransferVoucher:
    """Создать ваучер на трансфер из словаря."""
    return TransferVoucher(
        booking_number=data.get("booking_number", ""),
        guest_name=data.get("guest_name", ""),
        pickup_location=data.get("pickup_location", ""),
        pickup_address=data.get("pickup_address", ""),
        pickup_coordinates=data.get("pickup_coordinates", ""),
        dropoff_location=data.get("dropoff_location", ""),
        dropoff_address=data.get("dropoff_address", ""),
        dropoff_coordinates=data.get("dropoff_coordinates", ""),
        date=data.get("date", ""),
        pickup_time=data.get("pickup_time", ""),
        flight_number=data.get("flight_number", ""),
        flight_time=data.get("flight_time", ""),
        terminal=data.get("terminal", ""),
        driver_name=data.get("driver_name", ""),
        driver_phone=data.get("driver_phone", ""),
        car_model=data.get("car_model", ""),
        car_number=data.get("car_number", ""),
        car_color=data.get("car_color", ""),
        pax=data.get("pax", 1),
        luggage=data.get("luggage", ""),
        child_seat=data.get("child_seat", False),
        meet_and_greet=data.get("meet_and_greet", False),
        notes=data.get("notes", ""),
    )

def create_ticket_voucher_from_dict(data: Dict) -> TicketVoucher:
    """Создать ваучер на билеты из словаря."""
    return TicketVoucher(
        booking_number=data.get("booking_number", ""),
        guest_name=data.get("guest_name", ""),
        attraction_name=data.get("attraction_name", ""),
        attraction_name_en=data.get("attraction_name_en", ""),
        ticket_type=data.get("ticket_type", "General Admission"),
        quantity=data.get("quantity", 1),
        adults=data.get("adults", 1),
        children=data.get("children", 0),
        date=data.get("date", ""),
        valid_until=data.get("valid_until", ""),
        time_slot=data.get("time_slot", ""),
        address=data.get("address", ""),
        coordinates=data.get("coordinates", ""),
        barcode=data.get("barcode", ""),
        qr_data=data.get("qr_data", ""),
        original_booking_ref=data.get("original_booking_ref", ""),
        notes=data.get("notes", ""),
    )

def create_gift_voucher_from_dict(data: Dict) -> GiftVoucher:
    """Создать подарочный сертификат из словаря."""
    return GiftVoucher(
        certificate_number=data.get("certificate_number", ""),
        amount=data.get("amount", 0),
        currency=data.get("currency", "AED"),
        recipient_name=data.get("recipient_name", ""),
        purchaser_name=data.get("purchaser_name", ""),
        issue_date=data.get("issue_date", ""),
        valid_until=data.get("valid_until", ""),
        message=data.get("message", ""),
        redeemable_for=data.get("redeemable_for", []),
        terms=data.get("terms", []),
    )

# ═══════════════════════════════════════════════════════════════
# CLI ИНТЕРФЕЙС
# ═══════════════════════════════════════════════════════════════

def main():
    """Главная функция с демонстрацией."""
    import argparse

    parser = argparse.ArgumentParser(description="Генератор ваучеров")
    parser.add_argument("--demo", action="store_true", help="Создать демо-ваучеры")
    parser.add_argument("--type", choices=["tour", "transfer", "tickets", "gift"],
                       help="Тип ваучера")
    parser.add_argument("--json", type=str, help="JSON файл с данными ваучера")
    parser.add_argument("--mobile", action="store_true", help="Создать мобильную версию")
    parser.add_argument("--both", action="store_true", help="Создать обе версии")

    args = parser.parse_args()

    generator = VoucherPDFGenerator()

    if args.demo:
        print("Создание демо-ваучеров...")
        print(f"Папка: {VOUCHERS_DIR}")

        # Демо тур
        tour = TourVoucher(
            guest_name="IVANOV IVAN",
            tour_name="Сафари в пустыне с барбекю",
            tour_name_en="Desert Safari with BBQ Dinner",
            date="28.01.2026",
            time="14:30",
            duration="6 часов",
            meeting_point="Lobby of Atlantis The Palm Hotel",
            meeting_coordinates="25.1304,55.1172",
            guide_name="Ahmed",
            guide_phone="+971 50 123 4567",
            driver_name="Mohammed",
            driver_phone="+971 50 987 6543",
            car_model="Toyota Land Cruiser",
            car_number="Dubai A 12345",
            pax=4,
            included=[
                "Hotel pickup and drop-off",
                "Dune bashing",
                "Camel ride",
                "BBQ dinner with drinks",
                "Belly dance show",
                "Henna painting"
            ],
            not_included=[
                "Quad bike (optional, 150 AED)",
                "Professional photos"
            ],
            notes="Please wear comfortable clothes. Bring sunglasses and sunscreen.",
            language="EN"
        )

        a4, mobile = generator.generate_both_versions(tour)
        print(f"  Tour voucher: {a4}")
        print(f"  Tour mobile: {mobile}")

        # Демо трансфер
        transfer = TransferVoucher(
            guest_name="PETROV PETR",
            pickup_location="Dubai International Airport",
            pickup_address="Terminal 3, Arrivals",
            pickup_coordinates="25.2532,55.3657",
            dropoff_location="Burj Al Arab",
            dropoff_address="Jumeirah Beach Road",
            dropoff_coordinates="25.1412,55.1853",
            date="29.01.2026",
            pickup_time="15:30",
            flight_number="EK 132",
            flight_time="15:00",
            terminal="Terminal 3",
            driver_name="Ali Hassan",
            driver_phone="+971 50 555 1234",
            car_model="Mercedes S-Class",
            car_number="Dubai B 54321",
            car_color="Black",
            pax=2,
            luggage="2 suitcases + 2 carry-on",
            meet_and_greet=True,
            notes="Driver will meet you at arrivals with a name board."
        )

        a4, mobile = generator.generate_both_versions(transfer)
        print(f"  Transfer voucher: {a4}")
        print(f"  Transfer mobile: {mobile}")

        # Демо билеты
        tickets = TicketVoucher(
            guest_name="SIDOROV SERGEY",
            attraction_name="Ferrari World Abu Dhabi",
            attraction_name_en="Ferrari World Abu Dhabi",
            ticket_type="Premium All Access",
            adults=2,
            children=1,
            quantity=3,
            date="30.01.2026",
            time_slot="10:00 - 22:00",
            address="Yas Island, Abu Dhabi",
            coordinates="24.4839,54.6073",
            original_booking_ref="FW-2026-ABC123",
            notes="Includes fast track access to all rides. Height restrictions apply for some attractions."
        )

        a4, mobile = generator.generate_both_versions(tickets)
        print(f"  Tickets voucher: {a4}")
        print(f"  Tickets mobile: {mobile}")

        # Демо подарочный сертификат
        gift = GiftVoucher(
            amount=5000,
            currency="AED",
            recipient_name="Maria Ivanova",
            purchaser_name="Ivan Ivanov",
            message="Wishing you an amazing adventure in the UAE! Happy Birthday!",
            redeemable_for=[
                "Desert Safari experiences",
                "City tours",
                "Yacht charters",
                "Theme park tickets",
                "Airport transfers"
            ],
            terms=[
                "Valid for 12 months from issue date",
                "Non-refundable and non-transferable",
                "Cannot be exchanged for cash",
                "Present this certificate when booking"
            ]
        )

        a4, mobile = generator.generate_both_versions(gift)
        print(f"  Gift voucher: {a4}")
        print(f"  Gift mobile: {mobile}")

        print(f"\nБаза кодов: {VOUCHER_CODES_FILE}")
        print("Готово!")

    elif args.json:
        # Загрузить данные из JSON
        with open(args.json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        voucher_type = args.type or data.get("voucher_type", "tour")

        if voucher_type == "tour":
            voucher = create_tour_voucher_from_dict(data)
        elif voucher_type == "transfer":
            voucher = create_transfer_voucher_from_dict(data)
        elif voucher_type == "tickets":
            voucher = create_ticket_voucher_from_dict(data)
        elif voucher_type == "gift":
            voucher = create_gift_voucher_from_dict(data)
        else:
            print(f"Неизвестный тип: {voucher_type}")
            return

        if args.both:
            a4, mobile = generator.generate_both_versions(voucher)
            print(f"A4: {a4}")
            print(f"Mobile: {mobile}")
        else:
            path = generator.generate_voucher(voucher, mobile=args.mobile)
            print(f"Voucher: {path}")

    else:
        parser.print_help()
        print("\nПримеры:")
        print("  python voucher_generator.py --demo")
        print("  python voucher_generator.py --type tour --json tour_data.json")
        print("  python voucher_generator.py --type gift --json gift_data.json --both")

if __name__ == "__main__":
    main()
