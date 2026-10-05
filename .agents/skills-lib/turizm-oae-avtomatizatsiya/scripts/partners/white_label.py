#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
White-label решение для туристических агентов.

Позволяет агентам продавать услуги под собственным брендом:
- Кастомизация бренда (логотип, цвета, контакты)
- Генерация брендированных материалов (PDF, ваучеры, инвойсы)
- Встраиваемый виджет бронирования (iframe, JS)
- Landing page генератор с SEO
- Гибкие настройки наценки и условий
- Аналитика продаж через виджет
"""

import os
import sys
import json
import uuid
import hashlib
import secrets
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union, Literal
from io import BytesIO
import base64
import urllib.parse
import re

sys.stdout.reconfigure(encoding='utf-8')

# Jinja2 для шаблонов
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape, Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("ПРЕДУПРЕЖДЕНИЕ: jinja2 не установлен. pip install jinja2")

# WeasyPrint для PDF
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("ПРЕДУПРЕЖДЕНИЕ: weasyprint не установлен. pip install weasyprint")

# Pillow для работы с изображениями
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("ПРЕДУПРЕЖДЕНИЕ: pillow не установлен. pip install pillow")

# QR-код
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

try:
    from config import CHATS_DIR, ensure_directories
except ImportError:
    CHATS_DIR = Path("D:/Downloads/Chats")
    def ensure_directories():
        pass


# ═══════════════════════════════════════════════════════════════
# КОНСТАНТЫ И ПУТИ
# ═══════════════════════════════════════════════════════════════

WHITE_LABEL_DIR = CHATS_DIR / "_white_label"
AGENTS_DIR = WHITE_LABEL_DIR / "agents"
TEMPLATES_DIR = Path(__file__).parent / "templates" / "white_label"
WIDGETS_DIR = WHITE_LABEL_DIR / "widgets"
LANDING_DIR = WHITE_LABEL_DIR / "landing_pages"
ANALYTICS_DIR = WHITE_LABEL_DIR / "analytics"

# Базовый URL для виджетов (настраивается)
BASE_WIDGET_URL = os.getenv("WHITE_LABEL_WIDGET_URL", "https://widget.marselluxury.ae")
BASE_API_URL = os.getenv("WHITE_LABEL_API_URL", "https://api.marselluxury.ae")


# ═══════════════════════════════════════════════════════════════
# МОДЕЛИ ДАННЫХ
# ═══════════════════════════════════════════════════════════════

@dataclass
class BrandSettings:
    """Настройки бренда агента."""
    # Основная информация
    agent_id: str = ""
    company_name: str = ""
    company_name_short: str = ""
    legal_name: str = ""
    tagline: str = ""

    # Контакты
    phone: str = ""
    phone_whatsapp: str = ""
    email: str = ""
    website: str = ""
    address: List[str] = field(default_factory=list)

    # Домен
    subdomain: str = ""  # agent.marselluxury.ae
    custom_domain: str = ""  # www.agent-travel.com

    # Визуальный брендинг
    logo_path: str = ""
    logo_base64: str = ""
    favicon_path: str = ""

    # Цветовая схема
    colors: Dict[str, str] = field(default_factory=lambda: {
        "primary": "#1a5f7a",      # Основной цвет
        "secondary": "#c9a227",    # Акцентный (золотой)
        "accent": "#3498db",       # Дополнительный акцент
        "text": "#2c3e50",         # Текст
        "text_light": "#7f8c8d",   # Светлый текст
        "background": "#ffffff",   # Фон
        "background_alt": "#f8f9fa",  # Альтернативный фон
        "success": "#27ae60",
        "warning": "#f39c12",
        "error": "#e74c3c",
    })

    # Типографика
    fonts: Dict[str, str] = field(default_factory=lambda: {
        "heading": "Montserrat, Arial, sans-serif",
        "body": "Open Sans, Arial, sans-serif",
        "accent": "Playfair Display, Georgia, serif",
    })

    # Соцсети
    social: Dict[str, str] = field(default_factory=dict)

    # Юридическая информация
    license_number: str = ""
    trn: str = ""  # Tax Registration Number

    # Банковские реквизиты (для инвойсов)
    bank_details: Dict[str, str] = field(default_factory=dict)

    created_at: str = ""
    updated_at: str = ""


@dataclass
class PricingSettings:
    """Настройки ценообразования агента."""
    agent_id: str = ""

    # Глобальная наценка
    default_markup_percent: float = 15.0
    default_markup_fixed: float = 0.0

    # Наценка по категориям
    category_markup: Dict[str, float] = field(default_factory=lambda: {
        "tours": 15.0,
        "transfers": 10.0,
        "tickets": 12.0,
        "rentals": 20.0,
        "restaurants": 10.0,
        "hotels": 15.0,
    })

    # Наценка по продуктам (product_id -> markup)
    product_markup: Dict[str, float] = field(default_factory=dict)

    # Валюты
    base_currency: str = "AED"
    display_currencies: List[str] = field(default_factory=lambda: ["AED", "USD", "EUR", "RUB"])

    # Округление цен
    round_to: int = 5  # Округлять до 5 AED
    round_up: bool = True  # Округлять вверх

    # Скрытие оригинальных цен
    hide_original_prices: bool = True
    hide_supplier_info: bool = True

    # Минимальная маржа
    min_margin_percent: float = 5.0
    min_margin_fixed: float = 50.0  # AED


@dataclass
class WidgetSettings:
    """Настройки виджета бронирования."""
    agent_id: str = ""
    widget_id: str = ""

    # Тип виджета
    widget_type: str = "iframe"  # iframe, popup, inline, floating

    # Размеры
    width: str = "100%"
    height: str = "600px"
    min_width: str = "320px"
    max_width: str = "1200px"

    # Позиция (для floating)
    position: str = "bottom-right"  # bottom-right, bottom-left, center

    # Отображаемые категории
    show_categories: List[str] = field(default_factory=lambda: [
        "tours", "transfers", "tickets", "rentals"
    ])

    # Языки
    default_language: str = "ru"
    available_languages: List[str] = field(default_factory=lambda: ["ru", "en", "ar"])

    # Функции
    enable_booking: bool = True
    enable_cart: bool = True
    enable_wishlist: bool = False
    enable_reviews: bool = True
    enable_chat: bool = True

    # Кастомные стили (CSS)
    custom_css: str = ""

    # Callback URL для событий
    callback_url: str = ""

    # Tracking
    google_analytics_id: str = ""
    facebook_pixel_id: str = ""
    yandex_metrika_id: str = ""


@dataclass
class LandingPageSettings:
    """Настройки landing page."""
    agent_id: str = ""
    page_id: str = ""

    # SEO
    title: str = ""
    meta_description: str = ""
    meta_keywords: List[str] = field(default_factory=list)
    og_image: str = ""
    canonical_url: str = ""

    # Контент
    hero_title: str = ""
    hero_subtitle: str = ""
    hero_image: str = ""
    hero_cta_text: str = "Забронировать"
    hero_cta_url: str = ""

    # Секции
    sections: List[Dict[str, Any]] = field(default_factory=list)

    # Шаблон
    template: str = "modern"  # modern, classic, minimal, luxury

    # Форма бронирования
    form_fields: List[str] = field(default_factory=lambda: [
        "name", "phone", "email", "date", "guests", "message"
    ])
    form_submit_url: str = ""

    # Footer
    show_footer: bool = True
    footer_links: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class SalesRecord:
    """Запись о продаже через виджет."""
    sale_id: str = ""
    agent_id: str = ""
    widget_id: str = ""

    # Клиент
    customer_name: str = ""
    customer_email: str = ""
    customer_phone: str = ""

    # Заказ
    order_id: str = ""
    products: List[Dict[str, Any]] = field(default_factory=list)

    # Суммы
    subtotal: float = 0.0
    agent_markup: float = 0.0
    total: float = 0.0
    currency: str = "AED"

    # Комиссия
    agent_commission: float = 0.0
    platform_fee: float = 0.0

    # Статус
    status: str = "pending"  # pending, confirmed, completed, cancelled, refunded
    payment_status: str = "unpaid"  # unpaid, partial, paid, refunded

    # Источник
    source_url: str = ""
    referrer: str = ""
    utm_source: str = ""
    utm_medium: str = ""
    utm_campaign: str = ""

    # Timestamps
    created_at: str = ""
    updated_at: str = ""


# ═══════════════════════════════════════════════════════════════
# МЕНЕДЖЕР АГЕНТОВ
# ═══════════════════════════════════════════════════════════════

class AgentManager:
    """Управление агентами и их настройками."""

    def __init__(self):
        self._ensure_dirs()
        self.agents_file = AGENTS_DIR / "agents.json"
        self.agents: Dict[str, BrandSettings] = {}
        self._load_agents()

    def _ensure_dirs(self):
        """Создание необходимых директорий."""
        for dir_path in [WHITE_LABEL_DIR, AGENTS_DIR, WIDGETS_DIR,
                         LANDING_DIR, ANALYTICS_DIR, TEMPLATES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _load_agents(self):
        """Загрузка списка агентов."""
        if self.agents_file.exists():
            try:
                with open(self.agents_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for agent_id, agent_data in data.items():
                        self.agents[agent_id] = BrandSettings(**agent_data)
            except Exception as e:
                print(f"Ошибка загрузки агентов: {e}")

    def _save_agents(self):
        """Сохранение списка агентов."""
        data = {agent_id: asdict(agent) for agent_id, agent in self.agents.items()}
        with open(self.agents_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_agent(self, company_name: str, **kwargs) -> BrandSettings:
        """Создание нового агента."""
        agent_id = kwargs.get('agent_id') or self._generate_agent_id(company_name)

        # Создаём subdomain из названия
        subdomain = kwargs.get('subdomain') or self._generate_subdomain(company_name)

        brand = BrandSettings(
            agent_id=agent_id,
            company_name=company_name,
            company_name_short=kwargs.get('company_name_short', company_name[:20]),
            subdomain=subdomain,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            **{k: v for k, v in kwargs.items() if k not in ['agent_id', 'subdomain', 'company_name_short']}
        )

        self.agents[agent_id] = brand
        self._save_agents()

        # Создаём директорию агента
        agent_dir = AGENTS_DIR / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / "assets").mkdir(exist_ok=True)
        (agent_dir / "materials").mkdir(exist_ok=True)
        (agent_dir / "exports").mkdir(exist_ok=True)

        # Сохраняем настройки агента
        self._save_agent_settings(agent_id, brand)

        # Создаём дефолтные настройки ценообразования
        self._create_default_pricing(agent_id)

        print(f"Агент создан: {agent_id}")
        print(f"  Subdomain: {subdomain}.marselluxury.ae")

        return brand

    def _generate_agent_id(self, company_name: str) -> str:
        """Генерация уникального ID агента."""
        base = re.sub(r'[^a-z0-9]', '', company_name.lower())[:10]
        suffix = secrets.token_hex(4)
        return f"{base}_{suffix}"

    def _generate_subdomain(self, company_name: str) -> str:
        """Генерация subdomain из названия компании."""
        # Транслитерация и очистка
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        }

        result = company_name.lower()
        for ru, en in translit_map.items():
            result = result.replace(ru, en)

        result = re.sub(r'[^a-z0-9]', '-', result)
        result = re.sub(r'-+', '-', result).strip('-')

        return result[:30]

    def _save_agent_settings(self, agent_id: str, brand: BrandSettings):
        """Сохранение настроек агента."""
        agent_dir = AGENTS_DIR / agent_id
        settings_file = agent_dir / "brand_settings.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(brand), f, ensure_ascii=False, indent=2)

    def _create_default_pricing(self, agent_id: str):
        """Создание дефолтных настроек ценообразования."""
        pricing = PricingSettings(agent_id=agent_id)
        agent_dir = AGENTS_DIR / agent_id
        pricing_file = agent_dir / "pricing_settings.json"
        with open(pricing_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(pricing), f, ensure_ascii=False, indent=2)

    def get_agent(self, agent_id: str) -> Optional[BrandSettings]:
        """Получение агента по ID."""
        return self.agents.get(agent_id)

    def update_agent(self, agent_id: str, **kwargs) -> Optional[BrandSettings]:
        """Обновление настроек агента."""
        if agent_id not in self.agents:
            return None

        brand = self.agents[agent_id]
        for key, value in kwargs.items():
            if hasattr(brand, key):
                setattr(brand, key, value)

        brand.updated_at = datetime.now().isoformat()
        self._save_agents()
        self._save_agent_settings(agent_id, brand)

        return brand

    def upload_logo(self, agent_id: str, logo_path: str) -> bool:
        """Загрузка логотипа агента."""
        if not PILLOW_AVAILABLE:
            print("Pillow не установлен")
            return False

        if agent_id not in self.agents:
            return False

        try:
            # Открываем и оптимизируем
            img = Image.open(logo_path)

            # Конвертируем в RGBA если нужно
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Создаём разные размеры
            sizes = {
                'logo_full': (400, 200),
                'logo_header': (200, 80),
                'logo_favicon': (32, 32),
                'logo_square': (200, 200),
            }

            agent_dir = AGENTS_DIR / agent_id / "assets"

            for name, size in sizes.items():
                resized = img.copy()
                resized.thumbnail(size, Image.Resampling.LANCZOS)

                # Сохраняем PNG
                output_path = agent_dir / f"{name}.png"
                resized.save(output_path, 'PNG', optimize=True)

                # Для favicon также сохраняем ICO
                if name == 'logo_favicon':
                    ico_path = agent_dir / "favicon.ico"
                    resized.save(ico_path, 'ICO')

            # Обновляем настройки
            brand = self.agents[agent_id]
            brand.logo_path = str(agent_dir / "logo_full.png")
            brand.favicon_path = str(agent_dir / "favicon.ico")

            # Создаём base64 для встраивания
            buffer = BytesIO()
            img.thumbnail((200, 80), Image.Resampling.LANCZOS)
            img.save(buffer, 'PNG')
            brand.logo_base64 = base64.b64encode(buffer.getvalue()).decode()

            self._save_agents()
            self._save_agent_settings(agent_id, brand)

            print(f"Логотип загружен для агента {agent_id}")
            return True

        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
            return False

    def set_colors(self, agent_id: str, colors: Dict[str, str]) -> bool:
        """Установка цветовой схемы."""
        if agent_id not in self.agents:
            return False

        brand = self.agents[agent_id]
        brand.colors.update(colors)
        brand.updated_at = datetime.now().isoformat()

        self._save_agents()
        self._save_agent_settings(agent_id, brand)

        return True

    def list_agents(self) -> List[Dict[str, Any]]:
        """Список всех агентов."""
        return [
            {
                "agent_id": agent_id,
                "company_name": brand.company_name,
                "subdomain": brand.subdomain,
                "email": brand.email,
                "created_at": brand.created_at,
            }
            for agent_id, brand in self.agents.items()
        ]


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАТОР МАТЕРИАЛОВ
# ═══════════════════════════════════════════════════════════════

class MaterialGenerator:
    """Генерация брендированных материалов."""

    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self._init_jinja()

    def _init_jinja(self):
        """Инициализация Jinja2."""
        if not JINJA2_AVAILABLE:
            return

        # Создаём директорию шаблонов если нет
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(['html', 'xml']),
        )

        # Добавляем фильтры
        self.jinja_env.filters['currency'] = self._format_currency
        self.jinja_env.filters['date'] = self._format_date

    def _format_currency(self, value: float, currency: str = "AED") -> str:
        """Форматирование валюты."""
        symbols = {"AED": "AED", "USD": "$", "EUR": "€", "RUB": "₽"}
        symbol = symbols.get(currency, currency)
        return f"{symbol} {value:,.2f}"

    def _format_date(self, date_str: str, fmt: str = "%d.%m.%Y") -> str:
        """Форматирование даты."""
        try:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime(fmt)
        except:
            return date_str

    def _get_brand_context(self, agent_id: str) -> Dict[str, Any]:
        """Получение контекста бренда для шаблонов."""
        brand = self.agent_manager.get_agent(agent_id)
        if not brand:
            return {}

        return {
            "brand": asdict(brand),
            "company_name": brand.company_name,
            "logo_base64": brand.logo_base64,
            "colors": brand.colors,
            "fonts": brand.fonts,
            "phone": brand.phone,
            "email": brand.email,
            "website": brand.website,
            "address": brand.address,
        }

    def generate_pdf_catalog(
        self,
        agent_id: str,
        products: List[Dict[str, Any]],
        title: str = "Каталог услуг",
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Генерация PDF каталога с брендом агента."""
        if not WEASYPRINT_AVAILABLE or not JINJA2_AVAILABLE:
            print("Требуется weasyprint и jinja2")
            return None

        brand = self.agent_manager.get_agent(agent_id)
        if not brand:
            print(f"Агент {agent_id} не найден")
            return None

        # Контекст для шаблона
        context = self._get_brand_context(agent_id)
        context.update({
            "title": title,
            "products": products,
            "generated_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "year": datetime.now().year,
        })

        # HTML контент (встроенный шаблон)
        html_content = self._render_catalog_html(context)

        # Генерация PDF
        if not output_path:
            agent_dir = AGENTS_DIR / agent_id / "materials"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(agent_dir / f"catalog_{timestamp}.pdf")

        try:
            font_config = FontConfiguration()
            html = HTML(string=html_content)
            html.write_pdf(output_path, font_config=font_config)
            print(f"PDF каталог создан: {output_path}")
            return output_path
        except Exception as e:
            print(f"Ошибка генерации PDF: {e}")
            return None

    def _render_catalog_html(self, context: Dict[str, Any]) -> str:
        """Рендеринг HTML для каталога."""
        colors = context.get('colors', {})

        template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&family=Montserrat:wght@600;700&display=swap');

        @page {{
            size: A4;
            margin: 15mm;
        }}

        body {{
            font-family: 'Open Sans', Arial, sans-serif;
            color: {colors.get('text', '#2c3e50')};
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }}

        .header {{
            background: linear-gradient(135deg, {colors.get('primary', '#1a5f7a')}, {colors.get('accent', '#3498db')});
            color: white;
            padding: 30px;
            margin: -15mm -15mm 20px -15mm;
            text-align: center;
        }}

        .header h1 {{
            font-family: 'Montserrat', Arial, sans-serif;
            margin: 0 0 10px 0;
            font-size: 28px;
        }}

        .header .tagline {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .logo {{
            max-height: 60px;
            margin-bottom: 15px;
        }}

        .catalog-title {{
            text-align: center;
            font-family: 'Montserrat', Arial, sans-serif;
            color: {colors.get('primary', '#1a5f7a')};
            font-size: 24px;
            margin: 30px 0;
            padding-bottom: 15px;
            border-bottom: 3px solid {colors.get('secondary', '#c9a227')};
        }}

        .product-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}

        .product-card {{
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            page-break-inside: avoid;
        }}

        .product-image {{
            width: 100%;
            height: 150px;
            background: {colors.get('background_alt', '#f8f9fa')};
            display: flex;
            align-items: center;
            justify-content: center;
            color: {colors.get('text_light', '#7f8c8d')};
        }}

        .product-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .product-content {{
            padding: 15px;
        }}

        .product-name {{
            font-family: 'Montserrat', Arial, sans-serif;
            font-size: 16px;
            font-weight: 600;
            color: {colors.get('primary', '#1a5f7a')};
            margin: 0 0 8px 0;
        }}

        .product-description {{
            font-size: 12px;
            color: {colors.get('text_light', '#7f8c8d')};
            margin: 0 0 10px 0;
        }}

        .product-price {{
            font-size: 18px;
            font-weight: 700;
            color: {colors.get('secondary', '#c9a227')};
        }}

        .product-details {{
            font-size: 11px;
            color: {colors.get('text_light', '#7f8c8d')};
            margin-top: 8px;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid {colors.get('primary', '#1a5f7a')};
            text-align: center;
            font-size: 12px;
        }}

        .footer .contacts {{
            margin: 15px 0;
        }}

        .footer .contact-item {{
            display: inline-block;
            margin: 0 15px;
        }}
    </style>
</head>
<body>
    <div class="header">
        {"<img class='logo' src='data:image/png;base64," + context.get('logo_base64', '') + "' />" if context.get('logo_base64') else ""}
        <h1>{context.get('company_name', 'Company')}</h1>
        <div class="tagline">{context.get('brand', {}).get('tagline', '')}</div>
    </div>

    <h2 class="catalog-title">{context.get('title', 'Catalog')}</h2>

    <div class="product-grid">
"""

        for product in context.get('products', []):
            template += f"""
        <div class="product-card">
            <div class="product-image">
                {"<img src='" + product.get('image', '') + "' />" if product.get('image') else "No Image"}
            </div>
            <div class="product-content">
                <h3 class="product-name">{product.get('name', 'Product')}</h3>
                <p class="product-description">{product.get('description', '')[:100]}...</p>
                <div class="product-price">AED {product.get('price', 0):,.0f}</div>
                <div class="product-details">
                    {product.get('duration', '')} | {product.get('category', '')}
                </div>
            </div>
        </div>
"""

        template += f"""
    </div>

    <div class="footer">
        <div class="contacts">
            <span class="contact-item">{context.get('phone', '')}</span>
            <span class="contact-item">{context.get('email', '')}</span>
            <span class="contact-item">{context.get('website', '')}</span>
        </div>
        <div>Generated: {context.get('generated_at', '')} | {context.get('company_name', '')}</div>
    </div>
</body>
</html>
"""
        return template

    def generate_voucher(
        self,
        agent_id: str,
        voucher_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Генерация ваучера с брендом агента."""
        if not WEASYPRINT_AVAILABLE:
            print("Требуется weasyprint")
            return None

        brand = self.agent_manager.get_agent(agent_id)
        if not brand:
            return None

        context = self._get_brand_context(agent_id)
        context.update({
            "voucher": voucher_data,
            "voucher_code": voucher_data.get('code', secrets.token_hex(6).upper()),
            "generated_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
        })

        # Генерация QR-кода
        if QRCODE_AVAILABLE:
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr_data = f"VOUCHER:{context['voucher_code']}|{brand.subdomain}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            context['qr_base64'] = base64.b64encode(buffer.getvalue()).decode()

        html_content = self._render_voucher_html(context)

        if not output_path:
            agent_dir = AGENTS_DIR / agent_id / "materials"
            output_path = str(agent_dir / f"voucher_{context['voucher_code']}.pdf")

        try:
            html = HTML(string=html_content)
            html.write_pdf(output_path)
            print(f"Ваучер создан: {output_path}")
            return output_path
        except Exception as e:
            print(f"Ошибка генерации ваучера: {e}")
            return None

    def _render_voucher_html(self, context: Dict[str, Any]) -> str:
        """Рендеринг HTML для ваучера."""
        colors = context.get('colors', {})
        voucher = context.get('voucher', {})

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A5 landscape; margin: 10mm; }}

        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: white;
        }}

        .voucher {{
            border: 3px solid {colors.get('primary', '#1a5f7a')};
            border-radius: 15px;
            padding: 20px;
            position: relative;
            background: linear-gradient(135deg, white 0%, {colors.get('background_alt', '#f8f9fa')} 100%);
        }}

        .voucher-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid {colors.get('secondary', '#c9a227')};
            padding-bottom: 15px;
            margin-bottom: 15px;
        }}

        .logo {{ max-height: 50px; }}

        .voucher-code {{
            background: {colors.get('primary', '#1a5f7a')};
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
        }}

        .voucher-title {{
            color: {colors.get('primary', '#1a5f7a')};
            font-size: 22px;
            font-weight: bold;
            margin: 0 0 10px 0;
        }}

        .voucher-service {{
            font-size: 18px;
            color: {colors.get('text', '#2c3e50')};
            margin-bottom: 15px;
        }}

        .voucher-details {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            font-size: 13px;
        }}

        .detail-item {{
            display: flex;
        }}

        .detail-label {{
            color: {colors.get('text_light', '#7f8c8d')};
            min-width: 80px;
        }}

        .detail-value {{
            color: {colors.get('text', '#2c3e50')};
            font-weight: 500;
        }}

        .qr-section {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            text-align: center;
        }}

        .qr-code {{
            width: 80px;
            height: 80px;
        }}

        .voucher-footer {{
            margin-top: 20px;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
            font-size: 11px;
            color: {colors.get('text_light', '#7f8c8d')};
            display: flex;
            justify-content: space-between;
        }}
    </style>
</head>
<body>
    <div class="voucher">
        <div class="voucher-header">
            <div>
                {"<img class='logo' src='data:image/png;base64," + context.get('logo_base64', '') + "' />" if context.get('logo_base64') else f"<strong>{context.get('company_name', '')}</strong>"}
            </div>
            <div class="voucher-code">{context.get('voucher_code', '')}</div>
        </div>

        <h2 class="voucher-title">VOUCHER</h2>
        <div class="voucher-service">{voucher.get('service_name', 'Service')}</div>

        <div class="voucher-details">
            <div class="detail-item">
                <span class="detail-label">Guest:</span>
                <span class="detail-value">{voucher.get('guest_name', '')}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Date:</span>
                <span class="detail-value">{voucher.get('date', '')}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Time:</span>
                <span class="detail-value">{voucher.get('time', '')}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Pax:</span>
                <span class="detail-value">{voucher.get('pax', 1)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Pickup:</span>
                <span class="detail-value">{voucher.get('pickup_location', '')}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Contact:</span>
                <span class="detail-value">{voucher.get('contact_phone', context.get('phone', ''))}</span>
            </div>
        </div>

        {"<div class='qr-section'><img class='qr-code' src='data:image/png;base64," + context.get('qr_base64', '') + "' /></div>" if context.get('qr_base64') else ""}

        <div class="voucher-footer">
            <span>{context.get('phone', '')} | {context.get('email', '')}</span>
            <span>Generated: {context.get('generated_at', '')}</span>
        </div>
    </div>
</body>
</html>
"""

    def generate_invoice(
        self,
        agent_id: str,
        invoice_data: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Генерация инвойса с брендом агента."""
        if not WEASYPRINT_AVAILABLE:
            print("Требуется weasyprint")
            return None

        brand = self.agent_manager.get_agent(agent_id)
        if not brand:
            return None

        # Генерация номера инвойса
        invoice_number = invoice_data.get('invoice_number') or self._generate_invoice_number(agent_id)

        context = self._get_brand_context(agent_id)
        context.update({
            "invoice": invoice_data,
            "invoice_number": invoice_number,
            "invoice_date": invoice_data.get('date', datetime.now().strftime("%d.%m.%Y")),
            "due_date": invoice_data.get('due_date', (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")),
            "items": invoice_data.get('items', []),
            "subtotal": sum(item.get('amount', 0) for item in invoice_data.get('items', [])),
            "vat_rate": invoice_data.get('vat_rate', 5),
            "generated_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
        })

        context['vat_amount'] = context['subtotal'] * context['vat_rate'] / 100
        context['total'] = context['subtotal'] + context['vat_amount']

        html_content = self._render_invoice_html(context)

        if not output_path:
            agent_dir = AGENTS_DIR / agent_id / "materials"
            output_path = str(agent_dir / f"invoice_{invoice_number}.pdf")

        try:
            html = HTML(string=html_content)
            html.write_pdf(output_path)
            print(f"Инвойс создан: {output_path}")
            return output_path
        except Exception as e:
            print(f"Ошибка генерации инвойса: {e}")
            return None

    def _generate_invoice_number(self, agent_id: str) -> str:
        """Генерация номера инвойса."""
        prefix = agent_id[:3].upper()
        year = datetime.now().year
        seq = secrets.randbelow(9000) + 1000
        return f"{prefix}-{year}-{seq}"

    def _render_invoice_html(self, context: Dict[str, Any]) -> str:
        """Рендеринг HTML для инвойса."""
        colors = context.get('colors', {})
        invoice = context.get('invoice', {})
        brand_data = context.get('brand', {})

        items_html = ""
        for i, item in enumerate(context.get('items', []), 1):
            items_html += f"""
            <tr>
                <td>{i}</td>
                <td>{item.get('description', '')}</td>
                <td style="text-align: center;">{item.get('quantity', 1)}</td>
                <td style="text-align: right;">AED {item.get('unit_price', 0):,.2f}</td>
                <td style="text-align: right;">AED {item.get('amount', 0):,.2f}</td>
            </tr>
"""

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A4; margin: 15mm; }}

        body {{
            font-family: Arial, sans-serif;
            color: {colors.get('text', '#2c3e50')};
            line-height: 1.5;
            margin: 0;
            padding: 0;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid {colors.get('primary', '#1a5f7a')};
        }}

        .logo {{ max-height: 60px; }}

        .company-info {{
            text-align: right;
            font-size: 12px;
        }}

        .company-name {{
            font-size: 18px;
            font-weight: bold;
            color: {colors.get('primary', '#1a5f7a')};
            margin-bottom: 5px;
        }}

        .invoice-title {{
            background: {colors.get('primary', '#1a5f7a')};
            color: white;
            padding: 15px 20px;
            margin: 0 -15mm;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .invoice-title h1 {{
            margin: 0;
            font-size: 24px;
        }}

        .invoice-number {{
            font-size: 14px;
        }}

        .parties {{
            display: flex;
            justify-content: space-between;
            margin: 30px 0;
        }}

        .party {{
            width: 45%;
        }}

        .party-title {{
            font-weight: bold;
            color: {colors.get('primary', '#1a5f7a')};
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 2px solid {colors.get('secondary', '#c9a227')};
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th {{
            background: {colors.get('primary', '#1a5f7a')};
            color: white;
            padding: 12px;
            text-align: left;
            font-size: 13px;
        }}

        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 13px;
        }}

        .totals {{
            width: 300px;
            margin-left: auto;
            margin-top: 20px;
        }}

        .total-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }}

        .total-final {{
            background: {colors.get('primary', '#1a5f7a')};
            color: white;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
            margin-top: 10px;
        }}

        .bank-details {{
            margin-top: 30px;
            padding: 15px;
            background: {colors.get('background_alt', '#f8f9fa')};
            border-radius: 5px;
            font-size: 12px;
        }}

        .bank-details h4 {{
            margin: 0 0 10px 0;
            color: {colors.get('primary', '#1a5f7a')};
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            font-size: 11px;
            color: {colors.get('text_light', '#7f8c8d')};
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            {"<img class='logo' src='data:image/png;base64," + context.get('logo_base64', '') + "' />" if context.get('logo_base64') else ""}
        </div>
        <div class="company-info">
            <div class="company-name">{context.get('company_name', '')}</div>
            <div>{', '.join(context.get('address', []))}</div>
            <div>Tel: {context.get('phone', '')} | Email: {context.get('email', '')}</div>
            {"<div>TRN: " + brand_data.get('trn', '') + "</div>" if brand_data.get('trn') else ""}
        </div>
    </div>

    <div class="invoice-title">
        <h1>TAX INVOICE</h1>
        <div class="invoice-number">
            <div>Invoice #: {context.get('invoice_number', '')}</div>
            <div>Date: {context.get('invoice_date', '')}</div>
            <div>Due: {context.get('due_date', '')}</div>
        </div>
    </div>

    <div class="parties">
        <div class="party">
            <div class="party-title">Bill To:</div>
            <div><strong>{invoice.get('client_name', '')}</strong></div>
            <div>{invoice.get('client_address', '')}</div>
            <div>{invoice.get('client_email', '')}</div>
            <div>{invoice.get('client_phone', '')}</div>
        </div>
        <div class="party">
            <div class="party-title">Reference:</div>
            <div>Booking Ref: {invoice.get('booking_ref', '')}</div>
            <div>Service Date: {invoice.get('service_date', '')}</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th style="width: 40px;">#</th>
                <th>Description</th>
                <th style="width: 60px; text-align: center;">Qty</th>
                <th style="width: 100px; text-align: right;">Unit Price</th>
                <th style="width: 100px; text-align: right;">Amount</th>
            </tr>
        </thead>
        <tbody>
            {items_html}
        </tbody>
    </table>

    <div class="totals">
        <div class="total-row">
            <span>Subtotal:</span>
            <span>AED {context.get('subtotal', 0):,.2f}</span>
        </div>
        <div class="total-row">
            <span>VAT ({context.get('vat_rate', 5)}%):</span>
            <span>AED {context.get('vat_amount', 0):,.2f}</span>
        </div>
        <div class="total-final">
            <span>TOTAL:</span>
            <span>AED {context.get('total', 0):,.2f}</span>
        </div>
    </div>

    {"<div class='bank-details'><h4>Bank Details:</h4><div>Bank: " + brand_data.get('bank_details', {}).get('bank_name', '') + "</div><div>Account: " + brand_data.get('bank_details', {}).get('account_number', '') + "</div><div>IBAN: " + brand_data.get('bank_details', {}).get('iban', '') + "</div><div>SWIFT: " + brand_data.get('bank_details', {}).get('swift', '') + "</div></div>" if brand_data.get('bank_details') else ""}

    <div class="footer">
        <p>Thank you for your business!</p>
        <p>{context.get('company_name', '')} | {context.get('website', '')} | Generated: {context.get('generated_at', '')}</p>
    </div>
</body>
</html>
"""

    def generate_email_template(
        self,
        agent_id: str,
        template_type: str,
        context_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Генерация email шаблона с брендом."""
        brand = self.agent_manager.get_agent(agent_id)
        if not brand:
            return {}

        templates = {
            "booking_confirmation": {
                "subject": f"Booking Confirmation - {context_data.get('booking_ref', '')} | {brand.company_name}",
                "body": self._email_booking_confirmation(brand, context_data),
            },
            "payment_reminder": {
                "subject": f"Payment Reminder - Invoice {context_data.get('invoice_number', '')} | {brand.company_name}",
                "body": self._email_payment_reminder(brand, context_data),
            },
            "voucher_delivery": {
                "subject": f"Your Voucher - {context_data.get('service_name', '')} | {brand.company_name}",
                "body": self._email_voucher_delivery(brand, context_data),
            },
            "welcome": {
                "subject": f"Welcome to {brand.company_name}!",
                "body": self._email_welcome(brand, context_data),
            },
        }

        return templates.get(template_type, {})

    def _email_booking_confirmation(self, brand: BrandSettings, data: Dict) -> str:
        """Email подтверждения бронирования."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #2c3e50; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {brand.colors.get('primary', '#1a5f7a')}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px 20px; }}
        .booking-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ background: #f1f1f1; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{brand.company_name}</h1>
            <p>Booking Confirmation</p>
        </div>
        <div class="content">
            <p>Dear {data.get('client_name', 'Guest')},</p>
            <p>Thank you for your booking! We are pleased to confirm your reservation.</p>

            <div class="booking-box">
                <h3>Booking Details</h3>
                <p><strong>Reference:</strong> {data.get('booking_ref', '')}</p>
                <p><strong>Service:</strong> {data.get('service_name', '')}</p>
                <p><strong>Date:</strong> {data.get('service_date', '')}</p>
                <p><strong>Time:</strong> {data.get('service_time', '')}</p>
                <p><strong>Guests:</strong> {data.get('pax', 1)}</p>
                <p><strong>Total:</strong> AED {data.get('total', 0):,.2f}</p>
            </div>

            <p>If you have any questions, please contact us:</p>
            <p>Phone: {brand.phone}<br>Email: {brand.email}</p>

            <p>Best regards,<br>{brand.company_name} Team</p>
        </div>
        <div class="footer">
            <p>{brand.company_name} | {brand.website}</p>
        </div>
    </div>
</body>
</html>
"""

    def _email_payment_reminder(self, brand: BrandSettings, data: Dict) -> str:
        """Email напоминания об оплате."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #2c3e50; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {brand.colors.get('primary', '#1a5f7a')}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px 20px; }}
        .amount-box {{ background: {brand.colors.get('secondary', '#c9a227')}; color: white; padding: 20px; text-align: center; border-radius: 8px; font-size: 24px; }}
        .footer {{ background: #f1f1f1; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{brand.company_name}</h1>
            <p>Payment Reminder</p>
        </div>
        <div class="content">
            <p>Dear {data.get('client_name', 'Client')},</p>
            <p>This is a friendly reminder that payment for the following invoice is due:</p>

            <p><strong>Invoice #:</strong> {data.get('invoice_number', '')}<br>
            <strong>Due Date:</strong> {data.get('due_date', '')}</p>

            <div class="amount-box">
                Amount Due: AED {data.get('amount', 0):,.2f}
            </div>

            <p style="margin-top: 20px;">Please ensure payment is made by the due date to avoid any delays.</p>

            <p>Best regards,<br>{brand.company_name}</p>
        </div>
        <div class="footer">
            <p>{brand.phone} | {brand.email}</p>
        </div>
    </div>
</body>
</html>
"""

    def _email_voucher_delivery(self, brand: BrandSettings, data: Dict) -> str:
        """Email с ваучером."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #2c3e50; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {brand.colors.get('primary', '#1a5f7a')}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 30px 20px; }}
        .voucher-code {{ background: {brand.colors.get('secondary', '#c9a227')}; color: white; padding: 15px; text-align: center; border-radius: 8px; font-size: 20px; font-weight: bold; letter-spacing: 3px; }}
        .footer {{ background: #f1f1f1; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{brand.company_name}</h1>
            <p>Your Voucher</p>
        </div>
        <div class="content">
            <p>Dear {data.get('guest_name', 'Guest')},</p>
            <p>Please find attached your voucher for:</p>

            <h2>{data.get('service_name', '')}</h2>
            <p><strong>Date:</strong> {data.get('date', '')}<br>
            <strong>Time:</strong> {data.get('time', '')}</p>

            <div class="voucher-code">
                {data.get('voucher_code', '')}
            </div>

            <p style="margin-top: 20px;">Please present this voucher (printed or on your phone) upon arrival.</p>

            <p>For any questions, contact us at {brand.phone}</p>

            <p>Have a wonderful experience!<br>{brand.company_name} Team</p>
        </div>
        <div class="footer">
            <p>{brand.website}</p>
        </div>
    </div>
</body>
</html>
"""

    def _email_welcome(self, brand: BrandSettings, data: Dict) -> str:
        """Приветственный email."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #2c3e50; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {brand.colors.get('primary', '#1a5f7a')}; color: white; padding: 40px 20px; text-align: center; }}
        .content {{ padding: 30px 20px; }}
        .cta-button {{ display: inline-block; background: {brand.colors.get('secondary', '#c9a227')}; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
        .footer {{ background: #f1f1f1; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to {brand.company_name}!</h1>
            <p>{brand.tagline}</p>
        </div>
        <div class="content">
            <p>Dear {data.get('name', 'Friend')},</p>
            <p>Thank you for joining us! We're excited to help you discover amazing experiences in the UAE.</p>

            <p>With {brand.company_name}, you can:</p>
            <ul>
                <li>Book exclusive tours and excursions</li>
                <li>Arrange private transfers</li>
                <li>Get tickets to top attractions</li>
                <li>And much more!</li>
            </ul>

            <p style="text-align: center; margin: 30px 0;">
                <a href="{brand.website}" class="cta-button">Explore Our Services</a>
            </p>

            <p>Questions? We're here to help!<br>
            Call: {brand.phone}<br>
            Email: {brand.email}</p>

            <p>Best regards,<br>{brand.company_name} Team</p>
        </div>
        <div class="footer">
            <p>{brand.website}</p>
        </div>
    </div>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАТОР ВИДЖЕТОВ
# ═══════════════════════════════════════════════════════════════

class WidgetGenerator:
    """Генерация встраиваемых виджетов бронирования."""

    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager

    def create_widget(
        self,
        agent_id: str,
        settings: Optional[WidgetSettings] = None
    ) -> Dict[str, Any]:
        """Создание виджета для агента."""
        brand = self.agent_manager.get_agent(agent_id)
        if not brand:
            return {"error": "Agent not found"}

        widget_id = settings.widget_id if settings else secrets.token_hex(8)

        if not settings:
            settings = WidgetSettings(
                agent_id=agent_id,
                widget_id=widget_id,
            )
        else:
            settings.agent_id = agent_id
            settings.widget_id = widget_id

        # Сохраняем настройки виджета
        widget_dir = WIDGETS_DIR / agent_id
        widget_dir.mkdir(parents=True, exist_ok=True)

        widget_file = widget_dir / f"{widget_id}.json"
        with open(widget_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(settings), f, ensure_ascii=False, indent=2)

        # Генерируем код для встраивания
        embed_codes = self._generate_embed_codes(brand, settings)

        return {
            "widget_id": widget_id,
            "agent_id": agent_id,
            "settings": asdict(settings),
            "embed_codes": embed_codes,
        }

    def _generate_embed_codes(
        self,
        brand: BrandSettings,
        settings: WidgetSettings
    ) -> Dict[str, str]:
        """Генерация кодов для встраивания."""
        widget_url = f"{BASE_WIDGET_URL}/w/{settings.widget_id}"

        # Iframe код
        iframe_code = f"""<!-- {brand.company_name} Booking Widget -->
<iframe
    src="{widget_url}"
    width="{settings.width}"
    height="{settings.height}"
    style="border: none; min-width: {settings.min_width}; max-width: {settings.max_width};"
    allow="payment"
    loading="lazy"
></iframe>
"""

        # JavaScript код
        js_code = f"""<!-- {brand.company_name} Booking Widget -->
<div id="booking-widget-{settings.widget_id}"></div>
<script>
(function() {{
    var config = {{
        widgetId: '{settings.widget_id}',
        containerId: 'booking-widget-{settings.widget_id}',
        type: '{settings.widget_type}',
        width: '{settings.width}',
        height: '{settings.height}',
        language: '{settings.default_language}',
        theme: {{
            primaryColor: '{brand.colors.get("primary", "#1a5f7a")}',
            secondaryColor: '{brand.colors.get("secondary", "#c9a227")}',
            fontFamily: '{brand.fonts.get("body", "Arial, sans-serif")}'
        }},
        features: {{
            booking: {str(settings.enable_booking).lower()},
            cart: {str(settings.enable_cart).lower()},
            reviews: {str(settings.enable_reviews).lower()},
            chat: {str(settings.enable_chat).lower()}
        }},
        callbacks: {{
            onReady: function() {{ console.log('Widget ready'); }},
            onBooking: function(data) {{ console.log('Booking:', data); }},
            onError: function(error) {{ console.error('Widget error:', error); }}
        }}
    }};

    var script = document.createElement('script');
    script.src = '{BASE_WIDGET_URL}/widget.js';
    script.onload = function() {{
        if (window.BookingWidget) {{
            window.BookingWidget.init(config);
        }}
    }};
    document.head.appendChild(script);
}})();
</script>
"""

        # Floating button код
        floating_code = f"""<!-- {brand.company_name} Floating Button -->
<script>
(function() {{
    var btn = document.createElement('div');
    btn.id = 'booking-float-btn';
    btn.innerHTML = '<span>Book Now</span>';
    btn.style.cssText = 'position:fixed;{settings.position.replace("-", ":")}:20px;background:{brand.colors.get("primary", "#1a5f7a")};color:white;padding:15px 25px;border-radius:30px;cursor:pointer;font-family:Arial;font-weight:bold;box-shadow:0 4px 15px rgba(0,0,0,0.2);z-index:9999;transition:transform 0.3s;';
    btn.onmouseover = function() {{ this.style.transform = 'scale(1.05)'; }};
    btn.onmouseout = function() {{ this.style.transform = 'scale(1)'; }};
    btn.onclick = function() {{
        var popup = document.createElement('div');
        popup.innerHTML = '<iframe src="{widget_url}" style="width:100%;height:100%;border:none;"></iframe><button onclick="this.parentElement.remove()" style="position:absolute;top:10px;right:10px;background:white;border:none;font-size:24px;cursor:pointer;">&times;</button>';
        popup.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:90%;max-width:500px;height:80vh;background:white;border-radius:10px;box-shadow:0 10px 40px rgba(0,0,0,0.3);z-index:10000;';
        document.body.appendChild(popup);
    }};
    document.body.appendChild(btn);
}})();
</script>
"""

        # React компонент
        react_code = f"""// {brand.company_name} Booking Widget - React Component
import React, {{ useEffect, useRef }} from 'react';

const BookingWidget = ({{ onBooking, onReady }}) => {{
    const containerRef = useRef(null);

    useEffect(() => {{
        const script = document.createElement('script');
        script.src = '{BASE_WIDGET_URL}/widget.js';
        script.onload = () => {{
            if (window.BookingWidget) {{
                window.BookingWidget.init({{
                    widgetId: '{settings.widget_id}',
                    container: containerRef.current,
                    callbacks: {{ onBooking, onReady }}
                }});
            }}
        }};
        document.head.appendChild(script);

        return () => {{
            if (window.BookingWidget) {{
                window.BookingWidget.destroy();
            }}
        }};
    }}, []);

    return <div ref={{containerRef}} style={{{{ width: '{settings.width}', height: '{settings.height}' }}}} />;
}};

export default BookingWidget;
"""

        return {
            "iframe": iframe_code,
            "javascript": js_code,
            "floating": floating_code,
            "react": react_code,
            "direct_url": widget_url,
        }

    def generate_custom_css(
        self,
        agent_id: str,
        widget_id: str,
        custom_styles: Dict[str, Any]
    ) -> str:
        """Генерация кастомного CSS для виджета."""
        brand = self.agent_manager.get_agent(agent_id)
        if not brand:
            return ""

        colors = custom_styles.get('colors', brand.colors)
        fonts = custom_styles.get('fonts', brand.fonts)

        css = f"""
/* Custom Widget Styles for {brand.company_name} */
.booking-widget {{
    --primary-color: {colors.get('primary', '#1a5f7a')};
    --secondary-color: {colors.get('secondary', '#c9a227')};
    --accent-color: {colors.get('accent', '#3498db')};
    --text-color: {colors.get('text', '#2c3e50')};
    --text-light: {colors.get('text_light', '#7f8c8d')};
    --background: {colors.get('background', '#ffffff')};
    --background-alt: {colors.get('background_alt', '#f8f9fa')};
    --success-color: {colors.get('success', '#27ae60')};
    --warning-color: {colors.get('warning', '#f39c12')};
    --error-color: {colors.get('error', '#e74c3c')};

    --font-heading: {fonts.get('heading', 'Montserrat, Arial, sans-serif')};
    --font-body: {fonts.get('body', 'Open Sans, Arial, sans-serif')};
    --font-accent: {fonts.get('accent', 'Georgia, serif')};

    font-family: var(--font-body);
    color: var(--text-color);
    background: var(--background);
}}

.booking-widget .header {{
    background: var(--primary-color);
    color: white;
}}

.booking-widget .btn-primary {{
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 5px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.3s;
}}

.booking-widget .btn-primary:hover {{
    opacity: 0.9;
}}

.booking-widget .btn-secondary {{
    background: var(--secondary-color);
    color: white;
}}

.booking-widget .price {{
    color: var(--secondary-color);
    font-size: 1.5em;
    font-weight: 700;
}}

.booking-widget .card {{
    background: var(--background);
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    overflow: hidden;
    transition: box-shadow 0.3s;
}}

.booking-widget .card:hover {{
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}}

.booking-widget h1, .booking-widget h2, .booking-widget h3 {{
    font-family: var(--font-heading);
    color: var(--primary-color);
}}

.booking-widget .success {{
    color: var(--success-color);
}}

.booking-widget .error {{
    color: var(--error-color);
}}
"""

        # Сохраняем CSS
        widget_dir = WIDGETS_DIR / agent_id
        css_file = widget_dir / f"{widget_id}_custom.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css)

        return css


# ═══════════════════════════════════════════════════════════════
# ГЕНЕРАТОР LANDING PAGE
# ═══════════════════════════════════════════════════════════════

class LandingPageGenerator:
    """Генератор landing pages для агентов."""

    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager

    def create_landing_page(
        self,
        agent_id: str,
        settings: LandingPageSettings,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Создание landing page."""
        brand = self.agent_manager.get_agent(agent_id)
        if not brand:
            return {"error": "Agent not found"}

        page_id = settings.page_id or secrets.token_hex(6)
        settings.page_id = page_id
        settings.agent_id = agent_id

        # Генерируем HTML
        html_content = self._render_landing_page(brand, settings, products)

        # Сохраняем
        page_dir = LANDING_DIR / agent_id
        page_dir.mkdir(parents=True, exist_ok=True)

        html_file = page_dir / f"{page_id}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        settings_file = page_dir / f"{page_id}_settings.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(settings), f, ensure_ascii=False, indent=2)

        # URL страницы
        page_url = f"https://{brand.subdomain}.marselluxury.ae/lp/{page_id}"
        if brand.custom_domain:
            page_url = f"https://{brand.custom_domain}/lp/{page_id}"

        return {
            "page_id": page_id,
            "agent_id": agent_id,
            "html_file": str(html_file),
            "url": page_url,
            "settings": asdict(settings),
        }

    def _render_landing_page(
        self,
        brand: BrandSettings,
        settings: LandingPageSettings,
        products: List[Dict[str, Any]]
    ) -> str:
        """Рендеринг HTML landing page."""
        colors = brand.colors

        # Секции продуктов
        products_html = ""
        for product in products[:8]:
            products_html += f"""
            <div class="product-card">
                <div class="product-image" style="background-image: url('{product.get('image', '')}');">
                    {"<span class='badge'>" + product.get('badge', '') + "</span>" if product.get('badge') else ""}
                </div>
                <div class="product-content">
                    <h3>{product.get('name', '')}</h3>
                    <p>{product.get('description', '')[:120]}...</p>
                    <div class="product-meta">
                        <span class="duration">{product.get('duration', '')}</span>
                        <span class="price">from AED {product.get('price', 0):,.0f}</span>
                    </div>
                    <a href="{product.get('url', '#')}" class="btn btn-outline">View Details</a>
                </div>
            </div>
"""

        # Дополнительные секции
        sections_html = ""
        for section in settings.sections:
            section_type = section.get('type', 'text')
            if section_type == 'text':
                sections_html += f"""
                <section class="section section-text">
                    <div class="container">
                        <h2>{section.get('title', '')}</h2>
                        <p>{section.get('content', '')}</p>
                    </div>
                </section>
"""
            elif section_type == 'features':
                features_html = ""
                for feature in section.get('items', []):
                    features_html += f"""
                    <div class="feature">
                        <div class="feature-icon">{feature.get('icon', '★')}</div>
                        <h4>{feature.get('title', '')}</h4>
                        <p>{feature.get('description', '')}</p>
                    </div>
"""
                sections_html += f"""
                <section class="section section-features">
                    <div class="container">
                        <h2>{section.get('title', 'Why Choose Us')}</h2>
                        <div class="features-grid">{features_html}</div>
                    </div>
                </section>
"""
            elif section_type == 'testimonials':
                testimonials_html = ""
                for testimonial in section.get('items', []):
                    testimonials_html += f"""
                    <div class="testimonial">
                        <p>"{testimonial.get('text', '')}"</p>
                        <div class="author">— {testimonial.get('author', '')}</div>
                    </div>
"""
                sections_html += f"""
                <section class="section section-testimonials">
                    <div class="container">
                        <h2>{section.get('title', 'What Our Guests Say')}</h2>
                        <div class="testimonials-grid">{testimonials_html}</div>
                    </div>
                </section>
"""

        # Форма бронирования
        form_fields_html = ""
        for field in settings.form_fields:
            field_config = {
                "name": {"type": "text", "label": "Your Name", "placeholder": "John Doe", "required": True},
                "phone": {"type": "tel", "label": "Phone", "placeholder": "+971 50 123 4567", "required": True},
                "email": {"type": "email", "label": "Email", "placeholder": "your@email.com", "required": True},
                "date": {"type": "date", "label": "Preferred Date", "required": True},
                "guests": {"type": "number", "label": "Number of Guests", "placeholder": "2", "required": False},
                "message": {"type": "textarea", "label": "Message", "placeholder": "Any special requests...", "required": False},
            }

            config = field_config.get(field, {"type": "text", "label": field.title(), "required": False})
            required = "required" if config.get("required") else ""

            if config["type"] == "textarea":
                form_fields_html += f"""
                <div class="form-group">
                    <label>{config['label']}</label>
                    <textarea name="{field}" placeholder="{config.get('placeholder', '')}" {required}></textarea>
                </div>
"""
            else:
                form_fields_html += f"""
                <div class="form-group">
                    <label>{config['label']}</label>
                    <input type="{config['type']}" name="{field}" placeholder="{config.get('placeholder', '')}" {required}>
                </div>
"""

        # Footer links
        footer_links_html = ""
        for link in settings.footer_links:
            footer_links_html += f'<a href="{link.get("url", "#")}">{link.get("text", "")}</a>'

        # Полный HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{settings.title or brand.company_name}</title>
    <meta name="description" content="{settings.meta_description}">
    <meta name="keywords" content="{', '.join(settings.meta_keywords)}">

    <!-- Open Graph -->
    <meta property="og:title" content="{settings.title or brand.company_name}">
    <meta property="og:description" content="{settings.meta_description}">
    {"<meta property='og:image' content='" + settings.og_image + "'>" if settings.og_image else ""}
    <meta property="og:type" content="website">

    <!-- Canonical -->
    {"<link rel='canonical' href='" + settings.canonical_url + "'>" if settings.canonical_url else ""}

    <!-- Favicon -->
    {"<link rel='icon' href='" + brand.favicon_path + "'>" if brand.favicon_path else ""}

    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Open+Sans:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        :root {{
            --primary: {colors.get('primary', '#1a5f7a')};
            --secondary: {colors.get('secondary', '#c9a227')};
            --accent: {colors.get('accent', '#3498db')};
            --text: {colors.get('text', '#2c3e50')};
            --text-light: {colors.get('text_light', '#7f8c8d')};
            --bg: {colors.get('background', '#ffffff')};
            --bg-alt: {colors.get('background_alt', '#f8f9fa')};
        }}

        body {{
            font-family: 'Open Sans', Arial, sans-serif;
            color: var(--text);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        /* Header */
        .header {{
            background: white;
            padding: 15px 0;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header .container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            font-family: 'Montserrat', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: var(--primary);
            text-decoration: none;
        }}

        .logo img {{
            max-height: 50px;
        }}

        .nav a {{
            color: var(--text);
            text-decoration: none;
            margin-left: 30px;
            font-weight: 500;
            transition: color 0.3s;
        }}

        .nav a:hover {{
            color: var(--primary);
        }}

        /* Hero */
        .hero {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            color: white;
            padding: 150px 0 100px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('{settings.hero_image}') center/cover;
            opacity: 0.3;
        }}

        .hero .container {{
            position: relative;
            z-index: 1;
        }}

        .hero h1 {{
            font-family: 'Montserrat', sans-serif;
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        .hero p {{
            font-size: 20px;
            max-width: 600px;
            margin: 0 auto 30px;
            opacity: 0.95;
        }}

        /* Buttons */
        .btn {{
            display: inline-block;
            padding: 15px 35px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            cursor: pointer;
            border: none;
            font-size: 16px;
        }}

        .btn-primary {{
            background: var(--secondary);
            color: white;
        }}

        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }}

        .btn-outline {{
            background: transparent;
            border: 2px solid var(--primary);
            color: var(--primary);
        }}

        .btn-outline:hover {{
            background: var(--primary);
            color: white;
        }}

        /* Sections */
        .section {{
            padding: 80px 0;
        }}

        .section h2 {{
            font-family: 'Montserrat', sans-serif;
            font-size: 36px;
            text-align: center;
            margin-bottom: 50px;
            color: var(--primary);
        }}

        .section-alt {{
            background: var(--bg-alt);
        }}

        /* Products Grid */
        .products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 30px;
        }}

        .product-card {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .product-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}

        .product-image {{
            height: 200px;
            background: var(--bg-alt) center/cover;
            position: relative;
        }}

        .product-image .badge {{
            position: absolute;
            top: 15px;
            left: 15px;
            background: var(--secondary);
            color: white;
            padding: 5px 12px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
        }}

        .product-content {{
            padding: 20px;
        }}

        .product-content h3 {{
            font-family: 'Montserrat', sans-serif;
            font-size: 18px;
            margin-bottom: 10px;
            color: var(--primary);
        }}

        .product-content p {{
            font-size: 14px;
            color: var(--text-light);
            margin-bottom: 15px;
        }}

        .product-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .product-meta .duration {{
            font-size: 13px;
            color: var(--text-light);
        }}

        .product-meta .price {{
            font-size: 18px;
            font-weight: 700;
            color: var(--secondary);
        }}

        /* Features */
        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 40px;
        }}

        .feature {{
            text-align: center;
        }}

        .feature-icon {{
            font-size: 48px;
            margin-bottom: 15px;
        }}

        .feature h4 {{
            font-family: 'Montserrat', sans-serif;
            margin-bottom: 10px;
            color: var(--primary);
        }}

        /* Testimonials */
        .testimonials-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
        }}

        .testimonial {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }}

        .testimonial p {{
            font-style: italic;
            margin-bottom: 15px;
        }}

        .testimonial .author {{
            color: var(--text-light);
            font-weight: 600;
        }}

        /* Booking Form */
        .booking-section {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            color: white;
            padding: 80px 0;
        }}

        .booking-section h2 {{
            color: white;
        }}

        .booking-form {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        .form-group label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--text);
        }}

        .form-group input,
        .form-group textarea,
        .form-group select {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}

        .form-group input:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: var(--primary);
        }}

        .form-group textarea {{
            min-height: 100px;
            resize: vertical;
        }}

        .booking-form .btn {{
            width: 100%;
            padding: 15px;
            font-size: 18px;
        }}

        /* Footer */
        .footer {{
            background: var(--primary);
            color: white;
            padding: 50px 0 30px;
        }}

        .footer-content {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 40px;
            margin-bottom: 40px;
        }}

        .footer h4 {{
            font-family: 'Montserrat', sans-serif;
            margin-bottom: 20px;
        }}

        .footer a {{
            color: rgba(255,255,255,0.8);
            text-decoration: none;
            display: block;
            margin-bottom: 10px;
            transition: color 0.3s;
        }}

        .footer a:hover {{
            color: var(--secondary);
        }}

        .footer-bottom {{
            border-top: 1px solid rgba(255,255,255,0.2);
            padding-top: 30px;
            text-align: center;
            font-size: 14px;
            opacity: 0.8;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 32px; }}
            .hero p {{ font-size: 16px; }}
            .nav {{ display: none; }}
            .section h2 {{ font-size: 28px; }}
        }}
    </style>

    <!-- Tracking -->
    {f"<script async src='https://www.googletagmanager.com/gtag/js?id={settings.google_analytics_id}'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{settings.google_analytics_id}');</script>" if hasattr(settings, 'google_analytics_id') and settings.google_analytics_id else ""}
</head>
<body>
    <header class="header">
        <div class="container">
            <a href="/" class="logo">
                {"<img src='data:image/png;base64," + brand.logo_base64 + "' alt='" + brand.company_name + "'>" if brand.logo_base64 else brand.company_name}
            </a>
            <nav class="nav">
                <a href="#services">Services</a>
                <a href="#about">About</a>
                <a href="#contact">Contact</a>
                <a href="{settings.hero_cta_url or '#booking'}" class="btn btn-primary" style="margin-left:20px;padding:10px 20px;">{settings.hero_cta_text}</a>
            </nav>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <h1>{settings.hero_title or f"Welcome to {brand.company_name}"}</h1>
            <p>{settings.hero_subtitle or brand.tagline}</p>
            <a href="{settings.hero_cta_url or '#booking'}" class="btn btn-primary">{settings.hero_cta_text}</a>
        </div>
    </section>

    <section class="section" id="services">
        <div class="container">
            <h2>Our Services</h2>
            <div class="products-grid">
                {products_html}
            </div>
        </div>
    </section>

    {sections_html}

    <section class="booking-section" id="booking">
        <div class="container">
            <h2>Book Now</h2>
            <form class="booking-form" action="{settings.form_submit_url or '#'}" method="POST">
                {form_fields_html}
                <button type="submit" class="btn btn-primary">{settings.hero_cta_text}</button>
            </form>
        </div>
    </section>

    {"<footer class='footer' id='contact'><div class='container'><div class='footer-content'><div><h4>" + brand.company_name + "</h4><p>" + brand.tagline + "</p></div><div><h4>Contact</h4><p>" + brand.phone + "</p><p>" + brand.email + "</p><p>" + ', '.join(brand.address) + "</p></div><div><h4>Links</h4>" + footer_links_html + "</div></div><div class='footer-bottom'>&copy; " + str(datetime.now().year) + " " + brand.company_name + ". All rights reserved.</div></div></footer>" if settings.show_footer else ""}
</body>
</html>
"""

        return html


# ═══════════════════════════════════════════════════════════════
# МЕНЕДЖЕР ЦЕНООБРАЗОВАНИЯ
# ═══════════════════════════════════════════════════════════════

class PricingManager:
    """Управление ценообразованием для агентов."""

    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager

    def get_pricing(self, agent_id: str) -> Optional[PricingSettings]:
        """Получение настроек ценообразования."""
        pricing_file = AGENTS_DIR / agent_id / "pricing_settings.json"
        if not pricing_file.exists():
            return None

        try:
            with open(pricing_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return PricingSettings(**data)
        except Exception as e:
            print(f"Ошибка загрузки pricing: {e}")
            return None

    def update_pricing(self, agent_id: str, **kwargs) -> Optional[PricingSettings]:
        """Обновление настроек ценообразования."""
        pricing = self.get_pricing(agent_id)
        if not pricing:
            pricing = PricingSettings(agent_id=agent_id)

        for key, value in kwargs.items():
            if hasattr(pricing, key):
                setattr(pricing, key, value)

        pricing_file = AGENTS_DIR / agent_id / "pricing_settings.json"
        with open(pricing_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(pricing), f, ensure_ascii=False, indent=2)

        return pricing

    def calculate_price(
        self,
        agent_id: str,
        base_price: float,
        category: Optional[str] = None,
        product_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Расчёт цены с наценкой агента."""
        pricing = self.get_pricing(agent_id)
        if not pricing:
            return {
                "base_price": base_price,
                "agent_price": base_price,
                "markup": 0,
                "markup_percent": 0,
            }

        # Определяем наценку
        markup_percent = pricing.default_markup_percent

        # Наценка по продукту (приоритет)
        if product_id and product_id in pricing.product_markup:
            markup_percent = pricing.product_markup[product_id]
        # Наценка по категории
        elif category and category in pricing.category_markup:
            markup_percent = pricing.category_markup[category]

        # Расчёт
        markup_amount = base_price * markup_percent / 100
        markup_amount += pricing.default_markup_fixed

        # Минимальная маржа
        min_margin = max(
            base_price * pricing.min_margin_percent / 100,
            pricing.min_margin_fixed
        )
        markup_amount = max(markup_amount, min_margin)

        agent_price = base_price + markup_amount

        # Округление
        if pricing.round_to > 0:
            if pricing.round_up:
                agent_price = (int(agent_price / pricing.round_to) + 1) * pricing.round_to
            else:
                agent_price = round(agent_price / pricing.round_to) * pricing.round_to

        return {
            "base_price": base_price,
            "agent_price": agent_price,
            "markup": agent_price - base_price,
            "markup_percent": (agent_price - base_price) / base_price * 100,
            "currency": pricing.base_currency,
            "hide_original": pricing.hide_original_prices,
        }

    def apply_pricing_to_products(
        self,
        agent_id: str,
        products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Применение ценообразования к списку продуктов."""
        pricing = self.get_pricing(agent_id)
        result = []

        for product in products:
            base_price = product.get('price', 0)
            category = product.get('category')
            product_id = product.get('id')

            price_info = self.calculate_price(agent_id, base_price, category, product_id)

            product_copy = product.copy()
            product_copy['display_price'] = price_info['agent_price']
            product_copy['original_price'] = base_price if not pricing.hide_original_prices else None
            product_copy['currency'] = price_info['currency']

            # Скрываем информацию о поставщике
            if pricing and pricing.hide_supplier_info:
                product_copy.pop('supplier', None)
                product_copy.pop('supplier_price', None)
                product_copy.pop('supplier_ref', None)

            result.append(product_copy)

        return result


# ═══════════════════════════════════════════════════════════════
# АНАЛИТИКА ПРОДАЖ
# ═══════════════════════════════════════════════════════════════

class SalesAnalytics:
    """Аналитика продаж через виджеты."""

    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager

    def _get_sales_file(self, agent_id: str) -> Path:
        """Путь к файлу продаж агента."""
        return ANALYTICS_DIR / agent_id / "sales.json"

    def _load_sales(self, agent_id: str) -> List[SalesRecord]:
        """Загрузка продаж агента."""
        sales_file = self._get_sales_file(agent_id)
        if not sales_file.exists():
            return []

        try:
            with open(sales_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [SalesRecord(**s) for s in data]
        except Exception as e:
            print(f"Ошибка загрузки продаж: {e}")
            return []

    def _save_sales(self, agent_id: str, sales: List[SalesRecord]):
        """Сохранение продаж."""
        sales_file = self._get_sales_file(agent_id)
        sales_file.parent.mkdir(parents=True, exist_ok=True)

        with open(sales_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(s) for s in sales], f, ensure_ascii=False, indent=2)

    def record_sale(self, agent_id: str, sale_data: Dict[str, Any]) -> SalesRecord:
        """Запись новой продажи."""
        sale = SalesRecord(
            sale_id=secrets.token_hex(8),
            agent_id=agent_id,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            **sale_data
        )

        sales = self._load_sales(agent_id)
        sales.append(sale)
        self._save_sales(agent_id, sales)

        return sale

    def get_sales_report(
        self,
        agent_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение отчёта о продажах."""
        sales = self._load_sales(agent_id)

        # Фильтрация по датам
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            sales = [s for s in sales if datetime.fromisoformat(s.created_at) >= start_dt]

        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            sales = [s for s in sales if datetime.fromisoformat(s.created_at) <= end_dt]

        # Расчёты
        total_sales = len(sales)
        total_revenue = sum(s.total for s in sales)
        total_markup = sum(s.agent_markup for s in sales)
        total_commission = sum(s.agent_commission for s in sales)

        # По статусам
        by_status = {}
        for sale in sales:
            by_status[sale.status] = by_status.get(sale.status, 0) + 1

        # По виджетам
        by_widget = {}
        for sale in sales:
            widget = sale.widget_id or "direct"
            if widget not in by_widget:
                by_widget[widget] = {"count": 0, "revenue": 0}
            by_widget[widget]["count"] += 1
            by_widget[widget]["revenue"] += sale.total

        # По источникам (UTM)
        by_source = {}
        for sale in sales:
            source = sale.utm_source or "direct"
            if source not in by_source:
                by_source[source] = {"count": 0, "revenue": 0}
            by_source[source]["count"] += 1
            by_source[source]["revenue"] += sale.total

        # Конверсия (приблизительная)
        # Нужны данные о посещениях для точного расчёта

        return {
            "agent_id": agent_id,
            "period": {
                "start": start_date,
                "end": end_date,
            },
            "summary": {
                "total_sales": total_sales,
                "total_revenue": total_revenue,
                "total_markup": total_markup,
                "total_commission": total_commission,
                "average_order": total_revenue / total_sales if total_sales > 0 else 0,
                "currency": "AED",
            },
            "by_status": by_status,
            "by_widget": by_widget,
            "by_source": by_source,
            "sales": [asdict(s) for s in sales[-50:]],  # Последние 50
        }

    def get_conversion_stats(
        self,
        agent_id: str,
        visits: int,
        period: str = "month"
    ) -> Dict[str, Any]:
        """Статистика конверсии."""
        sales = self._load_sales(agent_id)

        # Фильтр по периоду
        now = datetime.now()
        if period == "day":
            cutoff = now - timedelta(days=1)
        elif period == "week":
            cutoff = now - timedelta(weeks=1)
        elif period == "month":
            cutoff = now - timedelta(days=30)
        elif period == "year":
            cutoff = now - timedelta(days=365)
        else:
            cutoff = now - timedelta(days=30)

        period_sales = [s for s in sales if datetime.fromisoformat(s.created_at) >= cutoff]

        conversions = len(period_sales)
        conversion_rate = (conversions / visits * 100) if visits > 0 else 0

        return {
            "period": period,
            "visits": visits,
            "conversions": conversions,
            "conversion_rate": round(conversion_rate, 2),
            "revenue": sum(s.total for s in period_sales),
            "average_order": sum(s.total for s in period_sales) / conversions if conversions > 0 else 0,
        }


# ═══════════════════════════════════════════════════════════════
# ГЛАВНЫЙ КЛАСС WHITE LABEL
# ═══════════════════════════════════════════════════════════════

class WhiteLabelPlatform:
    """Главный класс платформы White Label."""

    def __init__(self):
        self.agent_manager = AgentManager()
        self.material_generator = MaterialGenerator(self.agent_manager)
        self.widget_generator = WidgetGenerator(self.agent_manager)
        self.landing_generator = LandingPageGenerator(self.agent_manager)
        self.pricing_manager = PricingManager(self.agent_manager)
        self.analytics = SalesAnalytics(self.agent_manager)

    def create_agent(self, company_name: str, **kwargs) -> BrandSettings:
        """Создание нового агента."""
        return self.agent_manager.create_agent(company_name, **kwargs)

    def setup_agent_brand(
        self,
        agent_id: str,
        logo_path: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
        **brand_info
    ) -> bool:
        """Настройка бренда агента."""
        success = True

        if logo_path:
            success = self.agent_manager.upload_logo(agent_id, logo_path) and success

        if colors:
            success = self.agent_manager.set_colors(agent_id, colors) and success

        if brand_info:
            self.agent_manager.update_agent(agent_id, **brand_info)

        return success

    def generate_catalog(
        self,
        agent_id: str,
        products: List[Dict[str, Any]],
        title: str = "Product Catalog"
    ) -> Optional[str]:
        """Генерация PDF каталога."""
        # Применяем ценообразование
        priced_products = self.pricing_manager.apply_pricing_to_products(agent_id, products)
        return self.material_generator.generate_pdf_catalog(agent_id, priced_products, title)

    def generate_voucher(
        self,
        agent_id: str,
        voucher_data: Dict[str, Any]
    ) -> Optional[str]:
        """Генерация ваучера."""
        return self.material_generator.generate_voucher(agent_id, voucher_data)

    def generate_invoice(
        self,
        agent_id: str,
        invoice_data: Dict[str, Any]
    ) -> Optional[str]:
        """Генерация инвойса."""
        return self.material_generator.generate_invoice(agent_id, invoice_data)

    def create_widget(
        self,
        agent_id: str,
        settings: Optional[WidgetSettings] = None
    ) -> Dict[str, Any]:
        """Создание виджета бронирования."""
        return self.widget_generator.create_widget(agent_id, settings)

    def create_landing_page(
        self,
        agent_id: str,
        settings: LandingPageSettings,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Создание landing page."""
        # Применяем ценообразование
        priced_products = self.pricing_manager.apply_pricing_to_products(agent_id, products)
        return self.landing_generator.create_landing_page(agent_id, settings, priced_products)

    def set_pricing(self, agent_id: str, **pricing_options) -> Optional[PricingSettings]:
        """Настройка ценообразования."""
        return self.pricing_manager.update_pricing(agent_id, **pricing_options)

    def get_sales_report(
        self,
        agent_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение отчёта о продажах."""
        return self.analytics.get_sales_report(agent_id, start_date, end_date)


# ═══════════════════════════════════════════════════════════════
# CLI ИНТЕРФЕЙС
# ═══════════════════════════════════════════════════════════════

def main():
    """CLI интерфейс."""
    import argparse

    parser = argparse.ArgumentParser(
        description="White Label Platform - продажа услуг под брендом агента"
    )

    subparsers = parser.add_subparsers(dest="command", help="Команды")

    # create-agent
    create_parser = subparsers.add_parser("create-agent", help="Создать агента")
    create_parser.add_argument("company_name", help="Название компании")
    create_parser.add_argument("--email", help="Email")
    create_parser.add_argument("--phone", help="Телефон")
    create_parser.add_argument("--website", help="Веб-сайт")

    # list-agents
    subparsers.add_parser("list-agents", help="Список агентов")

    # upload-logo
    logo_parser = subparsers.add_parser("upload-logo", help="Загрузить логотип")
    logo_parser.add_argument("agent_id", help="ID агента")
    logo_parser.add_argument("logo_path", help="Путь к логотипу")

    # set-colors
    colors_parser = subparsers.add_parser("set-colors", help="Установить цвета")
    colors_parser.add_argument("agent_id", help="ID агента")
    colors_parser.add_argument("--primary", help="Основной цвет (hex)")
    colors_parser.add_argument("--secondary", help="Акцентный цвет (hex)")

    # create-widget
    widget_parser = subparsers.add_parser("create-widget", help="Создать виджет")
    widget_parser.add_argument("agent_id", help="ID агента")
    widget_parser.add_argument("--type", choices=["iframe", "popup", "floating"], default="iframe")

    # generate-catalog
    catalog_parser = subparsers.add_parser("generate-catalog", help="Генерировать каталог")
    catalog_parser.add_argument("agent_id", help="ID агента")
    catalog_parser.add_argument("--products", help="JSON файл с продуктами")
    catalog_parser.add_argument("--title", default="Product Catalog", help="Заголовок")

    # set-pricing
    pricing_parser = subparsers.add_parser("set-pricing", help="Настроить ценообразование")
    pricing_parser.add_argument("agent_id", help="ID агента")
    pricing_parser.add_argument("--markup", type=float, help="Наценка в %")
    pricing_parser.add_argument("--round-to", type=int, help="Округление")

    # sales-report
    report_parser = subparsers.add_parser("sales-report", help="Отчёт о продажах")
    report_parser.add_argument("agent_id", help="ID агента")
    report_parser.add_argument("--start", help="Начальная дата (YYYY-MM-DD)")
    report_parser.add_argument("--end", help="Конечная дата (YYYY-MM-DD)")

    args = parser.parse_args()

    platform = WhiteLabelPlatform()

    if args.command == "create-agent":
        kwargs = {}
        if args.email:
            kwargs['email'] = args.email
        if args.phone:
            kwargs['phone'] = args.phone
        if args.website:
            kwargs['website'] = args.website

        agent = platform.create_agent(args.company_name, **kwargs)
        print(f"\nАгент создан:")
        print(f"  ID: {agent.agent_id}")
        print(f"  Subdomain: {agent.subdomain}.marselluxury.ae")
        print(f"  Директория: {AGENTS_DIR / agent.agent_id}")

    elif args.command == "list-agents":
        agents = platform.agent_manager.list_agents()
        if not agents:
            print("Агентов нет")
        else:
            print("\nАгенты:")
            for a in agents:
                print(f"  {a['agent_id']}: {a['company_name']} ({a['subdomain']})")

    elif args.command == "upload-logo":
        success = platform.agent_manager.upload_logo(args.agent_id, args.logo_path)
        print("Логотип загружен" if success else "Ошибка загрузки")

    elif args.command == "set-colors":
        colors = {}
        if args.primary:
            colors['primary'] = args.primary
        if args.secondary:
            colors['secondary'] = args.secondary

        if colors:
            success = platform.agent_manager.set_colors(args.agent_id, colors)
            print("Цвета обновлены" if success else "Ошибка обновления")
        else:
            print("Укажите хотя бы один цвет")

    elif args.command == "create-widget":
        settings = WidgetSettings(widget_type=args.type)
        result = platform.create_widget(args.agent_id, settings)

        if "error" in result:
            print(f"Ошибка: {result['error']}")
        else:
            print(f"\nВиджет создан:")
            print(f"  Widget ID: {result['widget_id']}")
            print(f"  URL: {result['embed_codes']['direct_url']}")
            print(f"\niFrame код:")
            print(result['embed_codes']['iframe'])

    elif args.command == "generate-catalog":
        # Загружаем продукты
        products = []
        if args.products and Path(args.products).exists():
            with open(args.products, 'r', encoding='utf-8') as f:
                products = json.load(f)
        else:
            # Демо продукты
            products = [
                {"name": "Desert Safari", "description": "Experience the magic of Dubai desert", "price": 250, "duration": "6 hours", "category": "tours"},
                {"name": "Burj Khalifa Tour", "description": "Visit the world's tallest building", "price": 180, "duration": "3 hours", "category": "tickets"},
                {"name": "Dubai Marina Yacht", "description": "Private yacht cruise", "price": 800, "duration": "4 hours", "category": "rentals"},
            ]

        path = platform.generate_catalog(args.agent_id, products, args.title)
        if path:
            print(f"\nКаталог создан: {path}")

    elif args.command == "set-pricing":
        kwargs = {}
        if args.markup is not None:
            kwargs['default_markup_percent'] = args.markup
        if args.round_to is not None:
            kwargs['round_to'] = args.round_to

        pricing = platform.set_pricing(args.agent_id, **kwargs)
        if pricing:
            print(f"\nЦенообразование обновлено:")
            print(f"  Наценка: {pricing.default_markup_percent}%")
            print(f"  Округление: {pricing.round_to} AED")

    elif args.command == "sales-report":
        report = platform.get_sales_report(args.agent_id, args.start, args.end)
        print(f"\n=== Отчёт о продажах: {args.agent_id} ===")
        print(f"Всего продаж: {report['summary']['total_sales']}")
        print(f"Выручка: AED {report['summary']['total_revenue']:,.2f}")
        print(f"Наценка: AED {report['summary']['total_markup']:,.2f}")
        print(f"Средний чек: AED {report['summary']['average_order']:,.2f}")

        if report['by_status']:
            print("\nПо статусам:")
            for status, count in report['by_status'].items():
                print(f"  {status}: {count}")

        if report['by_source']:
            print("\nПо источникам:")
            for source, data in report['by_source'].items():
                print(f"  {source}: {data['count']} продаж, AED {data['revenue']:,.2f}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
