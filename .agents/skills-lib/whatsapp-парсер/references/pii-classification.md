# Классификация персональных данных (PII)

Справочник по обнаружению, классификации и защите персональных данных при парсинге WhatsApp чатов.

## Зачем это нужно

### Законодательные требования

1. **GDPR** (General Data Protection Regulation):
   - Требует согласия на обработку персональных данных
   - Права субъектов: доступ, исправление, удаление, переносимость
   - Обязательное уведомление о утечках в течение 72 часов

2. **Законодательство ОАЭ**:
   - Federal Decree-Law No. 45/2021 о защите данных
   - Особые требования к хранению данных граждан ОАЭ

3. **PCI DSS** (для платежных данных):
   - Запрет хранения CVV/CVC
   - Шифрование номеров карт
   - Маскирование при отображении

### Бизнес-риски

- Штрафы до 4% годового оборота (GDPR)
- Репутационный ущерб при утечках
- Потеря доверия клиентов

---

## Уровни чувствительности

```python
class SensitivityLevel(Enum):
    """Уровни чувствительности данных"""
    PUBLIC = 1          # Публичная информация
    INTERNAL = 2        # Внутренняя информация
    CONFIDENTIAL = 3    # Конфиденциальная
    RESTRICTED = 4      # Ограниченный доступ
    CRITICAL = 5        # Критическая (PII, финансы)
```

### Описание уровней

| Уровень | Описание | Примеры | Требования |
|---------|----------|---------|------------|
| **PUBLIC** | Публичная информация | Название компании, общие цены | Без ограничений |
| **INTERNAL** | Внутренняя информация | Внутренние процедуры, графики работы | Только для сотрудников |
| **CONFIDENTIAL** | Конфиденциальная | Имена клиентов, телефоны, email | Согласие клиента, маскирование |
| **RESTRICTED** | Ограниченный доступ | Даты рождения, адреса, фото документов | Шифрование, ограниченный доступ |
| **CRITICAL** | Критическая | Паспорта, карты, медданные | Шифрование, минимальный срок хранения, аудит |

---

## Классификация данных

### Категории данных туристического бизнеса ОАЭ

```
Чувствительные данные:
├── Персональные идентификаторы
│   ├── Номера паспортов
│   ├── Номера виз
│   ├── Номера Emirates ID
│   └── Национальные ID других стран
├── Финансовые данные
│   ├── Номера банковских карт
│   ├── IBAN / номера счетов
│   ├── Данные о платежах
│   └── CVV/CVC коды
├── Контактные данные
│   ├── Телефонные номера
│   ├── Email адреса
│   ├── Физические адреса
│   └── Данные соцсетей
├── Биометрия
│   ├── Фото документов
│   ├── Фото лиц
│   └── Отпечатки (редко)
└── Чувствительная информация
    ├── Даты рождения
    ├── Медицинские данные
    ├── Религиозные предпочтения
    └── Информация о детях
```

### Таблица DATA_CLASSIFICATIONS

```python
from enum import Enum
from dataclasses import dataclass

class DataCategory(Enum):
    """Категории данных"""
    PASSPORT = 'passport'
    VISA = 'visa'
    EMIRATES_ID = 'emirates_id'
    CREDIT_CARD = 'credit_card'
    BANK_ACCOUNT = 'bank_account'
    PHONE = 'phone'
    EMAIL = 'email'
    ADDRESS = 'address'
    DATE_OF_BIRTH = 'date_of_birth'
    PHOTO = 'photo'
    MEDICAL = 'medical'
    FINANCIAL_TRANSACTION = 'financial_transaction'
    PERSONAL_NAME = 'personal_name'

@dataclass
class DataClassification:
    """Классификация данных"""
    category: DataCategory
    sensitivity: SensitivityLevel
    retention_days: int          # Сколько дней хранить
    requires_consent: bool       # Требуется согласие
    requires_encryption: bool    # Требуется шифрование
    can_export: bool             # Можно экспортировать
    gdpr_relevant: bool          # Попадает под GDPR

# Таблица классификации
DATA_CLASSIFICATIONS = {
    DataCategory.PASSPORT: DataClassification(
        category=DataCategory.PASSPORT,
        sensitivity=SensitivityLevel.CRITICAL,
        retention_days=90,
        requires_consent=True,
        requires_encryption=True,
        can_export=False,
        gdpr_relevant=True
    ),
    DataCategory.VISA: DataClassification(
        category=DataCategory.VISA,
        sensitivity=SensitivityLevel.CRITICAL,
        retention_days=90,
        requires_consent=True,
        requires_encryption=True,
        can_export=False,
        gdpr_relevant=True
    ),
    DataCategory.EMIRATES_ID: DataClassification(
        category=DataCategory.EMIRATES_ID,
        sensitivity=SensitivityLevel.CRITICAL,
        retention_days=90,
        requires_consent=True,
        requires_encryption=True,
        can_export=False,
        gdpr_relevant=True
    ),
    DataCategory.CREDIT_CARD: DataClassification(
        category=DataCategory.CREDIT_CARD,
        sensitivity=SensitivityLevel.CRITICAL,
        retention_days=0,  # НЕ ХРАНИТЬ!
        requires_consent=True,
        requires_encryption=True,
        can_export=False,
        gdpr_relevant=True
    ),
    DataCategory.BANK_ACCOUNT: DataClassification(
        category=DataCategory.BANK_ACCOUNT,
        sensitivity=SensitivityLevel.CRITICAL,
        retention_days=365,
        requires_consent=True,
        requires_encryption=True,
        can_export=False,
        gdpr_relevant=True
    ),
    DataCategory.PHONE: DataClassification(
        category=DataCategory.PHONE,
        sensitivity=SensitivityLevel.CONFIDENTIAL,
        retention_days=365,
        requires_consent=True,
        requires_encryption=False,
        can_export=True,
        gdpr_relevant=True
    ),
    DataCategory.EMAIL: DataClassification(
        category=DataCategory.EMAIL,
        sensitivity=SensitivityLevel.CONFIDENTIAL,
        retention_days=365,
        requires_consent=True,
        requires_encryption=False,
        can_export=True,
        gdpr_relevant=True
    ),
    DataCategory.ADDRESS: DataClassification(
        category=DataCategory.ADDRESS,
        sensitivity=SensitivityLevel.CONFIDENTIAL,
        retention_days=365,
        requires_consent=True,
        requires_encryption=False,
        can_export=True,
        gdpr_relevant=True
    ),
    DataCategory.DATE_OF_BIRTH: DataClassification(
        category=DataCategory.DATE_OF_BIRTH,
        sensitivity=SensitivityLevel.RESTRICTED,
        retention_days=365,
        requires_consent=True,
        requires_encryption=True,
        can_export=True,
        gdpr_relevant=True
    ),
    DataCategory.PERSONAL_NAME: DataClassification(
        category=DataCategory.PERSONAL_NAME,
        sensitivity=SensitivityLevel.CONFIDENTIAL,
        retention_days=730,
        requires_consent=True,
        requires_encryption=False,
        can_export=True,
        gdpr_relevant=True
    ),
    DataCategory.PHOTO: DataClassification(
        category=DataCategory.PHOTO,
        sensitivity=SensitivityLevel.RESTRICTED,
        retention_days=180,
        requires_consent=True,
        requires_encryption=True,
        can_export=False,
        gdpr_relevant=True
    ),
    DataCategory.MEDICAL: DataClassification(
        category=DataCategory.MEDICAL,
        sensitivity=SensitivityLevel.CRITICAL,
        retention_days=365,
        requires_consent=True,
        requires_encryption=True,
        can_export=False,
        gdpr_relevant=True
    ),
    DataCategory.FINANCIAL_TRANSACTION: DataClassification(
        category=DataCategory.FINANCIAL_TRANSACTION,
        sensitivity=SensitivityLevel.RESTRICTED,
        retention_days=2555,  # 7 лет для финансовой отчетности
        requires_consent=False,  # Законные основания
        requires_encryption=True,
        can_export=False,
        gdpr_relevant=False
    ),
}
```

### Сводная таблица

| Категория | Уровень | Хранение (дни) | Согласие | Шифрование | Экспорт |
|-----------|---------|----------------|----------|------------|---------|
| Паспорт | CRITICAL | 90 | Да | Да | Нет |
| Виза | CRITICAL | 90 | Да | Да | Нет |
| Emirates ID | CRITICAL | 90 | Да | Да | Нет |
| Карта | CRITICAL | 0 | Да | Да | Нет |
| Банк. счет | CRITICAL | 365 | Да | Да | Нет |
| Телефон | CONFIDENTIAL | 365 | Да | Нет | Да |
| Email | CONFIDENTIAL | 365 | Да | Нет | Да |
| Адрес | CONFIDENTIAL | 365 | Да | Нет | Да |
| Дата рождения | RESTRICTED | 365 | Да | Да | Да |
| Имя | CONFIDENTIAL | 730 | Да | Нет | Да |
| Фото | RESTRICTED | 180 | Да | Да | Нет |
| Мед. данные | CRITICAL | 365 | Да | Да | Нет |

---

## Regex паттерны PII

### Документы

```python
import re

class PIIPatterns:
    """Паттерны для обнаружения PII"""

    # === ДОКУМЕНТЫ ===

    # Паспорт (различные форматы)
    PASSPORT_PATTERN = re.compile(
        r'\b[A-Z]{1,2}\d{6,9}\b|'  # Стандартный формат (AB1234567)
        r'\b\d{2}\s*\d{7}\b|'       # Российский паспорт (серия номер)
        r'\b\d{9}\b',               # Только цифры
        re.IGNORECASE
    )

    # Российский паспорт (серия и номер)
    RUSSIAN_PASSPORT_PATTERN = re.compile(
        r'\b(\d{2})\s*(\d{2})\s*(\d{6})\b|'  # 00 00 000000
        r'\bсерия\s*(\d{2}\s*\d{2})\s*(?:номер|№)?\s*(\d{6})\b',
        re.IGNORECASE
    )

    # Emirates ID
    EMIRATES_ID_PATTERN = re.compile(
        r'\b784-?\d{4}-?\d{7}-?\d\b|'  # 784-XXXX-XXXXXXX-X
        r'\b784\d{12}\b'               # 784XXXXXXXXXXXXX
    )

    # Номер визы ОАЭ
    VISA_PATTERN = re.compile(
        r'\b[A-Z]{2,3}/?\d{4,}/?\d{4,}\b|'  # XX/XXXX/XXXX
        r'\b\d{3}/\d{4}/\d{7}\b'            # XXX/XXXX/XXXXXXX
    )
```

### Банковские данные

```python
    # === БАНКОВСКИЕ ДАННЫЕ ===

    # Номер банковской карты (все форматы)
    CREDIT_CARD_PATTERN = re.compile(
        r'\b(?:\d{4}[-\s]?){3}\d{4}\b|'  # 4111-1111-1111-1111
        r'\b\d{16}\b'                     # 4111111111111111
    )

    # IBAN
    IBAN_PATTERN = re.compile(
        r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]{0,16})?\b'
    )

    # CVV/CVC
    CVV_PATTERN = re.compile(
        r'\b(?:CVV|CVC|CSC|CVV2)\s*[:\s]*(\d{3,4})\b|'
        r'\b(?<=\s)\d{3}(?=\s|$)\b',  # 3 цифры отдельно
        re.IGNORECASE
    )

    # Номер счета (общий)
    BANK_ACCOUNT_PATTERN = re.compile(
        r'\b\d{10,20}\b'  # 10-20 цифр подряд
    )

    # Российский номер счета
    RUSSIAN_BANK_ACCOUNT_PATTERN = re.compile(
        r'\b\d{20}\b'  # 20 цифр
    )
```

### Контактные данные

```python
    # === КОНТАКТЫ ===

    # Телефон ОАЭ
    UAE_PHONE_PATTERN = re.compile(
        r'\b(?:\+971|00971|971)?[-\s]?'
        r'(?:50|52|54|55|56|58|2|3|4|6|7|9)[-\s]?'
        r'\d{3}[-\s]?\d{4}\b'
    )

    # Телефон Россия
    RUSSIAN_PHONE_PATTERN = re.compile(
        r'\b(?:\+7|8|7)?[-\s]?'
        r'(?:\(?\d{3}\)?[-\s]?)?'
        r'\d{3}[-\s]?\d{2}[-\s]?\d{2}\b'
    )

    # Международный телефон
    INTERNATIONAL_PHONE_PATTERN = re.compile(
        r'\+\d{1,3}[-\s]?\d{2,4}[-\s]?\d{3,4}[-\s]?\d{3,4}\b'
    )

    # Email
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
```

### Даты и адреса

```python
    # === ДАТЫ ===

    # Дата рождения (с контекстом)
    DATE_OF_BIRTH_PATTERN = re.compile(
        r'\b(?:DOB|Date\s*of\s*Birth|Дата\s*рождения|ДР)\s*[:\s]*'
        r'(\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4})\b',
        re.IGNORECASE
    )

    # Общий формат даты
    DATE_GENERAL_PATTERN = re.compile(
        r'\b(\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4})\b'
    )

    # === АДРЕСА ===

    # Адрес с номером дома
    ADDRESS_PATTERN = re.compile(
        r'\b(?:ул\.|улица|street|st\.|avenue|ave\.|road|rd\.)\s*'
        r'[А-Яа-яA-Za-z\s]+,?\s*(?:д\.|дом|house|bldg\.?)\s*\d+',
        re.IGNORECASE
    )

    # Почтовый индекс
    POSTAL_CODE_PATTERN = re.compile(
        r'\b\d{5,6}\b|'                    # Общий (5-6 цифр)
        r'\b[A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2}\b'  # UK формат
    )
```

### Примеры использования

```python
# Проверка текста на PII
def detect_pii(text: str) -> list:
    """Обнаружение PII в тексте"""
    results = []

    patterns = [
        ('passport', PIIPatterns.PASSPORT_PATTERN),
        ('emirates_id', PIIPatterns.EMIRATES_ID_PATTERN),
        ('credit_card', PIIPatterns.CREDIT_CARD_PATTERN),
        ('phone_uae', PIIPatterns.UAE_PHONE_PATTERN),
        ('email', PIIPatterns.EMAIL_PATTERN),
    ]

    for name, pattern in patterns:
        for match in pattern.finditer(text):
            results.append({
                'type': name,
                'value': match.group(),
                'position': (match.start(), match.end())
            })

    return results

# Пример
text = "Клиент: Иван, паспорт AB1234567, тел +971 50 123 4567"
pii = detect_pii(text)
# [{'type': 'passport', 'value': 'AB1234567', ...},
#  {'type': 'phone_uae', 'value': '+971 50 123 4567', ...}]
```

---

## Маскирование данных

### Стратегии маскирования

```python
from enum import Enum

class MaskingStrategy(Enum):
    """Стратегии маскирования"""
    FULL = 'full'           # Полное скрытие: **********
    PARTIAL = 'partial'     # Частичное: 4111****1234
    HASH = 'hash'           # Хэширование: HASH:a1b2c3...
    TOKENIZE = 'tokenize'   # Токенизация: TOK:abc123
    REDACT = 'redact'       # Удаление: [REDACTED]
    ENCRYPT = 'encrypt'     # Шифрование: ENC:...
```

### Класс PIIMasker

```python
from dataclasses import dataclass
from typing import Dict, Optional
import hashlib
import secrets

@dataclass
class MaskingRule:
    """Правило маскирования"""
    category: DataCategory
    strategy: MaskingStrategy
    keep_first: int = 0      # Сколько символов показывать в начале
    keep_last: int = 0       # Сколько символов показывать в конце
    replacement_char: str = '*'
    preserve_format: bool = True  # Сохранять пробелы и дефисы

class PIIMasker:
    """Маскирование PII данных"""

    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key
        self.token_vault: Dict[str, str] = {}  # token -> original

        # Правила по умолчанию
        self.rules: Dict[DataCategory, MaskingRule] = {
            DataCategory.CREDIT_CARD: MaskingRule(
                category=DataCategory.CREDIT_CARD,
                strategy=MaskingStrategy.PARTIAL,
                keep_first=4,
                keep_last=4
            ),
            DataCategory.PASSPORT: MaskingRule(
                category=DataCategory.PASSPORT,
                strategy=MaskingStrategy.PARTIAL,
                keep_first=2,
                keep_last=2
            ),
            DataCategory.PHONE: MaskingRule(
                category=DataCategory.PHONE,
                strategy=MaskingStrategy.PARTIAL,
                keep_first=4,
                keep_last=2
            ),
            DataCategory.EMAIL: MaskingRule(
                category=DataCategory.EMAIL,
                strategy=MaskingStrategy.PARTIAL,
                keep_first=2,
                keep_last=0,  # Показываем домен
                preserve_format=True
            ),
            DataCategory.BANK_ACCOUNT: MaskingRule(
                category=DataCategory.BANK_ACCOUNT,
                strategy=MaskingStrategy.PARTIAL,
                keep_first=2,
                keep_last=4
            ),
            DataCategory.EMIRATES_ID: MaskingRule(
                category=DataCategory.EMIRATES_ID,
                strategy=MaskingStrategy.PARTIAL,
                keep_first=3,
                keep_last=1
            ),
            DataCategory.DATE_OF_BIRTH: MaskingRule(
                category=DataCategory.DATE_OF_BIRTH,
                strategy=MaskingStrategy.FULL
            ),
        }

    def mask(self, value: str, category: DataCategory) -> str:
        """Маскирование значения"""
        rule = self.rules.get(category)
        if not rule:
            return self._full_mask(value)

        maskers = {
            MaskingStrategy.FULL: self._full_mask,
            MaskingStrategy.PARTIAL: lambda v: self._partial_mask(v, rule),
            MaskingStrategy.HASH: self._hash_mask,
            MaskingStrategy.TOKENIZE: self._tokenize,
            MaskingStrategy.REDACT: lambda v: '[REDACTED]',
        }

        masker = maskers.get(rule.strategy, self._full_mask)
        return masker(value)

    def _full_mask(self, value: str) -> str:
        """Полное маскирование"""
        return '*' * len(value)

    def _partial_mask(self, value: str, rule: MaskingRule) -> str:
        """Частичное маскирование"""
        if len(value) <= rule.keep_first + rule.keep_last:
            return self._full_mask(value)

        # Специальная обработка для email
        if rule.category == DataCategory.EMAIL and '@' in value:
            return self._mask_email(value, rule)

        prefix = value[:rule.keep_first]
        suffix = value[-rule.keep_last:] if rule.keep_last > 0 else ''
        middle_len = len(value) - rule.keep_first - rule.keep_last

        if rule.preserve_format:
            # Сохраняем пробелы и дефисы
            middle = value[rule.keep_first:len(value) - rule.keep_last if rule.keep_last else len(value)]
            masked_middle = ''.join(
                c if c in ' -' else rule.replacement_char
                for c in middle
            )
        else:
            masked_middle = rule.replacement_char * middle_len

        return prefix + masked_middle + suffix

    def _mask_email(self, value: str, rule: MaskingRule) -> str:
        """Маскирование email с сохранением домена"""
        parts = value.split('@')
        if len(parts) != 2:
            return self._full_mask(value)

        local, domain = parts
        if len(local) <= rule.keep_first:
            masked_local = local
        else:
            masked_local = local[:rule.keep_first] + '*' * (len(local) - rule.keep_first)

        return f'{masked_local}@{domain}'

    def _hash_mask(self, value: str) -> str:
        """Хэширование значения"""
        hash_obj = hashlib.sha256(value.encode())
        return f'HASH:{hash_obj.hexdigest()[:16]}'

    def _tokenize(self, value: str) -> str:
        """Токенизация с сохранением в vault"""
        # Проверяем, есть ли уже токен
        for token, original in self.token_vault.items():
            if original == value:
                return token

        # Создаем новый токен
        token = f'TOK:{secrets.token_hex(8)}'
        self.token_vault[token] = value

        return token

    def detokenize(self, token: str) -> Optional[str]:
        """Восстановление из токена"""
        return self.token_vault.get(token)
```

### Примеры результатов маскирования

| Категория | Оригинал | Замаскировано |
|-----------|----------|---------------|
| Паспорт | AB1234567 | AB*****67 |
| Карта | 4111 1111 1111 1234 | 4111 **** **** 1234 |
| Телефон | +971 50 123 4567 | +971******67 |
| Email | ivan.petrov@gmail.com | iv**********@gmail.com |
| IBAN | AE070331234567890123456 | AE********************56 |
| Emirates ID | 784-1234-5678901-2 | 784-**********-2 |
| Дата рождения | 15.03.1985 | ********** |

---

## Безопасная обработка данных

### Класс SecureDataPipeline

Полный pipeline для безопасной обработки сообщений с PII:

```python
class SecureDataPipeline:
    """Безопасный pipeline обработки данных"""

    def __init__(
        self,
        encryption_service,
        pii_masker: PIIMasker,
        audit_logger,
        rbac_service
    ):
        self.encryption = encryption_service
        self.masker = pii_masker
        self.audit = audit_logger
        self.rbac = rbac_service

    async def process_message(
        self,
        message: Dict,
        user,
        request_context: Dict
    ) -> Dict:
        """Безопасная обработка сообщения"""

        # 1. Проверка доступа
        if not self.rbac.check_permission(user, Permission.CUSTOMER_VIEW):
            self.audit.log(
                user_id=user.user_id,
                action=AuditAction.ACCESS_DENIED,
                resource_type='message',
                resource_id=message.get('id'),
                success=False
            )
            raise PermissionError("Access denied")

        # 2. Определяем уровень маскирования по роли
        access_level = self.rbac.get_user_access_level(user)
        masking_context = MaskingContext(
            user_role=access_level,
            purpose='display',
            customer_consent=False,
            is_own_data=False
        )

        # 3. Обнаруживаем PII
        detector = PIIDetector()
        pii_matches = detector.detect(message.get('text', ''))

        # 4. Маскируем в зависимости от уровня доступа
        contextual_masker = ContextualMasker(self.masker)
        masked_text = contextual_masker.mask_text_for_context(
            message.get('text', ''),
            masking_context
        )

        # 5. Логируем доступ
        self.audit.log(
            user_id=user.user_id,
            action=AuditAction.VIEW,
            resource_type='message',
            resource_id=message.get('id'),
            data_categories=[m.category for m in pii_matches],
            success=True
        )

        # 6. Возвращаем безопасные данные
        return {
            'id': message.get('id'),
            'text': masked_text,
            'timestamp': message.get('timestamp'),
            'sender': message.get('sender'),
            'pii_detected': len(pii_matches) > 0,
            'masking_applied': access_level != AccessLevel.ADMIN
        }
```

### Пример использования

```python
# Инициализация
masker = PIIMasker()

# Тестовое сообщение
message = {
    'id': 'msg_001',
    'text': 'Мой паспорт AB1234567, телефон +971 50 123 4567',
    'timestamp': '2025-01-28T12:00:00',
    'sender': '+971501234567'
}

# Обработка для агента
result = await pipeline.process_message(message, agent_user, context)
print(result['text'])
# Выведет: Мой паспорт AB*****67, телефон +971******67
```

---

## Политики доступа (RBAC)

### Уровни доступа

```python
class AccessLevel(Enum):
    """Уровни доступа"""
    PUBLIC = 1
    AGENT = 2
    MANAGER = 3
    ADMIN = 4
    SYSTEM = 5
```

### Разрешения

```python
class Permission(Enum):
    """Разрешения"""
    # Данные клиентов
    CUSTOMER_VIEW = 'customer:view'
    CUSTOMER_VIEW_FULL = 'customer:view:full'  # Без маскирования
    CUSTOMER_CREATE = 'customer:create'
    CUSTOMER_UPDATE = 'customer:update'
    CUSTOMER_DELETE = 'customer:delete'
    CUSTOMER_EXPORT = 'customer:export'

    # Бронирования
    BOOKING_VIEW = 'booking:view'
    BOOKING_CREATE = 'booking:create'
    BOOKING_UPDATE = 'booking:update'
    BOOKING_CANCEL = 'booking:cancel'

    # Платежи
    PAYMENT_VIEW = 'payment:view'
    PAYMENT_VIEW_FULL = 'payment:view:full'
    PAYMENT_PROCESS = 'payment:process'
    PAYMENT_REFUND = 'payment:refund'

    # Документы
    DOCUMENT_VIEW = 'document:view'
    DOCUMENT_DECRYPT = 'document:decrypt'
    DOCUMENT_UPLOAD = 'document:upload'
    DOCUMENT_DELETE = 'document:delete'

    # Аудит
    AUDIT_VIEW = 'audit:view'
    AUDIT_EXPORT = 'audit:export'

    # Администрирование
    USER_MANAGE = 'user:manage'
    ROLE_MANAGE = 'role:manage'
    SETTINGS_MANAGE = 'settings:manage'
```

### Стандартные роли

| Роль | Уровень | Основные разрешения |
|------|---------|---------------------|
| **viewer** | AGENT | Просмотр клиентов, бронирований, платежей (замаскированно) |
| **agent** | AGENT | + Создание/редактирование клиентов, бронирований, загрузка документов |
| **manager** | MANAGER | + Полный просмотр данных, отмена броней, рефанды, аудит |
| **admin** | ADMIN | + Управление пользователями, настройками, экспорт аудита |

### Матрица маскирования по ролям

| Роль | Карта | Паспорт | Телефон | Email |
|------|-------|---------|---------|-------|
| PUBLIC | `****` | `****` | `****` | `****` |
| AGENT | `4111****1234` | `AB***67` | `+971****67` | `iv**@gmail.com` |
| MANAGER | `4111****1234` | `AB***67` | Полный | Полный |
| ADMIN | `4111****1234` | Полный | Полный | Полный |

**Примечание**: Номера карт ВСЕГДА маскируются, даже для ADMIN (требования PCI DSS).

### Контекстно-зависимое маскирование

```python
@dataclass
class MaskingContext:
    """Контекст для маскирования"""
    user_role: AccessLevel
    purpose: str  # 'display', 'export', 'log', 'analytics'
    customer_consent: bool
    is_own_data: bool  # Запрашивает ли клиент свои данные

# Особые правила:
# - Для экспорта: всегда строгое маскирование
# - Для логов: REDACTED для критических данных
# - Клиент + согласие: полные данные
```

---

## Чек-лист безопасности

### При разработке

- [ ] Все regex паттерны для PII задокументированы
- [ ] Паттерны покрывают форматы ОАЭ, России и международные
- [ ] Реализована валидация (Luhn для карт)
- [ ] Есть тесты для всех паттернов

### Маскирование

- [ ] Определены правила для каждой категории PII
- [ ] Реализовано контекстно-зависимое маскирование
- [ ] CVV/CVC никогда не хранятся
- [ ] Номера карт хранятся только замаскированными

### Шифрование

- [ ] Используется AES-256 / Fernet
- [ ] Ключи хранятся отдельно от данных
- [ ] Реализована ротация ключей (90 дней)
- [ ] Есть план восстановления ключей

### Аудит

- [ ] Логируются все операции с PII
- [ ] Логи защищены от изменения (checksum)
- [ ] Настроены оповещения о подозрительной активности
- [ ] Логи НЕ содержат незамаскированных PII

### Доступ

- [ ] Реализован RBAC
- [ ] Принцип минимальных привилегий
- [ ] Есть процесс пересмотра доступов
- [ ] Реализовано разделение обязанностей

### GDPR

- [ ] Реализованы права субъектов данных
- [ ] Система управления согласиями
- [ ] Определены сроки хранения
- [ ] Есть процедура удаления данных

---

## См. также

- [SKILL.md](../SKILL.md) - Основной скилл парсинга WhatsApp
- [faq.md](faq.md) - Часто задаваемые вопросы
- [troubleshooting.md](troubleshooting.md) - Решение проблем
