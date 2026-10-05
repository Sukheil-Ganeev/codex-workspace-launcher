#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SMS Messaging via Twilio

Полная интеграция с Twilio для SMS рассылок:
- Отправка одиночных и bulk SMS
- Шаблоны сообщений с персонализацией
- Входящие SMS с webhook
- Автоответы и forwarding в WhatsApp
- Delivery reports и статистика
- Alphanumeric Sender ID
- Rate limiting и оптимальное время

Требования:
    pip install twilio flask requests python-dotenv

Переменные окружения:
    TWILIO_ACCOUNT_SID - Account SID из Twilio Console
    TWILIO_AUTH_TOKEN - Auth Token из Twilio Console
    TWILIO_PHONE_NUMBER - Номер отправителя (+1234567890)
    TWILIO_MESSAGING_SERVICE_SID - SID Messaging Service (опционально)
    TWILIO_ALPHA_SENDER_ID - Alphanumeric Sender ID (опционально)
"""

import os
import json
import time
import hashlib
import logging
import threading
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import wraps
import random

# Twilio SDK
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    from twilio.twiml.messaging_response import MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None
    TwilioRestException = Exception
    MessagingResponse = None

# Flask для webhook
try:
    from flask import Flask, request, Response
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# FastAPI (альтернатива)
try:
    from fastapi import FastAPI, Request, Form
    from fastapi.responses import PlainTextResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Локальные импорты
try:
    from config import CHATS_DIR, ANALYTICS_DIR, TELEGRAM_CONFIG
except ImportError:
    CHATS_DIR = Path("D:/Downloads/Chats")
    ANALYTICS_DIR = CHATS_DIR / "_аналитика"
    TELEGRAM_CONFIG = {}

# WhatsApp API для forwarding
try:
    from whatsapp_api import WhatsAppAPI
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    WhatsAppAPI = None


# ===============================================================================
# LOGGING
# ===============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ===============================================================================
# CONFIGURATION
# ===============================================================================
@dataclass
class TwilioConfig:
    """Конфигурация Twilio."""
    account_sid: str = ""
    auth_token: str = ""
    phone_number: str = ""  # Default From number
    messaging_service_sid: str = ""  # Messaging Service SID
    alpha_sender_id: str = ""  # Alphanumeric Sender ID (max 11 chars)

    # Webhook
    webhook_url: str = ""
    status_callback_url: str = ""

    # Rate limiting
    messages_per_second: float = 10.0  # Twilio allows higher for toll-free
    bulk_batch_size: int = 100
    bulk_delay_seconds: float = 0.1

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 2.0

    # Optimal sending times (UTC hours)
    optimal_hours_start: int = 9  # 9 AM local
    optimal_hours_end: int = 21   # 9 PM local

    # WhatsApp forwarding
    forward_to_whatsapp: bool = False
    whatsapp_forward_number: str = ""  # Manager's WhatsApp

    @classmethod
    def from_env(cls) -> "TwilioConfig":
        """Загрузить конфигурацию из переменных окружения."""
        return cls(
            account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
            auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
            phone_number=os.getenv("TWILIO_PHONE_NUMBER", ""),
            messaging_service_sid=os.getenv("TWILIO_MESSAGING_SERVICE_SID", ""),
            alpha_sender_id=os.getenv("TWILIO_ALPHA_SENDER_ID", ""),
            webhook_url=os.getenv("TWILIO_WEBHOOK_URL", ""),
            status_callback_url=os.getenv("TWILIO_STATUS_CALLBACK_URL", ""),
            forward_to_whatsapp=os.getenv("TWILIO_FORWARD_WHATSAPP", "false").lower() == "true",
            whatsapp_forward_number=os.getenv("TWILIO_WHATSAPP_FORWARD_NUMBER", ""),
        )

    def validate(self) -> bool:
        """Проверить обязательные параметры."""
        if not self.account_sid:
            logger.error("TWILIO_ACCOUNT_SID не установлен")
            return False
        if not self.auth_token:
            logger.error("TWILIO_AUTH_TOKEN не установлен")
            return False
        if not self.phone_number and not self.messaging_service_sid:
            logger.error("TWILIO_PHONE_NUMBER или TWILIO_MESSAGING_SERVICE_SID должен быть установлен")
            return False
        return True

    def get_sender(self, country_code: str = "") -> str:
        """
        Получить оптимальный sender ID для страны.

        Args:
            country_code: Код страны (AE, RU, US...)

        Returns:
            Номер телефона или Alpha Sender ID
        """
        # Страны поддерживающие Alphanumeric Sender ID
        alpha_supported = ["AE", "GB", "DE", "FR", "AU", "NZ", "SG", "IN"]

        if country_code in alpha_supported and self.alpha_sender_id:
            return self.alpha_sender_id

        return self.phone_number


# Глобальная конфигурация
config = TwilioConfig.from_env()


# ===============================================================================
# ENUMS & DATA CLASSES
# ===============================================================================
class SMSStatus(Enum):
    """Статусы SMS сообщений."""
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    UNDELIVERED = "undelivered"
    FAILED = "failed"
    RECEIVED = "received"  # Для входящих


class MessageType(Enum):
    """Типы сообщений для шаблонов."""
    BOOKING_CONFIRMATION = "booking_confirmation"
    TOUR_REMINDER = "tour_reminder"
    DRIVER_EN_ROUTE = "driver_en_route"
    REVIEW_REQUEST = "review_request"
    PROMO = "promo"
    PAYMENT_REMINDER = "payment_reminder"
    CUSTOM = "custom"


@dataclass
class SMSResult:
    """Результат отправки SMS."""
    success: bool
    sid: Optional[str] = None  # Twilio Message SID
    phone: Optional[str] = None
    status: Optional[str] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    price: Optional[str] = None
    price_unit: Optional[str] = None
    segments: int = 1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class IncomingSMS:
    """Входящее SMS сообщение."""
    sid: str
    from_phone: str
    to_phone: str
    body: str
    num_media: int = 0
    media_urls: List[str] = field(default_factory=list)
    from_city: Optional[str] = None
    from_state: Optional[str] = None
    from_country: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DeliveryReport:
    """Отчёт о доставке SMS."""
    sid: str
    status: str
    to_phone: str
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


# ===============================================================================
# SMS TEMPLATES
# ===============================================================================
class SMSTemplates:
    """
    Шаблоны SMS сообщений для туристического бизнеса.

    SMS ограничены 160 символами (GSM-7) или 70 (Unicode).
    Шаблоны оптимизированы для минимального количества сегментов.
    """

    # Максимальная длина SMS
    GSM7_SINGLE = 160
    GSM7_MULTI = 153  # Per segment in multipart
    UNICODE_SINGLE = 70
    UNICODE_MULTI = 67

    TEMPLATES = {
        "booking_confirmation": {
            "ru": "{name}, бронирование #{num} подтверждено! {tour} {date} в {time}. Встреча: {pickup}",
            "en": "{name}, booking #{num} confirmed! {tour} {date} at {time}. Pickup: {pickup}",
            "ar": "{name}، تم تأكيد الحجز #{num}! {tour} {date} الساعة {time}. الاستلام: {pickup}"
        },
        "tour_reminder": {
            "ru": "{name}, завтра {tour}! Водитель заберёт вас в {time} из {pickup}. Тел: {driver_phone}",
            "en": "{name}, tomorrow {tour}! Driver picks you at {time} from {pickup}. Tel: {driver_phone}",
            "ar": "{name}، غداً {tour}! السائق سيصلك الساعة {time} من {pickup}. هاتف: {driver_phone}"
        },
        "driver_en_route": {
            "ru": "{name}, водитель выехал! Будет через {eta} мин. Авто: {car}. Тел: {driver_phone}",
            "en": "{name}, driver on the way! ETA {eta} min. Car: {car}. Tel: {driver_phone}",
            "ar": "{name}، السائق في الطريق! الوصول خلال {eta} دقيقة. السيارة: {car}. هاتف: {driver_phone}"
        },
        "review_request": {
            "ru": "{name}, спасибо за выбор {company}! Оставьте отзыв: {link}",
            "en": "{name}, thank you for choosing {company}! Leave a review: {link}",
            "ar": "{name}، شكراً لاختيارك {company}! اترك تقييماً: {link}"
        },
        "promo": {
            "ru": "{name}, специально для вас: {offer}! Действует до {valid_until}. Подробнее: {link}",
            "en": "{name}, special for you: {offer}! Valid until {valid_until}. Details: {link}",
            "ar": "{name}، خاص لك: {offer}! صالح حتى {valid_until}. التفاصيل: {link}"
        },
        "payment_reminder": {
            "ru": "{name}, напоминаем об оплате {amount} за бронь #{num}. Срок: {due_date}",
            "en": "{name}, reminder: {amount} due for booking #{num}. Due date: {due_date}",
            "ar": "{name}، تذكير: {amount} مستحق للحجز #{num}. تاريخ الاستحقاق: {due_date}"
        },
    }

    # Автоответы на ключевые слова
    AUTO_REPLIES = {
        "stop": {
            "ru": "Вы отписались от рассылки. Для возобновления напишите START",
            "en": "You've unsubscribed. To resubscribe, text START",
        },
        "start": {
            "ru": "Вы подписались на рассылку. Для отписки напишите STOP",
            "en": "You've subscribed. To unsubscribe, text STOP",
        },
        "help": {
            "ru": "Служба поддержки: +971501234567. WhatsApp: wa.me/971501234567",
            "en": "Support: +971501234567. WhatsApp: wa.me/971501234567",
        },
        "info": {
            "ru": "Marsel Tours - экскурсии по ОАЭ. Сайт: marseltours.ae",
            "en": "Marsel Tours - UAE excursions. Website: marseltours.ae",
        },
    }

    @classmethod
    def get_template(cls, template_type: str, language: str = "ru") -> Optional[str]:
        """Получить шаблон по типу и языку."""
        template = cls.TEMPLATES.get(template_type, {})
        return template.get(language) or template.get("en")

    @classmethod
    def render(
        cls,
        template_type: str,
        params: Dict[str, str],
        language: str = "ru"
    ) -> Optional[str]:
        """
        Отрендерить шаблон с параметрами.

        Args:
            template_type: Тип шаблона
            params: Параметры для подстановки
            language: Язык шаблона

        Returns:
            Готовое сообщение или None
        """
        template = cls.get_template(template_type, language)
        if not template:
            return None

        try:
            return template.format(**params)
        except KeyError as e:
            logger.error(f"Отсутствует параметр шаблона: {e}")
            return None

    @classmethod
    def count_segments(cls, text: str) -> int:
        """
        Подсчитать количество SMS сегментов.

        GSM-7: 160 символов (single), 153 (multipart)
        Unicode: 70 символов (single), 67 (multipart)
        """
        # Проверяем, нужен ли Unicode
        gsm7_chars = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ ÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
        is_gsm7 = all(c in gsm7_chars for c in text)

        length = len(text)

        if is_gsm7:
            if length <= cls.GSM7_SINGLE:
                return 1
            return (length + cls.GSM7_MULTI - 1) // cls.GSM7_MULTI
        else:
            if length <= cls.UNICODE_SINGLE:
                return 1
            return (length + cls.UNICODE_MULTI - 1) // cls.UNICODE_MULTI

    @classmethod
    def get_auto_reply(cls, keyword: str, language: str = "ru") -> Optional[str]:
        """Получить автоответ по ключевому слову."""
        keyword_lower = keyword.lower().strip()
        replies = cls.AUTO_REPLIES.get(keyword_lower, {})
        return replies.get(language) or replies.get("en")

    @classmethod
    def list_templates(cls) -> List[str]:
        """Список доступных шаблонов."""
        return list(cls.TEMPLATES.keys())


# ===============================================================================
# TWILIO SMS CLIENT
# ===============================================================================
class TwilioSMS:
    """
    Клиент Twilio SMS API.

    Пример использования:
        sms = TwilioSMS()
        result = sms.send("+971501234567", "Привет!")
        if result.success:
            print(f"Отправлено: {result.sid}")
    """

    def __init__(self, cfg: Optional[TwilioConfig] = None):
        if not TWILIO_AVAILABLE:
            raise ImportError("Twilio SDK не установлен: pip install twilio")

        self.config = cfg or config

        if not self.config.validate():
            raise ValueError("Неверная конфигурация Twilio")

        self.client = Client(self.config.account_sid, self.config.auth_token)

        # Rate limiting
        self._last_request_time = 0
        self._request_interval = 1.0 / self.config.messages_per_second
        self._lock = threading.Lock()

        # Statistics
        self.stats = {
            "sent": 0,
            "delivered": 0,
            "failed": 0,
            "total_cost": 0.0,
            "total_segments": 0,
        }

        # Opt-out list (телефоны отписавшихся)
        self._opt_out_file = ANALYTICS_DIR / "sms_opt_out.json"
        self._opt_out_list = self._load_opt_out()

    def _rate_limit(self):
        """Соблюдение rate limit."""
        with self._lock:
            now = time.time()
            elapsed = now - self._last_request_time
            if elapsed < self._request_interval:
                time.sleep(self._request_interval - elapsed)
            self._last_request_time = time.time()

    def _format_phone(self, phone: str) -> str:
        """
        Форматировать номер телефона в E.164.

        Примеры:
            +971501234567 -> +971501234567
            971501234567 -> +971501234567
            0501234567 -> +971501234567 (UAE default)
        """
        phone = ''.join(filter(str.isdigit, phone))

        if phone.startswith('0') and len(phone) == 10:
            # UAE local format
            phone = '971' + phone[1:]

        if not phone.startswith('+'):
            phone = '+' + phone

        return phone

    def _get_country_code(self, phone: str) -> str:
        """Определить код страны по номеру телефона."""
        phone = self._format_phone(phone)

        country_prefixes = {
            "+971": "AE",  # UAE
            "+7": "RU",    # Russia
            "+1": "US",    # USA/Canada
            "+44": "GB",   # UK
            "+49": "DE",   # Germany
            "+33": "FR",   # France
            "+91": "IN",   # India
        }

        for prefix, code in country_prefixes.items():
            if phone.startswith(prefix):
                return code

        return "UNKNOWN"

    def _load_opt_out(self) -> set:
        """Загрузить список отписавшихся."""
        if self._opt_out_file.exists():
            try:
                data = json.loads(self._opt_out_file.read_text(encoding="utf-8"))
                return set(data)
            except:
                pass
        return set()

    def _save_opt_out(self):
        """Сохранить список отписавшихся."""
        self._opt_out_file.parent.mkdir(parents=True, exist_ok=True)
        self._opt_out_file.write_text(
            json.dumps(list(self._opt_out_list), ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def add_opt_out(self, phone: str):
        """Добавить номер в opt-out список."""
        phone = self._format_phone(phone)
        self._opt_out_list.add(phone)
        self._save_opt_out()
        logger.info(f"Opt-out добавлен: {phone}")

    def remove_opt_out(self, phone: str):
        """Удалить номер из opt-out списка."""
        phone = self._format_phone(phone)
        self._opt_out_list.discard(phone)
        self._save_opt_out()
        logger.info(f"Opt-out удалён: {phone}")

    def is_opted_out(self, phone: str) -> bool:
        """Проверить, отписан ли номер."""
        return self._format_phone(phone) in self._opt_out_list

    # -------------------------------------------------------------------------
    # ОТПРАВКА SMS
    # -------------------------------------------------------------------------
    def send(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None,
        status_callback: Optional[str] = None,
        schedule_at: Optional[datetime] = None,
        validity_period: int = 14400,  # 4 часа (секунды)
        smart_encoded: bool = True
    ) -> SMSResult:
        """
        Отправить SMS сообщение.

        Args:
            to: Номер телефона получателя
            body: Текст сообщения
            from_number: Номер отправителя (опционально)
            status_callback: URL для delivery callback
            schedule_at: Время отправки (опционально, Twilio Messaging Service)
            validity_period: Срок действия сообщения (секунды)
            smart_encoded: Оптимизировать кодировку

        Returns:
            SMSResult
        """
        phone = self._format_phone(to)

        # Проверка opt-out
        if self.is_opted_out(phone):
            return SMSResult(
                success=False,
                phone=phone,
                error_message="Recipient has opted out"
            )

        self._rate_limit()

        # Определяем отправителя
        if not from_number:
            country = self._get_country_code(phone)
            from_number = self.config.get_sender(country)

        # Параметры сообщения
        message_params = {
            "to": phone,
            "body": body,
        }

        # Используем Messaging Service или номер
        if self.config.messaging_service_sid:
            message_params["messaging_service_sid"] = self.config.messaging_service_sid

            # Scheduled messages (только с Messaging Service)
            if schedule_at:
                message_params["send_at"] = schedule_at.strftime("%Y-%m-%dT%H:%M:%SZ")
                message_params["schedule_type"] = "fixed"
        else:
            message_params["from_"] = from_number

        # Status callback
        if status_callback or self.config.status_callback_url:
            message_params["status_callback"] = status_callback or self.config.status_callback_url

        # Validity period
        message_params["validity_period"] = validity_period

        try:
            message = self.client.messages.create(**message_params)

            # Подсчёт сегментов
            segments = SMSTemplates.count_segments(body)

            self.stats["sent"] += 1
            self.stats["total_segments"] += segments

            logger.info(f"SMS отправлено -> {phone}: {body[:50]}... ({segments} сегм.)")

            return SMSResult(
                success=True,
                sid=message.sid,
                phone=phone,
                status=message.status,
                segments=segments
            )

        except TwilioRestException as e:
            self.stats["failed"] += 1
            logger.error(f"Ошибка Twilio: {e.code} - {e.msg}")

            return SMSResult(
                success=False,
                phone=phone,
                error_code=e.code,
                error_message=e.msg
            )

    def send_template(
        self,
        to: str,
        template_type: str,
        params: Dict[str, str],
        language: str = "ru",
        **kwargs
    ) -> SMSResult:
        """
        Отправить SMS по шаблону.

        Args:
            to: Номер телефона
            template_type: Тип шаблона
            params: Параметры для подстановки
            language: Язык сообщения
            **kwargs: Дополнительные параметры для send()

        Returns:
            SMSResult
        """
        body = SMSTemplates.render(template_type, params, language)

        if not body:
            return SMSResult(
                success=False,
                phone=to,
                error_message=f"Template '{template_type}' not found or missing params"
            )

        return self.send(to, body, **kwargs)

    # -------------------------------------------------------------------------
    # BULK ОТПРАВКА
    # -------------------------------------------------------------------------
    def send_bulk(
        self,
        recipients: List[Dict[str, str]],
        message_template: str,
        delay_between: float = 0.1,
        progress_callback: Optional[Callable[[int, int, SMSResult], None]] = None
    ) -> Dict:
        """
        Массовая отправка SMS с персонализацией.

        Args:
            recipients: Список получателей [{"phone": "...", "name": "...", ...}]
            message_template: Шаблон сообщения с плейсхолдерами {name}, {phone}...
            delay_between: Задержка между сообщениями (секунды)
            progress_callback: Callback для отслеживания прогресса

        Returns:
            Статистика: {"sent": N, "failed": N, "total_cost": X, "results": [...]}
        """
        results = []
        sent = 0
        failed = 0
        total_segments = 0
        total = len(recipients)

        for i, recipient in enumerate(recipients):
            phone = recipient.get("phone", "")
            if not phone:
                continue

            # Персонализация
            message = message_template
            for key, value in recipient.items():
                message = message.replace(f"{{{key}}}", str(value))

            # Отправка
            result = self.send(phone, message)
            results.append(result.to_dict())

            if result.success:
                sent += 1
                total_segments += result.segments
            else:
                failed += 1

            # Callback
            if progress_callback:
                progress_callback(i + 1, total, result)

            # Задержка
            if i < total - 1:
                time.sleep(delay_between)

        return {
            "sent": sent,
            "failed": failed,
            "total": total,
            "total_segments": total_segments,
            "results": results
        }

    def send_bulk_template(
        self,
        recipients: List[Dict[str, str]],
        template_type: str,
        language: str = "ru",
        delay_between: float = 0.1,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Массовая отправка по шаблону.

        Args:
            recipients: Список с phone и параметрами шаблона
            template_type: Тип шаблона
            language: Язык
            delay_between: Задержка
            progress_callback: Callback прогресса

        Returns:
            Статистика
        """
        results = []
        sent = 0
        failed = 0
        total_segments = 0
        total = len(recipients)

        for i, recipient in enumerate(recipients):
            phone = recipient.pop("phone", "")
            if not phone:
                continue

            result = self.send_template(phone, template_type, recipient, language)
            recipient["phone"] = phone  # Восстанавливаем

            results.append(result.to_dict())

            if result.success:
                sent += 1
                total_segments += result.segments
            else:
                failed += 1

            if progress_callback:
                progress_callback(i + 1, total, result)

            if i < total - 1:
                time.sleep(delay_between)

        return {
            "sent": sent,
            "failed": failed,
            "total": total,
            "total_segments": total_segments,
            "results": results
        }

    # -------------------------------------------------------------------------
    # СТАТУС И ОТЧЁТЫ
    # -------------------------------------------------------------------------
    def get_message_status(self, message_sid: str) -> Optional[Dict]:
        """
        Получить статус сообщения по SID.

        Returns:
            Dict с информацией о сообщении
        """
        try:
            message = self.client.messages(message_sid).fetch()

            return {
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "body": message.body,
                "date_sent": str(message.date_sent) if message.date_sent else None,
                "date_updated": str(message.date_updated) if message.date_updated else None,
                "price": message.price,
                "price_unit": message.price_unit,
                "error_code": message.error_code,
                "error_message": message.error_message,
                "num_segments": message.num_segments,
            }
        except TwilioRestException as e:
            logger.error(f"Ошибка получения статуса: {e}")
            return None

    def get_delivery_report(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Получить отчёт о доставке за период.

        Args:
            date_from: Начало периода
            date_to: Конец периода
            status: Фильтр по статусу
            limit: Максимум записей

        Returns:
            Список сообщений
        """
        try:
            params = {"limit": limit}

            if date_from:
                params["date_sent_after"] = date_from
            if date_to:
                params["date_sent_before"] = date_to
            if status:
                params["status"] = status

            messages = self.client.messages.list(**params)

            return [
                {
                    "sid": m.sid,
                    "to": m.to,
                    "status": m.status,
                    "date_sent": str(m.date_sent) if m.date_sent else None,
                    "price": m.price,
                    "error_code": m.error_code,
                }
                for m in messages
            ]
        except TwilioRestException as e:
            logger.error(f"Ошибка получения отчёта: {e}")
            return []

    def get_cost_report(
        self,
        date_from: datetime,
        date_to: Optional[datetime] = None
    ) -> Dict:
        """
        Получить отчёт о стоимости за период.

        Returns:
            Dict с разбивкой по странам и итогами
        """
        date_to = date_to or datetime.now()
        messages = self.get_delivery_report(date_from, date_to, limit=1000)

        by_country = {}
        total_cost = 0.0
        total_messages = 0
        total_delivered = 0
        total_failed = 0

        for msg in messages:
            phone = msg["to"]
            country = self._get_country_code(phone)
            price = float(msg["price"] or 0)
            status = msg["status"]

            if country not in by_country:
                by_country[country] = {
                    "count": 0,
                    "cost": 0.0,
                    "delivered": 0,
                    "failed": 0
                }

            by_country[country]["count"] += 1
            by_country[country]["cost"] += price

            if status == "delivered":
                by_country[country]["delivered"] += 1
                total_delivered += 1
            elif status in ("failed", "undelivered"):
                by_country[country]["failed"] += 1
                total_failed += 1

            total_cost += price
            total_messages += 1

        return {
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            },
            "total": {
                "messages": total_messages,
                "cost": round(total_cost, 4),
                "currency": "USD",
                "delivered": total_delivered,
                "failed": total_failed,
                "delivery_rate": round(total_delivered / total_messages * 100, 2) if total_messages else 0
            },
            "by_country": by_country
        }

    # -------------------------------------------------------------------------
    # ОПТИМАЛЬНОЕ ВРЕМЯ
    # -------------------------------------------------------------------------
    def get_optimal_send_time(
        self,
        timezone_offset: int = 4  # UAE = UTC+4
    ) -> datetime:
        """
        Получить оптимальное время для отправки.

        Учитывает:
        - Рабочие часы (9-21)
        - Не отправлять ночью
        - Не отправлять в выходные рано утром

        Args:
            timezone_offset: Смещение от UTC

        Returns:
            Оптимальное datetime для отправки
        """
        now_utc = datetime.utcnow()
        now_local = now_utc + timedelta(hours=timezone_offset)

        hour = now_local.hour
        weekday = now_local.weekday()  # 0 = Monday

        # Если сейчас оптимальное время - отправляем сразу
        if self.config.optimal_hours_start <= hour < self.config.optimal_hours_end:
            return now_utc

        # Если ночь - ждём утра
        if hour < self.config.optimal_hours_start:
            delay_hours = self.config.optimal_hours_start - hour
        else:
            # После 21:00 - ждём следующего утра
            delay_hours = 24 - hour + self.config.optimal_hours_start

        # В пятницу/субботу (ОАЭ выходные) откладываем на воскресенье
        if weekday == 4:  # Friday
            delay_hours += 48
        elif weekday == 5:  # Saturday
            delay_hours += 24

        optimal = now_utc + timedelta(hours=delay_hours)

        # Добавляем случайный разброс (до 30 мин) для естественности
        optimal += timedelta(minutes=random.randint(0, 30))

        return optimal

    def should_send_now(self, timezone_offset: int = 4) -> bool:
        """Проверить, оптимально ли сейчас отправлять SMS."""
        now_local = datetime.utcnow() + timedelta(hours=timezone_offset)
        hour = now_local.hour
        return self.config.optimal_hours_start <= hour < self.config.optimal_hours_end


# ===============================================================================
# WEBHOOK HANDLER
# ===============================================================================
class SMSWebhookHandler:
    """
    Обработчик Webhook от Twilio.

    Обрабатывает:
    - Входящие SMS
    - Delivery status callbacks
    - Автоответы
    - Forwarding в WhatsApp
    """

    def __init__(self, cfg: Optional[TwilioConfig] = None):
        self.config = cfg or config
        self.sms_client: Optional[TwilioSMS] = None
        self.whatsapp_client: Optional[WhatsAppAPI] = None

        # Callbacks
        self._message_handlers: List[Callable[[IncomingSMS], None]] = []
        self._status_handlers: List[Callable[[DeliveryReport], None]] = []

        # Auto-reply enabled
        self.auto_reply_enabled = True
        self.default_language = "ru"

        # Message logger
        self._log_file = ANALYTICS_DIR / "sms_incoming.json"

    def set_sms_client(self, client: TwilioSMS):
        """Установить SMS клиент для автоответов."""
        self.sms_client = client

    def set_whatsapp_client(self, client):
        """Установить WhatsApp клиент для forwarding."""
        self.whatsapp_client = client

    def on_message(self, handler: Callable[[IncomingSMS], None]):
        """Декоратор для обработчика входящих SMS."""
        self._message_handlers.append(handler)
        return handler

    def on_status(self, handler: Callable[[DeliveryReport], None]):
        """Декоратор для обработчика статусов."""
        self._status_handlers.append(handler)
        return handler

    def process_incoming(self, form_data: Dict) -> str:
        """
        Обработать входящее SMS.

        Args:
            form_data: Данные из Twilio webhook (request.form)

        Returns:
            TwiML response
        """
        incoming = IncomingSMS(
            sid=form_data.get("MessageSid", ""),
            from_phone=form_data.get("From", ""),
            to_phone=form_data.get("To", ""),
            body=form_data.get("Body", ""),
            num_media=int(form_data.get("NumMedia", 0)),
            from_city=form_data.get("FromCity"),
            from_state=form_data.get("FromState"),
            from_country=form_data.get("FromCountry"),
        )

        # Извлечение медиа URL
        for i in range(incoming.num_media):
            media_url = form_data.get(f"MediaUrl{i}")
            if media_url:
                incoming.media_urls.append(media_url)

        logger.info(f"Входящее SMS от {incoming.from_phone}: {incoming.body[:50]}...")

        # Логирование
        self._log_message(incoming)

        # Вызов обработчиков
        for handler in self._message_handlers:
            try:
                handler(incoming)
            except Exception as e:
                logger.error(f"Ошибка в обработчике: {e}")

        # Проверка opt-out/opt-in
        body_lower = incoming.body.lower().strip()

        if body_lower in ("stop", "unsubscribe", "отписаться"):
            if self.sms_client:
                self.sms_client.add_opt_out(incoming.from_phone)
            return self._twiml_response(
                SMSTemplates.get_auto_reply("stop", self.default_language)
            )

        if body_lower in ("start", "subscribe", "подписаться"):
            if self.sms_client:
                self.sms_client.remove_opt_out(incoming.from_phone)
            return self._twiml_response(
                SMSTemplates.get_auto_reply("start", self.default_language)
            )

        # Автоответ
        if self.auto_reply_enabled:
            auto_reply = SMSTemplates.get_auto_reply(body_lower, self.default_language)
            if auto_reply:
                return self._twiml_response(auto_reply)

        # Forwarding в WhatsApp
        if self.config.forward_to_whatsapp and self.whatsapp_client:
            self._forward_to_whatsapp(incoming)

        # Пустой ответ если нет автоответа
        return self._twiml_response(None)

    def process_status(self, form_data: Dict) -> str:
        """
        Обработать callback статуса доставки.

        Args:
            form_data: Данные из Twilio callback

        Returns:
            OK response
        """
        report = DeliveryReport(
            sid=form_data.get("MessageSid", ""),
            status=form_data.get("MessageStatus", ""),
            to_phone=form_data.get("To", ""),
            error_code=int(form_data.get("ErrorCode", 0)) or None,
            error_message=form_data.get("ErrorMessage"),
        )

        logger.info(f"Status update: {report.sid} -> {report.status}")

        # Вызов обработчиков
        for handler in self._status_handlers:
            try:
                handler(report)
            except Exception as e:
                logger.error(f"Ошибка в обработчике статуса: {e}")

        return "OK"

    def _twiml_response(self, message: Optional[str]) -> str:
        """Создать TwiML response."""
        if not TWILIO_AVAILABLE or not MessagingResponse:
            return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'

        response = MessagingResponse()
        if message:
            response.message(message)
        return str(response)

    def _forward_to_whatsapp(self, incoming: IncomingSMS):
        """Переслать SMS в WhatsApp."""
        if not self.whatsapp_client or not self.config.whatsapp_forward_number:
            return

        try:
            forward_text = (
                f"[SMS от {incoming.from_phone}]\n"
                f"Город: {incoming.from_city or 'N/A'}\n"
                f"Страна: {incoming.from_country or 'N/A'}\n\n"
                f"{incoming.body}"
            )

            self.whatsapp_client.send_text(
                self.config.whatsapp_forward_number,
                forward_text
            )
            logger.info(f"SMS переслано в WhatsApp: {self.config.whatsapp_forward_number}")
        except Exception as e:
            logger.error(f"Ошибка forwarding в WhatsApp: {e}")

    def _log_message(self, incoming: IncomingSMS):
        """Логировать входящее сообщение."""
        self._log_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            if self._log_file.exists():
                data = json.loads(self._log_file.read_text(encoding="utf-8"))
            else:
                data = []

            data.append(incoming.to_dict())

            # Ограничение размера
            if len(data) > 5000:
                data = data[-5000:]

            self._log_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Ошибка логирования SMS: {e}")


# ===============================================================================
# FLASK WEBHOOK SERVER
# ===============================================================================
def create_flask_app(webhook_handler: SMSWebhookHandler) -> "Flask":
    """
    Создать Flask приложение для SMS webhook.

    Usage:
        handler = SMSWebhookHandler()

        @handler.on_message
        def on_sms(msg):
            print(f"SMS от {msg.from_phone}: {msg.body}")

        app = create_flask_app(handler)
        app.run(port=5001)
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask не установлен: pip install flask")

    app = Flask(__name__)

    @app.route("/sms/incoming", methods=["POST"])
    def incoming_sms():
        """Webhook для входящих SMS."""
        twiml = webhook_handler.process_incoming(request.form.to_dict())
        return Response(twiml, mimetype="application/xml")

    @app.route("/sms/status", methods=["POST"])
    def sms_status():
        """Webhook для статусов доставки."""
        result = webhook_handler.process_status(request.form.to_dict())
        return result, 200

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "timestamp": datetime.now().isoformat()}

    return app


# ===============================================================================
# SMS LOGGER
# ===============================================================================
class SMSLogger:
    """
    Логирование SMS сообщений.
    """

    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or (ANALYTICS_DIR / "sms_messages.json")
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        """Создать файл если не существует."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            self.log_file.write_text("[]", encoding="utf-8")

    def log_outgoing(self, result: SMSResult, template_type: str = None, content: str = ""):
        """Логировать исходящее SMS."""
        record = {
            "direction": "outgoing",
            "sid": result.sid,
            "phone": result.phone,
            "template": template_type,
            "content": content[:200],
            "success": result.success,
            "status": result.status,
            "segments": result.segments,
            "error_code": result.error_code,
            "error_message": result.error_message,
            "timestamp": datetime.now().isoformat()
        }
        self._append(record)

    def log_incoming(self, message: IncomingSMS):
        """Логировать входящее SMS."""
        record = {
            "direction": "incoming",
            "sid": message.sid,
            "phone": message.from_phone,
            "content": message.body[:200],
            "country": message.from_country,
            "timestamp": datetime.now().isoformat()
        }
        self._append(record)

    def _append(self, record: Dict):
        """Добавить запись в лог."""
        with self._lock:
            try:
                data = json.loads(self.log_file.read_text(encoding="utf-8"))
                data.append(record)

                if len(data) > 10000:
                    data = data[-10000:]

                self.log_file.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
            except Exception as e:
                logger.error(f"Ошибка логирования: {e}")

    def get_statistics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict:
        """
        Получить статистику SMS.

        Returns:
            Dict со статистикой
        """
        try:
            data = json.loads(self.log_file.read_text(encoding="utf-8"))
        except:
            data = []

        # Фильтрация по датам
        if date_from or date_to:
            filtered = []
            for record in data:
                ts = datetime.fromisoformat(record.get("timestamp", "2000-01-01"))
                if date_from and ts < date_from:
                    continue
                if date_to and ts > date_to:
                    continue
                filtered.append(record)
            data = filtered

        # Подсчёт статистики
        outgoing = [r for r in data if r.get("direction") == "outgoing"]
        incoming = [r for r in data if r.get("direction") == "incoming"]

        outgoing_success = [r for r in outgoing if r.get("success")]
        outgoing_failed = [r for r in outgoing if not r.get("success")]

        total_segments = sum(r.get("segments", 1) for r in outgoing_success)

        # По странам
        by_country = {}
        for r in data:
            country = r.get("country", "UNKNOWN")
            if country not in by_country:
                by_country[country] = 0
            by_country[country] += 1

        # По шаблонам
        by_template = {}
        for r in outgoing:
            template = r.get("template") or "custom"
            if template not in by_template:
                by_template[template] = 0
            by_template[template] += 1

        return {
            "total": len(data),
            "outgoing": {
                "total": len(outgoing),
                "success": len(outgoing_success),
                "failed": len(outgoing_failed),
                "segments": total_segments,
                "delivery_rate": round(len(outgoing_success) / len(outgoing) * 100, 2) if outgoing else 0
            },
            "incoming": {
                "total": len(incoming)
            },
            "by_country": by_country,
            "by_template": by_template
        }


# ===============================================================================
# CONVENIENCE FUNCTIONS
# ===============================================================================
def send_booking_sms(
    phone: str,
    name: str,
    booking_num: str,
    tour: str,
    date: str,
    time: str,
    pickup: str,
    language: str = "ru"
) -> SMSResult:
    """Отправить SMS подтверждение бронирования."""
    sms = TwilioSMS()
    return sms.send_template(
        to=phone,
        template_type="booking_confirmation",
        params={
            "name": name,
            "num": booking_num,
            "tour": tour,
            "date": date,
            "time": time,
            "pickup": pickup
        },
        language=language
    )


def send_reminder_sms(
    phone: str,
    name: str,
    tour: str,
    time: str,
    pickup: str,
    driver_phone: str,
    language: str = "ru"
) -> SMSResult:
    """Отправить SMS напоминание о туре."""
    sms = TwilioSMS()
    return sms.send_template(
        to=phone,
        template_type="tour_reminder",
        params={
            "name": name,
            "tour": tour,
            "time": time,
            "pickup": pickup,
            "driver_phone": driver_phone
        },
        language=language
    )


def send_driver_sms(
    phone: str,
    name: str,
    eta: str,
    car: str,
    driver_phone: str,
    language: str = "ru"
) -> SMSResult:
    """Отправить SMS о выезде водителя."""
    sms = TwilioSMS()
    return sms.send_template(
        to=phone,
        template_type="driver_en_route",
        params={
            "name": name,
            "eta": eta,
            "car": car,
            "driver_phone": driver_phone
        },
        language=language
    )


def send_review_sms(
    phone: str,
    name: str,
    company: str,
    link: str,
    language: str = "ru"
) -> SMSResult:
    """Отправить SMS с запросом отзыва."""
    sms = TwilioSMS()
    return sms.send_template(
        to=phone,
        template_type="review_request",
        params={
            "name": name,
            "company": company,
            "link": link
        },
        language=language
    )


# ===============================================================================
# MAIN / DEMO
# ===============================================================================
def main():
    """Демонстрация возможностей."""
    print("=" * 60)
    print("Twilio SMS Integration")
    print("=" * 60)

    # Проверка Twilio SDK
    if not TWILIO_AVAILABLE:
        print("\n[!] Twilio SDK не установлен")
        print("    pip install twilio")
        return

    print("\n[OK] Twilio SDK установлен")

    # Проверка конфигурации
    cfg = TwilioConfig.from_env()

    if not cfg.validate():
        print("\n[!] Конфигурация не полная. Установите переменные окружения:")
        print("    TWILIO_ACCOUNT_SID")
        print("    TWILIO_AUTH_TOKEN")
        print("    TWILIO_PHONE_NUMBER")
        print("")
        print("Опционально:")
        print("    TWILIO_MESSAGING_SERVICE_SID")
        print("    TWILIO_ALPHA_SENDER_ID")
        return

    print(f"\n[OK] Конфигурация загружена")
    print(f"    Account SID: {cfg.account_sid[:10]}...")
    print(f"    Phone: {cfg.phone_number}")
    if cfg.alpha_sender_id:
        print(f"    Alpha Sender: {cfg.alpha_sender_id}")

    # Инициализация клиента
    try:
        sms = TwilioSMS(cfg)
        print("\n[OK] Twilio клиент инициализирован")
    except Exception as e:
        print(f"\n[!] Ошибка инициализации: {e}")
        return

    # Список шаблонов
    print("\n[TEMPLATES] Доступные шаблоны:")
    for template in SMSTemplates.list_templates():
        print(f"    - {template}")

    # Подсчёт сегментов
    print("\n[SEGMENTS] Примеры:")
    test_messages = [
        "Hello World",  # GSM-7, 1 segment
        "Привет мир! Это тестовое сообщение на русском языке.",  # Unicode
        "A" * 160,  # GSM-7, 1 segment (max)
        "A" * 161,  # GSM-7, 2 segments
    ]

    for msg in test_messages:
        segments = SMSTemplates.count_segments(msg)
        print(f"    '{msg[:30]}...' ({len(msg)} chars) = {segments} segment(s)")

    # Оптимальное время
    print("\n[TIMING] Оптимальное время отправки:")
    optimal = sms.get_optimal_send_time(timezone_offset=4)
    print(f"    Сейчас оптимально: {sms.should_send_now(4)}")
    print(f"    Следующее оптимальное: {optimal}")

    # Webhook handler
    print("\n[WEBHOOK] Настройка обработчика...")
    handler = SMSWebhookHandler(cfg)
    handler.set_sms_client(sms)

    @handler.on_message
    def on_sms(msg: IncomingSMS):
        print(f"    <- SMS от {msg.from_phone}: {msg.body}")

    @handler.on_status
    def on_status(report: DeliveryReport):
        print(f"    [STATUS] {report.sid}: {report.status}")

    print("    Обработчик готов")

    # Logger
    print("\n[LOGGER] Инициализация...")
    sms_logger = SMSLogger()
    print(f"    Файл: {sms_logger.log_file}")

    print("\n" + "=" * 60)
    print("Готово к использованию!")
    print("=" * 60)

    # Примеры (закомментировано)
    # result = sms.send("+971501234567", "Test message")
    # print(f"Result: {result}")


if __name__ == "__main__":
    main()
