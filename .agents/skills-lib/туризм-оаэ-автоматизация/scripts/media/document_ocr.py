#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR для распознавания документов из фото в чатах.

Типы документов:
- Паспорта (имя, номер, дата рождения, гражданство)
- Визы (тип, номер, даты действия)
- Чеки/квитанции (сумма, дата, назначение)
- Банковские переводы (сумма, отправитель, получатель)
- Билеты (рейс, дата, имя)

OCR движки:
- pytesseract (локальный, бесплатный)
- Google Vision API (точный, платный)
- Claude Vision API (умный, платный)
"""

import sys
import os
import re
import json
import base64
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

sys.stdout.reconfigure(encoding='utf-8')

# Импорт конфигурации
try:
    from config import (
        CHATS_DIR, MEDIA_DIR, JSON_DIR,
        API_KEYS, PATTERNS
    )
except ImportError:
    CHATS_DIR = Path("D:/Downloads/Chats")
    MEDIA_DIR = CHATS_DIR / "_медиа"
    JSON_DIR = CHATS_DIR / "_база" / "json"
    API_KEYS = {}
    PATTERNS = {}


# ═══════════════════════════════════════════════════════════════
# OCR КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════
TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"D:\Downloads\tesseract.exe")
GOOGLE_VISION_KEY = os.getenv("GOOGLE_VISION_KEY", API_KEYS.get("google_vision", ""))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", API_KEYS.get("anthropic", ""))

# Провайдер OCR: tesseract | google | claude
OCR_PROVIDER = os.getenv("OCR_PROVIDER", "tesseract")

# Настройки безопасности
MASK_SENSITIVE_DATA = True  # Маскирование в логах
ENCRYPT_OUTPUT = False       # Шифрование выходных файлов
ENCRYPTION_KEY = os.getenv("OCR_ENCRYPTION_KEY", "")


class DocumentType(Enum):
    """Типы документов."""
    PASSPORT = "passport"
    VISA = "visa"
    RECEIPT = "receipt"
    BANK_TRANSFER = "bank_transfer"
    TICKET = "ticket"
    ID_CARD = "id_card"
    UNKNOWN = "unknown"


@dataclass
class DocumentData:
    """Структура данных документа."""
    doc_type: str
    confidence: float
    raw_text: str
    extracted: Dict[str, Any]
    source_file: str
    processed_at: str
    checksum: str


# ═══════════════════════════════════════════════════════════════
# ВАЛИДАТОРЫ
# ═══════════════════════════════════════════════════════════════
class Validators:
    """Валидаторы форматов документов."""

    @staticmethod
    def validate_passport_number(number: str, country: str = None) -> bool:
        """Проверка формата номера паспорта."""
        if not number:
            return False

        patterns = {
            # Российский загранпаспорт: 2 цифры серия + 7 цифр номер
            "RU": r"^\d{2}\s?\d{7}$",
            # UAE passport
            "AE": r"^[A-Z]?\d{6,9}$",
            # Казахстан
            "KZ": r"^N?\d{7,9}$",
            # Общий паттерн
            None: r"^[A-Z0-9]{6,12}$"
        }

        pattern = patterns.get(country, patterns[None])
        return bool(re.match(pattern, number.replace(" ", ""), re.IGNORECASE))

    @staticmethod
    def validate_iban(iban: str) -> bool:
        """Проверка IBAN с контрольной суммой."""
        if not iban:
            return False

        iban = iban.replace(" ", "").upper()

        # Проверка базового формата
        if not re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{4,30}$", iban):
            return False

        # Перестановка первых 4 символов в конец
        rearranged = iban[4:] + iban[:4]

        # Замена букв на числа (A=10, B=11, ...)
        numeric = ""
        for char in rearranged:
            if char.isdigit():
                numeric += char
            else:
                numeric += str(ord(char) - ord('A') + 10)

        # Проверка по модулю 97
        return int(numeric) % 97 == 1

    @staticmethod
    def validate_card_number(number: str) -> bool:
        """Проверка номера карты алгоритмом Луна."""
        if not number:
            return False

        number = number.replace(" ", "").replace("-", "")

        if not number.isdigit() or len(number) < 13 or len(number) > 19:
            return False

        # Алгоритм Луна
        digits = [int(d) for d in number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]

        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))

        return checksum % 10 == 0

    @staticmethod
    def validate_flight_number(flight: str) -> bool:
        """Проверка номера рейса."""
        if not flight:
            return False
        return bool(re.match(r"^[A-Z]{2}\s?\d{1,4}[A-Z]?$", flight.upper()))

    @staticmethod
    def validate_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
        """Парсинг и валидация даты."""
        if not date_str:
            return None

        formats = formats or [
            "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d",
            "%d %b %Y", "%d %B %Y",
            "%d.%m.%y", "%d/%m/%y"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue

        return None


# ═══════════════════════════════════════════════════════════════
# ПРЕДОБРАБОТКА ИЗОБРАЖЕНИЙ
# ═══════════════════════════════════════════════════════════════
class ImagePreprocessor:
    """Предобработка изображений для улучшения OCR."""

    def __init__(self):
        self.cv2 = None
        self.np = None
        self._load_libs()

    def _load_libs(self):
        """Ленивая загрузка библиотек."""
        try:
            import cv2
            import numpy as np
            self.cv2 = cv2
            self.np = np
        except ImportError:
            logging.warning("OpenCV не установлен. Предобработка отключена.")

    def preprocess(self, image_path: str) -> str:
        """
        Предобработка изображения для OCR.

        Возвращает путь к обработанному изображению.
        """
        if not self.cv2:
            return image_path

        try:
            # Загрузка изображения
            img = self.cv2.imread(image_path)
            if img is None:
                return image_path

            # Конвертация в оттенки серого
            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)

            # Увеличение контраста (CLAHE)
            clahe = self.cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            contrast = clahe.apply(gray)

            # Удаление шума
            denoised = self.cv2.fastNlMeansDenoising(contrast, None, 10, 7, 21)

            # Бинаризация (Otsu)
            _, binary = self.cv2.threshold(
                denoised, 0, 255,
                self.cv2.THRESH_BINARY + self.cv2.THRESH_OTSU
            )

            # Исправление наклона (deskew)
            binary = self._deskew(binary)

            # Сохранение обработанного изображения
            output_path = image_path.replace(".", "_processed.")
            self.cv2.imwrite(output_path, binary)

            return output_path

        except Exception as e:
            logging.error(f"Ошибка предобработки: {e}")
            return image_path

    def _deskew(self, image):
        """Исправление наклона документа."""
        if not self.cv2 or not self.np:
            return image

        # Определение угла наклона
        coords = self.np.column_stack(self.np.where(image > 0))

        if len(coords) < 10:
            return image

        angle = self.cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Поворот изображения
        if abs(angle) > 0.5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = self.cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = self.cv2.warpAffine(
                image, M, (w, h),
                flags=self.cv2.INTER_CUBIC,
                borderMode=self.cv2.BORDER_REPLICATE
            )
            return rotated

        return image


# ═══════════════════════════════════════════════════════════════
# OCR ДВИЖКИ
# ═══════════════════════════════════════════════════════════════
class TesseractOCR:
    """OCR с использованием pytesseract."""

    def __init__(self, tesseract_path: str = TESSERACT_PATH):
        self.tesseract_path = tesseract_path
        self._setup()

    def _setup(self):
        """Настройка pytesseract."""
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
            self.pytesseract = pytesseract
        except ImportError:
            raise ImportError(
                "pytesseract не установлен. "
                "Установите: pip install pytesseract"
            )

    def recognize(self, image_path: str, lang: str = "rus+eng") -> Tuple[str, float]:
        """
        Распознавание текста из изображения.

        Returns:
            Tuple[str, float]: (текст, уверенность 0-1)
        """
        try:
            from PIL import Image

            img = Image.open(image_path)

            # Получение текста с уверенностью
            data = self.pytesseract.image_to_data(
                img, lang=lang, output_type=self.pytesseract.Output.DICT
            )

            # Извлечение текста
            text_parts = []
            confidences = []

            for i, word in enumerate(data['text']):
                if word.strip():
                    text_parts.append(word)
                    conf = data['conf'][i]
                    if conf > 0:
                        confidences.append(conf)

            text = " ".join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.5

            return text, avg_confidence

        except Exception as e:
            logging.error(f"Tesseract OCR ошибка: {e}")
            return "", 0.0


class GoogleVisionOCR:
    """OCR с использованием Google Cloud Vision API."""

    def __init__(self, api_key: str = GOOGLE_VISION_KEY):
        self.api_key = api_key
        if not api_key:
            raise ValueError("GOOGLE_VISION_KEY не установлен")

    def recognize(self, image_path: str) -> Tuple[str, float]:
        """Распознавание текста через Google Vision API."""
        try:
            import requests

            # Чтение и кодирование изображения
            with open(image_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")

            # Запрос к API
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"

            payload = {
                "requests": [{
                    "image": {"content": content},
                    "features": [
                        {"type": "TEXT_DETECTION"},
                        {"type": "DOCUMENT_TEXT_DETECTION"}
                    ]
                }]
            }

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            # Извлечение текста
            if "responses" in result and result["responses"]:
                annotations = result["responses"][0]

                if "fullTextAnnotation" in annotations:
                    text = annotations["fullTextAnnotation"]["text"]
                    # Google Vision не возвращает общую уверенность,
                    # используем среднюю по блокам
                    confidence = 0.95  # Высокая по умолчанию
                    return text, confidence

                elif "textAnnotations" in annotations:
                    text = annotations["textAnnotations"][0]["description"]
                    return text, 0.9

            return "", 0.0

        except Exception as e:
            logging.error(f"Google Vision OCR ошибка: {e}")
            return "", 0.0


class ClaudeVisionOCR:
    """OCR с использованием Claude Vision API."""

    def __init__(self, api_key: str = ANTHROPIC_API_KEY):
        self.api_key = api_key
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY не установлен")

    def recognize(self, image_path: str, doc_type_hint: str = None) -> Tuple[str, float]:
        """Распознавание текста через Claude Vision API."""
        try:
            import requests

            # Чтение и кодирование изображения
            with open(image_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")

            # Определение MIME типа
            ext = Path(image_path).suffix.lower()
            mime_types = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp"
            }
            media_type = mime_types.get(ext, "image/jpeg")

            # Формирование промпта
            prompt = self._build_prompt(doc_type_hint)

            # Запрос к API
            url = "https://api.anthropic.com/v1/messages"

            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
                "anthropic-version": "2023-06-01"
            }

            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4096,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": content
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()

            # Извлечение текста
            if "content" in result and result["content"]:
                text = result["content"][0]["text"]
                return text, 0.98  # Claude обычно очень точен

            return "", 0.0

        except Exception as e:
            logging.error(f"Claude Vision OCR ошибка: {e}")
            return "", 0.0

    def _build_prompt(self, doc_type_hint: str = None) -> str:
        """Формирование промпта для Claude."""
        base_prompt = """Извлеки ВСЕ текстовые данные с этого изображения документа.

Формат ответа - только JSON без markdown:
{
    "raw_text": "весь текст с документа",
    "document_type": "passport|visa|receipt|bank_transfer|ticket|id_card|unknown",
    "extracted_fields": {
        // для паспорта:
        "full_name": "",
        "passport_number": "",
        "date_of_birth": "",
        "nationality": "",
        "expiry_date": "",
        "issuing_country": "",

        // для визы:
        "visa_type": "",
        "visa_number": "",
        "valid_from": "",
        "valid_until": "",
        "entries": "",

        // для чека/квитанции:
        "amount": "",
        "currency": "",
        "date": "",
        "merchant": "",
        "purpose": "",

        // для банковского перевода:
        "amount": "",
        "currency": "",
        "sender": "",
        "receiver": "",
        "date": "",
        "reference": "",

        // для билета:
        "passenger_name": "",
        "flight_number": "",
        "departure_date": "",
        "departure_city": "",
        "arrival_city": "",
        "booking_reference": ""
    },
    "confidence": 0.95
}

Верни ТОЛЬКО JSON, без пояснений."""

        if doc_type_hint:
            base_prompt += f"\n\nПодсказка: это скорее всего {doc_type_hint}"

        return base_prompt


# ═══════════════════════════════════════════════════════════════
# ОПРЕДЕЛЕНИЕ ТИПА ДОКУМЕНТА
# ═══════════════════════════════════════════════════════════════
class DocumentClassifier:
    """Классификатор типов документов."""

    # Ключевые слова для определения типа
    KEYWORDS = {
        DocumentType.PASSPORT: [
            "passport", "паспорт", "passeport", "reisepass",
            "nationality", "гражданство", "date of birth",
            "дата рождения", "place of birth", "sex", "пол"
        ],
        DocumentType.VISA: [
            "visa", "виза", "valid until", "действительна до",
            "entries", "въезд", "duration of stay", "срок пребывания",
            "type of visa", "тип визы"
        ],
        DocumentType.RECEIPT: [
            "receipt", "чек", "квитанция", "invoice", "счёт",
            "total", "итого", "amount", "сумма", "payment",
            "оплата", "vat", "ндс", "tax"
        ],
        DocumentType.BANK_TRANSFER: [
            "transfer", "перевод", "payment order", "платёжное поручение",
            "sender", "отправитель", "beneficiary", "получатель",
            "iban", "swift", "bic", "reference"
        ],
        DocumentType.TICKET: [
            "boarding pass", "посадочный талон", "flight", "рейс",
            "passenger", "пассажир", "seat", "место", "gate",
            "departure", "вылет", "arrival", "прилёт",
            "booking reference", "номер бронирования"
        ],
        DocumentType.ID_CARD: [
            "identity card", "удостоверение", "id card",
            "emirates id", "resident", "резидент"
        ]
    }

    def classify(self, text: str) -> Tuple[DocumentType, float]:
        """
        Определение типа документа по тексту.

        Returns:
            Tuple[DocumentType, float]: (тип документа, уверенность)
        """
        text_lower = text.lower()

        scores = {}
        for doc_type, keywords in self.KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            scores[doc_type] = score

        if not scores or max(scores.values()) == 0:
            return DocumentType.UNKNOWN, 0.3

        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]

        # Нормализация уверенности
        confidence = min(0.95, 0.5 + (max_score * 0.1))

        return best_type, confidence


# ═══════════════════════════════════════════════════════════════
# ЭКСТРАКТОРЫ ДАННЫХ
# ═══════════════════════════════════════════════════════════════
class PassportExtractor:
    """Извлечение данных из паспорта."""

    def extract(self, text: str) -> Dict[str, Any]:
        """Извлечение полей паспорта."""
        data = {}

        # Полное имя (MRZ или обычный текст)
        name_patterns = [
            r"(?:Name|Имя|Фамилия)[:\s]+([A-ZА-ЯЁ][a-zа-яё]+(?:\s+[A-ZА-ЯЁ][a-zа-яё]+)*)",
            r"(?:Surname|Фамилия)[:\s]+([A-ZА-ЯЁ]+)",
            r"([A-Z]{2,}(?:\s+[A-Z]{2,})+)"  # MRZ формат
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                data["full_name"] = match.group(1).strip()
                break

        # Номер паспорта
        passport_patterns = [
            r"(?:Passport\s*No|Номер\s*паспорта|№)[:\s]*([A-Z]?\d{2}\s?\d{6,7})",
            r"\b(\d{2}\s?\d{7})\b",  # Российский формат
            r"\b([A-Z]{1,2}\d{6,9})\b"  # Международный
        ]
        for pattern in passport_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                number = match.group(1).replace(" ", "")
                if Validators.validate_passport_number(number):
                    data["passport_number"] = number
                    break

        # Дата рождения
        dob_patterns = [
            r"(?:Date\s*of\s*Birth|DOB|Дата\s*рождения)[:\s]*(\d{2}[./]\d{2}[./]\d{4})",
            r"(?:Born|Родился)[:\s]*(\d{2}[./]\d{2}[./]\d{4})"
        ]
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date = Validators.validate_date(match.group(1))
                if date:
                    data["date_of_birth"] = date.strftime("%Y-%m-%d")
                    break

        # Гражданство
        nationality_patterns = [
            r"(?:Nationality|Гражданство)[:\s]*([A-ZА-ЯЁ][a-zа-яё]+(?:\s+[A-ZА-ЯЁ][a-zа-яё]+)?)",
            r"(?:Citizen\s*of|Гражданин)[:\s]*([A-ZА-ЯЁ]+)"
        ]
        for pattern in nationality_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["nationality"] = match.group(1).strip()
                break

        # Срок действия
        expiry_patterns = [
            r"(?:Date\s*of\s*Expiry|Expiry|Срок\s*действия|Действителен\s*до)[:\s]*(\d{2}[./]\d{2}[./]\d{4})"
        ]
        for pattern in expiry_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date = Validators.validate_date(match.group(1))
                if date:
                    data["expiry_date"] = date.strftime("%Y-%m-%d")
                    break

        # Пол
        sex_match = re.search(r"(?:Sex|Пол)[:\s]*([MFМЖmf])", text, re.IGNORECASE)
        if sex_match:
            sex = sex_match.group(1).upper()
            data["sex"] = "M" if sex in "MМ" else "F"

        return data


class VisaExtractor:
    """Извлечение данных из визы."""

    def extract(self, text: str) -> Dict[str, Any]:
        """Извлечение полей визы."""
        data = {}

        # Тип визы
        visa_type_patterns = [
            r"(?:Type\s*of\s*Visa|Тип\s*визы|Category)[:\s]*([A-Z]{1,2}\d?)",
            r"(?:Tourist|Business|Work|Transit|Туристическая|Рабочая|Деловая)"
        ]
        for pattern in visa_type_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["visa_type"] = match.group(0).strip()
                break

        # Номер визы
        visa_num_patterns = [
            r"(?:Visa\s*No|Номер\s*визы)[:\s]*([A-Z0-9]+)",
            r"(?:Number)[:\s]*([A-Z]?\d{6,12})"
        ]
        for pattern in visa_num_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["visa_number"] = match.group(1).strip()
                break

        # Даты действия
        date_patterns = [
            (r"(?:Valid\s*From|From|С)[:\s]*(\d{2}[./]\d{2}[./]\d{4})", "valid_from"),
            (r"(?:Valid\s*Until|Until|До|Expiry)[:\s]*(\d{2}[./]\d{2}[./]\d{4})", "valid_until")
        ]
        for pattern, field in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date = Validators.validate_date(match.group(1))
                if date:
                    data[field] = date.strftime("%Y-%m-%d")

        # Количество въездов
        entries_match = re.search(r"(?:Entries|Въезд(?:ы|ов)?)[:\s]*(\d+|Multiple|Single|Многократная)", text, re.IGNORECASE)
        if entries_match:
            data["entries"] = entries_match.group(1)

        return data


class ReceiptExtractor:
    """Извлечение данных из чеков и квитанций."""

    def extract(self, text: str) -> Dict[str, Any]:
        """Извлечение полей чека."""
        data = {}

        # Сумма с валютой
        amount_patterns = [
            r"(?:Total|Итого|Amount|Сумма)[:\s]*([A-Z]{3})?[\s]*(\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d{2})?)",
            r"(\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d{2})?)\s*(AED|USD|RUB|EUR|руб|дирхам|долл)",
            r"(?:AED|USD|RUB|EUR)\s*(\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d{2})?)"
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                # Попытка определить сумму и валюту
                for g in groups:
                    if g and re.match(r"\d", g):
                        data["amount"] = g.replace(" ", "").replace(",", ".")
                    elif g and re.match(r"[A-ZА-Яа-я]", g):
                        data["currency"] = g.upper()
                break

        # Дата
        date_patterns = [
            r"(?:Date|Дата)[:\s]*(\d{2}[./]\d{2}[./]\d{4})",
            r"(\d{2}[./]\d{2}[./]\d{4})"
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date = Validators.validate_date(match.group(1))
                if date:
                    data["date"] = date.strftime("%Y-%m-%d")
                    break

        # Продавец/Магазин
        merchant_patterns = [
            r"^([A-ZА-ЯЁ][A-Za-zА-Яа-яЁё\s&]+(?:LLC|Ltd|Inc|ООО|ИП)?)",
            r"(?:Merchant|Продавец|Store|Магазин)[:\s]*([^\n]+)"
        ]
        for pattern in merchant_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                data["merchant"] = match.group(1).strip()
                break

        # Назначение платежа
        purpose_patterns = [
            r"(?:Description|Описание|Purpose|Назначение)[:\s]*([^\n]+)",
            r"(?:For|За)[:\s]*([^\n]+)"
        ]
        for pattern in purpose_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["purpose"] = match.group(1).strip()
                break

        return data


class BankTransferExtractor:
    """Извлечение данных из банковских переводов."""

    def extract(self, text: str) -> Dict[str, Any]:
        """Извлечение полей банковского перевода."""
        data = {}

        # Сумма
        amount_match = re.search(
            r"(?:Amount|Сумма)[:\s]*([A-Z]{3})?[\s]*(\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d{2})?)",
            text, re.IGNORECASE
        )
        if amount_match:
            data["amount"] = amount_match.group(2).replace(" ", "").replace(",", ".")
            if amount_match.group(1):
                data["currency"] = amount_match.group(1)

        # IBAN
        iban_match = re.search(r"\b([A-Z]{2}\d{2}[A-Z0-9]{4,30})\b", text)
        if iban_match:
            iban = iban_match.group(1)
            if Validators.validate_iban(iban):
                data["iban"] = iban

        # Отправитель
        sender_patterns = [
            r"(?:Sender|From|Отправитель|От)[:\s]*([^\n]+)",
            r"(?:Payer|Плательщик)[:\s]*([^\n]+)"
        ]
        for pattern in sender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["sender"] = match.group(1).strip()
                break

        # Получатель
        receiver_patterns = [
            r"(?:Beneficiary|Receiver|To|Получатель|Кому)[:\s]*([^\n]+)",
            r"(?:Payee)[:\s]*([^\n]+)"
        ]
        for pattern in receiver_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["receiver"] = match.group(1).strip()
                break

        # Референс
        ref_match = re.search(
            r"(?:Reference|Ref|Референс)[:\s]*([A-Z0-9]+)",
            text, re.IGNORECASE
        )
        if ref_match:
            data["reference"] = ref_match.group(1)

        # Дата
        date_match = re.search(r"(\d{2}[./]\d{2}[./]\d{4})", text)
        if date_match:
            date = Validators.validate_date(date_match.group(1))
            if date:
                data["date"] = date.strftime("%Y-%m-%d")

        return data


class TicketExtractor:
    """Извлечение данных из билетов."""

    def extract(self, text: str) -> Dict[str, Any]:
        """Извлечение полей билета."""
        data = {}

        # Имя пассажира
        name_patterns = [
            r"(?:Passenger|Name|Пассажир|Имя)[:\s]*([A-ZА-ЯЁ][a-zа-яё]+(?:\s+[A-ZА-ЯЁ][a-zа-яё]+)+)",
            r"(?:MR|MRS|MS)\s+([A-Z]+(?:\s+[A-Z]+)+)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["passenger_name"] = match.group(1).strip()
                break

        # Номер рейса
        flight_match = re.search(r"\b([A-Z]{2}\s?\d{1,4}[A-Z]?)\b", text)
        if flight_match:
            flight = flight_match.group(1).replace(" ", "")
            if Validators.validate_flight_number(flight):
                data["flight_number"] = flight

        # Дата вылета
        date_patterns = [
            r"(?:Date|Departure|Дата|Вылет)[:\s]*(\d{2}[./]\d{2}[./]\d{4})",
            r"(\d{2}\s+[A-ZА-Яа-я]{3,10}\s+\d{4})"  # 25 Dec 2024
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date = Validators.validate_date(match.group(1))
                if date:
                    data["departure_date"] = date.strftime("%Y-%m-%d")
                    break

        # Города
        city_patterns = [
            (r"(?:From|Departure|Откуда|Вылет)[:\s]*([A-ZА-ЯЁ][a-zа-яё]+)", "departure_city"),
            (r"(?:To|Arrival|Куда|Прилёт)[:\s]*([A-ZА-ЯЁ][a-zа-яё]+)", "arrival_city")
        ]
        for pattern, field in city_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[field] = match.group(1).strip()

        # Код бронирования
        booking_patterns = [
            r"(?:Booking\s*(?:Reference|Code)|PNR|Код\s*бронирования)[:\s]*([A-Z0-9]{6})",
            r"\b([A-Z]{6})\b"  # 6-буквенный код
        ]
        for pattern in booking_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["booking_reference"] = match.group(1)
                break

        # Место
        seat_match = re.search(r"(?:Seat|Место)[:\s]*(\d{1,2}[A-Z])", text, re.IGNORECASE)
        if seat_match:
            data["seat"] = seat_match.group(1)

        return data


# ═══════════════════════════════════════════════════════════════
# БЕЗОПАСНОСТЬ
# ═══════════════════════════════════════════════════════════════
class SecurityManager:
    """Управление безопасностью данных."""

    SENSITIVE_PATTERNS = {
        "passport_number": (r"\d{2}\s?\d{7}", lambda m: m[:2] + "***" + m[-2:]),
        "iban": (r"[A-Z]{2}\d{2}[A-Z0-9]+", lambda m: m[:4] + "****" + m[-4:]),
        "card_number": (r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}", lambda m: m[:4] + " **** **** " + m[-4:]),
        "phone": (r"\+?\d{10,15}", lambda m: m[:4] + "****" + m[-2:]),
        "date_of_birth": (r"\d{2}[./]\d{2}[./]\d{4}", lambda m: "**/**/****")
    }

    @classmethod
    def mask_sensitive(cls, text: str) -> str:
        """Маскирование чувствительных данных."""
        masked = text
        for field, (pattern, masker) in cls.SENSITIVE_PATTERNS.items():
            matches = re.findall(pattern, masked)
            for match in matches:
                masked = masked.replace(match, masker(match))
        return masked

    @classmethod
    def mask_dict(cls, data: Dict) -> Dict:
        """Маскирование словаря с данными."""
        masked = {}
        for key, value in data.items():
            if isinstance(value, str):
                masked[key] = cls.mask_sensitive(value)
            elif isinstance(value, dict):
                masked[key] = cls.mask_dict(value)
            else:
                masked[key] = value
        return masked

    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """Простое XOR-шифрование (для демонстрации)."""
        if not key:
            return data

        # В продакшне используйте cryptography.fernet
        encrypted = []
        for i, char in enumerate(data):
            key_char = key[i % len(key)]
            encrypted.append(chr(ord(char) ^ ord(key_char)))

        return base64.b64encode("".join(encrypted).encode()).decode()

    @staticmethod
    def decrypt_data(data: str, key: str) -> str:
        """Расшифровка XOR."""
        if not key:
            return data

        decoded = base64.b64decode(data).decode()
        decrypted = []
        for i, char in enumerate(decoded):
            key_char = key[i % len(key)]
            decrypted.append(chr(ord(char) ^ ord(key_char)))

        return "".join(decrypted)


# ═══════════════════════════════════════════════════════════════
# ГЛАВНЫЙ OCR ПРОЦЕССОР
# ═══════════════════════════════════════════════════════════════
class DocumentOCR:
    """Главный класс OCR обработки документов."""

    def __init__(self, provider: str = OCR_PROVIDER):
        self.provider = provider
        self.preprocessor = ImagePreprocessor()
        self.classifier = DocumentClassifier()
        self.ocr_engine = self._init_ocr_engine()

        # Экстракторы по типам документов
        self.extractors = {
            DocumentType.PASSPORT: PassportExtractor(),
            DocumentType.VISA: VisaExtractor(),
            DocumentType.RECEIPT: ReceiptExtractor(),
            DocumentType.BANK_TRANSFER: BankTransferExtractor(),
            DocumentType.TICKET: TicketExtractor(),
            DocumentType.ID_CARD: PassportExtractor(),  # Похожая структура
        }

        # Настройка логирования
        self._setup_logging()

    def _init_ocr_engine(self):
        """Инициализация OCR движка."""
        if self.provider == "tesseract":
            return TesseractOCR()
        elif self.provider == "google":
            return GoogleVisionOCR()
        elif self.provider == "claude":
            return ClaudeVisionOCR()
        else:
            logging.warning(f"Неизвестный провайдер {self.provider}, использую tesseract")
            return TesseractOCR()

    def _setup_logging(self):
        """Настройка логирования с маскированием."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def process_image(self, image_path: str, doc_type_hint: str = None) -> DocumentData:
        """
        Обработка одного изображения документа.

        Args:
            image_path: Путь к изображению
            doc_type_hint: Подсказка типа документа (опционально)

        Returns:
            DocumentData: Структурированные данные документа
        """
        image_path = str(image_path)

        # Вычисление контрольной суммы
        with open(image_path, "rb") as f:
            checksum = hashlib.md5(f.read()).hexdigest()

        # Предобработка
        processed_path = self.preprocessor.preprocess(image_path)

        # OCR
        if self.provider == "claude":
            # Claude сам извлекает структурированные данные
            raw_text, confidence = self.ocr_engine.recognize(processed_path, doc_type_hint)

            # Попытка парсинга JSON ответа Claude
            try:
                claude_data = json.loads(raw_text)
                doc_type = DocumentType(claude_data.get("document_type", "unknown"))
                extracted = claude_data.get("extracted_fields", {})
                raw_text = claude_data.get("raw_text", raw_text)
                confidence = claude_data.get("confidence", confidence)
            except (json.JSONDecodeError, ValueError):
                # Если не JSON, обрабатываем как обычный текст
                doc_type, type_confidence = self.classifier.classify(raw_text)
                confidence = min(confidence, type_confidence)
                extracted = self._extract_data(raw_text, doc_type)
        else:
            # Для других движков - стандартная обработка
            raw_text, confidence = self.ocr_engine.recognize(processed_path)

            # Определение типа документа
            if doc_type_hint:
                try:
                    doc_type = DocumentType(doc_type_hint)
                except ValueError:
                    doc_type, _ = self.classifier.classify(raw_text)
            else:
                doc_type, type_confidence = self.classifier.classify(raw_text)
                confidence = min(confidence, type_confidence)

            # Извлечение данных
            extracted = self._extract_data(raw_text, doc_type)

        # Удаление временного файла
        if processed_path != image_path and os.path.exists(processed_path):
            os.remove(processed_path)

        # Логирование (с маскированием)
        if MASK_SENSITIVE_DATA:
            log_data = SecurityManager.mask_dict(extracted)
            logging.info(f"Обработан {doc_type.value}: {log_data}")
        else:
            logging.info(f"Обработан {doc_type.value}")

        return DocumentData(
            doc_type=doc_type.value,
            confidence=confidence,
            raw_text=raw_text,
            extracted=extracted,
            source_file=image_path,
            processed_at=datetime.now().isoformat(),
            checksum=checksum
        )

    def _extract_data(self, text: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Извлечение данных в зависимости от типа документа."""
        extractor = self.extractors.get(doc_type)
        if extractor:
            return extractor.extract(text)
        return {}

    def process_directory(self, directory: str, output_dir: str = None) -> Dict[str, List[DocumentData]]:
        """
        Обработка всех изображений в директории.

        Args:
            directory: Путь к директории с изображениями
            output_dir: Директория для сохранения результатов

        Returns:
            Dict с результатами по типам документов
        """
        directory = Path(directory)
        output_dir = Path(output_dir) if output_dir else directory / "ocr_results"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Поиск изображений
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}
        images = [
            f for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        logging.info(f"Найдено {len(images)} изображений в {directory}")

        # Обработка
        results = {
            "documents": [],
            "passports": [],
            "receipts": [],
            "errors": []
        }

        for image_path in images:
            try:
                doc_data = self.process_image(str(image_path))
                results["documents"].append(doc_data)

                # Распределение по категориям
                if doc_data.doc_type == "passport":
                    results["passports"].append(doc_data)
                elif doc_data.doc_type in ["receipt", "bank_transfer"]:
                    results["receipts"].append(doc_data)

            except Exception as e:
                logging.error(f"Ошибка обработки {image_path}: {e}")
                results["errors"].append({
                    "file": str(image_path),
                    "error": str(e)
                })

        # Сохранение результатов
        self._save_results(results, output_dir)

        return results

    def _save_results(self, results: Dict, output_dir: Path):
        """Сохранение результатов в JSON файлы."""

        # documents.json - все документы
        documents_data = [asdict(d) for d in results["documents"]]
        self._save_json(output_dir / "documents.json", documents_data)

        # passport_data.json - только паспорта
        if results["passports"]:
            passport_data = [asdict(d) for d in results["passports"]]
            self._save_json(output_dir / "passport_data.json", passport_data)

        # receipts.json - чеки и платежи
        if results["receipts"]:
            receipts_data = [asdict(d) for d in results["receipts"]]
            self._save_json(output_dir / "receipts.json", receipts_data)

        # errors.json - если были ошибки
        if results["errors"]:
            self._save_json(output_dir / "errors.json", results["errors"])

        logging.info(f"Результаты сохранены в {output_dir}")

    def _save_json(self, path: Path, data: Any):
        """Сохранение JSON с опциональным шифрованием."""
        json_str = json.dumps(data, ensure_ascii=False, indent=2)

        if ENCRYPT_OUTPUT and ENCRYPTION_KEY:
            json_str = SecurityManager.encrypt_data(json_str, ENCRYPTION_KEY)

        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)


# ═══════════════════════════════════════════════════════════════
# CLI ИНТЕРФЕЙС
# ═══════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="OCR для распознавания документов из фото в чатах",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Обработка одного изображения
  python document_ocr.py -i photo.jpg

  # Обработка директории
  python document_ocr.py -d D:/Downloads/Chats/_медиа

  # Использование Google Vision API
  python document_ocr.py -i photo.jpg --provider google

  # Использование Claude Vision API
  python document_ocr.py -i photo.jpg --provider claude

  # С указанием типа документа
  python document_ocr.py -i passport.jpg --type passport

Поддерживаемые типы документов:
  passport      - Паспорта
  visa          - Визы
  receipt       - Чеки и квитанции
  bank_transfer - Банковские переводы
  ticket        - Билеты
  id_card       - ID карты
"""
    )

    parser.add_argument(
        "-i", "--image",
        help="Путь к изображению для обработки"
    )
    parser.add_argument(
        "-d", "--directory",
        default=str(MEDIA_DIR),
        help="Директория с изображениями"
    )
    parser.add_argument(
        "-o", "--output",
        default=str(JSON_DIR / "ocr"),
        help="Директория для результатов"
    )
    parser.add_argument(
        "--provider",
        choices=["tesseract", "google", "claude"],
        default=OCR_PROVIDER,
        help="OCR провайдер"
    )
    parser.add_argument(
        "--type",
        choices=["passport", "visa", "receipt", "bank_transfer", "ticket", "id_card"],
        help="Тип документа (подсказка)"
    )
    parser.add_argument(
        "--no-preprocess",
        action="store_true",
        help="Отключить предобработку изображений"
    )
    parser.add_argument(
        "--mask",
        action="store_true",
        default=MASK_SENSITIVE_DATA,
        help="Маскировать чувствительные данные в логах"
    )
    parser.add_argument(
        "--encrypt",
        action="store_true",
        default=ENCRYPT_OUTPUT,
        help="Шифровать выходные файлы"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Подробный вывод"
    )

    args = parser.parse_args()

    # Настройка параметров безопасности из аргументов
    mask_data = args.mask
    encrypt_data = args.encrypt

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Инициализация OCR
    try:
        ocr = DocumentOCR(provider=args.provider)
    except Exception as e:
        print(f"Ошибка инициализации OCR: {e}")
        sys.exit(1)

    # Обработка
    if args.image:
        # Одно изображение
        if not os.path.exists(args.image):
            print(f"Файл не найден: {args.image}")
            sys.exit(1)

        result = ocr.process_image(args.image, args.type)

        print("\n" + "=" * 60)
        print(f"Тип документа: {result.doc_type}")
        print(f"Уверенность: {result.confidence:.1%}")
        print("=" * 60)

        if result.extracted:
            print("\nИзвлечённые данные:")
            for key, value in result.extracted.items():
                display_value = value
                if mask_data:
                    display_value = SecurityManager.mask_sensitive(str(value))
                print(f"  {key}: {display_value}")

        # Сохранение результата
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)

        result_file = output_path / f"{Path(args.image).stem}_ocr.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(asdict(result), f, ensure_ascii=False, indent=2)

        print(f"\nРезультат сохранён: {result_file}")

    else:
        # Директория
        if not os.path.exists(args.directory):
            print(f"Директория не найдена: {args.directory}")
            sys.exit(1)

        results = ocr.process_directory(args.directory, args.output)

        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ OCR")
        print("=" * 60)
        print(f"Всего обработано: {len(results['documents'])}")
        print(f"Паспортов: {len(results['passports'])}")
        print(f"Чеков/платежей: {len(results['receipts'])}")
        print(f"Ошибок: {len(results['errors'])}")
        print(f"\nРезультаты сохранены: {args.output}")


if __name__ == "__main__":
    main()
