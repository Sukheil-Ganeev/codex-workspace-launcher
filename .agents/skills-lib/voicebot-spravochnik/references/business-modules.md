# Business Modules -- Бизнес-логика

> Справочник по бизнес-модулям VoiceTranscriptionBot
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`
> Файлы: `core/categories.py`, `core/urgency.py`, `core/sentiment.py`, `core/key_facts.py`, `core/translator.py`, `core/note_detector.py`, `core/combiner.py`, `core/reminders.py`, `core/calculator.py`, `core/router.py`, `core/improver.py`, `core/llm_client.py`

---

## 9 бизнес-категорий

**Файл:** `core/categories.py`

### CATEGORY_KEYWORDS

| # | Ключ | Название (RU) | Ключевые слова (RU) | Ключевые слова (EN) |
|---|------|--------------|---------------------|---------------------|
| 1 | `excursions` | Экскурсии | экскурсия, сафари, тур, гид, маршрут, обзорная, поездка, абу-даби | desert safari, city tour, tour, guide, abu dhabi |
| 2 | `tickets` | Билеты | билет, парк, бурдж халифа, аквапарк, музей, входной, аттракцион, лувр | burj khalifa, aquaventure, museum, ticket, pass, louvre |
| 3 | `parks` | Парки развлечений | парк развлечений | ferrari world, img worlds, legoland, motiongate, warner bros |
| 4 | `cars` | Автомобили | машина, авто, автомобиль, аренда авто, ламборгини, бентли, мерседес, бмв, порше | car, rental, range rover, lamborghini, bentley, mercedes, bmw |
| 5 | `transfer` | Трансфер | трансфер, аэропорт, встреча, встретить, отвезти, довезти | transfer, airport, pickup, dropoff |
| 6 | `mvu` | МВУ | права, мву, водительское, удостоверение | international driving, license, driving permit, idp |
| 7 | `yachts` | Яхты | яхта, лодка, катер, рыбалка, марина, круиз | yacht, boat, fishing, marina, cruise |
| 8 | `water` | Водные развлечения | водный, гидроцикл, дайвинг, снорклинг, флайборд, каяк, парасейлинг | jet ski, diving, snorkeling, flyboard, banana boat, parasailing |
| 9 | `abayas` | Абаи/Одежда | абая, платье, ткань, одежда, шитьё, пошив, наряд | abaya, fashion, dress |

### Маршрутизация по команде (CATEGORY_GROUPS)

| Категория | Группа | Ответственный |
|-----------|--------|---------------|
| excursions | excursions | Сухейль (admin) |
| tickets | tickets | Сухейль (admin) |
| parks | **tickets** | Сухейль (admin) |
| cars | cars | Марсель |
| transfer | transfer | Марсель |
| mvu | mvu | Марсель |
| yachts | yachts | Мухаммад-Амин |
| water | water | Мухаммад-Амин |
| abayas | abayas | Камила |
| general (нет совпадения) | -- | Сухейль (fallback) |

### Функция categorize()

```python
def categorize(text: str) -> tuple[str, float, str | None]:
    # Returns: (category, confidence, team_category)
```

**Логика:**
- Case-insensitive keyword matching по всем 9 категориям
- Подсчёт совпадений для каждой категории
- Выбирается категория с максимумом совпадений

**Формула confidence:**
```
confidence = min(1.0, 0.3 + (hit_count - 1) * 0.25)
```

| Совпадений | Confidence |
|------------|-----------|
| 1 | 0.30 |
| 2 | 0.55 |
| 3 | 0.80 |
| 4+ | 1.00 |

Fallback: `("general", 0.0, None)` если нет совпадений.

### Функция categorize_smart() (LLM)

```python
async def categorize_smart(text: str, summary: str = "") -> tuple[str, float]:
```

- Gemini AI каскад (gemini-2.5-flash -> gemini-2.0-flash -> gemini-2.0-flash-lite) через `core/llm_client.py`
- Инжектирует уроки (voice_category, receipt_category)
- Fallback: regex `categorize()`

**Примечание:** Основной pipeline использует `categorize()`, не `categorize_smart()`.

---

## Urgency Detection (22 ключевых слова, 3 языка)

**Файл:** `core/urgency.py`

```python
def detect_urgency(text: str) -> tuple[bool, list[str]]:
    # Returns: (is_urgent, matched_keywords)
```

### Ключевые слова

| Язык | Ключевые слова |
|------|---------------|
| **Русский (12)** | срочно, срочный, срочная, срочное, срочные, немедленно, быстрее, скорее, как можно скорее, очень важно, экстренно, безотлагательно |
| **Английский (7)** | urgent, urgently, asap, immediately, right away, emergency, rush |
| **Арабский (3)** | عاجل, فوري, بسرعة |

### Логика

- Все ключевые слова скомпилированы в единый regex: `re.compile("|".join(...), re.IGNORECASE)`
- Одно совпадение = urgent (True)
- Возвращает все уникальные совпавшие слова
- **Чистый regex, без LLM.** Синхронная функция.

### Действие при обнаружении

При `is_urgent=True` в Telegram боте: автоматическая рассылка всем участникам команды через `bot.send_message()`.

---

## Sentiment Analysis (анализ тональности)

**Файл:** `core/sentiment.py`

```python
async def analyze_sentiment(
    text: str,
    summarizer,
) -> tuple[str, str]:
    # Returns: (sentiment, reason)
    # sentiment: "positive" | "neutral" | "negative"
    # reason: краткое пояснение (3-5 слов)
```

### Каскад

1. Gemini **lightest** (gemini-2.0-flash-lite) -- простая классификация
2. Groq Llama fallback (temperature=0.1, max_tokens=100)
3. Default: `("neutral", "")`

### Пропускается когда

- `is_note=True` (заметки всегда neutral)
- Текст короче 10 символов
- Любая ошибка -> `("neutral", "")`

### Emoji и метки

```python
# Emoji
"positive" -> "smiling face"
"neutral"  -> "neutral face"
"negative" -> "angry face"

# Labels
"positive" -> "Позитивное"
"neutral"  -> "Нейтральное"
"negative" -> "Негативное"
```

---

## Key Facts Extraction (извлечение ключевых фактов)

**Файл:** `core/key_facts.py`

```python
async def extract_key_facts(text: str) -> dict:
    # Returns: {"dates": [], "amounts": [], "names": [], "phones": []}
```

### Каскад

1. Gemini каскад (gemini-2.5-flash -> gemini-2.0-flash -> gemini-2.0-flash-lite)
2. Regex fallback `_extract_regex_fallback()`

### Regex паттерны

| Тип | Паттерн | Примеры |
|-----|---------|---------|
| Даты | `DD.MM.YYYY`, `DD/MM/YYYY`, `DD-MM-YYYY` | 15.03.2026, 22/02/2026 |
| Относительные даты | Ключевые слова | завтра, послезавтра, вчера, сегодня, today, tomorrow |
| Суммы | `число + валюта` | 500 AED, 1000$, 3000 руб |
| Телефоны | `+digit(10-15 цифр)` | +971553096985 |
| Имена (RU) | `[А-ЯЁ][а-яё]{2,}` | Ахмед, Марсель |
| Имена (EN) | `[A-Z][a-z]{2,}` | Ahmed, Marcel |

### Исключения для имён (58 слов)

Общие слова, не являющиеся именами: Привет, Здравствуйте, Спасибо, Дубай, Hello, Thanks, и т.д.

### Graceful Import

```python
try:
    from core.key_facts import extract_key_facts
except ImportError:
    extract_key_facts = None
```

Если модуль недоступен -- `result.key_facts` остаётся None.

---

## Translation (перевод)

**Файл:** `core/translator.py`

```python
def needs_translation(language: str) -> bool:
    # True если language не в {"ru", "russian"}

async def translate_to_russian(
    text: str, language: str, summarizer,
) -> str | None:
```

### Каскад

1. Gemini **best** (gemini-2.5-flash) -- перевод требует лучшую модель
2. Groq Llama (temperature=0.3, max_tokens=4096)
3. Returns None

### Промпт

```
Переведи следующий текст на русский язык.
Верни ТОЛЬКО перевод, без комментариев и пояснений.
```

### Пропускается когда

Язык `"ru"` или `"russian"` -> перевод не нужен.

---

## Voice Notes (заметки, 9 триггеров)

**Файл:** `core/note_detector.py`

```python
def detect_note(text: str) -> tuple[bool, str, list[str]]:
    # Returns: (is_note, clean_text, tags)
```

### 9 триггерных слов

| # | Триггер | Язык |
|---|---------|------|
| 1 | заметка | RU |
| 2 | запомни | RU |
| 3 | напоминание | RU |
| 4 | напомни | RU |
| 5 | todo | EN |
| 6 | note | EN |
| 7 | запиши | RU |
| 8 | записка | RU |
| 9 | памятка | RU |

**Паттерн детекции:** `^{trigger}[\s:,.\-!]*` -- триггер в начале текста.

### Автоматические теги (TAG_KEYWORDS)

| Ключевое слово | Тег |
|----------------|-----|
| яхта, yacht | яхта |
| машина, car, аренда | авто |
| трансфер, аэропорт | трансфер |
| экскурсия, тур, сафари | экскурсия |
| билет, парк | билеты |
| позвонить, перезвонить | звонок |
| оплата, оплатить, деньги | оплата |
| встреча, meeting | встреча |
| срочно, urgent, asap | срочно |

### Влияние на pipeline

Когда `is_note=True`:
- **Пропускаются:** sentiment, summarization, urgency, translation
- **Выполняются:** categorization, key facts, client detection, DB save
- DB save: `source_type="note"`, `is_note=1`, `tags` через запятую

---

## Combiner (объединение, 3 режима)

**Файл:** `core/combiner.py`

### 3 режима объединения

| Режим | Функция | Описание |
|-------|---------|----------|
| By count | `combine_recent(db, summarizer, user_id, count)` | Последние N (2-20) |
| By period | `merge_by_period(db, summarizer, user_id, period)` | today/yesterday/week/month |
| By category | `merge_by_category(db, summarizer, user_id, category, days)` | Категория за N дней (1-90) |

### Периоды

| Период | Label | SQL фильтр |
|--------|-------|-----------|
| today | за сегодня | `date(created_at) = date('now')` |
| yesterday | за вчера | `date(created_at) = date('now', '-1 day')` |
| week | за неделю | `date(created_at) >= date('now', '-7 days')` |
| month | за месяц | `date(created_at) >= date('now', '-30 days')` |

### Формат вывода

1. **Header:** "Объединено N голосовых [за период/категорию]"
2. **Summary:** Общее резюме от Summarizer
3. **TODOs:** Список задач (если есть)
4. **Entities:** Даты, суммы, имена (если есть)

### Preview

```python
def preview(records) -> str:
```

Показывает нумерованный список записей перед подтверждением:
```
Будут объединены:
1. #42 (14:30) -- Нужно забронировать сафари...
2. #43 (15:15) -- Клиент просит трансфер...
Всего: 2 записей
```

**Минимум:** 2 записи (при меньшем количестве -- предупреждение).

---

## Reminders (напоминания, 7 форматов дат)

**Файл:** `core/reminders.py`

### Поддерживаемые форматы

| # | Формат | Пример | Паттерн |
|---|--------|--------|---------|
| 1 | Русская дата | "15 марта", "22 февраля" | `\d{1,2}\s+{month_prefix}` |
| 2 | Английская дата | "March 15", "February 22" | `{month_prefix}\s+\d{1,2}` |
| 3 | День недели | "в пятницу", "на субботу" | keyword match |
| 4 | Завтра | "завтра" | keyword match |
| 5 | Послезавтра | "послезавтра" | keyword match |
| 6 | Через N дней | "через 3 дня" | `через\s+\d+\s+дн` |
| 7 | Через неделю | "через неделю" | `через\s+неделю` |

### Русские месяцы (префиксы)

| Префикс | Месяц | Префикс | Месяц |
|---------|-------|---------|-------|
| январ | 1 | июл | 7 |
| феврал | 2 | август | 8 |
| март | 3 | сентябр | 9 |
| апрел | 4 | октябр | 10 |
| мая, май | 5 | ноябр | 11 |
| июн | 6 | декабр | 12 |

### Русские дни недели (префиксы)

| Префикс | День (0=Mon) |
|---------|-------------|
| понедельник | 0 |
| вторник | 1 |
| среда, среду | 2 |
| четверг | 3 |
| пятниц | 4 |
| суббот | 5 |
| воскресень | 6 |

### Логика дат

- Если дата в прошлом -> переносится на следующий год
- Дни недели: вычисляется ближайшее будущее вхождение
- Результаты дедуплицируются по дате
- Каждый результат включает контекст (30 символов до/после)

### Формат вывода

```python
[{"date": "2026-03-15", "text": "15 марта", "source": "...context..."}]
```

---

## Tour Calculator (v5.4.0)

**Файл:** `core/calculator.py`

### Функции

```python
async def convert_currency(amount: float, from_cur: str, to_cur: str) -> dict
async def calculate_tour(product_name: str, guests: int, extras: list) -> dict
async def calculate_agent(product_name: str, guests: int, agent_commission: float) -> dict
```

### Возможности

- **Конвертация валют:** AED <-> RUB/USD/KZT/EUR; ExchangeRate-API v6 + v4 fallback; кеш 1 час
- **Расчёт туров:** из прайс-листа (`data/prices.json`) + доп. услуги (трансфер, фото, гид, VIP)
- **Агентский расчёт:** себестоимость, наценка, комиссия агента (%), прибыль
- **FSM-состояния:** 4 состояния в Telegram (конвертация/тур/агент/маршрут)
- **Команды:** `/calc`, `/rate`, `/calc 500 AED в рубли`, `/calc тур Сафари 4 человека`

---

## Route Builder (v5.4.0)

**Файл:** `core/router.py`

### Функции

```python
async def build_route(origin: str, destination: str) -> dict
async def optimize_day_plan(places: list, start_time: str = "09:00") -> dict
async def build_transit_route(origin: str, destination: str) -> dict
```

### Возможности

- **Google Maps Directions API:** расстояние, время, пробки в реальном времени
- **Salik tolls:** 8 ворот, 5 AED каждые, автоматическое определение на маршруте
- **Расход топлива:** расчёт на основе расстояния
- **TSP оптимизация:** Nearest Neighbor + 2-opt для оптимального порядка точек дня
- **Якорные точки:** Safari Zoo утром, Burj Khalifa на закате
- **Transit:** метро, автобус, nol card тарификация
- **Нормализация мест:** ~150 алиасов (рус/англ), `normalize_place()` + `PLACE_ALIASES`
- **Команды:** `/route`, `/route JBR -> Dubai Mall`, `/route план: Safari Zoo, Burj Khalifa`

---

## AI Text Improver (v5.6.0)

**Файл:** `core/improver.py`

### Функция

```python
async def improve_text(text: str, recipient: str, tone: str) -> dict
```

### Возможности

- **4 типа получателя:** личное, клиенту, агенту, поставщику
- **3 тона:** формальный, дружелюбный, нейтральный
- **20 триггеров:** улучши, improve, polish, proofread, исправь сообщение, отредактируй и др.
- **Gemini каскад + Groq fallback** через `core/llm_client.py`
- **Кнопки после результата:** [Другой стиль] + [Формат WA] [Формат TG]
- **Команды:** `/improve`, текстовые триггеры

---

## Unified LLM Client (v5.9.0)

**Файл:** `core/llm_client.py`

### Функция

```python
async def generate(prompt: str, task_type: TaskType, ...) -> str
```

### TaskType маршрутизация

| TaskType | Модели каскада |
|----------|---------------|
| `summarize` | gemini-2.5-flash -> gemini-2.0-flash -> gemini-2.0-flash-lite -> Groq Llama |
| `correct` | gemini-2.5-flash -> gemini-2.0-flash -> Groq Llama |
| `sentiment` | gemini-2.0-flash-lite -> Groq Llama |
| `translate` | gemini-2.5-flash -> Groq Llama |
| `categorize` | gemini-2.5-flash -> gemini-2.0-flash -> gemini-2.0-flash-lite |
| `improve` | gemini-2.5-flash -> gemini-2.0-flash -> Groq Llama |
| `format` | gemini-2.5-flash -> gemini-2.0-flash -> Groq Llama |

Единый интерфейс вместо прямого доступа к `summarizer._call_gemini()`. Доступ через `services.llm.generate()`.

---

## Cross-Module Integration Map

```
Voice Input
    |
    +---> [categories.py] -- категоризация -> [team.py] -- маршрутизация
    +---> [urgency.py] -- детекция срочности
    +---> [key_facts.py] -- даты, суммы, имена, телефоны
    |         +---> [reminders.py] -- создание напоминаний
    +---> [translator.py] -- перевод (если не русский)
    +---> [note_detector.py] -- детекция заметок
    +---> [client_detector.py] -- идентификация клиента
    +---> [combiner.py] -- объединение транскрипций
    +---> [lessons.py] -- инъекция уроков

Photo Input
    +---> [accounting.py] -- парсинг чеков
    |         +---> [expense_categories.py] -- категоризация расхода
    +---> [ocr.py] -- OCR текста

Video URL
    +---> [video_downloader.py] -- скачивание
    +---> [video_manager.py] -- SQLite трекинг
    +---> [cloud_storage.py] -- облако (если >50MB)

Calculator/Router
    +---> [calculator.py] -- конвертация валют, туры, агентский расчёт
    +---> [router.py] -- Google Maps маршруты, TSP, транзит, Salik
    +---> [improver.py] -- AI-улучшение текста

LLM Layer
    +---> [llm_client.py] -- единый интерфейс, TaskType маршрутизация
              +---> Gemini каскад (2.5-flash -> 2.0-flash -> 2.0-flash-lite)
              +---> Groq Llama fallback
```

---

## Lessons Integration (инъекция уроков)

| Модуль | Типы уроков |
|--------|------------|
| `categories.py` (smart) | voice_category, receipt_category |
| `accounting.py` | receipt_amount, receipt_vendor, receipt_category, receipt_date, receipt_currency |
| `key_facts.py` | key_facts |
| `summarizer.py` | voice_summary |
| `corrector.py` | voice_correction |
| `sentiment.py` | voice_sentiment |
