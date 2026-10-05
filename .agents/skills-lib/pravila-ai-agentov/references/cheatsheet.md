# Шпаргалка: Правила AI-агентов

## Матрица доступа (быстрая справка)

```
                    Продажник   CRM      Визовик
Имя, телефон, email    ✅        ✅         ✅
История покупок        ✅        ✅         ❌
Паспорт                ❌      ***1234      ✅
Карта                  ❌      ***1234      ❌
CVV                    ❌        ❌         ❌
IBAN                   ❌        ❌         ❌
```

---

## Быстрый код

### Фильтрация данных

```python
from skill import prepare_for_agent

# Для продажника
data = prepare_for_agent(client, "sales")

# Для CRM
data = prepare_for_agent(client, "crm")

# Для визовика
data = prepare_for_agent(client, "visa")
```

### Проверка сообщения

```python
from skill import sanitize_message

result = sanitize_message(message, "sales")

if result["requires_escalation"]:
    notify_manager(result["requires_escalation"])

# result = {
#   "clean_message": "...",
#   "detected": ["card_number"],
#   "requires_escalation": "payment"
# }
```

### Маскирование

```python
from skill import mask_value

mask_value("4276111122223333", "last4")  # "***3333"
mask_value("75 19 123456", "last4")      # "***3456"
```

---

## Системные промпты (копируй)

### Продажник (ключевые части)

```
## Чего ты НЕ можешь
- Принимать данные карт
- Видеть паспорта
- Гарантировать цены без менеджера

## При получении карты
"Для оплаты менеджер отправит безопасную ссылку."
→ requires_escalation = "payment"

## При получении паспорта
"Передаю документ визовому специалисту."
→ requires_escalation = "visa_specialist"
```

### CRM (ключевые части)

```
## Маскирование
- Паспорт: "***1234"
- Карта: "**** **** **** 1234"
- IBAN: "[IBAN скрыт]"

## При запросе чужих данных
"Я не могу предоставить данные других клиентов."
→ security_alert = true
```

### Визовик (ключевые части)

```
## Документы для визы ОАЭ
1. Паспорт (6+ месяцев)
2. Фото 3.5x4.5 белый фон
3. Бронь отеля / билеты

## При получении карты
"Для визы карта не нужна. Менеджер отправит ссылку на оплату."
→ requires_escalation = "payment"
```

---

## Паттерны детекции

```python
# Карта (Visa/MasterCard)
r'\b[45]\d{3}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'

# CVV
r'\b(cvv|cvc|cv2)[\s:]*\d{3,4}\b'

# IBAN
r'\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b'

# Паспорт РФ (внутренний)
r'\b\d{2}[\s]?\d{2}[\s]?\d{6}\b'

# Загранпаспорт
r'\b[A-Z]{1,2}\d{6,9}\b'
```

---

## Эскалация (когда и куда)

| Триггер | Куда | Ответ клиенту |
|---------|------|---------------|
| Паспорт у продажника | visa_specialist | "Передаю визовику" |
| Номер карты | payment | "Не присылайте карту в чат" |
| Жалоба | manager | "Подключаю менеджера" |
| Возврат | finance | "Менеджер свяжется" |
| Запрос чужих данных | security | "Не могу предоставить" |

---

## API вызов Claude

```python
import anthropic

client = anthropic.Anthropic(api_key="...")

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": f"Клиент: {client_data}\n\nСообщение: {message}"}
    ]
)

answer = response.content[0].text
tokens = response.usage.input_tokens + response.usage.output_tokens
```

---

## Логирование (безопасное)

```python
import re

def secure_log(msg: str) -> str:
    # Карты
    msg = re.sub(r'\b[45]\d{15}\b', '[CARD]', msg)
    # Паспорта
    msg = re.sub(r'\b\d{2}\s?\d{2}\s?\d{6}\b', '[PASSPORT]', msg)
    # CVV
    msg = re.sub(r'cvv[\s:]*\d{3,4}', '[CVV]', msg, flags=re.I)
    return msg
```

---

## Webhook FastAPI

```python
@app.post("/webhook/message")
async def handle(msg: WebhookMessage):
    # 1. Данные клиента
    client = get_client(msg.user_id)

    # 2. Фильтрация
    safe = prepare_for_agent(client, agent_type)

    # 3. Проверка сообщения
    check = sanitize_message(msg.message, agent_type)

    # 4. Claude
    response = agent.process(check["clean_message"], safe)

    # 5. Эскалация
    if check["requires_escalation"]:
        await notify_manager(check["requires_escalation"])

    return {"reply": response}
```

---

## Чеклист безопасности

```
[ ] prepare_for_agent() вызывается ДО Claude
[ ] sanitize_message() проверяет входящие
[ ] CVV НИКОГДА не сохраняется
[ ] Полные карты НЕ в логах
[ ] Паспорта только визовику
[ ] Эскалация работает
[ ] Уведомления доходят
[ ] security_alert логируется
```

---

## Типы виз ОАЭ (справка)

| Тип | Срок | Документы |
|-----|------|-----------|
| Туристическая | 30 дней | Паспорт, фото, бронь |
| Туристическая | 60 дней | Паспорт, фото, бронь |
| Мульти | 90 дней | Паспорт, фото, бронь, выписка |
| Транзит | 48-96ч | Паспорт, билеты |

Срок оформления: 3-5 дней (срочно 24-48ч)

---

## Частые ошибки

```
# НЕПРАВИЛЬНО - данные до фильтрации
response = claude.create(messages=[{"content": str(client_data)}])

# ПРАВИЛЬНО - сначала фильтрация
safe = prepare_for_agent(client_data, "sales")
response = claude.create(messages=[{"content": str(safe)}])
```

```
# НЕПРАВИЛЬНО - карта в логе
logger.info(f"Получена карта: {card_number}")

# ПРАВИЛЬНО - маскирование
logger.info(f"Получена карта: ***{card_number[-4:]}")
```

```
# НЕПРАВИЛЬНО - один агент на всё
agent = UniversalAgent()

# ПРАВИЛЬНО - специализация
agents = {
    "sales": SalesAgent(),
    "crm": CRMAgent(),
    "visa": VisaAgent()
}
```
