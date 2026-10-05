# Claude API -- Классификатор сообщений

Системный промпт, примеры использования и batch-обработка для классификации сообщений туристического бизнеса.

---

## Системный промпт классификатора

```python
CLASSIFIER_SYSTEM_PROMPT = """
Ты AI-классификатор сообщений туристического бизнеса в ОАЭ.

Анализируй входящие сообщения и возвращай JSON:

{
  "type": "inquiry|booking|support|complaint|spam|other",
  "subtype": "подтип согласно категории",
  "priority": "critical|high|medium|low",
  "intent": "конкретное намерение",
  "language": "ru|en|ar",
  "sentiment": "positive|neutral|negative",
  "entities": {
    "product": "название продукта если есть",
    "date": "дата если упоминается",
    "guests": "количество гостей",
    "budget": "бюджет если указан"
  },
  "suggested_action": "рекомендуемое действие",
  "auto_response": true|false,
  "confidence": 0.0-1.0
}

ПРАВИЛА:
1. complaint всегда priority: high или critical
2. booking на сегодня/завтра = priority: high
3. VIP клиенты (определяй по контексту) = priority +1
4. Голосовые сообщения уже транскрибированы
5. Если неуверен -- confidence < 0.7, auto_response: false
"""
```

---

## Пример использования Claude API

```python
import anthropic
import json

def classify_message(text: str, context: dict = None) -> dict:
    """
    Классификация сообщения через Claude API.

    Args:
        text: Текст сообщения
        context: Дополнительный контекст (история, клиент)

    Returns:
        dict: Результат классификации
    """
    client = anthropic.Anthropic()

    user_message = f"Классифицируй сообщение:\n\n{text}"

    if context:
        user_message += f"\n\nКонтекст клиента:\n{json.dumps(context, ensure_ascii=False)}"

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=CLASSIFIER_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    # Парсим JSON из ответа
    result = json.loads(response.content[0].text)
    return result


def generate_auto_response(classification: dict, templates: dict) -> str:
    """
    Генерация автоматического ответа на основе классификации.

    Args:
        classification: Результат classify_message()
        templates: Словарь шаблонов по типам

    Returns:
        str: Текст ответа или None
    """
    if not classification.get('auto_response', False):
        return None

    if classification['confidence'] < 0.7:
        return None

    intent = classification.get('intent', '')

    # Выбор шаблона
    template = templates.get(intent) or templates.get(classification['type'])

    if not template:
        return None

    # Персонализация через Claude
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system="Персонализируй шаблон ответа. Сохрани тон, добавь детали из контекста.",
        messages=[
            {
                "role": "user",
                "content": f"Шаблон: {template}\n\nКонтекст: {json.dumps(classification, ensure_ascii=False)}"
            }
        ]
    )

    return response.content[0].text
```

---

## Batch-классификация

```python
import asyncio
from anthropic import AsyncAnthropic

async def classify_batch(messages: list[dict]) -> list[dict]:
    """
    Асинхронная классификация пакета сообщений.

    Args:
        messages: Список сообщений [{id, text, context}, ...]

    Returns:
        list: Список классификаций
    """
    client = AsyncAnthropic()

    async def classify_one(msg: dict) -> dict:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=CLASSIFIER_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Классифицируй:\n\n{msg['text']}"}
            ]
        )
        result = json.loads(response.content[0].text)
        result['message_id'] = msg['id']
        return result

    tasks = [classify_one(msg) for msg in messages]
    results = await asyncio.gather(*tasks)

    return results

# Использование
messages = [
    {"id": 1, "text": "Сколько стоит тур в Абу-Даби?"},
    {"id": 2, "text": "Хочу забронировать на завтра"},
    {"id": 3, "text": "Водитель опоздал на час!"}
]

results = asyncio.run(classify_batch(messages))
for r in results:
    print(f"#{r['message_id']}: {r['type']} / {r['priority']}")
```

---

## Предиктивная аналитика

```python
# Модель вероятности покупки
features = {
    "message_count": 10,          # Количество сообщений
    "price_mentions": 3,          # Упоминания цены
    "has_specific_dates": True,   # Указаны даты
    "has_budget": True,           # Указан бюджет
    "positive_sentiment": 0.7,    # Доля позитива
    "days_since_contact": 2       # Дней с первого контакта
}

# Результат
prediction = {
    "purchase_probability": 0.85,
    "recommendation": "Высокая вероятность. Предложите скидку за быстрое решение."
}
```

---

## Автоматическая эскалация

```python
ESCALATION_RULES = {
    'immediate': {
        'conditions': ['sentiment <= 1', 'intent == "complaint"'],
        'action': 'notify_manager',
        'sla_minutes': 5
    },
    'urgent': {
        'conditions': ['sentiment <= 2', 'vip_client'],
        'action': 'assign_senior',
        'sla_minutes': 15
    },
    'standard': {
        'conditions': ['no_response_hours >= 2'],
        'action': 'reminder',
        'sla_minutes': 60
    }
}
```

---

## Fraud Detection (Обнаружение аномалий)

```python
FRAUD_SIGNALS = {
    'high_risk': [
        'срочно перевод', 'альтернативные реквизиты',
        'другой счёт', 'крипто оплата'
    ],
    'behavioral': [
        'новый аккаунт + большая сумма',
        'смена локации',
        'нетипичный паттерн сообщений'
    ]
}

# Действия при обнаружении
risk_score >= 0.5 -> manual_review
risk_score >= 0.7 -> block + alert_manager
```

---

## RAG система для FAQ

```python
# Архитектура
FAQ_Database -> Sentence Embeddings -> FAISS Index
                     |
User Query -> Embedding -> Similarity Search -> Top-K Results
                     |
             Claude -> Персонализированный ответ

# Порог автоответа
if similarity_score > 0.85:
    auto_send_response()
else:
    route_to_human()
```
