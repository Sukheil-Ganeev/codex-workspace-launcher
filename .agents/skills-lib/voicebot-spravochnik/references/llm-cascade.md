# LLM-каскад и AI-маршрутизация -- VoiceTranscriptionBot v6.1.0

> Обновлено: 2026-02-28

---

## Архитектура

### Единый LLMClient

**Файл:** `core/llm_client.py` -- центральный AI-клиент для всех 14 модулей.

**Принцип:** Ни один модуль НЕ создаёт собственный `genai.Client()`. Все AI-вызовы через `services.llm`.

**Константы (единый источник model ID):**

```python
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
GEMINI_MODELS_LIGHT = ["gemini-2.5-flash-lite"]
GROQ_MODEL = "llama-3.3-70b-versatile"
```

**Инициализация:**

1. `Summarizer.__init__()` создаёт `genai.Client` + строит `_gemini_models` список
2. `services.init_services()` создаёт `LLMClient` из `_gemini_models` и `_groq_client` Summarizer'а
3. Все модули используют `services.llm` (lazy import внутри функций)

```python
# core/services.py — init_services()
summarizer = Summarizer()
llm = LLMClient(
    gemini_models=summarizer._gemini_models,
    groq_client=summarizer._groq_client,
)
```

### Каскад fallback

```
gemini-2.5-flash ($0.30/1M input)
    ↓ ошибка / таймаут / rate limit
gemini-2.5-flash-lite ($0.10/1M input)
    ↓ ошибка
Groq llama-3.3-70b-versatile (бесплатно)
    ↓ ошибка
None / safe default (caller handles)
```

Pipeline **никогда не падает** из-за ошибки LLM -- каждый вызывающий модуль обрабатывает `None`.

---

## TaskType маршрутизация

6 типов задач с оптимальными параметрами:

```python
class TaskType(str, Enum):
    CLASSIFICATION = "classification"
    ANALYSIS       = "analysis"
    CREATIVE       = "creative"
    VISION         = "vision"
    TRANSFORMATION = "transformation"
    PLANNING       = "planning"
```

| TaskType | prefer_light | temperature | max_tokens | timeout | Модули |
|----------|-------------|-------------|------------|---------|--------|
| CLASSIFICATION | True (lite first) | 0.1 | 200 | 15с | corrector, sentiment, categories, ocr._rate |
| ANALYSIS | False (flash first) | 0.3 | 2048 | 30с | key_facts |
| CREATIVE | False | 0.7 | 4096 | 30с | improver, suggester |
| VISION | False | -- | -- | 60с | ocr._vision, accounting |
| TRANSFORMATION | False | 0.3 | 4096 | 30с | translator, formatter_tour |
| PLANNING | False | 0.2 | 2048 | 30с | calculator, router |

**Примечание:** Summarizer НЕ использует TaskType -- у него своя логика (см. ниже).

---

## Методы LLMClient

### generate(prompt, **kwargs) -- базовый

Низкоуровневый метод, используется другими методами внутри:

```python
async def generate(
    self, prompt: str, *,
    max_tokens: int = 4096,
    temperature: float = 0.3,
    timeout: float | None = None,
    use_all_models: bool = True,
    prefer_light: bool = False,
) -> str | None:
```

Логика:
1. Определяет порядок моделей (reversed если `prefer_light`)
2. Обходит `_gemini_models` в каскаде
3. Каждый вызов оборачивается в `asyncio.to_thread()` (sync Gemini SDK)
4. Rate limiting через `api_limit("gemini")` (asyncio.Semaphore)
5. API мониторинг через `_record_api()`
6. Fallback на Groq (если Gemini не ответил)
7. Возвращает `None` если все бэкенды упали

### generate_for_task(prompt, task_type, **overrides)

Текстовая генерация с параметрами из TASK_CONFIG:

```python
async def generate_for_task(
    self, prompt: str, task_type: TaskType, **overrides,
) -> str | None:
```

- Ищет конфиг для `task_type` в `TASK_CONFIG`
- Мержит с `overrides` от вызывающего
- Делегирует в `generate()`

### generate_with_image(prompt, image_path, **kwargs)

Vision-генерация (Gemini only, без Groq fallback):

```python
async def generate_with_image(
    self, prompt: str, image_path: str, *,
    timeout: float | None = None,
    prefer_light: bool = False,
) -> str | None:
```

- Открывает изображение через `PIL.Image.open()`
- Передаёт `[prompt, img]` в `contents`
- Каскад Gemini-моделей (как в `generate`)
- Groq НЕ используется (нет Vision)

### generate_image_for_task(prompt, image_path, task_type, **overrides)

Vision-генерация с параметрами из TASK_CONFIG:

```python
async def generate_image_for_task(
    self, prompt: str, image_path: str,
    task_type: TaskType = TaskType.VISION, **overrides,
) -> str | None:
```

- Ищет конфиг из `TASK_CONFIG`
- Делегирует в `generate_with_image()`

---

## Модели

| Model ID | Провайдер | Стоимость (input/output per 1M) | Free Tier | Назначение |
|----------|-----------|-------------------------------|-----------|-----------|
| gemini-2.5-flash | Google | $0.30 / $2.50 | 250 RPD | Primary LLM + Vision |
| gemini-2.5-flash-lite | Google | $0.10 / $0.40 | 1000 RPD | Light tasks (CLASSIFICATION) |
| llama-3.3-70b-versatile | Groq | бесплатно | rate limited | Emergency fallback |
| whisper-large-v3 | Groq | бесплатно | rate limited | Cloud STT |
| faster-whisper large-v3 | Local | -- | GPU needed | Local STT |

---

## Все 14 модулей и их AI-вызовы

| # | Модуль | Файл | Метод LLMClient | TaskType | Что делает |
|---|--------|------|-----------------|----------|-----------|
| 1 | Corrector | `core/corrector.py` | `generate_for_task` | CLASSIFICATION | Исправление ошибок распознавания |
| 2 | Sentiment | `core/sentiment.py` | `generate_for_task` | CLASSIFICATION | Анализ настроения (pos/neu/neg) |
| 3 | Categories | `core/categories.py` | `generate_for_task` | CLASSIFICATION | Smart-категоризация текста |
| 4 | OCR rate | `core/ocr.py` | `generate_for_task` | CLASSIFICATION | Оценка качества OCR-текста |
| 5 | OCR vision | `core/ocr.py` | `generate_image_for_task` | VISION | Распознавание текста с изображений |
| 6 | Accounting | `core/accounting.py` | `generate_image_for_task` | VISION | Парсинг чеков |
| 7 | Key Facts | `core/key_facts.py` | `generate_for_task` | ANALYSIS | Извлечение дат/сумм/имён |
| 8 | Translator | `core/translator.py` | `generate_for_task` | TRANSFORMATION | Перевод текста (4 языка) |
| 9 | Tour Formatter | `core/formatter_tour.py` | `generate_for_task` | TRANSFORMATION | AI-форматирование турпродуктов |
| 10 | Improver | `core/improver.py` | `generate_for_task` | CREATIVE | Улучшение сообщений |
| 11 | Suggester | `admin/suggester.py` | `generate_for_task` | CREATIVE | AI-суфлёр для админа |
| 12 | Calculator | `core/calculator.py` | `generate_for_task` | PLANNING | NL-парсинг расчётов |
| 13 | Router | `core/router.py` | `generate_for_task` | PLANNING | NL-парсинг маршрутов |
| 14 | Summarizer | `bot/summarizer.py` | **свой каскад** | -- | Суммаризация (см. ниже) |

---

## Summarizer (особый случай)

Summarizer НЕ использует `generate_for_task()` -- у него собственная логика каскада:

- Владеет Gemini-клиентом (делит его с LLMClient через `services.init_services`)
- Собственные методы: `summarize_gemini()`, `summarize_groq()`, `summarize()`
- Адаптивные промпты по длительности аудио
- Структурированный `SummaryResult` dataclass

### SummaryResult

```python
@dataclass
class SummaryResult:
    summary: str
    todos: list[str] = field(default_factory=list)
    entities: dict = field(default_factory=lambda: {
        "dates": [], "amounts": [], "names": []
    })
    method: str = ""  # "gemini/gemini-2.5-flash", "groq", "error"
```

### Адаптивные промпты

| Длительность | Промпт | Формат вывода |
|--------------|--------|---------------|
| `None` | `SYSTEM_PROMPT` | 2-3 предложения |
| `< 30 сек` | `_PROMPT_SHORT` | 1 предложение |
| `30-180 сек` | `SYSTEM_PROMPT` | 2-3 предложения |
| `> 180 сек` | `_PROMPT_LONG` | Буллет-поинты |
| `> 180 сек` (диктовка) | **Пропускается** | Суммаризация не создаётся |

### Каскад Summarizer

```
summarize(text, duration)
    |
    +-- summarize_gemini()
    |     gemini-2.5-flash → gemini-2.5-flash-lite
    |
    +-- summarize_groq()
    |     llama-3.3-70b-versatile
    |
    +-- Safe fallback (method="error")
          SummaryResult(summary="Ошибка генерации резюме", ...)
```

### System Prompt (суммаризация)

Промпт извлекает три элемента в формате JSON:

1. `summary` -- резюме 2-3 предложения
2. `todos` -- список задач/действий
3. `entities` -- `{dates: [], amounts: [], names: []}`

Контекст в промпте: "туристическая компания в Дубае (ОАЭ)".

```json
{
  "summary": "Клиент интересуется сафари в пустыне на 4 человека...",
  "todos": ["Забронировать сафари на 15 марта", "Отправить прайс"],
  "entities": {
    "dates": ["15 марта"],
    "amounts": ["500 AED"],
    "names": ["Ахмед"]
  }
}
```

---

## Lesson Injection

6 модулей инжектируют уроки в промпты:

| Модуль | Тип уроков | Max уроков |
|--------|-----------|-----------|
| summarizer | `voice_summary` | 7 |
| corrector | `voice_correction` | 5 |
| categories | `voice_category` | 5 |
| sentiment | `voice_sentiment` | 5 |
| accounting | `receipt_*` (5 типов) | 7 (дедуп) |
| key_facts | `key_facts` | 5 |

Паттерн:

```python
lessons = svc.lessons.get_relevant_lessons("voice_correction", limit=5)
if lessons:
    lessons_text = svc.lessons.format_lessons_for_prompt(lessons)
    prompt += "\n\n" + lessons_text
    for l in lessons:
        svc.lessons.mark_applied(l["id"])
```

Формат инъекции:

```
УРОКИ ИЗ ПРОШЛОГО ОПЫТА:
1. На чеках ENOC: правильная сумма с VAT, не SUBTOTAL
2. "Марсель" -- это имя сотрудника, не город
...
```

---

## JSON-парсинг ответов

**Файл:** `core/json_utils.py`

```python
def parse_llm_json(raw: str) -> dict | None:
```

Трёхуровневая стратегия:

```
parse_llm_json(raw)
    |
    +--[1] Прямой json.loads(raw)
    +--[2] Извлечение из ```json ... ``` блока
    +--[3] Извлечение первого { ... } или [ ... ] подстроки
    +--[X] Returns None
```

Используется в: summarizer, corrector, sentiment, categories, key_facts, accounting, calculator, router, improver, ocr.

---

## Rate Limiting

`asyncio.Semaphore` в `core/services.py` через `api_limit()`:

| API | Max concurrent | Зачем |
|-----|---------------|-------|
| Gemini | 10 | LLM + Vision |
| Groq | 5 | LLM + STT |
| Google Maps | 3 | Directions, Geocode |
| Google Vision | 3 | OCR |

Использование:

```python
from core.services import api_limit

async with api_limit("gemini"):
    raw = await asyncio.to_thread(_sync_gemini)
```

---

## Стоимость (~14,600 вызовов/мес)

| Ресурс | Free Tier | Использование | Оплата |
|--------|----------|---------------|--------|
| gemini-2.5-flash | 250 RPD | ~300/день | ~$1-2/мес |
| gemini-2.5-flash-lite | 1000 RPD | ~170/день | $0 |
| Groq | бесплатно | ~20/день | $0 |
| **Итого** | | | **~$5-7/мес** |

---

## Миграция моделей

Для смены модели -- изменить ТОЛЬКО `core/llm_client.py`:

```python
GEMINI_MODELS = ["new-model-name", "fallback-model"]
```

Все 14 модулей подхватят автоматически. Summarizer использует те же модели через shared `_gemini_models`.

---

## Ошибки и fallback

| Ситуация | Поведение |
|----------|----------|
| Gemini 429 (rate limit) | Переход к следующей модели в каскаде |
| Gemini timeout | Переход к следующей модели |
| Gemini server error (500) | Переход к следующей модели |
| Все Gemini упали | Fallback на Groq Llama |
| Groq тоже упал | `None` (caller handles) |
| JSON парсинг не удался | Попытка следующей модели |
| Пустой ответ от LLM | Попытка следующей модели |
| Изображение не открывается | `None` (generate_with_image) |
| LLMClient не инициализирован | Модуль возвращает safe default |

---

## Retry механизм

Только STT и суммаризация обёрнуты в `retry_async()`:

```python
summary_result = await retry_async(
    services.summarizer.summarize,
    corrected_text,
    duration=tr_result.duration,
    max_retries=2,
)
```

Остальные LLM-вызовы (коррекция, sentiment, key facts и др.) НЕ используют retry -- каскад сам по себе обеспечивает отказоустойчивость.

---

## Конфигурация

| Переменная | Default | Используется |
|------------|---------|-------------|
| `GEMINI_API_KEY` | `""` | Все 14 модулей через LLMClient/Summarizer |
| `GROQ_API_KEY` | `""` | Fallback LLM + STT |

---

## История

| Версия | Изменение |
|--------|-----------|
| v1.0 | Прямой доступ к `summarizer._gemini_models` (anti-pattern) |
| v5.9 | LLMClient создан, 7 модулей переведены |
| v6.0 | Все новые модули через LLMClient, split handlers |
| v6.1 Phase A | Замена deprecated gemini-2.0-flash/lite на gemini-2.5-flash-lite |
| v6.1 Phase B | Консолидация 5 bypass-модулей на `generate_for_task` |
| v6.1 Phase C | TaskType routing (6 типов, 13 вызовов + Summarizer) |
