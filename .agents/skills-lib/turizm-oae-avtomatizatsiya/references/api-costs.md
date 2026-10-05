# Стоимость API вызовов

## Таблица стоимости операций

| Операция | Модель | Стоимость за единицу | Примечание |
|----------|--------|----------------------|------------|
| Классификация | Claude Haiku | $0.0003/сообщение | ~300 токенов in + 200 out |
| Суммаризация | Claude Sonnet | $0.003/диалог | ~1500 токенов in + 500 out |
| Генерация ответа | Claude Sonnet | $0.002/ответ | ~500 токенов in + 300 out |
| Сложный анализ | Claude Opus | $0.03/запрос | Только для VIP кейсов |
| Транскрипция | Whisper | $0.006/минута | Любой язык |
| OCR документа | GPT-4 Vision | $0.01/изображение | ~1 изображение |
| OCR документа | Claude Vision | $0.008/изображение | Альтернатива |

## Детальный расчет по моделям

### Claude API (Anthropic)

| Модель | Input (за 1M токенов) | Output (за 1M токенов) |
|--------|----------------------|------------------------|
| Claude Haiku | $0.25 | $1.25 |
| Claude Sonnet | $3.00 | $15.00 |
| Claude Opus | $15.00 | $75.00 |

**Типичное потребление токенов:**

| Операция | Input tokens | Output tokens | Итого стоимость |
|----------|-------------|---------------|-----------------|
| Классификация | ~300 | ~200 | ~$0.0003 (Haiku) |
| Автоответ | ~500 | ~300 | ~$0.006 (Sonnet) |
| Суммаризация диалога | ~2000 | ~500 | ~$0.014 (Sonnet) |
| Глубокий анализ | ~3000 | ~1000 | ~$0.12 (Opus) |

### OpenAI API

| Сервис | Стоимость |
|--------|-----------|
| Whisper (транскрипция) | $0.006/минута |
| GPT-4 Vision | $0.01/изображение (low detail) |
| GPT-4 Vision | $0.03/изображение (high detail) |
| TTS (текст в речь) | $0.015/1000 символов |

### Другие сервисы

| Сервис | Стоимость |
|--------|-----------|
| Airtable | Бесплатно до 1000 записей/база |
| Airtable Pro | $20/месяц (50,000 записей) |
| make.com Free | 1,000 операций/месяц |
| make.com Core | $9/месяц (10,000 операций) |
| make.com Pro | $16/месяц (10,000+ операций) |
| Twilio SMS (ОАЭ) | ~$0.05/SMS |
| Twilio WhatsApp | $0.005/сообщение |

---

## Месячный бюджет (оценка)

### Сценарий: Малый бизнес (500 сообщений/день)

```
Месячный объем: ~15,000 сообщений

КЛАССИФИКАЦИЯ (100%):
  15,000 × $0.0003 = $4.50

АВТООТВЕТЫ (40% inquiry):
  6,000 × $0.002 = $12.00

ГОЛОСОВЫЕ (10%, ~2 мин среднее):
  1,500 × 2 × $0.006 = $18.00

OCR ДОКУМЕНТЫ (5%):
  750 × $0.01 = $7.50

СУММАРИЗАЦИЯ (1% сложных диалогов):
  150 × $0.003 = $0.45

================================
ИТОГО API: ~$42.50/месяц
================================

Дополнительно:
- make.com Core: $9/месяц
- Airtable Pro: $20/месяц

ОБЩИЙ БЮДЖЕТ: ~$72/месяц
```

### Сценарий: Средний бизнес (2000 сообщений/день)

```
Месячный объем: ~60,000 сообщений

КЛАССИФИКАЦИЯ (100%):
  60,000 × $0.0003 = $18.00

АВТООТВЕТЫ (35%):
  21,000 × $0.002 = $42.00

ГОЛОСОВЫЕ (15%, ~2 мин):
  9,000 × 2 × $0.006 = $108.00

OCR ДОКУМЕНТЫ (8%):
  4,800 × $0.01 = $48.00

СУММАРИЗАЦИЯ (2%):
  1,200 × $0.003 = $3.60

VIP АНАЛИЗ (0.5%):
  300 × $0.03 = $9.00

================================
ИТОГО API: ~$228.60/месяц
================================

Дополнительно:
- make.com Pro: $16/месяц
- Airtable Business: $45/месяц

ОБЩИЙ БЮДЖЕТ: ~$290/месяц
```

### Сценарий: Крупный бизнес (10,000 сообщений/день)

```
Месячный объем: ~300,000 сообщений

КЛАССИФИКАЦИЯ (100%):
  300,000 × $0.0003 = $90.00

АВТООТВЕТЫ (30%):
  90,000 × $0.002 = $180.00

ГОЛОСОВЫЕ (20%, ~2 мин):
  60,000 × 2 × $0.006 = $720.00

OCR ДОКУМЕНТЫ (10%):
  30,000 × $0.01 = $300.00

СУММАРИЗАЦИЯ (3%):
  9,000 × $0.003 = $27.00

VIP АНАЛИЗ (1%):
  3,000 × $0.03 = $90.00

================================
ИТОГО API: ~$1,407/месяц
================================

Дополнительно:
- make.com Teams: $29/месяц
- Airtable Enterprise: custom pricing
- Dedicated support

ОБЩИЙ БЮДЖЕТ: ~$1,500+/месяц
```

---

## Стратегии оптимизации стоимости

### 1. Правильный выбор модели

```python
def select_model(task_type: str, priority: str) -> str:
    """Выбирает оптимальную модель для задачи"""

    if task_type == "classification":
        return "claude-3-5-haiku-20241022"  # Самая дешевая

    if task_type == "auto_response":
        if priority == "critical":
            return "claude-sonnet-4-20250514"  # Качество важнее
        return "claude-3-5-haiku-20241022"  # Экономия

    if task_type == "deep_analysis":
        return "claude-opus-4-20250514"  # Только для сложных случаев

    return "claude-3-5-haiku-20241022"  # По умолчанию
```

### 2. Кэширование частых запросов

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=10000)
def get_cached_classification(message_hash: str) -> dict:
    """Кэш для повторяющихся сообщений"""
    # Возвращает None если нет в кэше
    return None

def classify_with_cache(message: str) -> dict:
    msg_hash = hashlib.md5(message.encode()).hexdigest()

    cached = get_cached_classification(msg_hash)
    if cached:
        return cached  # Бесплатно!

    result = classify_message(message)
    # Сохраняем в кэш
    return result
```

### 3. Batch обработка

```python
# Вместо 100 отдельных запросов
# Используйте batch API (до 80% экономии на overhead)

async def batch_classify(messages: list[str]) -> list[dict]:
    """Классификация пачкой - дешевле!"""

    combined_prompt = "\n\n---\n\n".join([
        f"[{i}] {msg}" for i, msg in enumerate(messages)
    ])

    response = await client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"Классифицируй эти {len(messages)} сообщений:\n\n{combined_prompt}"
        }]
    )

    # Парсим результат
    return parse_batch_response(response)
```

### 4. Фильтрация на входе

```python
def should_process(message: dict) -> bool:
    """Фильтрует сообщения ДО отправки в API"""

    # Спам
    if is_spam(message['text']):
        return False

    # Дубликаты
    if is_duplicate(message):
        return False

    # Слишком короткие
    if len(message['text']) < 3:
        return False

    # Системные сообщения
    if message.get('type') == 'system':
        return False

    return True

# Экономия: ~20-30% запросов
```

### 5. Понижение качества для низкого приоритета

```python
def get_response_config(priority: str) -> dict:
    """Настройки в зависимости от приоритета"""

    if priority == "low":
        return {
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": 256,
            "temperature": 0.3
        }

    if priority == "medium":
        return {
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": 512,
            "temperature": 0.5
        }

    if priority in ["high", "critical"]:
        return {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "temperature": 0.7
        }
```

---

## Мониторинг расходов

### Настройка алертов

```python
# Ежедневный чек расходов
async def check_daily_costs():
    usage = await anthropic_client.get_usage()

    if usage['today_cost'] > 50:  # $50/день лимит
        send_alert(
            channel="slack",
            message=f"Daily API cost alert: ${usage['today_cost']:.2f}"
        )

    if usage['month_cost'] > 1000:  # $1000/месяц лимит
        send_alert(
            channel="sms",
            message=f"Monthly budget exceeded: ${usage['month_cost']:.2f}"
        )
```

### Dashboard расходов

```python
# Данные для дашборда
cost_metrics = {
    "daily": {
        "classification": sum_daily_classification_cost(),
        "responses": sum_daily_response_cost(),
        "transcription": sum_daily_whisper_cost(),
        "ocr": sum_daily_ocr_cost()
    },
    "monthly": {
        "total": get_monthly_total(),
        "by_service": get_monthly_by_service(),
        "trend": get_cost_trend()
    },
    "budget": {
        "daily_limit": 50,
        "monthly_limit": 1000,
        "current_utilization": get_budget_utilization()
    }
}
```
