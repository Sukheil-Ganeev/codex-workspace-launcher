#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Реферальная программа с бонусами.

Функции:
- Генерация реферальных кодов (уникальный код, QR-код, короткая ссылка)
- Отслеживание рефералов (кто привёл кого, статус, сумма бронирований)
- Начисление бонусов (процент, фикс, многоуровневая система)
- Выплаты (баланс, история, запросы)
- Уведомления (бонусы, напоминания)
- Интеграция (Bitrix24, WhatsApp, отчёты)

Использование:
    # Генерация кода
    python referral_program.py --generate --phone +971501234567 --name "Иван"

    # Регистрация реферала
    python referral_program.py --register --code REF-ABC123 --referred-phone +971507654321

    # Обновление статуса
    python referral_program.py --update-status --referred-phone +971507654321 --status booked --amount 5000

    # Начисление бонуса
    python referral_program.py --credit-bonus --phone +971501234567 --amount 500 --reason "Бонус за реферала"

    # Запрос на выплату
    python referral_program.py --request-payout --phone +971501234567 --amount 1000

    # Баланс
    python referral_program.py --balance --phone +971501234567

    # Отчёт
    python referral_program.py --report --format xlsx --output referrals_report.xlsx

    # Синхронизация с Bitrix24
    python referral_program.py --sync-bitrix
"""

import os
import sys
import json
import uuid
import hashlib
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import base64
import io

# Добавляем путь к скриптам
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import JSON_DIR, ANALYTICS_DIR, BITRIX24_CONFIG

# Опциональные импорты
try:
    import qrcode
    from qrcode.image.pil import PilImage
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    print("Предупреждение: qrcode не установлен. pip install qrcode[pil]")

try:
    import pyshorteners
    HAS_SHORTENER = True
except ImportError:
    HAS_SHORTENER = False
    print("Предупреждение: pyshorteners не установлен. pip install pyshorteners")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Предупреждение: pandas не установлен. pip install pandas openpyxl")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(ANALYTICS_DIR / "referral_program.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ═══════════════════════════════════════════════════════════════════════════

REFERRAL_CONFIG = {
    # Базовый URL для реферальных ссылок
    "base_url": os.getenv("REFERRAL_BASE_URL", "https://marsel.travel/ref"),

    # Бонусная система
    "bonus": {
        # Процент от суммы бронирования реферала
        "percent": float(os.getenv("REFERRAL_BONUS_PERCENT", "5")),
        # Фиксированный бонус за регистрацию реферала (AED)
        "fixed_registration": float(os.getenv("REFERRAL_FIXED_REGISTRATION", "50")),
        # Фиксированный бонус за первое бронирование реферала (AED)
        "fixed_first_booking": float(os.getenv("REFERRAL_FIXED_FIRST_BOOKING", "100")),
        # Минимальная сумма для выплаты (AED)
        "min_payout": float(os.getenv("REFERRAL_MIN_PAYOUT", "200")),
        # Валюта
        "currency": "AED",
    },

    # Многоуровневая система (optional)
    "multilevel": {
        "enabled": os.getenv("REFERRAL_MULTILEVEL", "false").lower() == "true",
        "levels": {
            # Уровень 1: прямой реферал
            1: {"percent": 5.0, "description": "Прямой реферал"},
            # Уровень 2: реферал реферала
            2: {"percent": 2.0, "description": "Реферал 2-го уровня"},
            # Уровень 3: глубокий реферал
            3: {"percent": 1.0, "description": "Реферал 3-го уровня"},
        }
    },

    # Уведомления
    "notifications": {
        "enabled": True,
        "channels": ["whatsapp", "telegram"],
    },

    # Срок действия кода (дней, 0 = бессрочно)
    "code_expiry_days": 0,

    # Префикс кода
    "code_prefix": "REF-",

    # Длина кода (без префикса)
    "code_length": 6,
}

# Пути к файлам данных
REFERRALS_DIR = JSON_DIR / "referrals"
REFERRALS_FILE = REFERRALS_DIR / "referrals.json"
BONUSES_FILE = REFERRALS_DIR / "bonuses.json"
PAYOUTS_FILE = REFERRALS_DIR / "payouts.json"
CODES_FILE = REFERRALS_DIR / "codes.json"
QR_DIR = REFERRALS_DIR / "qr_codes"

# Создаём директории
REFERRALS_DIR.mkdir(parents=True, exist_ok=True)
QR_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# МОДЕЛИ ДАННЫХ
# ═══════════════════════════════════════════════════════════════════════════

class ReferralStatus(Enum):
    """Статус реферала."""
    REGISTERED = "registered"     # Зарегистрирован по реф. коду
    BOOKED = "booked"             # Сделал бронирование
    PAID = "paid"                 # Оплатил бронирование
    COMPLETED = "completed"       # Услуга оказана
    INACTIVE = "inactive"         # Неактивен (>90 дней без заказов)


class BonusType(Enum):
    """Тип бонуса."""
    PERCENT = "percent"           # Процент от суммы
    FIXED_REGISTRATION = "fixed_registration"  # Фикс за регистрацию
    FIXED_FIRST_BOOKING = "fixed_first_booking"  # Фикс за первое бронирование
    MULTILEVEL = "multilevel"     # Многоуровневый бонус
    MANUAL = "manual"             # Ручное начисление
    PROMO = "promo"               # Промо-бонус


class PayoutStatus(Enum):
    """Статус выплаты."""
    PENDING = "pending"           # Ожидает обработки
    APPROVED = "approved"         # Одобрено
    PROCESSING = "processing"     # В обработке
    COMPLETED = "completed"       # Выплачено
    REJECTED = "rejected"         # Отклонено


@dataclass
class ReferralCode:
    """Реферальный код."""
    code: str
    phone: str
    name: str
    created_at: str
    expires_at: Optional[str] = None
    short_url: Optional[str] = None
    qr_code_path: Optional[str] = None
    is_active: bool = True
    uses_count: int = 0
    total_revenue: float = 0.0
    total_bonus: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReferralCode':
        return cls(**data)


@dataclass
class Referral:
    """Реферал (приведённый клиент)."""
    id: str
    referrer_phone: str           # Телефон того, кто привёл
    referrer_code: str            # Код, по которому пришёл
    referred_phone: str           # Телефон реферала
    referred_name: str
    status: str = ReferralStatus.REGISTERED.value
    registered_at: str = ""
    first_booking_at: Optional[str] = None
    last_activity_at: Optional[str] = None
    total_bookings: int = 0
    total_amount: float = 0.0
    total_bonus_generated: float = 0.0
    level: int = 1                # Уровень в многоуровневой системе
    parent_referral_id: Optional[str] = None  # ID реферала-родителя
    notes: str = ""
    bitrix_id: Optional[str] = None

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.now().isoformat()
        if not self.id:
            self.id = str(uuid.uuid4())[:8]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Referral':
        return cls(**data)


@dataclass
class BonusTransaction:
    """Транзакция бонуса."""
    id: str
    phone: str                    # Телефон получателя бонуса
    amount: float
    currency: str = "AED"
    bonus_type: str = BonusType.PERCENT.value
    reason: str = ""
    referral_id: Optional[str] = None  # ID связанного реферала
    booking_id: Optional[str] = None   # ID связанного бронирования
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.id:
            self.id = str(uuid.uuid4())[:8]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BonusTransaction':
        return cls(**data)


@dataclass
class PayoutRequest:
    """Запрос на выплату."""
    id: str
    phone: str
    amount: float
    currency: str = "AED"
    status: str = PayoutStatus.PENDING.value
    requested_at: str = ""
    processed_at: Optional[str] = None
    payment_method: str = ""      # bank_transfer, cash, crypto
    payment_details: Dict[str, Any] = field(default_factory=dict)
    admin_notes: str = ""

    def __post_init__(self):
        if not self.requested_at:
            self.requested_at = datetime.now().isoformat()
        if not self.id:
            self.id = str(uuid.uuid4())[:8]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PayoutRequest':
        return cls(**data)


# ═══════════════════════════════════════════════════════════════════════════
# ХРАНИЛИЩЕ ДАННЫХ
# ═══════════════════════════════════════════════════════════════════════════

class ReferralStorage:
    """Хранилище данных реферальной программы."""

    def __init__(self):
        self.codes: Dict[str, ReferralCode] = {}
        self.referrals: Dict[str, Referral] = {}
        self.bonuses: List[BonusTransaction] = []
        self.payouts: List[PayoutRequest] = []
        self._load_all()

    def _load_all(self):
        """Загрузить все данные."""
        self._load_codes()
        self._load_referrals()
        self._load_bonuses()
        self._load_payouts()

    def _load_codes(self):
        """Загрузить реферальные коды."""
        if CODES_FILE.exists():
            try:
                with open(CODES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.codes = {
                        code: ReferralCode.from_dict(d)
                        for code, d in data.items()
                    }
                logger.info(f"Загружено {len(self.codes)} реферальных кодов")
            except Exception as e:
                logger.error(f"Ошибка загрузки кодов: {e}")

    def _load_referrals(self):
        """Загрузить рефералов."""
        if REFERRALS_FILE.exists():
            try:
                with open(REFERRALS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.referrals = {
                        ref_id: Referral.from_dict(d)
                        for ref_id, d in data.items()
                    }
                logger.info(f"Загружено {len(self.referrals)} рефералов")
            except Exception as e:
                logger.error(f"Ошибка загрузки рефералов: {e}")

    def _load_bonuses(self):
        """Загрузить бонусные транзакции."""
        if BONUSES_FILE.exists():
            try:
                with open(BONUSES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bonuses = [BonusTransaction.from_dict(d) for d in data]
                logger.info(f"Загружено {len(self.bonuses)} бонусных транзакций")
            except Exception as e:
                logger.error(f"Ошибка загрузки бонусов: {e}")

    def _load_payouts(self):
        """Загрузить запросы на выплату."""
        if PAYOUTS_FILE.exists():
            try:
                with open(PAYOUTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.payouts = [PayoutRequest.from_dict(d) for d in data]
                logger.info(f"Загружено {len(self.payouts)} запросов на выплату")
            except Exception as e:
                logger.error(f"Ошибка загрузки выплат: {e}")

    def save_codes(self):
        """Сохранить реферальные коды."""
        try:
            with open(CODES_FILE, 'w', encoding='utf-8') as f:
                data = {code: rc.to_dict() for code, rc in self.codes.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено {len(self.codes)} кодов")
        except Exception as e:
            logger.error(f"Ошибка сохранения кодов: {e}")

    def save_referrals(self):
        """Сохранить рефералов."""
        try:
            with open(REFERRALS_FILE, 'w', encoding='utf-8') as f:
                data = {ref_id: ref.to_dict() for ref_id, ref in self.referrals.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено {len(self.referrals)} рефералов")
        except Exception as e:
            logger.error(f"Ошибка сохранения рефералов: {e}")

    def save_bonuses(self):
        """Сохранить бонусные транзакции."""
        try:
            with open(BONUSES_FILE, 'w', encoding='utf-8') as f:
                data = [b.to_dict() for b in self.bonuses]
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено {len(self.bonuses)} бонусов")
        except Exception as e:
            logger.error(f"Ошибка сохранения бонусов: {e}")

    def save_payouts(self):
        """Сохранить запросы на выплату."""
        try:
            with open(PAYOUTS_FILE, 'w', encoding='utf-8') as f:
                data = [p.to_dict() for p in self.payouts]
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранено {len(self.payouts)} выплат")
        except Exception as e:
            logger.error(f"Ошибка сохранения выплат: {e}")

    def save_all(self):
        """Сохранить все данные."""
        self.save_codes()
        self.save_referrals()
        self.save_bonuses()
        self.save_payouts()


# ═══════════════════════════════════════════════════════════════════════════
# ГЕНЕРАТОР КОДОВ
# ═══════════════════════════════════════════════════════════════════════════

class ReferralCodeGenerator:
    """Генератор реферальных кодов."""

    def __init__(self, storage: ReferralStorage):
        self.storage = storage

    def generate_code(self, phone: str, name: str) -> ReferralCode:
        """Генерация уникального реферального кода."""
        # Проверяем, есть ли уже код для этого телефона
        for code, rc in self.storage.codes.items():
            if rc.phone == phone and rc.is_active:
                logger.info(f"Код уже существует для {phone}: {code}")
                return rc

        # Генерируем уникальный код
        prefix = REFERRAL_CONFIG["code_prefix"]
        length = REFERRAL_CONFIG["code_length"]

        while True:
            # Создаём код на основе хэша телефона + случайного UUID
            raw = f"{phone}:{uuid.uuid4().hex}"
            hash_val = hashlib.md5(raw.encode()).hexdigest().upper()
            code = f"{prefix}{hash_val[:length]}"

            if code not in self.storage.codes:
                break

        # Срок действия
        expires_at = None
        if REFERRAL_CONFIG["code_expiry_days"] > 0:
            expires_at = (
                datetime.now() +
                timedelta(days=REFERRAL_CONFIG["code_expiry_days"])
            ).isoformat()

        # Создаём объект кода
        referral_code = ReferralCode(
            code=code,
            phone=phone,
            name=name,
            created_at=datetime.now().isoformat(),
            expires_at=expires_at,
        )

        # Генерируем короткую ссылку
        referral_code.short_url = self._generate_short_url(code)

        # Генерируем QR-код
        referral_code.qr_code_path = self._generate_qr_code(code, referral_code.short_url)

        # Сохраняем
        self.storage.codes[code] = referral_code
        self.storage.save_codes()

        logger.info(f"Создан реферальный код {code} для {name} ({phone})")

        return referral_code

    def _generate_short_url(self, code: str) -> Optional[str]:
        """Генерация короткой ссылки."""
        if not HAS_SHORTENER:
            # Возвращаем прямую ссылку
            return f"{REFERRAL_CONFIG['base_url']}/{code}"

        try:
            # Полный URL
            full_url = f"{REFERRAL_CONFIG['base_url']}/{code}"

            # Пробуем разные сервисы
            shortener = pyshorteners.Shortener()

            # TinyURL (не требует API ключа)
            short_url = shortener.tinyurl.short(full_url)
            logger.info(f"Создана короткая ссылка: {short_url}")
            return short_url

        except Exception as e:
            logger.warning(f"Не удалось создать короткую ссылку: {e}")
            return f"{REFERRAL_CONFIG['base_url']}/{code}"

    def _generate_qr_code(self, code: str, url: str) -> Optional[str]:
        """Генерация QR-кода."""
        if not HAS_QRCODE:
            return None

        try:
            # Создаём QR-код
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url or f"{REFERRAL_CONFIG['base_url']}/{code}")
            qr.make(fit=True)

            # Генерируем изображение
            img = qr.make_image(fill_color="black", back_color="white")

            # Сохраняем
            qr_path = QR_DIR / f"{code}.png"
            img.save(str(qr_path))

            logger.info(f"Создан QR-код: {qr_path}")
            return str(qr_path)

        except Exception as e:
            logger.error(f"Ошибка создания QR-кода: {e}")
            return None

    def get_qr_base64(self, code: str) -> Optional[str]:
        """Получить QR-код в base64 для отправки."""
        if not HAS_QRCODE:
            return None

        rc = self.storage.codes.get(code)
        if not rc or not rc.qr_code_path:
            return None

        try:
            qr_path = Path(rc.qr_code_path)
            if qr_path.exists():
                with open(qr_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Ошибка чтения QR-кода: {e}")

        return None


# ═══════════════════════════════════════════════════════════════════════════
# ТРЕКЕР РЕФЕРАЛОВ
# ═══════════════════════════════════════════════════════════════════════════

class ReferralTracker:
    """Отслеживание рефералов."""

    def __init__(self, storage: ReferralStorage):
        self.storage = storage

    def register_referral(
        self,
        referral_code: str,
        referred_phone: str,
        referred_name: str = "",
        notes: str = ""
    ) -> Optional[Referral]:
        """Регистрация нового реферала."""
        # Проверяем код
        rc = self.storage.codes.get(referral_code)
        if not rc:
            logger.error(f"Код {referral_code} не найден")
            return None

        if not rc.is_active:
            logger.error(f"Код {referral_code} неактивен")
            return None

        if rc.expires_at:
            expires = datetime.fromisoformat(rc.expires_at)
            if datetime.now() > expires:
                logger.error(f"Код {referral_code} истёк")
                return None

        # Проверяем, не зарегистрирован ли уже этот телефон
        for ref in self.storage.referrals.values():
            if ref.referred_phone == referred_phone:
                logger.warning(f"Телефон {referred_phone} уже зарегистрирован как реферал")
                return ref

        # Определяем уровень (для многоуровневой системы)
        level = 1
        parent_id = None

        if REFERRAL_CONFIG["multilevel"]["enabled"]:
            # Ищем, является ли реферер сам рефералом
            for ref in self.storage.referrals.values():
                if ref.referred_phone == rc.phone:
                    level = ref.level + 1
                    parent_id = ref.id
                    break

        # Создаём реферала
        referral = Referral(
            id=str(uuid.uuid4())[:8],
            referrer_phone=rc.phone,
            referrer_code=referral_code,
            referred_phone=referred_phone,
            referred_name=referred_name,
            level=level,
            parent_referral_id=parent_id,
            notes=notes,
        )

        # Обновляем статистику кода
        rc.uses_count += 1

        # Сохраняем
        self.storage.referrals[referral.id] = referral
        self.storage.save_referrals()
        self.storage.save_codes()

        logger.info(f"Зарегистрирован реферал {referred_name} ({referred_phone}) по коду {referral_code}")

        return referral

    def update_status(
        self,
        referred_phone: str,
        status: ReferralStatus,
        amount: float = 0.0,
        booking_id: Optional[str] = None
    ) -> Optional[Referral]:
        """Обновление статуса реферала."""
        # Находим реферала
        referral = None
        for ref in self.storage.referrals.values():
            if ref.referred_phone == referred_phone:
                referral = ref
                break

        if not referral:
            logger.error(f"Реферал с телефоном {referred_phone} не найден")
            return None

        old_status = referral.status
        referral.status = status.value
        referral.last_activity_at = datetime.now().isoformat()

        # Обновляем статистику при бронировании
        if status in [ReferralStatus.BOOKED, ReferralStatus.PAID, ReferralStatus.COMPLETED]:
            if amount > 0:
                referral.total_bookings += 1
                referral.total_amount += amount

                # Обновляем статистику кода
                rc = self.storage.codes.get(referral.referrer_code)
                if rc:
                    rc.total_revenue += amount

            # Время первого бронирования
            if not referral.first_booking_at:
                referral.first_booking_at = datetime.now().isoformat()

        self.storage.save_referrals()
        self.storage.save_codes()

        logger.info(f"Статус реферала {referred_phone} изменён: {old_status} -> {status.value}")

        return referral

    def get_referrals_by_referrer(self, referrer_phone: str) -> List[Referral]:
        """Получить всех рефералов по телефону реферера."""
        return [
            ref for ref in self.storage.referrals.values()
            if ref.referrer_phone == referrer_phone
        ]

    def get_referral_stats(self, referrer_phone: str) -> Dict[str, Any]:
        """Статистика по рефералам."""
        referrals = self.get_referrals_by_referrer(referrer_phone)

        stats = {
            "total_referrals": len(referrals),
            "by_status": {},
            "total_bookings": 0,
            "total_revenue": 0.0,
            "total_bonus": 0.0,
        }

        for ref in referrals:
            # По статусам
            status = ref.status
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Общие показатели
            stats["total_bookings"] += ref.total_bookings
            stats["total_revenue"] += ref.total_amount
            stats["total_bonus"] += ref.total_bonus_generated

        return stats


# ═══════════════════════════════════════════════════════════════════════════
# БОНУСНАЯ СИСТЕМА
# ═══════════════════════════════════════════════════════════════════════════

class BonusManager:
    """Управление бонусами."""

    def __init__(self, storage: ReferralStorage, tracker: ReferralTracker):
        self.storage = storage
        self.tracker = tracker

    def credit_bonus(
        self,
        phone: str,
        amount: float,
        bonus_type: BonusType = BonusType.MANUAL,
        reason: str = "",
        referral_id: Optional[str] = None,
        booking_id: Optional[str] = None
    ) -> BonusTransaction:
        """Начисление бонуса."""
        transaction = BonusTransaction(
            id=str(uuid.uuid4())[:8],
            phone=phone,
            amount=amount,
            currency=REFERRAL_CONFIG["bonus"]["currency"],
            bonus_type=bonus_type.value,
            reason=reason,
            referral_id=referral_id,
            booking_id=booking_id,
        )

        self.storage.bonuses.append(transaction)
        self.storage.save_bonuses()

        # Обновляем статистику кода
        for code, rc in self.storage.codes.items():
            if rc.phone == phone:
                rc.total_bonus += amount
                break
        self.storage.save_codes()

        # Обновляем статистику реферала
        if referral_id and referral_id in self.storage.referrals:
            self.storage.referrals[referral_id].total_bonus_generated += amount
            self.storage.save_referrals()

        logger.info(f"Начислен бонус {amount} {transaction.currency} для {phone}: {reason}")

        return transaction

    def process_booking_bonus(
        self,
        referred_phone: str,
        booking_amount: float,
        booking_id: Optional[str] = None
    ) -> List[BonusTransaction]:
        """Обработка бонуса за бронирование реферала."""
        transactions = []

        # Находим реферала
        referral = None
        for ref in self.storage.referrals.values():
            if ref.referred_phone == referred_phone:
                referral = ref
                break

        if not referral:
            logger.warning(f"Реферал {referred_phone} не найден")
            return transactions

        cfg = REFERRAL_CONFIG["bonus"]

        # Фиксированный бонус за первое бронирование
        if referral.total_bookings == 0 and cfg["fixed_first_booking"] > 0:
            tx = self.credit_bonus(
                phone=referral.referrer_phone,
                amount=cfg["fixed_first_booking"],
                bonus_type=BonusType.FIXED_FIRST_BOOKING,
                reason=f"Бонус за первое бронирование реферала {referral.referred_name}",
                referral_id=referral.id,
                booking_id=booking_id,
            )
            transactions.append(tx)

        # Процент от бронирования
        if cfg["percent"] > 0:
            bonus_amount = booking_amount * cfg["percent"] / 100
            tx = self.credit_bonus(
                phone=referral.referrer_phone,
                amount=round(bonus_amount, 2),
                bonus_type=BonusType.PERCENT,
                reason=f"{cfg['percent']}% от бронирования {booking_amount} AED ({referral.referred_name})",
                referral_id=referral.id,
                booking_id=booking_id,
            )
            transactions.append(tx)

        # Многоуровневые бонусы
        if REFERRAL_CONFIG["multilevel"]["enabled"]:
            transactions.extend(
                self._process_multilevel_bonuses(referral, booking_amount, booking_id)
            )

        return transactions

    def _process_multilevel_bonuses(
        self,
        referral: Referral,
        booking_amount: float,
        booking_id: Optional[str]
    ) -> List[BonusTransaction]:
        """Обработка многоуровневых бонусов."""
        transactions = []
        levels = REFERRAL_CONFIG["multilevel"]["levels"]

        current_ref = referral
        level = 2  # Начинаем со 2-го уровня (1-й уже обработан)

        while current_ref.parent_referral_id and level in levels:
            parent = self.storage.referrals.get(current_ref.parent_referral_id)
            if not parent:
                break

            # Находим телефон родителя-реферера
            parent_referrer_phone = parent.referrer_phone

            # Начисляем бонус
            percent = levels[level]["percent"]
            bonus_amount = booking_amount * percent / 100

            tx = self.credit_bonus(
                phone=parent_referrer_phone,
                amount=round(bonus_amount, 2),
                bonus_type=BonusType.MULTILEVEL,
                reason=f"Многоуровневый бонус (уровень {level}): {percent}% от {booking_amount} AED",
                referral_id=referral.id,
                booking_id=booking_id,
            )
            transactions.append(tx)

            current_ref = parent
            level += 1

        return transactions

    def get_balance(self, phone: str) -> Dict[str, Any]:
        """Получить баланс бонусов."""
        # Все начисления
        total_credited = sum(
            b.amount for b in self.storage.bonuses
            if b.phone == phone
        )

        # Все выплаты (завершённые)
        total_paid = sum(
            p.amount for p in self.storage.payouts
            if p.phone == phone and p.status == PayoutStatus.COMPLETED.value
        )

        # Ожидающие выплаты
        pending_payout = sum(
            p.amount for p in self.storage.payouts
            if p.phone == phone and p.status in [
                PayoutStatus.PENDING.value,
                PayoutStatus.APPROVED.value,
                PayoutStatus.PROCESSING.value
            ]
        )

        available = total_credited - total_paid - pending_payout

        return {
            "phone": phone,
            "total_credited": round(total_credited, 2),
            "total_paid": round(total_paid, 2),
            "pending_payout": round(pending_payout, 2),
            "available": round(available, 2),
            "currency": REFERRAL_CONFIG["bonus"]["currency"],
            "min_payout": REFERRAL_CONFIG["bonus"]["min_payout"],
            "can_request_payout": available >= REFERRAL_CONFIG["bonus"]["min_payout"],
        }

    def get_history(self, phone: str) -> List[BonusTransaction]:
        """История начислений."""
        return [b for b in self.storage.bonuses if b.phone == phone]


# ═══════════════════════════════════════════════════════════════════════════
# ВЫПЛАТЫ
# ═══════════════════════════════════════════════════════════════════════════

class PayoutManager:
    """Управление выплатами."""

    def __init__(self, storage: ReferralStorage, bonus_manager: BonusManager):
        self.storage = storage
        self.bonus_manager = bonus_manager

    def request_payout(
        self,
        phone: str,
        amount: float,
        payment_method: str = "bank_transfer",
        payment_details: Dict[str, Any] = None
    ) -> Tuple[Optional[PayoutRequest], str]:
        """Запрос на выплату."""
        # Проверяем баланс
        balance = self.bonus_manager.get_balance(phone)

        if amount > balance["available"]:
            return None, f"Недостаточно средств. Доступно: {balance['available']} {balance['currency']}"

        min_payout = REFERRAL_CONFIG["bonus"]["min_payout"]
        if amount < min_payout:
            return None, f"Минимальная сумма выплаты: {min_payout} {balance['currency']}"

        # Создаём запрос
        payout = PayoutRequest(
            id=str(uuid.uuid4())[:8],
            phone=phone,
            amount=amount,
            currency=balance["currency"],
            payment_method=payment_method,
            payment_details=payment_details or {},
        )

        self.storage.payouts.append(payout)
        self.storage.save_payouts()

        logger.info(f"Создан запрос на выплату {amount} {payout.currency} для {phone}")

        return payout, "Запрос создан успешно"

    def process_payout(
        self,
        payout_id: str,
        status: PayoutStatus,
        admin_notes: str = ""
    ) -> Optional[PayoutRequest]:
        """Обработка запроса на выплату."""
        for payout in self.storage.payouts:
            if payout.id == payout_id:
                payout.status = status.value
                payout.processed_at = datetime.now().isoformat()
                payout.admin_notes = admin_notes

                self.storage.save_payouts()

                logger.info(f"Выплата {payout_id} обработана: {status.value}")
                return payout

        logger.error(f"Выплата {payout_id} не найдена")
        return None

    def get_pending_payouts(self) -> List[PayoutRequest]:
        """Получить ожидающие выплаты."""
        return [
            p for p in self.storage.payouts
            if p.status in [PayoutStatus.PENDING.value, PayoutStatus.APPROVED.value]
        ]


# ═══════════════════════════════════════════════════════════════════════════
# УВЕДОМЛЕНИЯ
# ═══════════════════════════════════════════════════════════════════════════

class NotificationManager:
    """Управление уведомлениями."""

    def __init__(self, storage: ReferralStorage):
        self.storage = storage
        self.templates = {
            "referral_registered": (
                "Отличные новости! Ваш друг {name} зарегистрировался "
                "по вашему реферальному коду. "
                "Вам будет начислен бонус при первом бронировании."
            ),
            "referral_booked": (
                "Ваш друг {name} забронировал тур! "
                "Сумма бронирования: {amount} AED. "
                "Вам начислен бонус: {bonus} AED."
            ),
            "bonus_credited": (
                "Вам начислен бонус {amount} AED. "
                "Причина: {reason}. "
                "Текущий баланс: {balance} AED."
            ),
            "payout_processed": (
                "Ваш запрос на выплату {amount} AED обработан. "
                "Статус: {status}."
            ),
            "reminder_use_bonus": (
                "У вас есть неиспользованный бонус {amount} AED. "
                "Используйте его при следующем бронировании или запросите выплату!"
            ),
            "share_code": (
                "Поделитесь своим реферальным кодом с друзьями!\n\n"
                "Код: {code}\n"
                "Ссылка: {url}\n\n"
                "За каждого друга, который забронирует тур, "
                "вы получите бонус {bonus_percent}% от суммы!"
            ),
        }

    def format_message(self, template_name: str, **kwargs) -> str:
        """Форматирование сообщения по шаблону."""
        template = self.templates.get(template_name, "")
        return template.format(**kwargs)

    def get_share_message(self, code: str) -> Dict[str, str]:
        """Получить сообщение для отправки друзьям."""
        rc = self.storage.codes.get(code)
        if not rc:
            return {}

        message = self.format_message(
            "share_code",
            code=code,
            url=rc.short_url or f"{REFERRAL_CONFIG['base_url']}/{code}",
            bonus_percent=REFERRAL_CONFIG["bonus"]["percent"],
        )

        return {
            "text": message,
            "qr_code_path": rc.qr_code_path,
        }

    async def send_whatsapp(self, phone: str, message: str) -> bool:
        """Отправка через WhatsApp API."""
        # Интеграция с whatsapp_api.py
        try:
            from whatsapp_api import WhatsAppAPI
            api = WhatsAppAPI()
            return await api.send_message(phone, message)
        except Exception as e:
            logger.error(f"Ошибка отправки WhatsApp: {e}")
            return False

    async def send_telegram(self, chat_id: str, message: str) -> bool:
        """Отправка через Telegram Bot API."""
        try:
            from telegram_bot import send_notification
            return await send_notification(chat_id, message)
        except Exception as e:
            logger.error(f"Ошибка отправки Telegram: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════
# ИНТЕГРАЦИЯ С BITRIX24
# ═══════════════════════════════════════════════════════════════════════════

class Bitrix24Integration:
    """Интеграция с Bitrix24."""

    def __init__(self, storage: ReferralStorage):
        self.storage = storage
        self.base_url = self._build_base_url()

    def _build_base_url(self) -> str:
        """Построение базового URL для API."""
        domain = BITRIX24_CONFIG.get("domain", "")
        user_id = BITRIX24_CONFIG.get("user_id", "")
        webhook_key = BITRIX24_CONFIG.get("webhook_key", "")

        if not all([domain, user_id, webhook_key]):
            return ""

        return f"https://{domain}.bitrix24.ru/rest/{user_id}/{webhook_key}"

    def is_configured(self) -> bool:
        """Проверка настройки интеграции."""
        return bool(self.base_url)

    def _call(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Вызов метода API."""
        if not self.is_configured():
            raise ValueError("Bitrix24 не настроен")

        if not HAS_REQUESTS:
            raise ImportError("requests не установлен")

        url = f"{self.base_url}/{method}"
        response = requests.post(url, json=params or {}, timeout=30)
        response.raise_for_status()
        return response.json()

    def sync_referral_code_to_contact(self, phone: str, code: str) -> Optional[str]:
        """Добавить реферальный код в контакт Bitrix24."""
        if not self.is_configured():
            logger.warning("Bitrix24 не настроен")
            return None

        try:
            # Ищем контакт по телефону
            result = self._call("crm.contact.list", {
                "filter": {"PHONE": phone},
                "select": ["ID", "NAME", "LAST_NAME"]
            })

            contacts = result.get("result", [])
            if not contacts:
                logger.warning(f"Контакт {phone} не найден в Bitrix24")
                return None

            contact_id = contacts[0]["ID"]

            # Обновляем поле referral_code
            self._call("crm.contact.update", {
                "id": contact_id,
                "fields": {
                    "UF_CRM_REFERRAL_CODE": code
                }
            })

            logger.info(f"Реферальный код {code} добавлен в контакт {contact_id}")
            return contact_id

        except Exception as e:
            logger.error(f"Ошибка синхронизации с Bitrix24: {e}")
            return None

    def sync_referral_to_smart_process(self, referral: Referral) -> Optional[str]:
        """Синхронизация реферала в смарт-процесс."""
        if not self.is_configured():
            return None

        try:
            # Получаем ID смарт-процесса "Рефералы"
            types_result = self._call("crm.type.list")
            types = types_result.get("result", {}).get("types", [])

            referral_type = None
            for t in types:
                if t.get("code") == "REFERRALS":
                    referral_type = t
                    break

            if not referral_type:
                logger.warning("Смарт-процесс 'Рефералы' не найден")
                return None

            entity_type_id = referral_type["entityTypeId"]

            # Создаём или обновляем элемент
            if referral.bitrix_id:
                # Обновляем
                self._call(f"crm.item.update", {
                    "entityTypeId": entity_type_id,
                    "id": referral.bitrix_id,
                    "fields": {
                        "ufCrmReferrerPhone": referral.referrer_phone,
                        "ufCrmReferredPhone": referral.referred_phone,
                        "ufCrmReferredName": referral.referred_name,
                        "ufCrmRevenue": referral.total_amount,
                        "ufCrmStatus": referral.status,
                    }
                })
                return referral.bitrix_id
            else:
                # Создаём
                result = self._call(f"crm.item.add", {
                    "entityTypeId": entity_type_id,
                    "fields": {
                        "title": f"Реферал: {referral.referred_name}",
                        "ufCrmReferrerPhone": referral.referrer_phone,
                        "ufCrmReferredPhone": referral.referred_phone,
                        "ufCrmReferredName": referral.referred_name,
                        "ufCrmRevenue": referral.total_amount,
                        "ufCrmStatus": referral.status,
                    }
                })

                item_id = result.get("result", {}).get("item", {}).get("id")
                if item_id:
                    referral.bitrix_id = str(item_id)
                    self.storage.save_referrals()
                    return str(item_id)

        except Exception as e:
            logger.error(f"Ошибка синхронизации реферала с Bitrix24: {e}")

        return None

    def sync_all(self):
        """Полная синхронизация с Bitrix24."""
        if not self.is_configured():
            logger.error("Bitrix24 не настроен")
            return

        # Синхронизируем коды в контакты
        for code, rc in self.storage.codes.items():
            self.sync_referral_code_to_contact(rc.phone, code)

        # Синхронизируем рефералов в смарт-процесс
        for ref in self.storage.referrals.values():
            self.sync_referral_to_smart_process(ref)

        logger.info("Синхронизация с Bitrix24 завершена")


# ═══════════════════════════════════════════════════════════════════════════
# ОТЧЁТЫ
# ═══════════════════════════════════════════════════════════════════════════

class ReportGenerator:
    """Генератор отчётов."""

    def __init__(self, storage: ReferralStorage, bonus_manager: BonusManager):
        self.storage = storage
        self.bonus_manager = bonus_manager

    def generate_summary(self) -> Dict[str, Any]:
        """Общая сводка по реферальной программе."""
        total_codes = len(self.storage.codes)
        active_codes = sum(1 for c in self.storage.codes.values() if c.is_active)

        total_referrals = len(self.storage.referrals)
        referrals_by_status = {}
        total_revenue = 0.0

        for ref in self.storage.referrals.values():
            status = ref.status
            referrals_by_status[status] = referrals_by_status.get(status, 0) + 1
            total_revenue += ref.total_amount

        total_bonuses = sum(b.amount for b in self.storage.bonuses)
        total_payouts = sum(
            p.amount for p in self.storage.payouts
            if p.status == PayoutStatus.COMPLETED.value
        )
        pending_payouts = sum(
            p.amount for p in self.storage.payouts
            if p.status in [PayoutStatus.PENDING.value, PayoutStatus.APPROVED.value]
        )

        return {
            "generated_at": datetime.now().isoformat(),
            "codes": {
                "total": total_codes,
                "active": active_codes,
            },
            "referrals": {
                "total": total_referrals,
                "by_status": referrals_by_status,
            },
            "financials": {
                "total_revenue": round(total_revenue, 2),
                "total_bonuses_credited": round(total_bonuses, 2),
                "total_payouts_completed": round(total_payouts, 2),
                "pending_payouts": round(pending_payouts, 2),
                "currency": REFERRAL_CONFIG["bonus"]["currency"],
            }
        }

    def generate_detailed_report(self, output_path: Optional[Path] = None, format: str = "xlsx") -> Path:
        """Детальный отчёт для бухгалтерии."""
        if not HAS_PANDAS:
            raise ImportError("pandas не установлен. pip install pandas openpyxl")

        # Данные по кодам
        codes_data = []
        for code, rc in self.storage.codes.items():
            codes_data.append({
                "Код": code,
                "Телефон": rc.phone,
                "Имя": rc.name,
                "Создан": rc.created_at,
                "Активен": "Да" if rc.is_active else "Нет",
                "Использований": rc.uses_count,
                "Выручка (AED)": rc.total_revenue,
                "Бонусы (AED)": rc.total_bonus,
            })

        # Данные по рефералам
        referrals_data = []
        for ref in self.storage.referrals.values():
            referrals_data.append({
                "ID": ref.id,
                "Реферер (тел)": ref.referrer_phone,
                "Код": ref.referrer_code,
                "Реферал (тел)": ref.referred_phone,
                "Реферал (имя)": ref.referred_name,
                "Статус": ref.status,
                "Дата регистрации": ref.registered_at,
                "Первое бронирование": ref.first_booking_at or "",
                "Бронирований": ref.total_bookings,
                "Сумма (AED)": ref.total_amount,
                "Бонус начислен (AED)": ref.total_bonus_generated,
                "Уровень": ref.level,
            })

        # Данные по бонусам
        bonuses_data = []
        for b in self.storage.bonuses:
            bonuses_data.append({
                "ID": b.id,
                "Телефон": b.phone,
                "Сумма": b.amount,
                "Валюта": b.currency,
                "Тип": b.bonus_type,
                "Причина": b.reason,
                "ID реферала": b.referral_id or "",
                "ID бронирования": b.booking_id or "",
                "Дата": b.created_at,
            })

        # Данные по выплатам
        payouts_data = []
        for p in self.storage.payouts:
            payouts_data.append({
                "ID": p.id,
                "Телефон": p.phone,
                "Сумма": p.amount,
                "Валюта": p.currency,
                "Статус": p.status,
                "Способ оплаты": p.payment_method,
                "Дата запроса": p.requested_at,
                "Дата обработки": p.processed_at or "",
                "Примечания": p.admin_notes,
            })

        # Создаём DataFrame'ы
        df_codes = pd.DataFrame(codes_data)
        df_referrals = pd.DataFrame(referrals_data)
        df_bonuses = pd.DataFrame(bonuses_data)
        df_payouts = pd.DataFrame(payouts_data)

        # Определяем путь
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = ANALYTICS_DIR / f"referral_report_{timestamp}.{format}"

        # Сохраняем
        if format == "xlsx":
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Сводка
                summary = self.generate_summary()
                df_summary = pd.DataFrame([
                    {"Показатель": "Всего кодов", "Значение": summary["codes"]["total"]},
                    {"Показатель": "Активных кодов", "Значение": summary["codes"]["active"]},
                    {"Показатель": "Всего рефералов", "Значение": summary["referrals"]["total"]},
                    {"Показатель": "Общая выручка (AED)", "Значение": summary["financials"]["total_revenue"]},
                    {"Показатель": "Начислено бонусов (AED)", "Значение": summary["financials"]["total_bonuses_credited"]},
                    {"Показатель": "Выплачено (AED)", "Значение": summary["financials"]["total_payouts_completed"]},
                    {"Показатель": "Ожидает выплаты (AED)", "Значение": summary["financials"]["pending_payouts"]},
                ])
                df_summary.to_excel(writer, sheet_name="Сводка", index=False)

                if not df_codes.empty:
                    df_codes.to_excel(writer, sheet_name="Коды", index=False)
                if not df_referrals.empty:
                    df_referrals.to_excel(writer, sheet_name="Рефералы", index=False)
                if not df_bonuses.empty:
                    df_bonuses.to_excel(writer, sheet_name="Бонусы", index=False)
                if not df_payouts.empty:
                    df_payouts.to_excel(writer, sheet_name="Выплаты", index=False)

        elif format == "csv":
            # Сохраняем как отдельные CSV
            base = output_path.stem
            parent = output_path.parent

            if not df_codes.empty:
                df_codes.to_csv(parent / f"{base}_codes.csv", index=False, encoding='utf-8-sig')
            if not df_referrals.empty:
                df_referrals.to_csv(parent / f"{base}_referrals.csv", index=False, encoding='utf-8-sig')
            if not df_bonuses.empty:
                df_bonuses.to_csv(parent / f"{base}_bonuses.csv", index=False, encoding='utf-8-sig')
            if not df_payouts.empty:
                df_payouts.to_csv(parent / f"{base}_payouts.csv", index=False, encoding='utf-8-sig')

        elif format == "json":
            report = {
                "summary": self.generate_summary(),
                "codes": codes_data,
                "referrals": referrals_data,
                "bonuses": bonuses_data,
                "payouts": payouts_data,
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"Отчёт сохранён: {output_path}")
        return output_path


# ═══════════════════════════════════════════════════════════════════════════
# ГЛАВНЫЙ КЛАСС
# ═══════════════════════════════════════════════════════════════════════════

class ReferralProgram:
    """Главный класс реферальной программы."""

    def __init__(self):
        self.storage = ReferralStorage()
        self.code_generator = ReferralCodeGenerator(self.storage)
        self.tracker = ReferralTracker(self.storage)
        self.bonus_manager = BonusManager(self.storage, self.tracker)
        self.payout_manager = PayoutManager(self.storage, self.bonus_manager)
        self.notifications = NotificationManager(self.storage)
        self.bitrix = Bitrix24Integration(self.storage)
        self.reports = ReportGenerator(self.storage, self.bonus_manager)

    def generate_code(self, phone: str, name: str) -> ReferralCode:
        """Генерация реферального кода."""
        return self.code_generator.generate_code(phone, name)

    def register_referral(
        self,
        code: str,
        referred_phone: str,
        referred_name: str = ""
    ) -> Optional[Referral]:
        """Регистрация реферала."""
        referral = self.tracker.register_referral(code, referred_phone, referred_name)

        if referral:
            # Начисляем бонус за регистрацию (если настроен)
            if REFERRAL_CONFIG["bonus"]["fixed_registration"] > 0:
                self.bonus_manager.credit_bonus(
                    phone=referral.referrer_phone,
                    amount=REFERRAL_CONFIG["bonus"]["fixed_registration"],
                    bonus_type=BonusType.FIXED_REGISTRATION,
                    reason=f"Бонус за регистрацию реферала {referred_name or referred_phone}",
                    referral_id=referral.id,
                )

        return referral

    def process_booking(
        self,
        referred_phone: str,
        amount: float,
        booking_id: Optional[str] = None
    ) -> List[BonusTransaction]:
        """Обработка бронирования реферала."""
        # Обновляем статус
        self.tracker.update_status(
            referred_phone=referred_phone,
            status=ReferralStatus.BOOKED,
            amount=amount,
            booking_id=booking_id,
        )

        # Начисляем бонусы
        return self.bonus_manager.process_booking_bonus(
            referred_phone=referred_phone,
            booking_amount=amount,
            booking_id=booking_id,
        )

    def get_balance(self, phone: str) -> Dict[str, Any]:
        """Получить баланс."""
        return self.bonus_manager.get_balance(phone)

    def request_payout(
        self,
        phone: str,
        amount: float,
        payment_method: str = "bank_transfer",
        payment_details: Dict[str, Any] = None
    ) -> Tuple[Optional[PayoutRequest], str]:
        """Запрос на выплату."""
        return self.payout_manager.request_payout(
            phone, amount, payment_method, payment_details
        )

    def get_share_message(self, code: str) -> Dict[str, str]:
        """Получить сообщение для отправки друзьям."""
        return self.notifications.get_share_message(code)

    def generate_report(
        self,
        output_path: Optional[Path] = None,
        format: str = "xlsx"
    ) -> Path:
        """Сгенерировать отчёт."""
        return self.reports.generate_detailed_report(output_path, format)

    def sync_bitrix(self):
        """Синхронизация с Bitrix24."""
        self.bitrix.sync_all()


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Реферальная программа с бонусами",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Генерация кода
  python referral_program.py --generate --phone +971501234567 --name "Иван"

  # Регистрация реферала
  python referral_program.py --register --code REF-ABC123 --referred-phone +971507654321

  # Обновление статуса
  python referral_program.py --update-status --referred-phone +971507654321 --status booked --amount 5000

  # Баланс
  python referral_program.py --balance --phone +971501234567

  # Отчёт
  python referral_program.py --report --format xlsx
        """
    )

    # Основные команды
    parser.add_argument("--generate", action="store_true", help="Генерация реферального кода")
    parser.add_argument("--register", action="store_true", help="Регистрация реферала")
    parser.add_argument("--update-status", action="store_true", help="Обновление статуса реферала")
    parser.add_argument("--credit-bonus", action="store_true", help="Начисление бонуса вручную")
    parser.add_argument("--request-payout", action="store_true", help="Запрос на выплату")
    parser.add_argument("--balance", action="store_true", help="Показать баланс")
    parser.add_argument("--history", action="store_true", help="История начислений")
    parser.add_argument("--report", action="store_true", help="Сгенерировать отчёт")
    parser.add_argument("--sync-bitrix", action="store_true", help="Синхронизация с Bitrix24")
    parser.add_argument("--summary", action="store_true", help="Показать сводку")

    # Параметры
    parser.add_argument("--phone", help="Номер телефона")
    parser.add_argument("--name", default="", help="Имя")
    parser.add_argument("--code", help="Реферальный код")
    parser.add_argument("--referred-phone", help="Телефон реферала")
    parser.add_argument("--referred-name", default="", help="Имя реферала")
    parser.add_argument("--status", choices=["registered", "booked", "paid", "completed"], help="Статус")
    parser.add_argument("--amount", type=float, default=0, help="Сумма")
    parser.add_argument("--reason", default="", help="Причина (для ручного бонуса)")
    parser.add_argument("--format", choices=["xlsx", "csv", "json"], default="xlsx", help="Формат отчёта")
    parser.add_argument("--output", help="Путь к выходному файлу")

    args = parser.parse_args()

    # Создаём программу
    program = ReferralProgram()

    try:
        if args.generate:
            if not args.phone:
                print("Ошибка: укажите --phone")
                return

            code = program.generate_code(args.phone, args.name)
            print(f"\nРеферальный код создан:")
            print(f"  Код: {code.code}")
            print(f"  Ссылка: {code.short_url}")
            print(f"  QR-код: {code.qr_code_path}")

            # Сообщение для отправки
            msg = program.get_share_message(code.code)
            print(f"\nСообщение для друзей:\n{msg['text']}")

        elif args.register:
            if not args.code or not args.referred_phone:
                print("Ошибка: укажите --code и --referred-phone")
                return

            referral = program.register_referral(
                args.code,
                args.referred_phone,
                args.referred_name
            )

            if referral:
                print(f"\nРеферал зарегистрирован:")
                print(f"  ID: {referral.id}")
                print(f"  Телефон: {referral.referred_phone}")
                print(f"  Имя: {referral.referred_name}")
                print(f"  Реферер: {referral.referrer_phone}")
            else:
                print("Ошибка регистрации реферала")

        elif args.update_status:
            if not args.referred_phone or not args.status:
                print("Ошибка: укажите --referred-phone и --status")
                return

            status_map = {
                "registered": ReferralStatus.REGISTERED,
                "booked": ReferralStatus.BOOKED,
                "paid": ReferralStatus.PAID,
                "completed": ReferralStatus.COMPLETED,
            }

            referral = program.tracker.update_status(
                referred_phone=args.referred_phone,
                status=status_map[args.status],
                amount=args.amount,
            )

            if referral:
                print(f"\nСтатус обновлён: {referral.status}")

                # Если бронирование - начисляем бонусы
                if args.status in ["booked", "paid"] and args.amount > 0:
                    bonuses = program.bonus_manager.process_booking_bonus(
                        args.referred_phone, args.amount
                    )
                    for b in bonuses:
                        print(f"  Начислен бонус: {b.amount} {b.currency}")
            else:
                print("Реферал не найден")

        elif args.credit_bonus:
            if not args.phone or not args.amount:
                print("Ошибка: укажите --phone и --amount")
                return

            tx = program.bonus_manager.credit_bonus(
                phone=args.phone,
                amount=args.amount,
                bonus_type=BonusType.MANUAL,
                reason=args.reason or "Ручное начисление",
            )

            print(f"\nБонус начислен:")
            print(f"  ID: {tx.id}")
            print(f"  Сумма: {tx.amount} {tx.currency}")
            print(f"  Причина: {tx.reason}")

        elif args.request_payout:
            if not args.phone or not args.amount:
                print("Ошибка: укажите --phone и --amount")
                return

            payout, message = program.request_payout(args.phone, args.amount)

            if payout:
                print(f"\nЗапрос на выплату создан:")
                print(f"  ID: {payout.id}")
                print(f"  Сумма: {payout.amount} {payout.currency}")
                print(f"  Статус: {payout.status}")
            else:
                print(f"Ошибка: {message}")

        elif args.balance:
            if not args.phone:
                print("Ошибка: укажите --phone")
                return

            balance = program.get_balance(args.phone)

            print(f"\nБаланс для {args.phone}:")
            print(f"  Начислено: {balance['total_credited']} {balance['currency']}")
            print(f"  Выплачено: {balance['total_paid']} {balance['currency']}")
            print(f"  Ожидает выплаты: {balance['pending_payout']} {balance['currency']}")
            print(f"  Доступно: {balance['available']} {balance['currency']}")
            print(f"  Можно запросить выплату: {'Да' if balance['can_request_payout'] else 'Нет'}")

        elif args.history:
            if not args.phone:
                print("Ошибка: укажите --phone")
                return

            history = program.bonus_manager.get_history(args.phone)

            print(f"\nИстория начислений для {args.phone}:")
            for b in history:
                print(f"  [{b.created_at[:10]}] {b.amount} {b.currency} - {b.reason}")

        elif args.report:
            output_path = Path(args.output) if args.output else None
            path = program.generate_report(output_path, args.format)
            print(f"\nОтчёт сохранён: {path}")

        elif args.sync_bitrix:
            program.sync_bitrix()
            print("Синхронизация с Bitrix24 завершена")

        elif args.summary:
            summary = program.reports.generate_summary()

            print("\n" + "=" * 50)
            print("СВОДКА ПО РЕФЕРАЛЬНОЙ ПРОГРАММЕ")
            print("=" * 50)
            print(f"\nКоды:")
            print(f"  Всего: {summary['codes']['total']}")
            print(f"  Активных: {summary['codes']['active']}")

            print(f"\nРефералы:")
            print(f"  Всего: {summary['referrals']['total']}")
            for status, count in summary['referrals']['by_status'].items():
                print(f"    {status}: {count}")

            print(f"\nФинансы:")
            print(f"  Общая выручка: {summary['financials']['total_revenue']} {summary['financials']['currency']}")
            print(f"  Начислено бонусов: {summary['financials']['total_bonuses_credited']} {summary['financials']['currency']}")
            print(f"  Выплачено: {summary['financials']['total_payouts_completed']} {summary['financials']['currency']}")
            print(f"  Ожидает выплаты: {summary['financials']['pending_payouts']} {summary['financials']['currency']}")

        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise


if __name__ == "__main__":
    main()
