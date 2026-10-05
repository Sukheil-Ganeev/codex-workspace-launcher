#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Email Marketing Integration - Mailchimp & SendGrid

Интеграция с Mailchimp и SendGrid для email-рассылок туристической компании.

Функциональность:
- Mailchimp API: списки, подписчики, сегменты, кампании
- SendGrid API: транзакционные письма, шаблоны, tracking
- Шаблоны писем: welcome, booking, reminder, feedback, promo, birthday
- Автоматизация: drip campaigns, triggered emails, A/B тесты
- Аналитика: open rate, click rate, отчёты
- GDPR: double opt-in, unsubscribe, data export/delete

Требования:
    pip install mailchimp-marketing sendgrid jinja2 python-dateutil
"""

import os
import json
import hashlib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import re

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════

# Mailchimp
MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY", "")
MAILCHIMP_SERVER_PREFIX = os.getenv("MAILCHIMP_SERVER_PREFIX", "us1")  # us1, us2, etc.
MAILCHIMP_LIST_ID = os.getenv("MAILCHIMP_LIST_ID", "")

# SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@example.com")
SENDGRID_FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Dubai Tours")

# Общие настройки
EMAIL_TEMPLATES_DIR = Path(__file__).parent / "templates" / "email"
COMPANY_NAME = "Dubai Tours"
COMPANY_WEBSITE = "https://example.com"
COMPANY_ADDRESS = "Dubai, UAE"
UNSUBSCRIBE_URL = "https://example.com/unsubscribe"


# ═══════════════════════════════════════════════════════════════
# ENUMS И DATACLASSES
# ═══════════════════════════════════════════════════════════════

class EmailProvider(Enum):
    """Провайдеры email."""
    MAILCHIMP = "mailchimp"
    SENDGRID = "sendgrid"


class SubscriberStatus(Enum):
    """Статусы подписчика."""
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    PENDING = "pending"  # Double opt-in pending
    CLEANED = "cleaned"  # Bounced
    ARCHIVED = "archived"


class EmailType(Enum):
    """Типы писем."""
    WELCOME = "welcome"
    BOOKING_CONFIRMATION = "booking_confirmation"
    TOUR_REMINDER = "tour_reminder"
    FEEDBACK_REQUEST = "feedback_request"
    PROMO = "promo"
    BIRTHDAY = "birthday"
    NEWSLETTER = "newsletter"
    TRANSACTIONAL = "transactional"


class ClientType(Enum):
    """Типы клиентов для сегментации."""
    TOURIST = "tourist"
    VIP = "vip"
    CORPORATE = "corporate"
    AGENT = "agent"
    B2B = "b2b"


class Country(Enum):
    """Страны для сегментации."""
    RU = "Russia"
    KZ = "Kazakhstan"
    UAE = "UAE"
    US = "USA"
    UK = "UK"
    OTHER = "Other"


@dataclass
class Subscriber:
    """Модель подписчика."""
    email: str
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    client_type: ClientType = ClientType.TOURIST
    country: Country = Country.OTHER
    language: str = "ru"
    birthday: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    status: SubscriberStatus = SubscriberStatus.PENDING
    gdpr_consent: bool = False
    gdpr_consent_date: Optional[datetime] = None
    source: str = "whatsapp"
    created_at: datetime = field(default_factory=datetime.now)

    def to_mailchimp_format(self) -> Dict:
        """Конвертировать в формат Mailchimp."""
        merge_fields = {
            "FNAME": self.first_name,
            "LNAME": self.last_name,
            "PHONE": self.phone,
            "CTYPE": self.client_type.value,
            "COUNTRY": self.country.value,
            "LANG": self.language,
            "SOURCE": self.source,
        }
        if self.birthday:
            merge_fields["BIRTHDAY"] = self.birthday.strftime("%m/%d")

        return {
            "email_address": self.email,
            "status": "pending" if not self.gdpr_consent else self.status.value,
            "merge_fields": merge_fields,
            "tags": self.tags,
        }

    def to_sendgrid_format(self) -> Dict:
        """Конвертировать в формат SendGrid Contacts."""
        contact = {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "custom_fields": {
                "phone": self.phone,
                "client_type": self.client_type.value,
                "country": self.country.value,
                "language": self.language,
                "source": self.source,
            }
        }
        if self.phone:
            contact["phone_number"] = self.phone
        return contact


@dataclass
class EmailCampaign:
    """Модель email кампании."""
    name: str
    subject: str
    email_type: EmailType
    content_html: str = ""
    content_text: str = ""
    from_name: str = SENDGRID_FROM_NAME
    from_email: str = SENDGRID_FROM_EMAIL
    reply_to: str = ""
    segment_id: Optional[str] = None
    list_id: Optional[str] = None
    schedule_time: Optional[datetime] = None
    ab_test: bool = False
    ab_variants: List[Dict] = field(default_factory=list)
    tracking: Dict = field(default_factory=lambda: {
        "opens": True,
        "clicks": True,
        "text_clicks": True
    })

    campaign_id: Optional[str] = None
    status: str = "draft"
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None

    # Статистика
    emails_sent: int = 0
    opens: int = 0
    clicks: int = 0
    unsubscribes: int = 0
    bounces: int = 0


@dataclass
class EmailStats:
    """Статистика email."""
    total_sent: int = 0
    delivered: int = 0
    opens: int = 0
    unique_opens: int = 0
    clicks: int = 0
    unique_clicks: int = 0
    bounces: int = 0
    spam_reports: int = 0
    unsubscribes: int = 0

    @property
    def delivery_rate(self) -> float:
        return (self.delivered / self.total_sent * 100) if self.total_sent else 0

    @property
    def open_rate(self) -> float:
        return (self.unique_opens / self.delivered * 100) if self.delivered else 0

    @property
    def click_rate(self) -> float:
        return (self.unique_clicks / self.delivered * 100) if self.delivered else 0

    @property
    def bounce_rate(self) -> float:
        return (self.bounces / self.total_sent * 100) if self.total_sent else 0

    @property
    def unsubscribe_rate(self) -> float:
        return (self.unsubscribes / self.delivered * 100) if self.delivered else 0


# ═══════════════════════════════════════════════════════════════
# ШАБЛОНЫ ПИСЕМ (JINJA2)
# ═══════════════════════════════════════════════════════════════

EMAIL_TEMPLATES = {
    EmailType.WELCOME: {
        "subject_ru": "Добро пожаловать в {{ company_name }}!",
        "subject_en": "Welcome to {{ company_name }}!",
        "body_ru": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #1a5f7a; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .button { display: inline-block; padding: 12px 24px; background: #1a5f7a; color: white; text-decoration: none; border-radius: 5px; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ company_name }}</h1>
        </div>
        <div class="content">
            <h2>Добро пожаловать, {{ first_name }}!</h2>
            <p>Спасибо за подписку на нашу рассылку. Теперь вы будете первым узнавать о:</p>
            <ul>
                <li>Новых экскурсиях и турах</li>
                <li>Специальных предложениях и скидках</li>
                <li>Полезных советах для путешествий в ОАЭ</li>
            </ul>
            <p style="text-align: center; margin-top: 30px;">
                <a href="{{ website_url }}" class="button">Посмотреть наши туры</a>
            </p>
        </div>
        <div class="footer">
            <p>{{ company_address }}</p>
            <p><a href="{{ unsubscribe_url }}">Отписаться от рассылки</a></p>
        </div>
    </div>
</body>
</html>
""",
        "body_en": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #1a5f7a; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .button { display: inline-block; padding: 12px 24px; background: #1a5f7a; color: white; text-decoration: none; border-radius: 5px; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ company_name }}</h1>
        </div>
        <div class="content">
            <h2>Welcome, {{ first_name }}!</h2>
            <p>Thank you for subscribing to our newsletter. You'll be the first to know about:</p>
            <ul>
                <li>New tours and excursions</li>
                <li>Special offers and discounts</li>
                <li>Useful travel tips for UAE</li>
            </ul>
            <p style="text-align: center; margin-top: 30px;">
                <a href="{{ website_url }}" class="button">Browse Our Tours</a>
            </p>
        </div>
        <div class="footer">
            <p>{{ company_address }}</p>
            <p><a href="{{ unsubscribe_url }}">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>
"""
    },

    EmailType.BOOKING_CONFIRMATION: {
        "subject_ru": "Подтверждение бронирования #{{ booking_id }}",
        "subject_en": "Booking Confirmation #{{ booking_id }}",
        "body_ru": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #1a5f7a; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .booking-details { background: white; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .booking-details table { width: 100%; }
        .booking-details td { padding: 8px 0; border-bottom: 1px solid #eee; }
        .total { font-size: 18px; font-weight: bold; color: #1a5f7a; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Подтверждение бронирования</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{ first_name }},</p>
            <p>Ваше бронирование успешно подтверждено!</p>

            <div class="booking-details">
                <h3>Детали бронирования:</h3>
                <table>
                    <tr>
                        <td><strong>Номер брони:</strong></td>
                        <td>{{ booking_id }}</td>
                    </tr>
                    <tr>
                        <td><strong>Услуга:</strong></td>
                        <td>{{ service_name }}</td>
                    </tr>
                    <tr>
                        <td><strong>Дата:</strong></td>
                        <td>{{ tour_date }}</td>
                    </tr>
                    <tr>
                        <td><strong>Время:</strong></td>
                        <td>{{ tour_time }}</td>
                    </tr>
                    <tr>
                        <td><strong>Количество гостей:</strong></td>
                        <td>{{ guests_count }}</td>
                    </tr>
                    <tr>
                        <td><strong>Место встречи:</strong></td>
                        <td>{{ pickup_location }}</td>
                    </tr>
                    <tr class="total">
                        <td><strong>Итого:</strong></td>
                        <td>{{ total_amount }} {{ currency }}</td>
                    </tr>
                </table>
            </div>

            <p><strong>Важно:</strong></p>
            <ul>
                <li>Будьте готовы за 15 минут до времени встречи</li>
                <li>Не забудьте взять удобную обувь и воду</li>
                <li>При себе иметь документы</li>
            </ul>

            <p>Контакт гида/водителя: {{ driver_phone }}</p>

            <p>По любым вопросам обращайтесь: {{ support_email }} или {{ support_phone }}</p>
        </div>
        <div class="footer">
            <p>{{ company_address }}</p>
        </div>
    </div>
</body>
</html>
"""
    },

    EmailType.TOUR_REMINDER: {
        "subject_ru": "Напоминание: завтра ваш тур {{ service_name }}",
        "subject_en": "Reminder: Your tour {{ service_name }} is tomorrow",
        "body_ru": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f4a460; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .reminder-box { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Напоминание о туре</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{ first_name }},</p>
            <p>Напоминаем, что <strong>завтра</strong> состоится ваш тур!</p>

            <div class="reminder-box">
                <p><strong>{{ service_name }}</strong></p>
                <p>Дата: {{ tour_date }}</p>
                <p>Время: {{ tour_time }}</p>
                <p>Место встречи: {{ pickup_location }}</p>
            </div>

            <p><strong>Что взять с собой:</strong></p>
            <ul>
                {% for item in checklist %}
                <li>{{ item }}</li>
                {% endfor %}
            </ul>

            <p>Контакт гида: {{ driver_phone }}</p>

            <p>Желаем приятного отдыха!</p>
        </div>
        <div class="footer">
            <p>{{ company_address }}</p>
        </div>
    </div>
</body>
</html>
"""
    },

    EmailType.FEEDBACK_REQUEST: {
        "subject_ru": "Как прошёл ваш тур? Оставьте отзыв",
        "subject_en": "How was your tour? Leave a review",
        "body_ru": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #28a745; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .rating { text-align: center; font-size: 24px; margin: 20px 0; }
        .rating a { text-decoration: none; margin: 0 5px; }
        .button { display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Спасибо за выбор нас!</h1>
        </div>
        <div class="content">
            <p>Уважаемый(ая) {{ first_name }},</p>
            <p>Надеемся, вам понравился тур <strong>{{ service_name }}</strong>!</p>

            <p>Ваше мнение очень важно для нас. Пожалуйста, оцените наш сервис:</p>

            <div class="rating">
                {% for i in range(1, 6) %}
                <a href="{{ review_url }}?rating={{ i }}">{{ '★' if i <= 3 else '☆' }}</a>
                {% endfor %}
            </div>

            <p style="text-align: center;">
                <a href="{{ review_url }}" class="button">Оставить отзыв</a>
            </p>

            <p>Также будем благодарны за отзыв на:</p>
            <ul>
                <li><a href="{{ google_review_url }}">Google Maps</a></li>
                <li><a href="{{ tripadvisor_url }}">TripAdvisor</a></li>
            </ul>

            <p>В качестве благодарности дарим вам скидку <strong>{{ discount }}%</strong> на следующий тур!</p>
            <p>Промокод: <strong>{{ promo_code }}</strong></p>
        </div>
        <div class="footer">
            <p>{{ company_address }}</p>
            <p><a href="{{ unsubscribe_url }}">Отписаться от рассылки</a></p>
        </div>
    </div>
</body>
</html>
"""
    },

    EmailType.PROMO: {
        "subject_ru": "{{ promo_title }} - скидка {{ discount }}%!",
        "subject_en": "{{ promo_title }} - {{ discount }}% OFF!",
        "body_ru": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .discount-badge { background: #ff6b6b; color: white; padding: 10px 20px; border-radius: 25px; display: inline-block; font-size: 24px; font-weight: bold; }
        .content { padding: 20px; background: #f9f9f9; }
        .tour-card { background: white; border-radius: 10px; overflow: hidden; margin: 15px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .tour-card img { width: 100%; height: 200px; object-fit: cover; }
        .tour-card-content { padding: 15px; }
        .old-price { text-decoration: line-through; color: #999; }
        .new-price { color: #ff6b6b; font-size: 24px; font-weight: bold; }
        .button { display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }
        .countdown { background: #333; color: white; padding: 15px; text-align: center; margin: 20px 0; border-radius: 5px; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="discount-badge">-{{ discount }}%</div>
            <h1>{{ promo_title }}</h1>
            <p>{{ promo_subtitle }}</p>
        </div>
        <div class="content">
            <p>{{ first_name }}, только для вас специальное предложение!</p>

            <div class="countdown">
                Акция действует до: <strong>{{ promo_end_date }}</strong>
            </div>

            {% for tour in tours %}
            <div class="tour-card">
                <img src="{{ tour.image_url }}" alt="{{ tour.name }}">
                <div class="tour-card-content">
                    <h3>{{ tour.name }}</h3>
                    <p>{{ tour.description }}</p>
                    <p>
                        <span class="old-price">{{ tour.old_price }} AED</span>
                        <span class="new-price">{{ tour.new_price }} AED</span>
                    </p>
                    <a href="{{ tour.url }}" class="button">Подробнее</a>
                </div>
            </div>
            {% endfor %}

            <p style="text-align: center; margin-top: 20px;">
                Промокод: <strong>{{ promo_code }}</strong>
            </p>
        </div>
        <div class="footer">
            <p>{{ company_address }}</p>
            <p><a href="{{ unsubscribe_url }}">Отписаться от рассылки</a></p>
        </div>
    </div>
</body>
</html>
"""
    },

    EmailType.BIRTHDAY: {
        "subject_ru": "С Днём Рождения, {{ first_name }}! Подарок внутри",
        "subject_en": "Happy Birthday, {{ first_name }}! Gift inside",
        "body_ru": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; }
        .gift-box { background: #fff; border: 3px dashed #f5576c; padding: 20px; margin: 20px 0; text-align: center; border-radius: 10px; }
        .promo-code { font-size: 28px; font-weight: bold; color: #f5576c; letter-spacing: 3px; }
        .content { padding: 20px; background: #f9f9f9; }
        .button { display: inline-block; padding: 12px 24px; background: #f5576c; color: white; text-decoration: none; border-radius: 5px; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>С Днём Рождения!</h1>
            <p>{{ first_name }}, желаем счастья и незабываемых путешествий!</p>
        </div>
        <div class="content">
            <p>Дорогой(ая) {{ first_name }},</p>
            <p>В честь вашего праздника дарим персональную скидку <strong>{{ discount }}%</strong> на любой тур!</p>

            <div class="gift-box">
                <p>Ваш подарочный промокод:</p>
                <p class="promo-code">{{ promo_code }}</p>
                <p>Действителен до {{ promo_expiry }}</p>
            </div>

            <p style="text-align: center;">
                <a href="{{ website_url }}/tours" class="button">Выбрать подарок себе</a>
            </p>

            <p>Пусть этот год принесёт вам яркие впечатления и незабываемые путешествия!</p>

            <p>С наилучшими пожеланиями,<br>Команда {{ company_name }}</p>
        </div>
        <div class="footer">
            <p>{{ company_address }}</p>
            <p><a href="{{ unsubscribe_url }}">Отписаться от рассылки</a></p>
        </div>
    </div>
</body>
</html>
"""
    },

    # Double Opt-In подтверждение
    "double_optin": {
        "subject_ru": "Подтвердите вашу подписку",
        "subject_en": "Confirm your subscription",
        "body_ru": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #1a5f7a; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .button { display: inline-block; padding: 15px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; font-size: 18px; }
        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ company_name }}</h1>
        </div>
        <div class="content">
            <h2>Подтвердите вашу подписку</h2>
            <p>Здравствуйте, {{ first_name }}!</p>
            <p>Для завершения подписки на рассылку {{ company_name }}, пожалуйста, нажмите кнопку ниже:</p>

            <p style="text-align: center; margin: 30px 0;">
                <a href="{{ confirm_url }}" class="button">Подтвердить подписку</a>
            </p>

            <p>Если вы не запрашивали подписку, просто проигнорируйте это письмо.</p>

            <p><small>Эта ссылка действительна 48 часов.</small></p>
        </div>
        <div class="footer">
            <p>{{ company_address }}</p>
        </div>
    </div>
</body>
</html>
"""
    }
}


# ═══════════════════════════════════════════════════════════════
# БАЗОВЫЙ КЛАСС EMAIL ПРОВАЙДЕРА
# ═══════════════════════════════════════════════════════════════

class EmailProviderBase(ABC):
    """Абстрактный базовый класс для email провайдеров."""

    @abstractmethod
    def add_subscriber(self, subscriber: Subscriber) -> Dict:
        """Добавить подписчика."""
        pass

    @abstractmethod
    def update_subscriber(self, email: str, data: Dict) -> Dict:
        """Обновить подписчика."""
        pass

    @abstractmethod
    def delete_subscriber(self, email: str) -> bool:
        """Удалить подписчика (GDPR)."""
        pass

    @abstractmethod
    def get_subscriber(self, email: str) -> Optional[Dict]:
        """Получить информацию о подписчике."""
        pass

    @abstractmethod
    def send_email(self, to_email: str, subject: str, html_content: str,
                   text_content: str = "", **kwargs) -> Dict:
        """Отправить одно письмо."""
        pass

    @abstractmethod
    def create_campaign(self, campaign: EmailCampaign) -> Dict:
        """Создать кампанию."""
        pass

    @abstractmethod
    def send_campaign(self, campaign_id: str) -> Dict:
        """Отправить кампанию."""
        pass

    @abstractmethod
    def get_campaign_stats(self, campaign_id: str) -> EmailStats:
        """Получить статистику кампании."""
        pass


# ═══════════════════════════════════════════════════════════════
# MAILCHIMP PROVIDER
# ═══════════════════════════════════════════════════════════════

class MailchimpProvider(EmailProviderBase):
    """Интеграция с Mailchimp API."""

    def __init__(self, api_key: str = None, server_prefix: str = None, list_id: str = None):
        self.api_key = api_key or MAILCHIMP_API_KEY
        self.server_prefix = server_prefix or MAILCHIMP_SERVER_PREFIX
        self.list_id = list_id or MAILCHIMP_LIST_ID
        self.client = None

        if self.api_key:
            self._init_client()

    def _init_client(self):
        """Инициализация Mailchimp клиента."""
        try:
            import mailchimp_marketing as MailchimpMarketing
            from mailchimp_marketing.api_client import ApiClientError

            self.client = MailchimpMarketing.Client()
            self.client.set_config({
                "api_key": self.api_key,
                "server": self.server_prefix
            })
            self.ApiClientError = ApiClientError
            logger.info("Mailchimp client initialized")
        except ImportError:
            logger.warning("mailchimp-marketing not installed. Run: pip install mailchimp-marketing")
            self.client = None

    def _get_subscriber_hash(self, email: str) -> str:
        """Получить MD5 хеш email для Mailchimp API."""
        return hashlib.md5(email.lower().encode()).hexdigest()

    def ping(self) -> bool:
        """Проверить соединение с Mailchimp."""
        if not self.client:
            return False
        try:
            response = self.client.ping.get()
            return response.get("health_status") == "Everything's Chimpy!"
        except Exception as e:
            logger.error(f"Mailchimp ping failed: {e}")
            return False

    # ═══════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ СПИСКАМИ
    # ═══════════════════════════════════════════════════════════

    def get_lists(self) -> List[Dict]:
        """Получить все списки рассылки."""
        if not self.client:
            return []
        try:
            response = self.client.lists.get_all_lists()
            return response.get("lists", [])
        except Exception as e:
            logger.error(f"Failed to get lists: {e}")
            return []

    def create_list(self, name: str, company: str, address: str,
                    from_name: str, from_email: str, subject: str,
                    permission_reminder: str = "You subscribed to our newsletter",
                    double_optin: bool = True) -> Optional[Dict]:
        """Создать новый список рассылки."""
        if not self.client:
            return None
        try:
            data = {
                "name": name,
                "contact": {
                    "company": company,
                    "address1": address,
                    "city": "Dubai",
                    "country": "AE"
                },
                "permission_reminder": permission_reminder,
                "campaign_defaults": {
                    "from_name": from_name,
                    "from_email": from_email,
                    "subject": subject,
                    "language": "ru"
                },
                "double_optin": double_optin,
                "email_type_option": True
            }
            response = self.client.lists.create_list(data)
            logger.info(f"Created list: {response['id']}")
            return response
        except Exception as e:
            logger.error(f"Failed to create list: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ ПОДПИСЧИКАМИ
    # ═══════════════════════════════════════════════════════════

    def add_subscriber(self, subscriber: Subscriber, list_id: str = None) -> Dict:
        """Добавить подписчика в список."""
        if not self.client:
            return {"error": "Client not initialized"}

        list_id = list_id or self.list_id
        try:
            data = subscriber.to_mailchimp_format()
            response = self.client.lists.add_list_member(list_id, data)
            logger.info(f"Added subscriber: {subscriber.email}")
            return response
        except self.ApiClientError as e:
            error = json.loads(e.text)
            logger.error(f"Failed to add subscriber: {error}")
            return {"error": error}

    def update_subscriber(self, email: str, data: Dict, list_id: str = None) -> Dict:
        """Обновить данные подписчика."""
        if not self.client:
            return {"error": "Client not initialized"}

        list_id = list_id or self.list_id
        subscriber_hash = self._get_subscriber_hash(email)

        try:
            response = self.client.lists.update_list_member(
                list_id, subscriber_hash, data
            )
            logger.info(f"Updated subscriber: {email}")
            return response
        except Exception as e:
            logger.error(f"Failed to update subscriber: {e}")
            return {"error": str(e)}

    def delete_subscriber(self, email: str, list_id: str = None) -> bool:
        """Полностью удалить подписчика (GDPR)."""
        if not self.client:
            return False

        list_id = list_id or self.list_id
        subscriber_hash = self._get_subscriber_hash(email)

        try:
            self.client.lists.delete_list_member_permanent(list_id, subscriber_hash)
            logger.info(f"Permanently deleted subscriber: {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete subscriber: {e}")
            return False

    def get_subscriber(self, email: str, list_id: str = None) -> Optional[Dict]:
        """Получить информацию о подписчике."""
        if not self.client:
            return None

        list_id = list_id or self.list_id
        subscriber_hash = self._get_subscriber_hash(email)

        try:
            response = self.client.lists.get_list_member(list_id, subscriber_hash)
            return response
        except Exception as e:
            logger.error(f"Failed to get subscriber: {e}")
            return None

    def unsubscribe(self, email: str, list_id: str = None) -> bool:
        """Отписать подписчика."""
        result = self.update_subscriber(
            email,
            {"status": "unsubscribed"},
            list_id
        )
        return "error" not in result

    def archive_subscriber(self, email: str, list_id: str = None) -> bool:
        """Архивировать подписчика."""
        if not self.client:
            return False

        list_id = list_id or self.list_id
        subscriber_hash = self._get_subscriber_hash(email)

        try:
            self.client.lists.delete_list_member(list_id, subscriber_hash)
            logger.info(f"Archived subscriber: {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to archive subscriber: {e}")
            return False

    def add_tags(self, email: str, tags: List[str], list_id: str = None) -> bool:
        """Добавить теги подписчику."""
        if not self.client:
            return False

        list_id = list_id or self.list_id
        subscriber_hash = self._get_subscriber_hash(email)

        try:
            tag_data = {"tags": [{"name": tag, "status": "active"} for tag in tags]}
            self.client.lists.update_list_member_tags(
                list_id, subscriber_hash, tag_data
            )
            logger.info(f"Added tags to {email}: {tags}")
            return True
        except Exception as e:
            logger.error(f"Failed to add tags: {e}")
            return False

    def batch_add_subscribers(self, subscribers: List[Subscriber],
                              list_id: str = None) -> Dict:
        """Пакетное добавление подписчиков."""
        if not self.client:
            return {"error": "Client not initialized"}

        list_id = list_id or self.list_id
        operations = []

        for subscriber in subscribers:
            operations.append({
                "method": "POST",
                "path": f"/lists/{list_id}/members",
                "body": json.dumps(subscriber.to_mailchimp_format())
            })

        try:
            response = self.client.batches.start({"operations": operations})
            logger.info(f"Started batch operation: {response['id']}")
            return response
        except Exception as e:
            logger.error(f"Failed to start batch: {e}")
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # СЕГМЕНТАЦИЯ
    # ═══════════════════════════════════════════════════════════

    def create_segment(self, name: str, conditions: List[Dict],
                       list_id: str = None) -> Optional[Dict]:
        """
        Создать сегмент.

        Пример условий:
        conditions = [
            {"condition_type": "TextMerge", "field": "CTYPE", "op": "is", "value": "vip"},
            {"condition_type": "TextMerge", "field": "COUNTRY", "op": "is", "value": "Russia"}
        ]
        """
        if not self.client:
            return None

        list_id = list_id or self.list_id

        try:
            data = {
                "name": name,
                "static_segment": [],
                "options": {
                    "match": "all",  # all | any
                    "conditions": conditions
                }
            }
            response = self.client.lists.create_segment(list_id, data)
            logger.info(f"Created segment: {response['id']} - {name}")
            return response
        except Exception as e:
            logger.error(f"Failed to create segment: {e}")
            return None

    def create_client_type_segment(self, client_type: ClientType,
                                   list_id: str = None) -> Optional[Dict]:
        """Создать сегмент по типу клиента."""
        conditions = [{
            "condition_type": "TextMerge",
            "field": "CTYPE",
            "op": "is",
            "value": client_type.value
        }]
        return self.create_segment(
            f"Clients - {client_type.value.upper()}",
            conditions,
            list_id
        )

    def create_country_segment(self, country: Country,
                               list_id: str = None) -> Optional[Dict]:
        """Создать сегмент по стране."""
        conditions = [{
            "condition_type": "TextMerge",
            "field": "COUNTRY",
            "op": "is",
            "value": country.value
        }]
        return self.create_segment(
            f"Country - {country.value}",
            conditions,
            list_id
        )

    def get_segments(self, list_id: str = None) -> List[Dict]:
        """Получить все сегменты."""
        if not self.client:
            return []

        list_id = list_id or self.list_id

        try:
            response = self.client.lists.list_segments(list_id)
            return response.get("segments", [])
        except Exception as e:
            logger.error(f"Failed to get segments: {e}")
            return []

    # ═══════════════════════════════════════════════════════════
    # КАМПАНИИ
    # ═══════════════════════════════════════════════════════════

    def create_campaign(self, campaign: EmailCampaign,
                        list_id: str = None) -> Dict:
        """Создать email кампанию."""
        if not self.client:
            return {"error": "Client not initialized"}

        list_id = list_id or self.list_id

        try:
            # Настройки получателей
            recipients = {"list_id": list_id}
            if campaign.segment_id:
                recipients["segment_opts"] = {"saved_segment_id": int(campaign.segment_id)}

            # Создание кампании
            data = {
                "type": "regular",
                "recipients": recipients,
                "settings": {
                    "subject_line": campaign.subject,
                    "title": campaign.name,
                    "from_name": campaign.from_name,
                    "reply_to": campaign.reply_to or campaign.from_email,
                    "to_name": "*|FNAME|* *|LNAME|*",
                    "auto_footer": True,
                    "inline_css": True
                },
                "tracking": campaign.tracking
            }

            response = self.client.campaigns.create(data)
            campaign_id = response["id"]
            campaign.campaign_id = campaign_id

            # Добавляем контент
            if campaign.content_html:
                self.client.campaigns.set_content(campaign_id, {
                    "html": campaign.content_html,
                    "plain_text": campaign.content_text or ""
                })

            logger.info(f"Created campaign: {campaign_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            return {"error": str(e)}

    def create_ab_campaign(self, campaign: EmailCampaign,
                           subject_variants: List[str],
                           test_size: int = 20,
                           wait_time: int = 60,
                           list_id: str = None) -> Dict:
        """
        Создать A/B тест кампании.

        Args:
            campaign: Базовая кампания
            subject_variants: Варианты тем письма [A, B]
            test_size: % аудитории для теста (по умолчанию 20%)
            wait_time: Время ожидания результатов в минутах
        """
        if not self.client:
            return {"error": "Client not initialized"}

        list_id = list_id or self.list_id

        try:
            recipients = {"list_id": list_id}
            if campaign.segment_id:
                recipients["segment_opts"] = {"saved_segment_id": int(campaign.segment_id)}

            data = {
                "type": "variate",
                "recipients": recipients,
                "variate_settings": {
                    "winner_criteria": "opens",  # opens | clicks | total_revenue
                    "wait_time": wait_time,
                    "test_size": test_size,
                    "subject_lines": subject_variants,
                    "from_names": [campaign.from_name],
                    "reply_to_addresses": [campaign.reply_to or campaign.from_email]
                },
                "settings": {
                    "title": campaign.name,
                    "from_name": campaign.from_name,
                    "reply_to": campaign.reply_to or campaign.from_email,
                    "auto_footer": True
                },
                "tracking": campaign.tracking
            }

            response = self.client.campaigns.create(data)
            logger.info(f"Created A/B campaign: {response['id']}")
            return response

        except Exception as e:
            logger.error(f"Failed to create A/B campaign: {e}")
            return {"error": str(e)}

    def send_campaign(self, campaign_id: str) -> Dict:
        """Отправить кампанию."""
        if not self.client:
            return {"error": "Client not initialized"}

        try:
            self.client.campaigns.send(campaign_id)
            logger.info(f"Campaign sent: {campaign_id}")
            return {"status": "sent", "campaign_id": campaign_id}
        except Exception as e:
            logger.error(f"Failed to send campaign: {e}")
            return {"error": str(e)}

    def schedule_campaign(self, campaign_id: str,
                          schedule_time: datetime) -> Dict:
        """Запланировать отправку кампании."""
        if not self.client:
            return {"error": "Client not initialized"}

        try:
            data = {"schedule_time": schedule_time.isoformat()}
            self.client.campaigns.schedule(campaign_id, data)
            logger.info(f"Campaign scheduled: {campaign_id} at {schedule_time}")
            return {"status": "scheduled", "campaign_id": campaign_id}
        except Exception as e:
            logger.error(f"Failed to schedule campaign: {e}")
            return {"error": str(e)}

    def get_campaign_stats(self, campaign_id: str) -> EmailStats:
        """Получить статистику кампании."""
        stats = EmailStats()

        if not self.client:
            return stats

        try:
            response = self.client.reports.get_campaign_report(campaign_id)

            stats.total_sent = response.get("emails_sent", 0)
            stats.opens = response.get("opens", {}).get("opens_total", 0)
            stats.unique_opens = response.get("opens", {}).get("unique_opens", 0)
            stats.clicks = response.get("clicks", {}).get("clicks_total", 0)
            stats.unique_clicks = response.get("clicks", {}).get("unique_clicks", 0)
            stats.unsubscribes = response.get("unsubscribed", 0)
            stats.bounces = response.get("bounces", {}).get("hard_bounces", 0) + \
                           response.get("bounces", {}).get("soft_bounces", 0)
            stats.delivered = stats.total_sent - stats.bounces

            return stats

        except Exception as e:
            logger.error(f"Failed to get campaign stats: {e}")
            return stats

    def send_email(self, to_email: str, subject: str, html_content: str,
                   text_content: str = "", **kwargs) -> Dict:
        """
        Отправить одиночное письмо через Mailchimp Transactional (Mandrill).
        Примечание: требуется отдельный Mandrill API ключ.
        """
        # Mailchimp Marketing API не поддерживает отправку одиночных писем напрямую
        # Для этого используется Mandrill (Mailchimp Transactional)
        logger.warning("Mailchimp Marketing API doesn't support single emails. Use SendGrid or Mandrill.")
        return {"error": "Use SendGrid for transactional emails"}


# ═══════════════════════════════════════════════════════════════
# SENDGRID PROVIDER
# ═══════════════════════════════════════════════════════════════

class SendGridProvider(EmailProviderBase):
    """Интеграция с SendGrid API."""

    def __init__(self, api_key: str = None, from_email: str = None, from_name: str = None):
        self.api_key = api_key or SENDGRID_API_KEY
        self.from_email = from_email or SENDGRID_FROM_EMAIL
        self.from_name = from_name or SENDGRID_FROM_NAME
        self.client = None

        if self.api_key:
            self._init_client()

    def _init_client(self):
        """Инициализация SendGrid клиента."""
        try:
            from sendgrid import SendGridAPIClient
            self.client = SendGridAPIClient(self.api_key)
            logger.info("SendGrid client initialized")
        except ImportError:
            logger.warning("sendgrid not installed. Run: pip install sendgrid")
            self.client = None

    # ═══════════════════════════════════════════════════════════
    # ОТПРАВКА ПИСЕМ
    # ═══════════════════════════════════════════════════════════

    def send_email(self, to_email: str, subject: str, html_content: str,
                   text_content: str = "", categories: List[str] = None,
                   custom_args: Dict = None, **kwargs) -> Dict:
        """Отправить транзакционное письмо."""
        if not self.client:
            return {"error": "Client not initialized"}

        try:
            from sendgrid.helpers.mail import (
                Mail, Email, To, Content, Category, CustomArg,
                TrackingSettings, ClickTracking, OpenTracking
            )

            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject
            )

            # Контент
            if html_content:
                message.add_content(Content("text/html", html_content))
            if text_content:
                message.add_content(Content("text/plain", text_content))

            # Категории для аналитики
            if categories:
                for cat in categories:
                    message.add_category(Category(cat))

            # Кастомные аргументы
            if custom_args:
                for key, value in custom_args.items():
                    message.add_custom_arg(CustomArg(key, str(value)))

            # Трекинг
            tracking = TrackingSettings()
            tracking.click_tracking = ClickTracking(True, True)
            tracking.open_tracking = OpenTracking(True)
            message.tracking_settings = tracking

            response = self.client.send(message)

            logger.info(f"Email sent to {to_email}, status: {response.status_code}")
            return {
                "status": "sent",
                "status_code": response.status_code,
                "message_id": response.headers.get("X-Message-Id")
            }

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"error": str(e)}

    def send_template_email(self, to_email: str, template_id: str,
                            dynamic_data: Dict, **kwargs) -> Dict:
        """Отправить письмо по шаблону SendGrid."""
        if not self.client:
            return {"error": "Client not initialized"}

        try:
            from sendgrid.helpers.mail import Mail, Email, To, Personalization

            message = Mail(from_email=Email(self.from_email, self.from_name))
            message.template_id = template_id

            personalization = Personalization()
            personalization.add_to(To(to_email))
            personalization.dynamic_template_data = dynamic_data
            message.add_personalization(personalization)

            response = self.client.send(message)

            logger.info(f"Template email sent to {to_email}")
            return {
                "status": "sent",
                "status_code": response.status_code,
                "message_id": response.headers.get("X-Message-Id")
            }

        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            return {"error": str(e)}

    def send_bulk_email(self, recipients: List[Dict], subject: str,
                        html_content: str, text_content: str = "") -> Dict:
        """
        Отправить массовую рассылку.

        recipients: [{"email": "...", "name": "...", "substitutions": {...}}, ...]
        """
        if not self.client:
            return {"error": "Client not initialized"}

        try:
            from sendgrid.helpers.mail import Mail, Email, Personalization, To

            message = Mail(from_email=Email(self.from_email, self.from_name))
            message.subject = subject

            for recipient in recipients:
                personalization = Personalization()
                personalization.add_to(To(recipient["email"], recipient.get("name")))

                # Подстановки для персонализации
                if "substitutions" in recipient:
                    for key, value in recipient["substitutions"].items():
                        personalization.add_substitution(key, value)

                message.add_personalization(personalization)

            from sendgrid.helpers.mail import Content
            if html_content:
                message.add_content(Content("text/html", html_content))
            if text_content:
                message.add_content(Content("text/plain", text_content))

            response = self.client.send(message)

            logger.info(f"Bulk email sent to {len(recipients)} recipients")
            return {
                "status": "sent",
                "status_code": response.status_code,
                "recipients_count": len(recipients)
            }

        except Exception as e:
            logger.error(f"Failed to send bulk email: {e}")
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ КОНТАКТАМИ
    # ═══════════════════════════════════════════════════════════

    def add_subscriber(self, subscriber: Subscriber) -> Dict:
        """Добавить контакт в SendGrid."""
        if not self.client:
            return {"error": "Client not initialized"}

        try:
            data = {
                "contacts": [subscriber.to_sendgrid_format()]
            }
            response = self.client.client.marketing.contacts.put(
                request_body=data
            )
            logger.info(f"Added contact: {subscriber.email}")
            return {"status": "added", "job_id": response.body}
        except Exception as e:
            logger.error(f"Failed to add contact: {e}")
            return {"error": str(e)}

    def update_subscriber(self, email: str, data: Dict) -> Dict:
        """Обновить контакт."""
        # В SendGrid update = add (upsert)
        subscriber = Subscriber(email=email, **data)
        return self.add_subscriber(subscriber)

    def delete_subscriber(self, email: str) -> bool:
        """Удалить контакт (GDPR)."""
        if not self.client:
            return False

        try:
            # Сначала найти contact_id
            response = self.client.client.marketing.contacts.search.post(
                request_body={"query": f"email = '{email}'"}
            )
            contacts = json.loads(response.body).get("result", [])

            if contacts:
                contact_id = contacts[0]["id"]
                self.client.client.marketing.contacts.delete(
                    query_params={"ids": contact_id}
                )
                logger.info(f"Deleted contact: {email}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete contact: {e}")
            return False

    def get_subscriber(self, email: str) -> Optional[Dict]:
        """Получить информацию о контакте."""
        if not self.client:
            return None

        try:
            response = self.client.client.marketing.contacts.search.post(
                request_body={"query": f"email = '{email}'"}
            )
            contacts = json.loads(response.body).get("result", [])
            return contacts[0] if contacts else None
        except Exception as e:
            logger.error(f"Failed to get contact: {e}")
            return None

    def add_to_list(self, email: str, list_id: str) -> bool:
        """Добавить контакт в список."""
        if not self.client:
            return False

        try:
            # Получить contact_id
            contact = self.get_subscriber(email)
            if not contact:
                return False

            data = {
                "list_ids": [list_id],
                "contacts": [{"email": email}]
            }
            self.client.client.marketing.contacts.put(request_body=data)
            logger.info(f"Added {email} to list {list_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add to list: {e}")
            return False

    # ═══════════════════════════════════════════════════════════
    # УПРАВЛЕНИЕ СПИСКАМИ
    # ═══════════════════════════════════════════════════════════

    def get_lists(self) -> List[Dict]:
        """Получить все списки контактов."""
        if not self.client:
            return []

        try:
            response = self.client.client.marketing.lists.get()
            return json.loads(response.body).get("result", [])
        except Exception as e:
            logger.error(f"Failed to get lists: {e}")
            return []

    def create_list(self, name: str) -> Optional[Dict]:
        """Создать список контактов."""
        if not self.client:
            return None

        try:
            response = self.client.client.marketing.lists.post(
                request_body={"name": name}
            )
            result = json.loads(response.body)
            logger.info(f"Created list: {result['id']} - {name}")
            return result
        except Exception as e:
            logger.error(f"Failed to create list: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # СЕГМЕНТЫ
    # ═══════════════════════════════════════════════════════════

    def create_segment(self, name: str, query_dsl: str,
                       parent_list_ids: List[str] = None) -> Optional[Dict]:
        """
        Создать сегмент.

        query_dsl пример: "email LIKE '%@gmail.com%' AND custom_fields.client_type = 'vip'"
        """
        if not self.client:
            return None

        try:
            data = {
                "name": name,
                "query_dsl": query_dsl
            }
            if parent_list_ids:
                data["parent_list_ids"] = parent_list_ids

            response = self.client.client.marketing.segments.post(
                request_body=data
            )
            result = json.loads(response.body)
            logger.info(f"Created segment: {result['id']} - {name}")
            return result

        except Exception as e:
            logger.error(f"Failed to create segment: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # ШАБЛОНЫ
    # ═══════════════════════════════════════════════════════════

    def get_templates(self) -> List[Dict]:
        """Получить все шаблоны."""
        if not self.client:
            return []

        try:
            response = self.client.client.templates.get(
                query_params={"generations": "dynamic"}
            )
            return json.loads(response.body).get("templates", [])
        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return []

    def create_template(self, name: str, generation: str = "dynamic") -> Optional[Dict]:
        """Создать шаблон."""
        if not self.client:
            return None

        try:
            response = self.client.client.templates.post(
                request_body={"name": name, "generation": generation}
            )
            result = json.loads(response.body)
            logger.info(f"Created template: {result['id']} - {name}")
            return result
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return None

    def create_template_version(self, template_id: str, name: str,
                                subject: str, html_content: str,
                                text_content: str = "") -> Optional[Dict]:
        """Создать версию шаблона."""
        if not self.client:
            return None

        try:
            data = {
                "name": name,
                "subject": subject,
                "html_content": html_content,
                "plain_content": text_content,
                "active": 1
            }
            response = self.client.client.templates._(template_id).versions.post(
                request_body=data
            )
            result = json.loads(response.body)
            logger.info(f"Created template version: {result['id']}")
            return result
        except Exception as e:
            logger.error(f"Failed to create template version: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # КАМПАНИИ (Single Sends)
    # ═══════════════════════════════════════════════════════════

    def create_campaign(self, campaign: EmailCampaign) -> Dict:
        """Создать Single Send кампанию."""
        if not self.client:
            return {"error": "Client not initialized"}

        try:
            data = {
                "name": campaign.name,
                "send_to": {
                    "list_ids": [campaign.list_id] if campaign.list_id else [],
                    "segment_ids": [campaign.segment_id] if campaign.segment_id else [],
                    "all": not campaign.list_id and not campaign.segment_id
                },
                "email_config": {
                    "subject": campaign.subject,
                    "html_content": campaign.content_html,
                    "plain_content": campaign.content_text,
                    "sender_id": None,  # Использовать verified sender
                    "suppression_group_id": None
                }
            }

            response = self.client.client.marketing.singlesends.post(
                request_body=data
            )
            result = json.loads(response.body)
            campaign.campaign_id = result["id"]

            logger.info(f"Created single send: {result['id']}")
            return result

        except Exception as e:
            logger.error(f"Failed to create single send: {e}")
            return {"error": str(e)}

    def send_campaign(self, campaign_id: str) -> Dict:
        """Отправить Single Send."""
        if not self.client:
            return {"error": "Client not initialized"}

        try:
            response = self.client.client.marketing.singlesends._(campaign_id).schedule.put(
                request_body={"send_at": "now"}
            )
            logger.info(f"Single send scheduled: {campaign_id}")
            return {"status": "scheduled", "campaign_id": campaign_id}
        except Exception as e:
            logger.error(f"Failed to send single send: {e}")
            return {"error": str(e)}

    def schedule_campaign(self, campaign_id: str,
                          schedule_time: datetime) -> Dict:
        """Запланировать отправку."""
        if not self.client:
            return {"error": "Client not initialized"}

        try:
            response = self.client.client.marketing.singlesends._(campaign_id).schedule.put(
                request_body={"send_at": schedule_time.isoformat()}
            )
            logger.info(f"Single send scheduled: {campaign_id} at {schedule_time}")
            return {"status": "scheduled", "campaign_id": campaign_id}
        except Exception as e:
            logger.error(f"Failed to schedule single send: {e}")
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # СТАТИСТИКА
    # ═══════════════════════════════════════════════════════════

    def get_campaign_stats(self, campaign_id: str) -> EmailStats:
        """Получить статистику Single Send."""
        stats = EmailStats()

        if not self.client:
            return stats

        try:
            response = self.client.client.marketing.stats.singlesends._(campaign_id).get()
            data = json.loads(response.body).get("results", [{}])[0]

            stats.total_sent = data.get("requests", 0)
            stats.delivered = data.get("delivered", 0)
            stats.opens = data.get("opens", 0)
            stats.unique_opens = data.get("unique_opens", 0)
            stats.clicks = data.get("clicks", 0)
            stats.unique_clicks = data.get("unique_clicks", 0)
            stats.bounces = data.get("bounces", 0)
            stats.spam_reports = data.get("spam_reports", 0)
            stats.unsubscribes = data.get("unsubscribes", 0)

            return stats

        except Exception as e:
            logger.error(f"Failed to get campaign stats: {e}")
            return stats

    def get_global_stats(self, start_date: datetime,
                         end_date: datetime = None) -> Dict:
        """Получить глобальную статистику."""
        if not self.client:
            return {}

        end_date = end_date or datetime.now()

        try:
            response = self.client.client.stats.get(
                query_params={
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            )
            return json.loads(response.body)
        except Exception as e:
            logger.error(f"Failed to get global stats: {e}")
            return {}


# ═══════════════════════════════════════════════════════════════
# EMAIL MARKETING MANAGER
# ═══════════════════════════════════════════════════════════════

class EmailMarketingManager:
    """
    Единый менеджер email маркетинга.
    Объединяет работу с Mailchimp и SendGrid.
    """

    def __init__(self,
                 primary_provider: EmailProvider = EmailProvider.SENDGRID,
                 mailchimp_config: Dict = None,
                 sendgrid_config: Dict = None):
        """
        Инициализация менеджера.

        Args:
            primary_provider: Основной провайдер для массовых рассылок
            mailchimp_config: Конфиг Mailchimp {api_key, server_prefix, list_id}
            sendgrid_config: Конфиг SendGrid {api_key, from_email, from_name}
        """
        self.primary_provider = primary_provider

        # Инициализация провайдеров
        mailchimp_config = mailchimp_config or {}
        sendgrid_config = sendgrid_config or {}

        self.mailchimp = MailchimpProvider(**mailchimp_config)
        self.sendgrid = SendGridProvider(**sendgrid_config)

        # Jinja2 для шаблонов
        try:
            from jinja2 import Environment, BaseLoader
            self.jinja_env = Environment(loader=BaseLoader())
        except ImportError:
            logger.warning("jinja2 not installed. Templates won't work.")
            self.jinja_env = None

    def get_provider(self, provider: EmailProvider = None) -> EmailProviderBase:
        """Получить провайдер по типу."""
        provider = provider or self.primary_provider
        if provider == EmailProvider.MAILCHIMP:
            return self.mailchimp
        return self.sendgrid

    # ═══════════════════════════════════════════════════════════
    # РАБОТА С ШАБЛОНАМИ
    # ═══════════════════════════════════════════════════════════

    def render_template(self, email_type: EmailType, language: str = "ru",
                        **context) -> Dict[str, str]:
        """
        Отрендерить шаблон письма.

        Returns:
            {"subject": "...", "html": "...", "text": "..."}
        """
        if not self.jinja_env:
            return {"error": "Jinja2 not available"}

        template_data = EMAIL_TEMPLATES.get(email_type)
        if not template_data:
            return {"error": f"Template not found: {email_type}"}

        # Дефолтный контекст
        default_context = {
            "company_name": COMPANY_NAME,
            "company_address": COMPANY_ADDRESS,
            "website_url": COMPANY_WEBSITE,
            "unsubscribe_url": UNSUBSCRIBE_URL,
            "first_name": "Guest",
            "current_year": datetime.now().year
        }
        context = {**default_context, **context}

        # Рендеринг
        subject_key = f"subject_{language}"
        body_key = f"body_{language}"

        subject_tpl = template_data.get(subject_key, template_data.get("subject_en", ""))
        body_tpl = template_data.get(body_key, template_data.get("body_en", ""))

        try:
            subject = self.jinja_env.from_string(subject_tpl).render(**context)
            html = self.jinja_env.from_string(body_tpl).render(**context)

            # Простая текстовая версия (убираем HTML теги)
            text = re.sub(r'<[^>]+>', '', html)
            text = re.sub(r'\s+', ' ', text).strip()

            return {
                "subject": subject,
                "html": html,
                "text": text
            }
        except Exception as e:
            logger.error(f"Template render error: {e}")
            return {"error": str(e)}

    # ═══════════════════════════════════════════════════════════
    # ОТПРАВКА ПИСЕМ
    # ═══════════════════════════════════════════════════════════

    def send_welcome_email(self, subscriber: Subscriber) -> Dict:
        """Отправить приветственное письмо."""
        rendered = self.render_template(
            EmailType.WELCOME,
            language=subscriber.language,
            first_name=subscriber.first_name or "Guest"
        )

        if "error" in rendered:
            return rendered

        return self.sendgrid.send_email(
            to_email=subscriber.email,
            subject=rendered["subject"],
            html_content=rendered["html"],
            text_content=rendered["text"],
            categories=["welcome", subscriber.client_type.value]
        )

    def send_booking_confirmation(self, subscriber: Subscriber,
                                  booking_data: Dict) -> Dict:
        """Отправить подтверждение бронирования."""
        context = {
            "first_name": subscriber.first_name,
            **booking_data
        }

        rendered = self.render_template(
            EmailType.BOOKING_CONFIRMATION,
            language=subscriber.language,
            **context
        )

        if "error" in rendered:
            return rendered

        return self.sendgrid.send_email(
            to_email=subscriber.email,
            subject=rendered["subject"],
            html_content=rendered["html"],
            text_content=rendered["text"],
            categories=["booking", "transactional"]
        )

    def send_tour_reminder(self, subscriber: Subscriber,
                           tour_data: Dict) -> Dict:
        """Отправить напоминание о туре."""
        context = {
            "first_name": subscriber.first_name,
            "checklist": [
                "Удобная обувь",
                "Солнцезащитный крем",
                "Вода",
                "Головной убор",
                "Документы"
            ],
            **tour_data
        }

        rendered = self.render_template(
            EmailType.TOUR_REMINDER,
            language=subscriber.language,
            **context
        )

        if "error" in rendered:
            return rendered

        return self.sendgrid.send_email(
            to_email=subscriber.email,
            subject=rendered["subject"],
            html_content=rendered["html"],
            text_content=rendered["text"],
            categories=["reminder", "transactional"]
        )

    def send_feedback_request(self, subscriber: Subscriber,
                              service_name: str,
                              promo_code: str = None,
                              discount: int = 10) -> Dict:
        """Отправить запрос отзыва после тура."""
        promo_code = promo_code or f"REVIEW{datetime.now().strftime('%m%d')}"

        context = {
            "first_name": subscriber.first_name,
            "service_name": service_name,
            "review_url": f"{COMPANY_WEBSITE}/review",
            "google_review_url": "https://g.page/review",
            "tripadvisor_url": "https://tripadvisor.com/review",
            "promo_code": promo_code,
            "discount": discount
        }

        rendered = self.render_template(
            EmailType.FEEDBACK_REQUEST,
            language=subscriber.language,
            **context
        )

        if "error" in rendered:
            return rendered

        return self.sendgrid.send_email(
            to_email=subscriber.email,
            subject=rendered["subject"],
            html_content=rendered["html"],
            text_content=rendered["text"],
            categories=["feedback", "post-tour"]
        )

    def send_birthday_email(self, subscriber: Subscriber,
                            discount: int = 15) -> Dict:
        """Отправить поздравление с днём рождения."""
        promo_code = f"BDAY{subscriber.first_name[:3].upper()}{datetime.now().strftime('%m')}"
        promo_expiry = (datetime.now() + timedelta(days=30)).strftime("%d.%m.%Y")

        context = {
            "first_name": subscriber.first_name,
            "promo_code": promo_code,
            "promo_expiry": promo_expiry,
            "discount": discount
        }

        rendered = self.render_template(
            EmailType.BIRTHDAY,
            language=subscriber.language,
            **context
        )

        if "error" in rendered:
            return rendered

        return self.sendgrid.send_email(
            to_email=subscriber.email,
            subject=rendered["subject"],
            html_content=rendered["html"],
            text_content=rendered["text"],
            categories=["birthday", "promo"]
        )

    def send_promo_campaign(self, campaign_name: str, tours: List[Dict],
                            promo_title: str, discount: int,
                            promo_code: str, promo_end_date: str,
                            segment_id: str = None,
                            list_id: str = None,
                            provider: EmailProvider = None) -> Dict:
        """Отправить промо-кампанию."""
        provider = provider or self.primary_provider

        context = {
            "promo_title": promo_title,
            "promo_subtitle": f"Скидка {discount}% на избранные туры",
            "discount": discount,
            "promo_code": promo_code,
            "promo_end_date": promo_end_date,
            "tours": tours
        }

        rendered = self.render_template(EmailType.PROMO, **context)

        if "error" in rendered:
            return rendered

        campaign = EmailCampaign(
            name=campaign_name,
            subject=rendered["subject"],
            email_type=EmailType.PROMO,
            content_html=rendered["html"],
            content_text=rendered["text"],
            segment_id=segment_id,
            list_id=list_id
        )

        prov = self.get_provider(provider)
        result = prov.create_campaign(campaign)

        if "error" not in result:
            # Отправляем сразу
            send_result = prov.send_campaign(campaign.campaign_id)
            result["send_status"] = send_result

        return result

    # ═══════════════════════════════════════════════════════════
    # GDPR ФУНКЦИИ
    # ═══════════════════════════════════════════════════════════

    def send_double_optin(self, subscriber: Subscriber,
                          confirm_url: str) -> Dict:
        """Отправить письмо подтверждения подписки (Double Opt-In)."""
        template_data = EMAIL_TEMPLATES.get("double_optin")
        if not template_data or not self.jinja_env:
            return {"error": "Template not available"}

        context = {
            "first_name": subscriber.first_name or "Guest",
            "company_name": COMPANY_NAME,
            "company_address": COMPANY_ADDRESS,
            "confirm_url": confirm_url
        }

        lang = subscriber.language
        subject = self.jinja_env.from_string(
            template_data.get(f"subject_{lang}", template_data["subject_en"])
        ).render(**context)

        html = self.jinja_env.from_string(
            template_data.get(f"body_{lang}", template_data["body_ru"])
        ).render(**context)

        return self.sendgrid.send_email(
            to_email=subscriber.email,
            subject=subject,
            html_content=html,
            categories=["double-optin", "gdpr"]
        )

    def handle_unsubscribe(self, email: str,
                           provider: EmailProvider = None) -> Dict:
        """Обработать отписку."""
        results = {}

        # Отписываем от Mailchimp
        if self.mailchimp.client:
            results["mailchimp"] = self.mailchimp.unsubscribe(email)

        # SendGrid - удаляем из всех списков или помечаем
        if self.sendgrid.client:
            # В SendGrid можно добавить в suppression group
            results["sendgrid"] = "marked_unsubscribed"

        logger.info(f"Unsubscribed: {email}")
        return results

    def export_subscriber_data(self, email: str) -> Dict:
        """Экспортировать данные подписчика (GDPR)."""
        data = {
            "email": email,
            "export_date": datetime.now().isoformat(),
            "mailchimp": None,
            "sendgrid": None
        }

        if self.mailchimp.client:
            data["mailchimp"] = self.mailchimp.get_subscriber(email)

        if self.sendgrid.client:
            data["sendgrid"] = self.sendgrid.get_subscriber(email)

        return data

    def delete_subscriber_data(self, email: str) -> Dict:
        """Удалить все данные подписчика (GDPR Right to Erasure)."""
        results = {
            "email": email,
            "deleted_at": datetime.now().isoformat(),
            "mailchimp": False,
            "sendgrid": False
        }

        if self.mailchimp.client:
            results["mailchimp"] = self.mailchimp.delete_subscriber(email)

        if self.sendgrid.client:
            results["sendgrid"] = self.sendgrid.delete_subscriber(email)

        logger.info(f"Deleted all data for: {email}")
        return results

    # ═══════════════════════════════════════════════════════════
    # АВТОМАТИЗАЦИЯ
    # ═══════════════════════════════════════════════════════════

    def setup_drip_campaign(self, campaign_name: str,
                            emails: List[Dict],
                            trigger: str = "signup",
                            list_id: str = None) -> Dict:
        """
        Настроить drip campaign (серию автоматических писем).

        emails: [
            {"delay_days": 0, "type": EmailType.WELCOME, "context": {}},
            {"delay_days": 3, "type": EmailType.PROMO, "context": {...}},
            {"delay_days": 7, "type": EmailType.FEEDBACK_REQUEST, "context": {...}}
        ]
        """
        # В реальности это требует настройки через UI Mailchimp/SendGrid
        # или использования их automation API

        drip_config = {
            "name": campaign_name,
            "trigger": trigger,
            "list_id": list_id,
            "emails": []
        }

        for email_config in emails:
            rendered = self.render_template(
                email_config["type"],
                **email_config.get("context", {})
            )
            drip_config["emails"].append({
                "delay_days": email_config["delay_days"],
                "subject": rendered.get("subject"),
                "html": rendered.get("html")
            })

        logger.info(f"Drip campaign config prepared: {campaign_name}")
        return drip_config

    def get_birthday_subscribers(self, days_ahead: int = 0) -> List[Dict]:
        """
        Получить подписчиков с днём рождения.

        Args:
            days_ahead: Сколько дней вперёд искать (0 = сегодня)
        """
        target_date = datetime.now() + timedelta(days=days_ahead)
        target_month = target_date.month
        target_day = target_date.day

        # Это нужно делать через API провайдера
        # Mailchimp поддерживает birthday merge field
        logger.info(f"Looking for birthdays on {target_month}/{target_day}")

        # Заглушка - в реальности нужен запрос к API
        return []

    # ═══════════════════════════════════════════════════════════
    # АНАЛИТИКА
    # ═══════════════════════════════════════════════════════════

    def get_campaign_report(self, campaign_id: str,
                            provider: EmailProvider = None) -> Dict:
        """Получить полный отчёт по кампании."""
        provider = provider or self.primary_provider
        prov = self.get_provider(provider)

        stats = prov.get_campaign_stats(campaign_id)

        return {
            "campaign_id": campaign_id,
            "provider": provider.value,
            "stats": {
                "total_sent": stats.total_sent,
                "delivered": stats.delivered,
                "delivery_rate": f"{stats.delivery_rate:.1f}%",
                "opens": stats.opens,
                "unique_opens": stats.unique_opens,
                "open_rate": f"{stats.open_rate:.1f}%",
                "clicks": stats.clicks,
                "unique_clicks": stats.unique_clicks,
                "click_rate": f"{stats.click_rate:.1f}%",
                "bounces": stats.bounces,
                "bounce_rate": f"{stats.bounce_rate:.1f}%",
                "unsubscribes": stats.unsubscribes,
                "unsubscribe_rate": f"{stats.unsubscribe_rate:.1f}%",
                "spam_reports": stats.spam_reports
            }
        }

    def generate_monthly_report(self, year: int, month: int) -> Dict:
        """Сгенерировать месячный отчёт."""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        report = {
            "period": f"{year}-{month:02d}",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "sendgrid_stats": {},
            "summary": {}
        }

        # SendGrid статистика
        if self.sendgrid.client:
            report["sendgrid_stats"] = self.sendgrid.get_global_stats(
                start_date, end_date
            )

        return report


# ═══════════════════════════════════════════════════════════════
# УТИЛИТЫ
# ═══════════════════════════════════════════════════════════════

def validate_email(email: str) -> bool:
    """Валидация email адреса."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def generate_promo_code(prefix: str = "PROMO", length: int = 6) -> str:
    """Сгенерировать промокод."""
    import random
    import string
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{suffix}"


def detect_country_from_phone(phone: str) -> Country:
    """Определить страну по телефону."""
    phone = phone.replace(" ", "").replace("-", "").replace("+", "")

    if phone.startswith("7") and len(phone) == 11:
        return Country.RU
    elif phone.startswith("77") and len(phone) == 11:
        return Country.KZ
    elif phone.startswith("971"):
        return Country.UAE
    elif phone.startswith("1") and len(phone) == 11:
        return Country.US
    elif phone.startswith("44"):
        return Country.UK

    return Country.OTHER


def detect_language_from_name(name: str) -> str:
    """Определить язык по имени (эвристика)."""
    # Кириллица
    if re.search(r'[а-яА-ЯёЁ]', name):
        return "ru"
    # Арабские символы
    if re.search(r'[\u0600-\u06FF]', name):
        return "ar"
    return "en"


# ═══════════════════════════════════════════════════════════════
# CLI ИНТЕРФЕЙС
# ═══════════════════════════════════════════════════════════════

def main():
    """CLI интерфейс для email маркетинга."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Email Marketing Manager - Mailchimp & SendGrid Integration"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Проверка соединения
    ping_parser = subparsers.add_parser("ping", help="Check API connections")

    # Отправка тестового письма
    test_parser = subparsers.add_parser("test", help="Send test email")
    test_parser.add_argument("--email", required=True, help="Recipient email")
    test_parser.add_argument("--type", default="welcome",
                            choices=["welcome", "booking", "reminder", "feedback", "birthday", "promo"],
                            help="Email type")
    test_parser.add_argument("--provider", default="sendgrid",
                            choices=["sendgrid", "mailchimp"],
                            help="Email provider")

    # Добавление подписчика
    add_parser = subparsers.add_parser("add", help="Add subscriber")
    add_parser.add_argument("--email", required=True, help="Email address")
    add_parser.add_argument("--name", default="", help="Full name")
    add_parser.add_argument("--phone", default="", help="Phone number")
    add_parser.add_argument("--type", default="tourist",
                           choices=["tourist", "vip", "corporate", "agent", "b2b"],
                           help="Client type")
    add_parser.add_argument("--provider", default="both",
                           choices=["mailchimp", "sendgrid", "both"],
                           help="Add to which provider")

    # Статистика кампании
    stats_parser = subparsers.add_parser("stats", help="Get campaign statistics")
    stats_parser.add_argument("--campaign-id", required=True, help="Campaign ID")
    stats_parser.add_argument("--provider", default="sendgrid",
                             choices=["sendgrid", "mailchimp"],
                             help="Email provider")

    # GDPR операции
    gdpr_parser = subparsers.add_parser("gdpr", help="GDPR operations")
    gdpr_parser.add_argument("--action", required=True,
                            choices=["export", "delete", "unsubscribe"],
                            help="GDPR action")
    gdpr_parser.add_argument("--email", required=True, help="Email address")

    # Списки
    lists_parser = subparsers.add_parser("lists", help="Manage lists")
    lists_parser.add_argument("--action", default="list",
                             choices=["list", "create"],
                             help="Action")
    lists_parser.add_argument("--name", help="List name (for create)")
    lists_parser.add_argument("--provider", default="mailchimp",
                             choices=["sendgrid", "mailchimp"],
                             help="Email provider")

    args = parser.parse_args()

    # Инициализация менеджера
    manager = EmailMarketingManager()

    if args.command == "ping":
        print("Checking API connections...")

        if manager.mailchimp.client:
            mc_ok = manager.mailchimp.ping()
            print(f"Mailchimp: {'OK' if mc_ok else 'FAILED'}")
        else:
            print("Mailchimp: NOT CONFIGURED")

        if manager.sendgrid.client:
            print("SendGrid: CONFIGURED")
        else:
            print("SendGrid: NOT CONFIGURED")

    elif args.command == "test":
        print(f"Sending test {args.type} email to {args.email}...")

        subscriber = Subscriber(
            email=args.email,
            first_name="Test",
            last_name="User"
        )

        if args.type == "welcome":
            result = manager.send_welcome_email(subscriber)
        elif args.type == "booking":
            result = manager.send_booking_confirmation(subscriber, {
                "booking_id": "TEST-001",
                "service_name": "Desert Safari",
                "tour_date": "01.01.2025",
                "tour_time": "15:00",
                "guests_count": 2,
                "pickup_location": "Hotel lobby",
                "total_amount": "500",
                "currency": "AED",
                "driver_phone": "+971 50 123 4567",
                "support_email": "support@example.com",
                "support_phone": "+971 50 123 4567"
            })
        elif args.type == "reminder":
            result = manager.send_tour_reminder(subscriber, {
                "service_name": "Desert Safari",
                "tour_date": "01.01.2025",
                "tour_time": "15:00",
                "pickup_location": "Hotel lobby",
                "driver_phone": "+971 50 123 4567"
            })
        elif args.type == "feedback":
            result = manager.send_feedback_request(subscriber, "Desert Safari")
        elif args.type == "birthday":
            result = manager.send_birthday_email(subscriber)
        else:
            result = {"error": "Unknown email type"}

        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "add":
        print(f"Adding subscriber: {args.email}")

        name_parts = args.name.split(" ", 1) if args.name else ["", ""]

        subscriber = Subscriber(
            email=args.email,
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else "",
            phone=args.phone,
            client_type=ClientType(args.type),
            country=detect_country_from_phone(args.phone) if args.phone else Country.OTHER,
            language=detect_language_from_name(name_parts[0]) if name_parts[0] else "en",
            gdpr_consent=True,
            gdpr_consent_date=datetime.now()
        )

        results = {}
        if args.provider in ["mailchimp", "both"]:
            if manager.mailchimp.client:
                results["mailchimp"] = manager.mailchimp.add_subscriber(subscriber)

        if args.provider in ["sendgrid", "both"]:
            if manager.sendgrid.client:
                results["sendgrid"] = manager.sendgrid.add_subscriber(subscriber)

        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.command == "stats":
        print(f"Getting stats for campaign: {args.campaign_id}")

        provider = EmailProvider.MAILCHIMP if args.provider == "mailchimp" else EmailProvider.SENDGRID
        report = manager.get_campaign_report(args.campaign_id, provider)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.command == "gdpr":
        print(f"GDPR {args.action} for: {args.email}")

        if args.action == "export":
            result = manager.export_subscriber_data(args.email)
        elif args.action == "delete":
            result = manager.delete_subscriber_data(args.email)
        elif args.action == "unsubscribe":
            result = manager.handle_unsubscribe(args.email)
        else:
            result = {"error": "Unknown action"}

        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    elif args.command == "lists":
        provider = EmailProvider.MAILCHIMP if args.provider == "mailchimp" else EmailProvider.SENDGRID
        prov = manager.get_provider(provider)

        if args.action == "list":
            print(f"Lists from {args.provider}:")
            lists = prov.get_lists()
            for lst in lists:
                print(f"  - {lst.get('id', lst.get('name'))}: {lst.get('name')}")

        elif args.action == "create":
            if not args.name:
                print("Error: --name required for create")
                return

            if args.provider == "mailchimp":
                result = prov.create_list(
                    name=args.name,
                    company=COMPANY_NAME,
                    address=COMPANY_ADDRESS,
                    from_name=SENDGRID_FROM_NAME,
                    from_email=SENDGRID_FROM_EMAIL,
                    subject=f"News from {COMPANY_NAME}"
                )
            else:
                result = prov.create_list(args.name)

            print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
