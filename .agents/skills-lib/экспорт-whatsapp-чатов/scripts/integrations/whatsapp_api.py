#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WhatsApp Business API Integration (Cloud API от Meta)

Полная интеграция с WhatsApp Business Cloud API:
- Отправка текстовых, шаблонных, медиа сообщений
- Интерактивные кнопки и списки
- Webhook для входящих сообщений
- Bulk операции с rate limiting
- Интеграция с Bitrix24
- Очередь сообщений

Требования:
    pip install requests flask redis python-dotenv

Переменные окружения:
    WHATSAPP_PHONE_NUMBER_ID - ID телефонного номера
    WHATSAPP_ACCESS_TOKEN - Access token из Meta
    WHATSAPP_VERIFY_TOKEN - Токен верификации webhook
    WHATSAPP_BUSINESS_ACCOUNT_ID - ID бизнес аккаунта
"""

import os
import json
import time
import hashlib
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import wraps
import queue
import random

import requests

# Попытка импорта Flask (опционально)
try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Попытка импорта FastAPI (опционально)
try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import PlainTextResponse, JSONResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Попытка импорта Redis (опционально)
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Локальные импорты
try:
    from config import BITRIX24_CONFIG, CHATS_DIR, ANALYTICS_DIR
except ImportError:
    BITRIX24_CONFIG = {}
    CHATS_DIR = Path("D:/Downloads/Chats")
    ANALYTICS_DIR = CHATS_DIR / "_аналитика"

# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass
class WhatsAppConfig:
    """Конфигурация WhatsApp Business API."""
    phone_number_id: str = ""
    access_token: str = ""
    verify_token: str = ""
    business_account_id: str = ""
    api_version: str = "v18.0"
    base_url: str = "https://graph.facebook.com"

    # Rate limiting
    messages_per_second: float = 80  # Meta allows ~80 msg/sec
    bulk_batch_size: int = 50
    bulk_delay_seconds: float = 1.0

    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0

    # Queue settings
    queue_file: str = "whatsapp_queue.json"
    use_redis: bool = False
    redis_url: str = "redis://localhost:6379/0"

    @classmethod
    def from_env(cls) -> "WhatsAppConfig":
        """Загрузить конфигурацию из переменных окружения."""
        return cls(
            phone_number_id=os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
            access_token=os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
            verify_token=os.getenv("WHATSAPP_VERIFY_TOKEN", ""),
            business_account_id=os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", ""),
            api_version=os.getenv("WHATSAPP_API_VERSION", "v18.0"),
            use_redis=os.getenv("WHATSAPP_USE_REDIS", "false").lower() == "true",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        )

    def validate(self) -> bool:
        """Проверить обязательные параметры."""
        if not self.phone_number_id:
            logger.error("WHATSAPP_PHONE_NUMBER_ID не установлен")
            return False
        if not self.access_token:
            logger.error("WHATSAPP_ACCESS_TOKEN не установлен")
            return False
        return True

    @property
    def messages_url(self) -> str:
        """URL для отправки сообщений."""
        return f"{self.base_url}/{self.api_version}/{self.phone_number_id}/messages"

    @property
    def media_url(self) -> str:
        """URL для загрузки медиа."""
        return f"{self.base_url}/{self.api_version}/{self.phone_number_id}/media"


# Глобальная конфигурация
config = WhatsAppConfig.from_env()


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS & DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════
class MessageStatus(Enum):
    """Статусы сообщений."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class MessageType(Enum):
    """Типы сообщений."""
    TEXT = "text"
    TEMPLATE = "template"
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACTS = "contacts"
    INTERACTIVE = "interactive"
    REACTION = "reaction"


@dataclass
class MessageResult:
    """Результат отправки сообщения."""
    success: bool
    message_id: Optional[str] = None
    phone: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class IncomingMessage:
    """Входящее сообщение."""
    message_id: str
    from_phone: str
    timestamp: str
    message_type: str
    text: Optional[str] = None
    media_id: Optional[str] = None
    media_url: Optional[str] = None
    caption: Optional[str] = None
    reaction: Optional[Dict] = None
    location: Optional[Dict] = None
    contacts: Optional[List] = None
    context: Optional[Dict] = None  # Reply context

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class StatusUpdate:
    """Обновление статуса сообщения."""
    message_id: str
    status: str
    timestamp: str
    recipient_id: str
    conversation_id: Optional[str] = None
    pricing_model: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════════
# MESSAGE TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════
class MessageTemplates:
    """
    Шаблоны сообщений для туристического бизнеса.

    Шаблоны должны быть предварительно созданы и одобрены в Meta Business Suite.
    """

    # Название шаблона -> структура
    TEMPLATES = {
        "booking_confirmation": {
            "name": "booking_confirmation_ru",
            "language": "ru",
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {"type": "text", "text": "{{tour_name}}"}
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "{{client_name}}"},
                        {"type": "text", "text": "{{date}}"},
                        {"type": "text", "text": "{{time}}"},
                        {"type": "text", "text": "{{pickup_location}}"},
                        {"type": "text", "text": "{{booking_number}}"},
                    ]
                }
            ]
        },
        "tour_reminder": {
            "name": "tour_reminder_ru",
            "language": "ru",
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "{{client_name}}"},
                        {"type": "text", "text": "{{tour_name}}"},
                        {"type": "text", "text": "{{date}}"},
                        {"type": "text", "text": "{{time}}"},
                        {"type": "text", "text": "{{driver_phone}}"},
                    ]
                }
            ]
        },
        "review_request": {
            "name": "review_request_ru",
            "language": "ru",
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "{{client_name}}"},
                        {"type": "text", "text": "{{tour_name}}"},
                    ]
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [
                        {"type": "text", "text": "{{review_url}}"}
                    ]
                }
            ]
        },
        "promo_broadcast": {
            "name": "promo_offer_ru",
            "language": "ru",
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {"type": "image", "image": {"link": "{{image_url}}"}}
                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "{{offer_title}}"},
                        {"type": "text", "text": "{{discount}}"},
                        {"type": "text", "text": "{{valid_until}}"},
                    ]
                }
            ]
        },
        "payment_reminder": {
            "name": "payment_reminder_ru",
            "language": "ru",
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "{{client_name}}"},
                        {"type": "text", "text": "{{amount}}"},
                        {"type": "text", "text": "{{booking_number}}"},
                        {"type": "text", "text": "{{due_date}}"},
                    ]
                }
            ]
        },
    }

    @classmethod
    def get_template(cls, template_name: str) -> Optional[Dict]:
        """Получить шаблон по имени."""
        return cls.TEMPLATES.get(template_name)

    @classmethod
    def build_template_message(
        cls,
        template_name: str,
        parameters: Dict[str, str]
    ) -> Optional[Dict]:
        """
        Построить сообщение из шаблона.

        Args:
            template_name: Имя шаблона
            parameters: Параметры для подстановки (ключ -> значение)

        Returns:
            Структура сообщения для API или None
        """
        template = cls.get_template(template_name)
        if not template:
            logger.error(f"Шаблон '{template_name}' не найден")
            return None

        # Копируем шаблон
        import copy
        message = copy.deepcopy(template)

        # Подставляем параметры
        for component in message.get("components", []):
            for param in component.get("parameters", []):
                if param["type"] == "text":
                    # Ищем placeholder в тексте
                    text = param.get("text", "")
                    for key, value in parameters.items():
                        placeholder = "{{" + key + "}}"
                        if placeholder in text:
                            param["text"] = text.replace(placeholder, str(value))
                elif param["type"] == "image":
                    if "image_url" in parameters:
                        param["image"]["link"] = parameters["image_url"]

        return message

    @classmethod
    def list_templates(cls) -> List[str]:
        """Список доступных шаблонов."""
        return list(cls.TEMPLATES.keys())


# ═══════════════════════════════════════════════════════════════════════════════
# WHATSAPP API CLIENT
# ═══════════════════════════════════════════════════════════════════════════════
class WhatsAppAPI:
    """
    Клиент WhatsApp Business Cloud API.

    Пример использования:
        api = WhatsAppAPI()
        result = api.send_text("971501234567", "Привет!")
        if result.success:
            print(f"Отправлено: {result.message_id}")
    """

    def __init__(self, cfg: Optional[WhatsAppConfig] = None):
        self.config = cfg or config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        })

        # Rate limiting
        self._last_request_time = 0
        self._request_interval = 1.0 / self.config.messages_per_second
        self._lock = threading.Lock()

        # Statistics
        self.stats = {
            "sent": 0,
            "delivered": 0,
            "read": 0,
            "failed": 0,
        }

    def _rate_limit(self):
        """Соблюдение rate limit."""
        with self._lock:
            now = time.time()
            elapsed = now - self._last_request_time
            if elapsed < self._request_interval:
                time.sleep(self._request_interval - elapsed)
            self._last_request_time = time.time()

    def _make_request(
        self,
        method: str,
        url: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        retry: int = 0
    ) -> Dict:
        """
        Выполнить HTTP запрос с retry логикой.
        """
        self._rate_limit()

        try:
            if method == "POST":
                if files:
                    # Для загрузки файлов убираем Content-Type
                    headers = {"Authorization": f"Bearer {self.config.access_token}"}
                    response = self.session.post(url, data=data, files=files, headers=headers)
                else:
                    response = self.session.post(url, json=data)
            elif method == "GET":
                response = self.session.get(url, params=data)
            else:
                raise ValueError(f"Неподдерживаемый метод: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if retry < self.config.max_retries:
                logger.warning(f"Retry {retry + 1}/{self.config.max_retries}: {e}")
                time.sleep(self.config.retry_delay * (retry + 1))
                return self._make_request(method, url, data, files, retry + 1)

            logger.error(f"Ошибка запроса: {e}")
            raise

    def _format_phone(self, phone: str) -> str:
        """
        Форматировать номер телефона.

        Убирает +, пробелы, дефисы. Оставляет только цифры.
        """
        return ''.join(filter(str.isdigit, phone))

    # ─────────────────────────────────────────────────────────────────────────
    # TEXT MESSAGES
    # ─────────────────────────────────────────────────────────────────────────
    def send_text(
        self,
        to: str,
        text: str,
        preview_url: bool = False,
        reply_to: Optional[str] = None
    ) -> MessageResult:
        """
        Отправить текстовое сообщение.

        Args:
            to: Номер телефона получателя (с кодом страны)
            text: Текст сообщения
            preview_url: Показывать preview для ссылок
            reply_to: ID сообщения для ответа

        Returns:
            MessageResult
        """
        phone = self._format_phone(to)

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": text
            }
        }

        if reply_to:
            payload["context"] = {"message_id": reply_to}

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1

            logger.info(f"Текст отправлен -> {phone}: {text[:50]}...")
            return MessageResult(success=True, message_id=message_id, phone=phone)

        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # TEMPLATE MESSAGES
    # ─────────────────────────────────────────────────────────────────────────
    def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "ru",
        components: Optional[List[Dict]] = None,
        parameters: Optional[Dict[str, str]] = None
    ) -> MessageResult:
        """
        Отправить шаблонное сообщение.

        Args:
            to: Номер телефона
            template_name: Имя шаблона (одобренного в Meta)
            language_code: Код языка (ru, en, ar)
            components: Компоненты шаблона (header, body, button параметры)
            parameters: Простой словарь параметров для автоподстановки

        Returns:
            MessageResult
        """
        phone = self._format_phone(to)

        # Если переданы простые параметры, строим components автоматически
        if parameters and not components:
            template_def = MessageTemplates.get_template(template_name)
            if template_def:
                built = MessageTemplates.build_template_message(template_name, parameters)
                if built:
                    template_name = built["name"]
                    language_code = built.get("language", language_code)
                    components = built.get("components", [])

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }

        if components:
            payload["template"]["components"] = components

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1

            logger.info(f"Шаблон '{template_name}' отправлен -> {phone}")
            return MessageResult(success=True, message_id=message_id, phone=phone)

        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # MEDIA MESSAGES
    # ─────────────────────────────────────────────────────────────────────────
    def upload_media(
        self,
        file_path: str,
        mime_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Загрузить медиа файл и получить media_id.

        Args:
            file_path: Путь к файлу
            mime_type: MIME тип (определяется автоматически если не указан)

        Returns:
            media_id или None
        """
        import mimetypes

        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return None

        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)

        with open(file_path, "rb") as f:
            files = {
                "file": (os.path.basename(file_path), f, mime_type)
            }
            data = {
                "messaging_product": "whatsapp"
            }

            try:
                response = self._make_request(
                    "POST",
                    self.config.media_url,
                    data=data,
                    files=files
                )
                media_id = response.get("id")
                logger.info(f"Медиа загружено: {media_id}")
                return media_id

            except Exception as e:
                logger.error(f"Ошибка загрузки медиа: {e}")
                return None

    def send_image(
        self,
        to: str,
        image: str,
        caption: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> MessageResult:
        """
        Отправить изображение.

        Args:
            to: Номер телефона
            image: URL изображения или media_id
            caption: Подпись
            reply_to: ID сообщения для ответа

        Returns:
            MessageResult
        """
        phone = self._format_phone(to)

        # Определяем, это URL или media_id
        image_obj = {}
        if image.startswith("http"):
            image_obj["link"] = image
        else:
            image_obj["id"] = image

        if caption:
            image_obj["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "image",
            "image": image_obj
        }

        if reply_to:
            payload["context"] = {"message_id": reply_to}

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1

            logger.info(f"Изображение отправлено -> {phone}")
            return MessageResult(success=True, message_id=message_id, phone=phone)

        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    def send_document(
        self,
        to: str,
        document: str,
        filename: Optional[str] = None,
        caption: Optional[str] = None
    ) -> MessageResult:
        """
        Отправить документ (PDF, DOCX и т.д.).

        Args:
            to: Номер телефона
            document: URL документа или media_id
            filename: Имя файла для отображения
            caption: Подпись

        Returns:
            MessageResult
        """
        phone = self._format_phone(to)

        doc_obj = {}
        if document.startswith("http"):
            doc_obj["link"] = document
        else:
            doc_obj["id"] = document

        if filename:
            doc_obj["filename"] = filename
        if caption:
            doc_obj["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "document",
            "document": doc_obj
        }

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1

            logger.info(f"Документ отправлен -> {phone}")
            return MessageResult(success=True, message_id=message_id, phone=phone)

        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    def send_video(
        self,
        to: str,
        video: str,
        caption: Optional[str] = None
    ) -> MessageResult:
        """Отправить видео."""
        phone = self._format_phone(to)

        video_obj = {}
        if video.startswith("http"):
            video_obj["link"] = video
        else:
            video_obj["id"] = video

        if caption:
            video_obj["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "video",
            "video": video_obj
        }

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1
            return MessageResult(success=True, message_id=message_id, phone=phone)
        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    def send_audio(self, to: str, audio: str) -> MessageResult:
        """Отправить аудио."""
        phone = self._format_phone(to)

        audio_obj = {"link": audio} if audio.startswith("http") else {"id": audio}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "audio",
            "audio": audio_obj
        }

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1
            return MessageResult(success=True, message_id=message_id, phone=phone)
        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # INTERACTIVE MESSAGES
    # ─────────────────────────────────────────────────────────────────────────
    def send_buttons(
        self,
        to: str,
        body_text: str,
        buttons: List[Dict[str, str]],
        header: Optional[str] = None,
        footer: Optional[str] = None
    ) -> MessageResult:
        """
        Отправить сообщение с кнопками (до 3 кнопок).

        Args:
            to: Номер телефона
            body_text: Основной текст
            buttons: Список кнопок [{"id": "btn_1", "title": "Да"}, ...]
            header: Заголовок (опционально)
            footer: Футер (опционально)

        Returns:
            MessageResult
        """
        phone = self._format_phone(to)

        if len(buttons) > 3:
            logger.warning("Максимум 3 кнопки, остальные будут обрезаны")
            buttons = buttons[:3]

        action = {
            "buttons": [
                {
                    "type": "reply",
                    "reply": {
                        "id": btn.get("id", f"btn_{i}"),
                        "title": btn["title"][:20]  # Max 20 chars
                    }
                }
                for i, btn in enumerate(buttons)
            ]
        }

        interactive = {
            "type": "button",
            "body": {"text": body_text},
            "action": action
        }

        if header:
            interactive["header"] = {"type": "text", "text": header}
        if footer:
            interactive["footer"] = {"text": footer}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "interactive",
            "interactive": interactive
        }

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1

            logger.info(f"Кнопки отправлены -> {phone}")
            return MessageResult(success=True, message_id=message_id, phone=phone)

        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    def send_list(
        self,
        to: str,
        body_text: str,
        button_text: str,
        sections: List[Dict],
        header: Optional[str] = None,
        footer: Optional[str] = None
    ) -> MessageResult:
        """
        Отправить сообщение со списком (list message).

        Args:
            to: Номер телефона
            body_text: Основной текст
            button_text: Текст кнопки открытия списка
            sections: Секции списка
                [
                    {
                        "title": "Экскурсии",
                        "rows": [
                            {"id": "tour_1", "title": "Дубай", "description": "Обзорная"},
                            {"id": "tour_2", "title": "Абу-Даби", "description": "Полный день"}
                        ]
                    }
                ]
            header: Заголовок
            footer: Футер

        Returns:
            MessageResult
        """
        phone = self._format_phone(to)

        interactive = {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_text[:20],
                "sections": sections
            }
        }

        if header:
            interactive["header"] = {"type": "text", "text": header}
        if footer:
            interactive["footer"] = {"text": footer}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "interactive",
            "interactive": interactive
        }

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1

            logger.info(f"Список отправлен -> {phone}")
            return MessageResult(success=True, message_id=message_id, phone=phone)

        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # REACTIONS
    # ─────────────────────────────────────────────────────────────────────────
    def send_reaction(
        self,
        to: str,
        message_id: str,
        emoji: str
    ) -> MessageResult:
        """
        Отправить реакцию на сообщение.

        Args:
            to: Номер телефона
            message_id: ID сообщения для реакции
            emoji: Эмодзи реакции

        Returns:
            MessageResult
        """
        phone = self._format_phone(to)

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": emoji
            }
        }

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            msg_id = response.get("messages", [{}])[0].get("id")
            return MessageResult(success=True, message_id=msg_id, phone=phone)
        except Exception as e:
            return MessageResult(success=False, phone=phone, error=str(e))

    def remove_reaction(self, to: str, message_id: str) -> MessageResult:
        """Удалить реакцию (отправить пустой emoji)."""
        return self.send_reaction(to, message_id, "")

    # ─────────────────────────────────────────────────────────────────────────
    # LOCATION & CONTACTS
    # ─────────────────────────────────────────────────────────────────────────
    def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None
    ) -> MessageResult:
        """Отправить локацию."""
        phone = self._format_phone(to)

        location = {
            "latitude": latitude,
            "longitude": longitude
        }
        if name:
            location["name"] = name
        if address:
            location["address"] = address

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "location",
            "location": location
        }

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1
            return MessageResult(success=True, message_id=message_id, phone=phone)
        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    def send_contacts(
        self,
        to: str,
        contacts: List[Dict]
    ) -> MessageResult:
        """
        Отправить контакты.

        Args:
            contacts: Список контактов
                [
                    {
                        "name": {"formatted_name": "Иван Иванов", "first_name": "Иван"},
                        "phones": [{"phone": "+971501234567", "type": "WORK"}]
                    }
                ]
        """
        phone = self._format_phone(to)

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "contacts",
            "contacts": contacts
        }

        try:
            response = self._make_request("POST", self.config.messages_url, payload)
            message_id = response.get("messages", [{}])[0].get("id")
            self.stats["sent"] += 1
            return MessageResult(success=True, message_id=message_id, phone=phone)
        except Exception as e:
            self.stats["failed"] += 1
            return MessageResult(success=False, phone=phone, error=str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # READ RECEIPTS
    # ─────────────────────────────────────────────────────────────────────────
    def mark_as_read(self, message_id: str) -> bool:
        """
        Отметить сообщение как прочитанное.

        Args:
            message_id: ID входящего сообщения

        Returns:
            True если успешно
        """
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        try:
            self._make_request("POST", self.config.messages_url, payload)
            return True
        except Exception as e:
            logger.error(f"Ошибка mark_as_read: {e}")
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # BUSINESS PROFILE
    # ─────────────────────────────────────────────────────────────────────────
    def get_business_profile(self) -> Optional[Dict]:
        """Получить бизнес профиль."""
        url = f"{self.config.base_url}/{self.config.api_version}/{self.config.phone_number_id}/whatsapp_business_profile"
        params = {"fields": "about,address,description,email,profile_picture_url,websites,vertical"}

        try:
            response = self._make_request("GET", url, params)
            return response.get("data", [{}])[0]
        except Exception as e:
            logger.error(f"Ошибка получения профиля: {e}")
            return None

    def get_phone_number_info(self) -> Optional[Dict]:
        """Получить информацию о номере телефона."""
        url = f"{self.config.base_url}/{self.config.api_version}/{self.config.phone_number_id}"
        params = {"fields": "verified_name,quality_rating,display_phone_number"}

        try:
            return self._make_request("GET", url, params)
        except Exception as e:
            logger.error(f"Ошибка получения информации о номере: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════════════
# WEBHOOK HANDLER
# ═══════════════════════════════════════════════════════════════════════════════
class WebhookHandler:
    """
    Обработчик Webhook от WhatsApp.

    Обрабатывает:
    - Входящие сообщения
    - Статусы доставки
    - Реакции
    """

    def __init__(self, verify_token: Optional[str] = None):
        self.verify_token = verify_token or config.verify_token

        # Callbacks
        self._message_handlers: List[Callable] = []
        self._status_handlers: List[Callable] = []
        self._reaction_handlers: List[Callable] = []
        self._error_handlers: List[Callable] = []

    def on_message(self, handler: Callable[[IncomingMessage], None]):
        """Декоратор для обработчика входящих сообщений."""
        self._message_handlers.append(handler)
        return handler

    def on_status(self, handler: Callable[[StatusUpdate], None]):
        """Декоратор для обработчика статусов."""
        self._status_handlers.append(handler)
        return handler

    def on_reaction(self, handler: Callable[[Dict], None]):
        """Декоратор для обработчика реакций."""
        self._reaction_handlers.append(handler)
        return handler

    def on_error(self, handler: Callable[[Exception], None]):
        """Декоратор для обработчика ошибок."""
        self._error_handlers.append(handler)
        return handler

    def verify(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Верификация webhook (GET запрос от Meta).

        Returns:
            challenge если верификация успешна, иначе None
        """
        if mode == "subscribe" and token == self.verify_token:
            logger.info("Webhook верифицирован")
            return challenge
        logger.warning(f"Неудачная верификация: mode={mode}")
        return None

    def process(self, payload: Dict) -> bool:
        """
        Обработать webhook payload.

        Args:
            payload: JSON payload от Meta

        Returns:
            True если обработано успешно
        """
        try:
            if payload.get("object") != "whatsapp_business_account":
                return False

            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})

                    # Обработка сообщений
                    for message in value.get("messages", []):
                        self._handle_message(message, value)

                    # Обработка статусов
                    for status in value.get("statuses", []):
                        self._handle_status(status)

            return True

        except Exception as e:
            logger.error(f"Ошибка обработки webhook: {e}")
            for handler in self._error_handlers:
                handler(e)
            return False

    def _handle_message(self, message: Dict, value: Dict):
        """Обработать входящее сообщение."""
        msg_type = message.get("type", "text")

        incoming = IncomingMessage(
            message_id=message.get("id"),
            from_phone=message.get("from"),
            timestamp=message.get("timestamp"),
            message_type=msg_type
        )

        # Извлечение контента в зависимости от типа
        if msg_type == "text":
            incoming.text = message.get("text", {}).get("body")

        elif msg_type in ("image", "document", "video", "audio", "sticker"):
            media = message.get(msg_type, {})
            incoming.media_id = media.get("id")
            incoming.caption = media.get("caption")

        elif msg_type == "location":
            incoming.location = message.get("location")

        elif msg_type == "contacts":
            incoming.contacts = message.get("contacts")

        elif msg_type == "reaction":
            reaction = message.get("reaction", {})
            incoming.reaction = reaction
            # Вызов отдельных обработчиков реакций
            for handler in self._reaction_handlers:
                handler(reaction)

        elif msg_type == "interactive":
            interactive = message.get("interactive", {})
            interactive_type = interactive.get("type")
            if interactive_type == "button_reply":
                incoming.text = interactive.get("button_reply", {}).get("id")
            elif interactive_type == "list_reply":
                incoming.text = interactive.get("list_reply", {}).get("id")

        # Контекст ответа
        if "context" in message:
            incoming.context = message["context"]

        # Вызов обработчиков
        for handler in self._message_handlers:
            try:
                handler(incoming)
            except Exception as e:
                logger.error(f"Ошибка в обработчике сообщений: {e}")

    def _handle_status(self, status: Dict):
        """Обработать обновление статуса."""
        update = StatusUpdate(
            message_id=status.get("id"),
            status=status.get("status"),
            timestamp=status.get("timestamp"),
            recipient_id=status.get("recipient_id"),
            conversation_id=status.get("conversation", {}).get("id"),
            pricing_model=status.get("pricing", {}).get("pricing_model")
        )

        for handler in self._status_handlers:
            try:
                handler(update)
            except Exception as e:
                logger.error(f"Ошибка в обработчике статусов: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MESSAGE QUEUE
# ═══════════════════════════════════════════════════════════════════════════════
class MessageQueue:
    """
    Очередь сообщений для отложенной отправки.

    Поддерживает:
    - Файловое хранилище (JSON)
    - Redis (опционально)
    """

    def __init__(self, cfg: Optional[WhatsAppConfig] = None):
        self.config = cfg or config
        self._file_queue = Path(ANALYTICS_DIR) / self.config.queue_file
        self._redis_client = None
        self._lock = threading.Lock()

        if self.config.use_redis and REDIS_AVAILABLE:
            try:
                self._redis_client = redis.from_url(self.config.redis_url)
                self._redis_client.ping()
                logger.info("Redis подключен для очереди")
            except Exception as e:
                logger.warning(f"Redis недоступен, используется файл: {e}")
                self._redis_client = None

    def add(
        self,
        to: str,
        message_type: str,
        content: Dict,
        scheduled_at: Optional[datetime] = None,
        priority: int = 0,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Добавить сообщение в очередь.

        Args:
            to: Номер телефона
            message_type: Тип сообщения (text, template, image...)
            content: Содержимое сообщения
            scheduled_at: Время отправки (None = немедленно)
            priority: Приоритет (выше = раньше)
            tags: Теги для группировки

        Returns:
            ID задачи в очереди
        """
        task_id = hashlib.md5(
            f"{to}{message_type}{time.time()}{random.random()}".encode()
        ).hexdigest()[:12]

        task = {
            "id": task_id,
            "to": to,
            "type": message_type,
            "content": content,
            "scheduled_at": scheduled_at.isoformat() if scheduled_at else None,
            "priority": priority,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "attempts": 0,
            "last_error": None
        }

        if self._redis_client:
            self._redis_client.lpush("whatsapp_queue", json.dumps(task))
        else:
            with self._lock:
                queue_data = self._load_file_queue()
                queue_data.append(task)
                self._save_file_queue(queue_data)

        logger.info(f"Добавлено в очередь: {task_id} -> {to}")
        return task_id

    def get_pending(self, limit: int = 100) -> List[Dict]:
        """Получить pending задачи."""
        now = datetime.now()

        if self._redis_client:
            tasks = []
            raw_tasks = self._redis_client.lrange("whatsapp_queue", 0, limit - 1)
            for raw in raw_tasks:
                task = json.loads(raw)
                if task["status"] == "pending":
                    scheduled = task.get("scheduled_at")
                    if not scheduled or datetime.fromisoformat(scheduled) <= now:
                        tasks.append(task)
            return sorted(tasks, key=lambda x: -x.get("priority", 0))
        else:
            with self._lock:
                queue_data = self._load_file_queue()
                pending = [
                    t for t in queue_data
                    if t["status"] == "pending" and (
                        not t.get("scheduled_at") or
                        datetime.fromisoformat(t["scheduled_at"]) <= now
                    )
                ]
                return sorted(pending, key=lambda x: -x.get("priority", 0))[:limit]

    def update_status(self, task_id: str, status: str, error: Optional[str] = None):
        """Обновить статус задачи."""
        if self._redis_client:
            # Для Redis нужна более сложная логика
            pass
        else:
            with self._lock:
                queue_data = self._load_file_queue()
                for task in queue_data:
                    if task["id"] == task_id:
                        task["status"] = status
                        task["attempts"] += 1
                        if error:
                            task["last_error"] = error
                        task["updated_at"] = datetime.now().isoformat()
                        break
                self._save_file_queue(queue_data)

    def remove_completed(self, older_than_days: int = 7):
        """Удалить завершённые задачи старше N дней."""
        cutoff = datetime.now() - timedelta(days=older_than_days)

        with self._lock:
            queue_data = self._load_file_queue()
            queue_data = [
                t for t in queue_data
                if t["status"] == "pending" or
                datetime.fromisoformat(t.get("updated_at", t["created_at"])) > cutoff
            ]
            self._save_file_queue(queue_data)

    def _load_file_queue(self) -> List[Dict]:
        """Загрузить очередь из файла."""
        if self._file_queue.exists():
            try:
                return json.loads(self._file_queue.read_text(encoding="utf-8"))
            except:
                return []
        return []

    def _save_file_queue(self, data: List[Dict]):
        """Сохранить очередь в файл."""
        self._file_queue.parent.mkdir(parents=True, exist_ok=True)
        self._file_queue.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# BULK OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════
class BulkSender:
    """
    Массовая рассылка с поддержкой:
    - Rate limiting
    - Персонализации
    - A/B тестирования
    - Прогресс-отчётов
    """

    def __init__(self, api: Optional[WhatsAppAPI] = None):
        self.api = api or WhatsAppAPI()
        self._stop_flag = False
        self._progress_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable[[int, int, Dict], None]):
        """
        Установить callback для отслеживания прогресса.

        Args:
            callback: функция(sent, total, last_result)
        """
        self._progress_callback = callback

    def stop(self):
        """Остановить текущую рассылку."""
        self._stop_flag = True

    def send_text_bulk(
        self,
        recipients: List[Dict[str, str]],
        message_template: str,
        delay_between: float = 1.0
    ) -> Dict:
        """
        Массовая отправка текстовых сообщений.

        Args:
            recipients: Список получателей [{"phone": "...", "name": "...", ...}, ...]
            message_template: Шаблон сообщения с плейсхолдерами {name}, {phone} и т.д.
            delay_between: Задержка между сообщениями (секунды)

        Returns:
            Статистика: {"sent": N, "failed": N, "results": [...]}
        """
        self._stop_flag = False
        results = []
        sent = 0
        failed = 0
        total = len(recipients)

        for i, recipient in enumerate(recipients):
            if self._stop_flag:
                logger.info("Рассылка остановлена")
                break

            # Персонализация
            message = message_template
            for key, value in recipient.items():
                message = message.replace(f"{{{key}}}", str(value))

            # Отправка
            result = self.api.send_text(recipient["phone"], message)
            results.append(result.to_dict())

            if result.success:
                sent += 1
            else:
                failed += 1

            # Callback
            if self._progress_callback:
                self._progress_callback(i + 1, total, result.to_dict())

            # Задержка
            if i < total - 1:
                time.sleep(delay_between)

        return {
            "sent": sent,
            "failed": failed,
            "total": total,
            "results": results
        }

    def send_template_bulk(
        self,
        recipients: List[Dict],
        template_name: str,
        language_code: str = "ru",
        delay_between: float = 1.0
    ) -> Dict:
        """
        Массовая отправка шаблонных сообщений.

        Args:
            recipients: Список с phone и параметрами шаблона
            template_name: Имя шаблона
            language_code: Код языка
            delay_between: Задержка

        Returns:
            Статистика
        """
        self._stop_flag = False
        results = []
        sent = 0
        failed = 0
        total = len(recipients)

        for i, recipient in enumerate(recipients):
            if self._stop_flag:
                break

            phone = recipient.pop("phone")
            result = self.api.send_template(
                to=phone,
                template_name=template_name,
                language_code=language_code,
                parameters=recipient
            )
            results.append(result.to_dict())

            if result.success:
                sent += 1
            else:
                failed += 1

            if self._progress_callback:
                self._progress_callback(i + 1, total, result.to_dict())

            if i < total - 1:
                time.sleep(delay_between)

        return {"sent": sent, "failed": failed, "total": total, "results": results}

    def ab_test(
        self,
        recipients: List[Dict],
        variants: List[Dict],
        metric_callback: Optional[Callable] = None
    ) -> Dict:
        """
        A/B тестирование сообщений.

        Args:
            recipients: Список получателей
            variants: Варианты сообщений
                [
                    {"name": "A", "type": "text", "content": "..."},
                    {"name": "B", "type": "text", "content": "..."}
                ]
            metric_callback: Функция для сбора метрик

        Returns:
            Результаты по вариантам
        """
        if not variants:
            raise ValueError("Нужен хотя бы один вариант")

        # Распределяем получателей по вариантам
        variant_count = len(variants)
        variant_results = {v["name"]: {"sent": 0, "failed": 0, "recipients": []} for v in variants}

        for i, recipient in enumerate(recipients):
            variant = variants[i % variant_count]
            variant_name = variant["name"]

            # Отправка в зависимости от типа
            if variant["type"] == "text":
                content = variant["content"]
                for key, value in recipient.items():
                    content = content.replace(f"{{{key}}}", str(value))
                result = self.api.send_text(recipient["phone"], content)

            elif variant["type"] == "template":
                result = self.api.send_template(
                    to=recipient["phone"],
                    template_name=variant["template_name"],
                    parameters=recipient
                )
            else:
                continue

            if result.success:
                variant_results[variant_name]["sent"] += 1
            else:
                variant_results[variant_name]["failed"] += 1

            variant_results[variant_name]["recipients"].append(recipient["phone"])

            time.sleep(self.api.config.bulk_delay_seconds)

        return variant_results


# ═══════════════════════════════════════════════════════════════════════════════
# BITRIX24 INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════
class Bitrix24Sync:
    """
    Синхронизация с Bitrix24 CRM.

    Функции:
    - Логирование сообщений в timeline контакта/сделки
    - Создание задач на основе сообщений
    - Обновление статусов
    """

    def __init__(self, bitrix_config: Optional[Dict] = None):
        self.config = bitrix_config or BITRIX24_CONFIG
        self._base_url = self._build_base_url()

    def _build_base_url(self) -> str:
        """Построить базовый URL для API."""
        domain = self.config.get("domain", "")
        user_id = self.config.get("user_id", "")
        webhook_key = self.config.get("webhook_key", "")

        if not all([domain, user_id, webhook_key]):
            return ""

        return f"https://{domain}.bitrix24.ru/rest/{user_id}/{webhook_key}"

    def is_configured(self) -> bool:
        """Проверить, настроен ли Bitrix24."""
        return bool(self._base_url)

    def log_message(
        self,
        phone: str,
        direction: str,  # "incoming" или "outgoing"
        message_text: str,
        message_type: str = "text",
        entity_type: str = "CONTACT",  # CONTACT, DEAL, LEAD
        entity_id: Optional[int] = None
    ) -> bool:
        """
        Залогировать сообщение в timeline Bitrix24.

        Args:
            phone: Номер телефона
            direction: Направление сообщения
            message_text: Текст сообщения
            message_type: Тип (text, image, document...)
            entity_type: Тип сущности (CONTACT, DEAL, LEAD)
            entity_id: ID сущности (если известен)

        Returns:
            True если успешно
        """
        if not self.is_configured():
            logger.warning("Bitrix24 не настроен")
            return False

        # Если entity_id не указан, ищем контакт по телефону
        if not entity_id and entity_type == "CONTACT":
            entity_id = self._find_contact_by_phone(phone)

        if not entity_id:
            logger.warning(f"Контакт не найден: {phone}")
            return False

        # Добавляем запись в timeline
        comment = f"[WhatsApp] {'<-' if direction == 'incoming' else '->'} {message_type}\n{message_text}"

        url = f"{self._base_url}/crm.timeline.comment.add.json"
        data = {
            "fields": {
                "ENTITY_ID": entity_id,
                "ENTITY_TYPE": entity_type,
                "COMMENT": comment
            }
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Ошибка логирования в Bitrix24: {e}")
            return False

    def _find_contact_by_phone(self, phone: str) -> Optional[int]:
        """Найти контакт по номеру телефона."""
        if not self.is_configured():
            return None

        # Форматируем номер
        phone_clean = ''.join(filter(str.isdigit, phone))

        url = f"{self._base_url}/crm.contact.list.json"
        data = {
            "filter": {"PHONE": phone_clean},
            "select": ["ID", "NAME", "LAST_NAME"]
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json().get("result", [])
            if result:
                return result[0].get("ID")
        except Exception as e:
            logger.error(f"Ошибка поиска контакта: {e}")

        return None

    def create_task_from_message(
        self,
        phone: str,
        message_text: str,
        responsible_id: int,
        deadline_hours: int = 24
    ) -> Optional[int]:
        """
        Создать задачу на основе входящего сообщения.

        Returns:
            ID задачи или None
        """
        if not self.is_configured():
            return None

        deadline = datetime.now() + timedelta(hours=deadline_hours)

        url = f"{self._base_url}/tasks.task.add.json"
        data = {
            "fields": {
                "TITLE": f"WhatsApp: {phone}",
                "DESCRIPTION": message_text,
                "RESPONSIBLE_ID": responsible_id,
                "DEADLINE": deadline.strftime("%Y-%m-%d %H:%M:%S"),
                "PRIORITY": 1
            }
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json().get("result", {}).get("task", {}).get("id")
        except Exception as e:
            logger.error(f"Ошибка создания задачи: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE LOGGER
# ═══════════════════════════════════════════════════════════════════════════════
class MessageLogger:
    """
    Логирование сообщений в JSON файл (SQLite опционально).
    """

    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file or (ANALYTICS_DIR / "whatsapp_messages.json")
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        """Создать файл если не существует."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            self.log_file.write_text("[]", encoding="utf-8")

    def log_outgoing(self, result: MessageResult, message_type: str, content: str):
        """Логировать исходящее сообщение."""
        record = {
            "direction": "outgoing",
            "message_id": result.message_id,
            "phone": result.phone,
            "type": message_type,
            "content": content[:500],  # Ограничиваем длину
            "success": result.success,
            "error": result.error,
            "timestamp": datetime.now().isoformat()
        }
        self._append(record)

    def log_incoming(self, message: IncomingMessage):
        """Логировать входящее сообщение."""
        record = {
            "direction": "incoming",
            "message_id": message.message_id,
            "phone": message.from_phone,
            "type": message.message_type,
            "content": message.text or message.caption or "",
            "media_id": message.media_id,
            "timestamp": datetime.now().isoformat()
        }
        self._append(record)

    def log_status(self, status: StatusUpdate):
        """Логировать обновление статуса."""
        record = {
            "type": "status_update",
            "message_id": status.message_id,
            "status": status.status,
            "recipient_id": status.recipient_id,
            "timestamp": datetime.now().isoformat()
        }
        self._append(record)

    def _append(self, record: Dict):
        """Добавить запись в лог."""
        with self._lock:
            try:
                data = json.loads(self.log_file.read_text(encoding="utf-8"))
                data.append(record)
                # Ограничиваем размер (последние 10000 записей)
                if len(data) > 10000:
                    data = data[-10000:]
                self.log_file.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
            except Exception as e:
                logger.error(f"Ошибка логирования: {e}")

    def get_history(
        self,
        phone: Optional[str] = None,
        direction: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Получить историю сообщений.

        Args:
            phone: Фильтр по номеру
            direction: Фильтр по направлению (incoming/outgoing)
            limit: Максимум записей

        Returns:
            Список записей
        """
        try:
            data = json.loads(self.log_file.read_text(encoding="utf-8"))

            if phone:
                phone_clean = ''.join(filter(str.isdigit, phone))
                data = [r for r in data if phone_clean in r.get("phone", "")]

            if direction:
                data = [r for r in data if r.get("direction") == direction]

            return data[-limit:]
        except:
            return []


# ═══════════════════════════════════════════════════════════════════════════════
# FLASK WEBHOOK SERVER
# ═══════════════════════════════════════════════════════════════════════════════
def create_flask_app(webhook_handler: WebhookHandler) -> "Flask":
    """
    Создать Flask приложение для webhook.

    Usage:
        handler = WebhookHandler()

        @handler.on_message
        def handle_message(msg):
            print(f"Получено: {msg.text}")

        app = create_flask_app(handler)
        app.run(port=5000)
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask не установлен: pip install flask")

    app = Flask(__name__)

    @app.route("/webhook", methods=["GET"])
    def verify():
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        result = webhook_handler.verify(mode, token, challenge)
        if result:
            return result, 200
        return "Verification failed", 403

    @app.route("/webhook", methods=["POST"])
    def webhook():
        payload = request.get_json()
        webhook_handler.process(payload)
        return "OK", 200

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI WEBHOOK SERVER
# ═══════════════════════════════════════════════════════════════════════════════
def create_fastapi_app(webhook_handler: WebhookHandler) -> "FastAPI":
    """
    Создать FastAPI приложение для webhook.

    Usage:
        handler = WebhookHandler()
        app = create_fastapi_app(handler)
        uvicorn.run(app, host="0.0.0.0", port=5000)
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI не установлен: pip install fastapi uvicorn")

    app = FastAPI(title="WhatsApp Webhook")

    @app.get("/webhook")
    async def verify(
        hub_mode: str = None,
        hub_verify_token: str = None,
        hub_challenge: str = None
    ):
        # FastAPI конвертирует hub.mode в hub_mode
        result = webhook_handler.verify(hub_mode, hub_verify_token, hub_challenge)
        if result:
            return PlainTextResponse(result)
        raise HTTPException(status_code=403, detail="Verification failed")

    @app.post("/webhook")
    async def webhook(request: Request):
        payload = await request.json()
        webhook_handler.process(payload)
        return JSONResponse({"status": "ok"})

    @app.get("/health")
    async def health():
        return {"status": "ok", "timestamp": datetime.now().isoformat()}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# QUEUE PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════════
class QueueProcessor:
    """
    Обработчик очереди сообщений.

    Запускается как отдельный поток/процесс для обработки
    отложенных и запланированных сообщений.
    """

    def __init__(
        self,
        api: Optional[WhatsAppAPI] = None,
        queue: Optional[MessageQueue] = None,
        logger: Optional[MessageLogger] = None
    ):
        self.api = api or WhatsAppAPI()
        self.queue = queue or MessageQueue()
        self.logger = logger or MessageLogger()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self, interval: float = 5.0):
        """
        Запустить обработчик.

        Args:
            interval: Интервал проверки очереди (секунды)
        """
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._process_loop,
            args=(interval,),
            daemon=True
        )
        self._thread.start()
        logger.info("Queue processor запущен")

    def stop(self):
        """Остановить обработчик."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("Queue processor остановлен")

    def _process_loop(self, interval: float):
        """Основной цикл обработки."""
        while self._running:
            try:
                tasks = self.queue.get_pending(limit=10)

                for task in tasks:
                    if not self._running:
                        break

                    self._process_task(task)
                    time.sleep(self.api.config.bulk_delay_seconds)

            except Exception as e:
                logger.error(f"Ошибка в queue processor: {e}")

            time.sleep(interval)

    def _process_task(self, task: Dict):
        """Обработать одну задачу."""
        task_id = task["id"]
        msg_type = task["type"]
        content = task["content"]
        to = task["to"]

        try:
            if msg_type == "text":
                result = self.api.send_text(to, content.get("text", ""))
            elif msg_type == "template":
                result = self.api.send_template(
                    to=to,
                    template_name=content.get("template_name"),
                    parameters=content.get("parameters", {})
                )
            elif msg_type == "image":
                result = self.api.send_image(
                    to=to,
                    image=content.get("image"),
                    caption=content.get("caption")
                )
            else:
                logger.warning(f"Неизвестный тип сообщения: {msg_type}")
                self.queue.update_status(task_id, "failed", f"Unknown type: {msg_type}")
                return

            if result.success:
                self.queue.update_status(task_id, "sent")
                self.logger.log_outgoing(result, msg_type, str(content))
            else:
                self.queue.update_status(task_id, "failed", result.error)

        except Exception as e:
            self.queue.update_status(task_id, "failed", str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def send_booking_confirmation(
    phone: str,
    client_name: str,
    tour_name: str,
    date: str,
    time: str,
    pickup_location: str,
    booking_number: str
) -> MessageResult:
    """
    Отправить подтверждение бронирования.

    Удобная функция для типичного use case.
    """
    api = WhatsAppAPI()
    return api.send_template(
        to=phone,
        template_name="booking_confirmation",
        parameters={
            "client_name": client_name,
            "tour_name": tour_name,
            "date": date,
            "time": time,
            "pickup_location": pickup_location,
            "booking_number": booking_number
        }
    )


def send_tour_reminder(
    phone: str,
    client_name: str,
    tour_name: str,
    date: str,
    time: str,
    driver_phone: str
) -> MessageResult:
    """Отправить напоминание о туре."""
    api = WhatsAppAPI()
    return api.send_template(
        to=phone,
        template_name="tour_reminder",
        parameters={
            "client_name": client_name,
            "tour_name": tour_name,
            "date": date,
            "time": time,
            "driver_phone": driver_phone
        }
    )


def send_review_request(
    phone: str,
    client_name: str,
    tour_name: str,
    review_url: str
) -> MessageResult:
    """Отправить запрос отзыва."""
    api = WhatsAppAPI()
    return api.send_template(
        to=phone,
        template_name="review_request",
        parameters={
            "client_name": client_name,
            "tour_name": tour_name,
            "review_url": review_url
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN / DEMO
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    """Демонстрация возможностей."""
    print("=" * 60)
    print("WhatsApp Business API Integration")
    print("=" * 60)

    # Проверка конфигурации
    cfg = WhatsAppConfig.from_env()
    if not cfg.validate():
        print("\n[!] Конфигурация не полная. Установите переменные окружения:")
        print("    WHATSAPP_PHONE_NUMBER_ID")
        print("    WHATSAPP_ACCESS_TOKEN")
        print("    WHATSAPP_VERIFY_TOKEN")
        print("    WHATSAPP_BUSINESS_ACCOUNT_ID")
        return

    print("\n[OK] Конфигурация загружена")
    print(f"    Phone Number ID: {cfg.phone_number_id[:10]}...")
    print(f"    API Version: {cfg.api_version}")

    # Инициализация
    api = WhatsAppAPI(cfg)

    # Получение информации о номере
    phone_info = api.get_phone_number_info()
    if phone_info:
        print(f"\n[INFO] Телефон: {phone_info.get('display_phone_number')}")
        print(f"       Качество: {phone_info.get('quality_rating')}")

    # Список доступных шаблонов
    print("\n[TEMPLATES] Доступные шаблоны:")
    for template in MessageTemplates.list_templates():
        print(f"    - {template}")

    # Демо webhook handler
    print("\n[WEBHOOK] Настройка обработчика...")
    handler = WebhookHandler(cfg.verify_token)

    @handler.on_message
    def on_message(msg: IncomingMessage):
        print(f"    <- Входящее от {msg.from_phone}: {msg.text}")

    @handler.on_status
    def on_status(status: StatusUpdate):
        print(f"    [STATUS] {status.message_id}: {status.status}")

    print("    Обработчик готов")

    # Демо очереди
    print("\n[QUEUE] Инициализация очереди...")
    msg_queue = MessageQueue()
    print(f"    Файл: {msg_queue._file_queue}")

    # Демо логгера
    print("\n[LOGGER] Инициализация логгера...")
    msg_logger = MessageLogger()
    print(f"    Файл: {msg_logger.log_file}")

    print("\n" + "=" * 60)
    print("Готово к использованию!")
    print("=" * 60)

    # Пример отправки (закомментировано)
    # result = api.send_text("+971501234567", "Тестовое сообщение")
    # print(f"Результат: {result}")


if __name__ == "__main__":
    main()
