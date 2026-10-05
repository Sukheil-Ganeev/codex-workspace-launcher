# Troubleshooting: Правила AI-агентов

## Проблемы с доступом к данным

### Агент видит данные, которые не должен видеть

**Симптомы:**
- Продажник упоминает паспортные данные
- В ответе появляются номера карт

**Диагностика:**
```python
# Проверьте что фильтрация вызывается
print("До фильтрации:", client_data)
filtered = prepare_for_agent(client_data, "sales")
print("После фильтрации:", filtered)
```

**Решение:**
1. Убедитесь что `prepare_for_agent()` вызывается ДО передачи в Claude
2. Проверьте профиль доступа в `ACCESS_PROFILES`
3. Убедитесь что поле добавлено в `forbidden_fields`

```python
# Добавьте недостающее поле
ACCESS_PROFILES[AgentType.SALES].forbidden_fields.append("new_sensitive_field")
```

---

### Агент НЕ видит данные, которые должен видеть

**Симптомы:**
- Агент говорит "У меня нет этой информации"
- В ответе отсутствуют ожидаемые данные

**Диагностика:**
```python
filtered = prepare_for_agent(client_data, "crm")
print("Отфильтрованные данные:", filtered)
print("Ожидалось поле 'preferences':", "preferences" in filtered)
```

**Решение:**
Добавьте поле в `allowed_fields`:
```python
ACCESS_PROFILES[AgentType.CRM].allowed_fields.append("missing_field")
```

---

### Маскирование работает неправильно

**Симптомы:**
- Карта показывается полностью
- Маска `***` вместо `***1234`

**Диагностика:**
```python
from skill import mask_value

print(mask_value("4276 1111 2222 3333", "last4"))
# Ожидается: ***3333
```

**Решение:**
Проверьте формат входных данных:
```python
def mask_value(value: str, mask_type: str) -> str:
    if not value:
        return value

    # Убираем пробелы и дефисы
    clean = re.sub(r'[\s\-]', '', str(value))

    if mask_type == "last4" and len(clean) >= 4:
        return f"***{clean[-4:]}"

    return "***"
```

---

## Проблемы с эскалацией

### Эскалация не срабатывает при отправке паспорта

**Симптомы:**
- Клиент присылает паспорт, но менеджер не получает уведомление
- Флаг `requires_escalation` = None

**Диагностика:**
```python
result = sanitize_message("Мой паспорт 75 19 123456", "sales")
print(result)
# Ожидается: {"requires_escalation": "visa_specialist", "detected": ["passport_ru"]}
```

**Решение:**
1. Проверьте регулярное выражение:
```python
# Паспорт РФ: 2 цифры (серия) + 2 цифры (серия) + 6 цифр (номер)
passport_ru_pattern = r'\b\d{2}[\s]?\d{2}[\s]?\d{6}\b'

# Тест
import re
test = "75 19 123456"
print(bool(re.search(passport_ru_pattern, test)))  # True
```

2. Убедитесь что обработчик эскалации подключен:
```python
if result.get("requires_escalation"):
    await notify_manager(result["requires_escalation"], chat_id)
```

---

### Эскалация срабатывает слишком часто

**Симптомы:**
- Ложные срабатывания на обычные числа
- "Номер заказа 123456" определяется как паспорт

**Решение:**
Уточните паттерны:
```python
# Более строгий паттерн для паспорта РФ
# Серия: 01-99, номер: 6 цифр
passport_ru_strict = r'\b(0[1-9]|[1-9]\d)[\s]?(0[1-9]|[1-9]\d)[\s]?\d{6}\b'

# Или добавьте контекст
def detect_passport(message: str) -> bool:
    keywords = ["паспорт", "документ", "серия", "номер"]
    has_keyword = any(kw in message.lower() for kw in keywords)
    has_pattern = bool(re.search(passport_pattern, message))
    return has_keyword and has_pattern
```

---

### Менеджер не получает уведомления

**Симптомы:**
- Эскалация срабатывает, но сообщение не доходит

**Диагностика:**
```python
# Проверьте очередь уведомлений
print(notification_queue.pending())

# Проверьте логи
print(get_logs(level="error", source="notifications"))
```

**Решение:**
1. Проверьте настройки Telegram бота менеджера
2. Проверьте что chat_id менеджера корректный
3. Добавьте повторную отправку:
```python
async def notify_with_retry(manager_id: str, message: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            await send_notification(manager_id, message)
            return True
        except Exception as e:
            log.error(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2 ** attempt)
    return False
```

---

## Проблемы с промптами

### Агент отвечает на английском вместо русского

**Решение:**
Добавьте явное указание языка в промпт:
```python
SYSTEM_PROMPT = """
...
## Язык общения
ВСЕГДА отвечай на русском языке, независимо от языка вопроса.
Исключение: если клиент явно просит общаться на другом языке.
"""
```

---

### Агент слишком многословный

**Решение:**
Добавьте ограничение в промпт:
```python
SYSTEM_PROMPT = """
...
## Формат ответов
- Максимум 3-4 предложения на сообщение
- Один вопрос за раз
- Без повторений и воды
- Emoji использовать минимально (1-2 на сообщение)
"""
```

---

### Агент не следует инструкциям по эскалации

**Решение:**
1. Переместите правила эскалации в начало промпта
2. Выделите их визуально:
```python
SYSTEM_PROMPT = """
## !!! КРИТИЧЕСКИ ВАЖНО - ЭСКАЛАЦИЯ !!!

При получении ПАСПОРТА или КАРТЫ:
1. НЕ обрабатывай данные
2. НЕМЕДЛЕННО установи флаг эскалации
3. Ответь стандартной фразой

Это правило НЕЛЬЗЯ нарушать ни при каких обстоятельствах.

---
[остальной промпт]
"""
```

---

## Проблемы с производительностью

### Ответы приходят медленно (>5 секунд)

**Диагностика:**
```python
import time

start = time.time()
response = agent.process_message(message, client_data)
elapsed = time.time() - start
print(f"Время ответа: {elapsed:.2f}s")
```

**Решение:**
1. Сократите системный промпт (меньше токенов = быстрее)
2. Ограничьте историю диалога (последние 10 сообщений)
3. Используйте claude-haiku-3-5-20241022 для простых вопросов
4. Кешируйте системный промпт:
```python
# Anthropic поддерживает кеширование промптов
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    system=[{
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"}
    }],
    messages=messages
)
```

---

### Высокое потребление токенов

**Диагностика:**
```python
# Посчитайте токены до отправки
from anthropic import Anthropic

client = Anthropic()
count = client.count_tokens(text)
print(f"Токенов в тексте: {count}")
```

**Решение:**
1. Сократите контекст клиента (только нужные поля)
2. Суммаризируйте длинную историю
3. Используйте сжатие:
```python
def compress_history(messages: list, max_messages: int = 10) -> list:
    if len(messages) <= max_messages:
        return messages

    # Оставляем первое и последние сообщения
    return [messages[0]] + messages[-(max_messages-1):]
```

---

## Проблемы с интеграцией

### WhatsApp webhook не получает сообщения

**Диагностика:**
```bash
# Проверьте что webhook доступен
curl -X POST https://your-domain.com/webhook/message \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

**Решение:**
1. Проверьте SSL сертификат (WhatsApp требует HTTPS)
2. Проверьте что URL зарегистрирован в WhatsApp Business
3. Проверьте firewall (порты 443)

---

### Telegram бот не отвечает

**Диагностика:**
```python
# Проверьте токен
from telegram import Bot

bot = Bot(token=TOKEN)
print(await bot.get_me())
```

**Решение:**
1. Проверьте что токен актуальный
2. Проверьте что бот не заблокирован
3. Проверьте polling/webhook конфликт:
```python
# Используйте ИЛИ polling ИЛИ webhook, не оба
# Для webhook отключите polling:
await bot.delete_webhook()
```

---

### Ошибки при работе с CRM

**Симптомы:**
- `get_client_from_crm()` возвращает пустой словарь
- Таймауты при запросах

**Решение:**
```python
async def get_client_from_crm(user_id: str, timeout: int = 5) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{CRM_API}/clients/{user_id}",
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    # Новый клиент
                    return {"is_new": True}
                else:
                    log.error(f"CRM error: {response.status}")
                    return {}
    except asyncio.TimeoutError:
        log.error("CRM timeout")
        return {}
```

---

## Логи и мониторинг

### Как найти проблему по логам

```python
# Структурированное логирование
import structlog

log = structlog.get_logger()

def process_message(message, client_id):
    log.info("message_received",
             client_id=client_id,
             message_length=len(message))

    result = sanitize_message(message, agent_type)
    log.info("message_sanitized",
             client_id=client_id,
             detected=result["detected"],
             escalation=result["requires_escalation"])

    # ... обработка

    log.info("response_sent",
             client_id=client_id,
             response_length=len(response),
             tokens_used=usage.total_tokens)
```

### Алерты

```python
# Алерт при security_alert
if result.get("security_alert"):
    send_alert(
        channel="security",
        message=f"Security alert from client {client_id}",
        severity="high"
    )

# Алерт при высоком расходе токенов
if usage.total_tokens > 5000:
    send_alert(
        channel="costs",
        message=f"High token usage: {usage.total_tokens}",
        severity="medium"
    )
```
