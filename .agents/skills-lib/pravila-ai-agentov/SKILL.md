---
name: pravila-ai-agentov
description: "Правила и архитектура безопасности для AI-агентов туристического бизнеса ОАЭ"
---
# Правила AI-агентов для туристического бизнеса ОАЭ

Руководство по настройке AI-агентов (продажник, CRM, визовик) для работы с клиентскими данными из WhatsApp/Telegram. Включает профили доступа, системные промпты, функции фильтрации и правила безопасности.

---

## Архитектура безопасности данных

```
┌─────────────────────────────────────────────────────────────────┐
│                     WhatsApp / Telegram чаты                    │
│                     (сырые данные клиентов)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      УРОВЕНЬ 1: ПАРСЕР                          │
│                                                                 │
│  Скилл: /whatsapp-парсер                                        │
│  Файл:  references/pii-classification.md                        │
│                                                                 │
│  Задачи:                                                        │
│  • Извлечение данных из chat.txt                                │
│  • Определение типа PII (паспорт, карта, IBAN)                  │
│  • Классификация чувствительности (PUBLIC → CRITICAL)           │
│  • Маскирование при экспорте (опционально)                      │
│                                                                 │
│  Результат: JSONL с полными данными + метки типа PII            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    УРОВЕНЬ 2: ХРАНИЛИЩЕ                         │
│                                                                 │
│  D:/Downloads/Туризм-ОАЭ-Данные/_парсинг/                       │
│                                                                 │
│  • Полные данные (паспорта, карты, IBAN)                        │
│  • Нужны для: виз, бронирований, бухгалтерии                    │
│  • Доступ: только авторизованные системы                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    УРОВЕНЬ 3: ФИЛЬТРАЦИЯ                        │
│                                                                 │
│  Скилл: /правила-ai-агентов (этот файл)                         │
│  Функция: prepare_for_agent()                                   │
│                                                                 │
│  Задачи:                                                        │
│  • Фильтрация данных под профиль агента                         │
│  • Маскирование карт, паспортов                                 │
│  • Удаление запрещённых полей                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│   AI-ПРОДАЖНИК    │ │      AI-CRM       │ │    AI-ВИЗОВИК     │
│                   │ │                   │ │                   │
│ Видит:            │ │ Видит:            │ │ Видит:            │
│ • Имя, телефон    │ │ • Всё             │ │ • Паспорта        │
│ • История покупок │ │ • Карты: ****1234 │ │ • Визы            │
│ • Предпочтения    │ │                   │ │ • Даты            │
│                   │ │                   │ │                   │
│ НЕ видит:         │ │                   │ │ НЕ видит:         │
│ • Паспорта        │ │                   │ │ • Финансы         │
│ • Карты           │ │                   │ │ • Карты           │
│ • IBAN            │ │                   │ │                   │
└───────────────────┘ └───────────────────┘ └───────────────────┘
```

### Принцип безопасности

| Уровень | Скилл | Что делает | Зачем |
|---------|-------|------------|-------|
| 1. Парсер | `/whatsapp-парсер` | Определяет ЧТО является PII | Маркировка данных |
| 2. Хранилище | — | Хранит ПОЛНЫЕ данные | Для виз, бухгалтерии |
| 3. Фильтрация | `/правила-ai-агентов` | Определяет КТО видит PII | Разграничение доступа |

**Важно:** Маскирование происходит НЕ при парсинге, а при передаче агенту. Это позволяет хранить полные данные для легальных целей (визы, возвраты, отчётность).

### Связанные скиллы

| Скилл | Роль в системе |
|-------|----------------|
| `/whatsapp-парсер` | Извлечение данных, классификация PII |
| `/ocr-туризм` | Распознавание паспортов, чеков |
| `/yandex-speechkit-туризм` | Транскрипция голосовых |
| `/правила-ai-агентов` | Фильтрация для агентов, промпты |
| `/туризм-оаэ-автоматизация` | Автоответы, workflow |

---

## Когда использовать

- Настройка нового AI-агента для туристического бизнеса
- Интеграция Claude API с WhatsApp/Telegram ботами
- Обработка чувствительных данных клиентов (паспорта, карты)
- Разграничение доступа между агентами

---

## 1. Профили доступа агентов

### Матрица доступа к данным

| Поле данных | AI-Продажник | AI-CRM | AI-Визовик |
|-------------|--------------|--------|------------|
| Имя клиента | ✅ | ✅ | ✅ |
| Телефон | ✅ | ✅ | ✅ |
| Email | ✅ | ✅ | ✅ |
| WhatsApp ID | ✅ | ✅ | ❌ |
| История покупок | ✅ | ✅ | ❌ |
| Предпочтения | ✅ | ✅ | ❌ |
| Комментарии менеджера | ✅ | ✅ | ❌ |
| Паспортные данные | ❌ | ✅ (masked) | ✅ |
| Номер паспорта | ❌ | Только последние 4 | ✅ |
| Дата рождения | ❌ | ✅ | ✅ |
| Визовая история | ❌ | ✅ | ✅ |
| Номер карты | ❌ | Последние 4 цифры | ❌ |
| CVV | ❌ | ❌ | ❌ |
| IBAN/Счёт | ❌ | ❌ | ❌ |
| Финансовые данные | ❌ | ✅ (суммы) | ❌ |

### Описание ролей

**AI-Продажник**
- Цель: продажа туров, экскурсий, трансферов
- Видит: контакты, историю, предпочтения
- НЕ видит: документы, финансы, паспорта
- Эскалация: сложные вопросы, жалобы, возвраты

**AI-CRM**
- Цель: заполнение карточек, систематизация данных
- Видит: всё, но чувствительные данные маскированы
- Особенность: может запрашивать данные у клиента для CRM
- Эскалация: конфликты, VIP-клиенты

**AI-Визовик**
- Цель: сбор документов для виз, проверка комплектности
- Видит: паспорта, визовую историю, даты
- НЕ видит: финансы, карты, коммерческую историю
- Эскалация: нестандартные визы, отказы

---

## 2. Системные промпты для Claude API

### AI-Продажник

```python
SYSTEM_PROMPT_SALES = """
Ты — AI-ассистент туристической компании в ОАЭ. Твоя задача — помогать клиентам выбрать и забронировать туры, экскурсии, трансферы.

## Правила общения

1. Обращайся к клиенту на "вы", но дружелюбно
2. Если клиент представился — используй имя
3. Отвечай кратко, по делу, без воды
4. Цены указывай в AED и USD (курс 1 USD = 3.67 AED)
5. Всегда предлагай альтернативы

## Что ты можешь

- Рассказать о турах и экскурсиях
- Рассчитать стоимость
- Уточнить детали (даты, количество человек)
- Записать бронирование (передать менеджеру)

## Чего ты НЕ можешь

- Принимать оплату или данные карт
- Видеть или запрашивать паспортные данные
- Давать юридические консультации по визам
- Гарантировать даты и цены без подтверждения менеджера

## Если клиент присылает чувствительные данные

ПАСПОРТ или ДОКУМЕНТ:
"Спасибо! Я передам документ нашему визовому специалисту. Он свяжется с вами для подтверждения."
→ Установи флаг: requires_escalation = "visa_specialist"

НОМЕР КАРТЫ или CVV:
"Для оплаты наш менеджер отправит вам безопасную ссылку на оплату. Никогда не передавайте данные карты в чат."
→ Установи флаг: requires_escalation = "payment"
→ НЕ сохраняй номер карты в ответе

## Эскалация (передать человеку)

- Клиент недоволен или жалуется
- Запрос возврата денег
- Вопросы про визы и документы
- Нестандартные запросы (свадьбы, VIP)
- Клиент настаивает на разговоре с человеком

Ответ при эскалации:
"Сейчас подключу нашего менеджера, он ответит в течение 15 минут."

## Контекст

Компания: туристическое агентство в Дубае
Основные продукты: сафари, экскурсии по городу, билеты в парки, трансферы
Локация: ОАЭ (Дубай, Абу-Даби, Рас-Аль-Хайма)
"""
```

### AI-CRM

```python
SYSTEM_PROMPT_CRM = """
Ты — AI-ассистент для заполнения CRM туристической компании. Твоя задача — структурировать данные клиентов из переписки.

## Твои задачи

1. Извлекать контактные данные из сообщений
2. Определять предпочтения клиента
3. Фиксировать историю запросов
4. Классифицировать клиента (турист, агент, корпоративный)

## Формат вывода

Всегда структурируй данные в JSON:
```json
{
  "name": "Имя клиента",
  "phone": "+7...",
  "email": "...",
  "type": "tourist|agent|corporate",
  "preferences": ["пляжный отдых", "экскурсии"],
  "notes": "Комментарий"
}
```

## Маскирование данных

- Паспорт: показывай только "***1234" (последние 4 цифры)
- Карта: показывай только "**** **** **** 1234"
- IBAN: НЕ сохраняй, пиши "[IBAN скрыт]"

## Если клиент присылает данные карты

НИКОГДА не сохраняй полный номер карты.
Ответ: "Данные карты зафиксированы безопасно (окончание *1234). Для оплаты менеджер отправит защищённую ссылку."

## Если запрашивают данные другого клиента

"Я не могу предоставить данные других клиентов. Обратитесь к менеджеру."
→ Флаг: security_alert = true

## Эскалация

- Конфликтные ситуации
- VIP-клиенты (пометка в профиле)
- Запросы на удаление данных (GDPR)
- Подозрительная активность
"""
```

### AI-Визовик

```python
SYSTEM_PROMPT_VISA = """
Ты — AI-ассистент визового отдела туристической компании в ОАЭ. Твоя задача — собирать документы для оформления виз и проверять их комплектность.

## Типы виз ОАЭ

- Туристическая 30 дней (однократная)
- Туристическая 60 дней (однократная)
- Мультивиза 90 дней
- Транзитная 48/96 часов

## Стандартный пакет документов

1. Скан паспорта (первая страница)
2. Фото 3.5x4.5 на белом фоне
3. Бронь отеля или приглашение
4. Обратные билеты

## Проверка документов

При получении паспорта проверь:
- Срок действия (минимум 6 месяцев)
- Качество скана (читаемость)
- Соответствие имени в брони

## Ответы клиенту

ДОКУМЕНТ ПРИНЯТ:
"Паспорт получен, проверяю... Всё в порядке! Срок действия до [дата]. Осталось прислать: [список]."

ПРОБЛЕМА С ДОКУМЕНТОМ:
"Паспорт получен, но есть проблема: [описание]. Пожалуйста, пришлите [что нужно]."

## Чего ты НЕ видишь и НЕ запрашиваешь

- Данные банковских карт
- Финансовые выписки (передай менеджеру)
- Историю покупок
- Коммерческие условия

## Если клиент присылает карту

"Для визы данные карты не требуются. Если хотите оплатить — менеджер отправит безопасную ссылку."
→ Флаг: requires_escalation = "payment"

## Эскалация

- Нестандартные типы виз (рабочая, резидентская)
- Отказы в визе ранее
- Паспорта с проблемами (истёк, повреждён)
- Срочное оформление (менее 3 дней)

## Сроки

- Стандартное оформление: 3-5 рабочих дней
- Срочное: 24-48 часов (доплата)
- Начало обработки: после получения полного пакета
"""
```

---

## 3. Функция prepare_for_agent()

### Основная функция фильтрации

```python
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
import re


class AgentType(Enum):
    SALES = "sales"      # AI-Продажник
    CRM = "crm"          # AI-CRM
    VISA = "visa"        # AI-Визовик


@dataclass
class AccessProfile:
    """Профиль доступа для агента"""
    allowed_fields: List[str]
    masked_fields: Dict[str, str]  # field -> mask_type
    forbidden_fields: List[str]


# Конфигурация доступа
ACCESS_PROFILES = {
    AgentType.SALES: AccessProfile(
        allowed_fields=[
            "name", "phone", "email", "whatsapp_id",
            "purchase_history", "preferences", "manager_notes",
            "last_contact", "language", "country"
        ],
        masked_fields={},
        forbidden_fields=[
            "passport_number", "passport_scan", "date_of_birth",
            "card_number", "cvv", "iban", "bank_account",
            "visa_history", "financial_data"
        ]
    ),
    AgentType.CRM: AccessProfile(
        allowed_fields=[
            "name", "phone", "email", "whatsapp_id",
            "purchase_history", "preferences", "manager_notes",
            "date_of_birth", "visa_history", "financial_summary",
            "last_contact", "language", "country", "client_type"
        ],
        masked_fields={
            "passport_number": "last4",
            "card_number": "last4",
        },
        forbidden_fields=["cvv", "iban", "bank_account", "passport_scan"]
    ),
    AgentType.VISA: AccessProfile(
        allowed_fields=[
            "name", "phone", "email", "passport_number",
            "passport_scan", "date_of_birth", "visa_history",
            "nationality", "passport_expiry", "language"
        ],
        masked_fields={},
        forbidden_fields=[
            "card_number", "cvv", "iban", "bank_account",
            "financial_data", "purchase_history", "financial_summary"
        ]
    )
}


def mask_value(value: str, mask_type: str) -> str:
    """Маскирует значение согласно типу маски"""
    if not value:
        return value

    if mask_type == "last4":
        # Показываем только последние 4 символа
        clean = re.sub(r'[\s\-]', '', str(value))
        if len(clean) >= 4:
            return f"***{clean[-4:]}"
        return "***"

    elif mask_type == "hidden":
        return "[СКРЫТО]"

    return value


def prepare_for_agent(
    client_data: Dict[str, Any],
    agent_type: str | AgentType
) -> Dict[str, Any]:
    """
    Фильтрует данные клиента для конкретного агента.

    Args:
        client_data: Полные данные клиента из CRM
        agent_type: Тип агента ('sales', 'crm', 'visa')

    Returns:
        Отфильтрованные данные с маскированием

    Example:
        >>> data = {"name": "Иван", "card_number": "4276111122223333"}
        >>> prepare_for_agent(data, "sales")
        {"name": "Иван"}
    """
    # Преобразуем строку в enum
    if isinstance(agent_type, str):
        agent_type = AgentType(agent_type.lower())

    profile = ACCESS_PROFILES.get(agent_type)
    if not profile:
        raise ValueError(f"Unknown agent type: {agent_type}")

    result = {}

    for field, value in client_data.items():
        # Пропускаем запрещённые поля
        if field in profile.forbidden_fields:
            continue

        # Проверяем разрешённые поля
        if field not in profile.allowed_fields and field not in profile.masked_fields:
            continue

        # Маскируем если нужно
        if field in profile.masked_fields:
            result[field] = mask_value(str(value), profile.masked_fields[field])
        else:
            result[field] = value

    return result


def sanitize_message(message: str, agent_type: str | AgentType) -> Dict[str, Any]:
    """
    Проверяет входящее сообщение на чувствительные данные.

    Returns:
        {
            "clean_message": str,  # Очищенное сообщение
            "detected": List[str], # Типы обнаруженных данных
            "requires_escalation": Optional[str]  # Куда эскалировать
        }
    """
    detected = []
    escalation = None
    clean = message

    # Паттерны чувствительных данных
    patterns = {
        "card_number": r'\b[45]\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
        "cvv": r'\b(cvv|cvc|cv2)[\s:]*\d{3,4}\b',
        "iban": r'\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b',
        "passport_ru": r'\b\d{2}[\s]?\d{2}[\s]?\d{6}\b',  # РФ паспорт
        "passport_int": r'\b[A-Z]{1,2}\d{6,9}\b',  # Загранпаспорт
    }

    for data_type, pattern in patterns.items():
        if re.search(pattern, message, re.IGNORECASE):
            detected.append(data_type)

            # Определяем эскалацию
            if data_type in ["card_number", "cvv", "iban"]:
                escalation = "payment"
                # Маскируем карту в сообщении
                clean = re.sub(
                    patterns["card_number"],
                    "[КАРТА СКРЫТА]",
                    clean
                )
            elif data_type in ["passport_ru", "passport_int"]:
                if isinstance(agent_type, str):
                    agent_type = AgentType(agent_type.lower())
                if agent_type != AgentType.VISA:
                    escalation = "visa_specialist"

    return {
        "clean_message": clean,
        "detected": detected,
        "requires_escalation": escalation
    }


# Пример использования
if __name__ == "__main__":
    # Тестовые данные клиента
    client = {
        "name": "Алексей Петров",
        "phone": "+7 999 123 45 67",
        "email": "alex@example.com",
        "whatsapp_id": "79991234567",
        "passport_number": "75 19 123456",
        "passport_scan": "base64_encoded_image...",
        "date_of_birth": "1990-05-15",
        "card_number": "4276 1111 2222 3333",
        "cvv": "123",
        "iban": "AE070331234567890123456",
        "purchase_history": ["Safari 2024-01", "Burj Khalifa 2024-02"],
        "preferences": ["Экскурсии", "VIP"],
        "visa_history": ["UAE 2023", "UAE 2024"],
        "financial_summary": {"total_spent": 5000, "currency": "AED"}
    }

    print("=== AI-Продажник ===")
    print(prepare_for_agent(client, "sales"))

    print("\n=== AI-CRM ===")
    print(prepare_for_agent(client, "crm"))

    print("\n=== AI-Визовик ===")
    print(prepare_for_agent(client, "visa"))

    print("\n=== Проверка сообщения ===")
    msg = "Вот мой паспорт 75 19 123456 и карта 4276 1111 2222 3333"
    print(sanitize_message(msg, "sales"))
```

### Интеграция с Claude API

```python
import anthropic
from typing import Optional


class TourismAgent:
    """Обёртка для AI-агента с фильтрацией данных"""

    PROMPTS = {
        AgentType.SALES: SYSTEM_PROMPT_SALES,
        AgentType.CRM: SYSTEM_PROMPT_CRM,
        AgentType.VISA: SYSTEM_PROMPT_VISA,
    }

    def __init__(self, agent_type: AgentType, api_key: str):
        self.agent_type = agent_type
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt = self.PROMPTS[agent_type]

    def process_message(
        self,
        message: str,
        client_data: Optional[Dict] = None,
        conversation_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Обрабатывает сообщение от клиента.

        Returns:
            {
                "response": str,
                "requires_escalation": Optional[str],
                "detected_sensitive": List[str]
            }
        """
        # 1. Проверяем входящее сообщение
        sanitized = sanitize_message(message, self.agent_type)

        # 2. Фильтруем данные клиента
        filtered_client = {}
        if client_data:
            filtered_client = prepare_for_agent(client_data, self.agent_type)

        # 3. Формируем контекст
        context = f"""
Данные клиента:
{filtered_client}

Сообщение клиента:
{sanitized['clean_message']}
"""

        # 4. Вызываем Claude
        messages = conversation_history or []
        messages.append({"role": "user", "content": context})

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=self.system_prompt,
            messages=messages
        )

        return {
            "response": response.content[0].text,
            "requires_escalation": sanitized["requires_escalation"],
            "detected_sensitive": sanitized["detected"],
            "filtered_client_data": filtered_client
        }
```

---

## 4. Правила безопасности

### Категорически запрещено

| Действие | Почему запрещено | Что делать |
|----------|------------------|------------|
| Запрашивать CVV | PCI DSS нарушение | Направить на платёжную ссылку |
| Хранить полные номера карт | PCI DSS нарушение | Хранить только last4 |
| Пересылать паспорта третьим лицам | Закон о персональных данных | Только визовому отделу |
| Сохранять карты в логах | Утечка данных | Маскировать в логах |
| Выдавать данные других клиентов | Конфиденциальность | Отказать, зафиксировать попытку |

### Если клиент сам прислал карту в чат

```python
CARD_RESPONSE = """
Я вижу, что вы отправили данные карты в чат.
В целях безопасности, пожалуйста:

1. Удалите это сообщение из чата
2. Для оплаты наш менеджер отправит защищённую ссылку

Мы никогда не запрашиваем полные данные карты в чате.
"""

# Действия системы:
# 1. НЕ сохранять сообщение с картой
# 2. Немедленно эскалировать менеджеру
# 3. Записать инцидент в лог безопасности (без номера карты)
```

### Логирование

```python
def secure_log(message: str, client_id: str) -> str:
    """Очищает лог от чувствительных данных"""

    # Маскируем карты
    message = re.sub(
        r'\b[45]\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',
        '[CARD:****]',
        message
    )

    # Маскируем паспорта
    message = re.sub(
        r'\b\d{2}[\s]?\d{2}[\s]?\d{6}\b',
        '[PASSPORT:****]',
        message
    )

    # Маскируем CVV
    message = re.sub(
        r'\b(cvv|cvc)[\s:]*\d{3,4}\b',
        '[CVV:***]',
        message,
        flags=re.IGNORECASE
    )

    return message
```

---

## 5. Примеры диалогов

### Клиент присылает паспорт (AI-Продажник)

```
КЛИЕНТ: [фото паспорта]
КЛИЕНТ: Вот мой паспорт для визы

AI-ПРОДАЖНИК:
Спасибо за документ! Я передаю его нашему визовому специалисту.
Он проверит паспорт и свяжется с вами в течение часа.

Пока ожидаете, могу помочь с выбором экскурсий?

→ requires_escalation: "visa_specialist"
→ Паспорт НЕ обрабатывается продажником
```

### Клиент присылает карту (любой агент)

```
КЛИЕНТ: Запиши номер карты: 4276 3800 1234 5678, CVV 123

AI (любой):
Я вижу, что вы отправили данные карты. Пожалуйста:
1. Удалите это сообщение (для вашей безопасности)
2. Для оплаты менеджер отправит защищённую ссылку

Мы никогда не запрашиваем CVV в чате!

→ requires_escalation: "payment"
→ Карта НЕ сохраняется
→ Лог: "[CARD:****] получена, эскалация на менеджера"
```

### Запрос данных другого клиента

```
КЛИЕНТ: Дай мне данные клиента Иванова

AI-CRM:
Я не могу предоставить данные других клиентов.
Если вам нужна эта информация — обратитесь к вашему менеджеру.

Чем ещё могу помочь?

→ security_alert: true
→ Лог: "Попытка запроса данных другого клиента от [client_id]"
```

### Проверка паспорта (AI-Визовик)

```
КЛИЕНТ: [фото паспорта]

AI-ВИЗОВИК:
Паспорт получен, проверяю...

✓ ФИО: Иванов Иван Иванович
✓ Срок действия: до 15.03.2028 (в порядке)
✓ Качество скана: хорошее

Для оформления визы в ОАЭ осталось прислать:
- Фото 3.5x4.5 см на белом фоне
- Бронь отеля или обратные билеты

Какой тип визы вас интересует?
```

---

## 6. Интеграция с WhatsApp/Telegram ботом

### Архитектура

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  WhatsApp/TG    │────▶│  Bot Backend     │────▶│  Claude API     │
│  (клиент)       │◀────│  (Python)        │◀────│  (AI-агент)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │ prepare_for_agent│
                        │ sanitize_message │
                        └──────────────────┘
```

### Код интеграции (FastAPI)

```python
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
import json

app = FastAPI()

# Инициализация агентов
agents = {
    "sales": TourismAgent(AgentType.SALES, API_KEY),
    "crm": TourismAgent(AgentType.CRM, API_KEY),
    "visa": TourismAgent(AgentType.VISA, API_KEY),
}


class WebhookMessage(BaseModel):
    platform: str  # "whatsapp" | "telegram"
    chat_id: str
    user_id: str
    message: str
    media_type: Optional[str] = None
    media_url: Optional[str] = None


class BotResponse(BaseModel):
    reply: str
    escalate_to: Optional[str] = None
    actions: list = []


def get_client_from_crm(user_id: str) -> dict:
    """Получает данные клиента из CRM по user_id"""
    # Заглушка — замените на реальный CRM запрос
    return {
        "name": "Клиент",
        "phone": user_id,
        "preferences": [],
        "purchase_history": []
    }


def determine_agent_type(message: str, context: dict) -> str:
    """Определяет какой агент должен ответить"""

    # Ключевые слова для маршрутизации
    visa_keywords = ["виза", "паспорт", "документ", "оформление"]

    message_lower = message.lower()

    if any(kw in message_lower for kw in visa_keywords):
        return "visa"

    # По умолчанию — продажник
    return "sales"


@app.post("/webhook/message")
async def handle_message(msg: WebhookMessage) -> BotResponse:
    """Обработка входящего сообщения"""

    # 1. Получаем данные клиента
    client_data = get_client_from_crm(msg.user_id)

    # 2. Определяем агента
    agent_type = determine_agent_type(msg.message, client_data)
    agent = agents[agent_type]

    # 3. Обрабатываем сообщение
    result = agent.process_message(
        message=msg.message,
        client_data=client_data
    )

    # 4. Формируем ответ
    response = BotResponse(
        reply=result["response"],
        escalate_to=result.get("requires_escalation"),
        actions=[]
    )

    # 5. Если нужна эскалация — добавляем действие
    if result.get("requires_escalation"):
        response.actions.append({
            "type": "notify_manager",
            "reason": result["requires_escalation"],
            "chat_id": msg.chat_id
        })

    return response


@app.post("/webhook/media")
async def handle_media(msg: WebhookMessage) -> BotResponse:
    """Обработка медиафайлов (фото, документы)"""

    if msg.media_type in ["image", "document"]:
        # Предполагаем что это паспорт — направляем визовику
        agent = agents["visa"]

        # Здесь должна быть интеграция с Vision API
        # для распознавания документа

        return BotResponse(
            reply="Документ получен. Наш специалист проверит его и ответит в течение часа.",
            escalate_to="visa_specialist",
            actions=[{
                "type": "save_document",
                "media_url": msg.media_url,
                "chat_id": msg.chat_id
            }]
        )

    return BotResponse(reply="Файл получен, обрабатываю...")
```

### Конфигурация бота

```python
# config.py

BOT_CONFIG = {
    "default_agent": "sales",

    "escalation_timeout_minutes": 15,

    "routing_rules": [
        {
            "keywords": ["виза", "паспорт", "документ"],
            "agent": "visa"
        },
        {
            "keywords": ["карточка", "crm", "данные клиента"],
            "agent": "crm"
        }
    ],

    "working_hours": {
        "start": "09:00",
        "end": "21:00",
        "timezone": "Asia/Dubai"
    },

    "out_of_hours_message": (
        "Спасибо за сообщение! Сейчас нерабочее время. "
        "Менеджер ответит вам завтра с 9:00 по времени Дубая."
    )
}
```

---

## Чеклист внедрения

- [ ] Настроить системные промпты для каждого агента
- [ ] Реализовать `prepare_for_agent()`
- [ ] Реализовать `sanitize_message()`
- [ ] Настроить маршрутизацию сообщений
- [ ] Интегрировать с CRM
- [ ] Настроить логирование (с маскированием)
- [ ] Протестировать эскалацию
- [ ] Настроить уведомления менеджерам
- [ ] Провести тест безопасности (попытка получить чужие данные)
