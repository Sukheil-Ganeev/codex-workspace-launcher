# Accounting -- Система учёта расходов

> Справочник по бухгалтерскому модулю VoiceTranscriptionBot
> Путь проекта: `D:/Downloads/VoiceTranscriptionBot/`
> Файлы: `core/accounting.py`, `core/expense_categories.py`, `core/export_expenses.py`

---

## Receipt Parser (парсинг чеков)

**Файл:** `core/accounting.py`

### Функция

```python
async def parse_receipt(image_path: str) -> dict:
```

### AI-вызов

Использует `services.llm.generate_image_for_task(prompt, image_path, TaskType.VISION)` -- единый LLMClient с каскадом Gemini Vision:
- `gemini-2.5-flash` -> `gemini-2.5-flash-lite`
- Groq не используется (нет Vision)
- Каскад и rate limiting управляются LLMClient автоматически

> Исправлен баг с блокировкой event loop в v6.1.0 (sync calls заменены на asyncio.to_thread через LLMClient)

### Процесс

1. Построение промпта с инъекцией уроков из прошлого опыта (5 типов)
2. Отправка изображения через `svc.llm.generate_image_for_task()` (PIL.Image + Gemini Vision)
3. Парсинг JSON-ответа через `parse_llm_json()`
4. Валидация и нормализация ответа (`_validate_receipt`)

### Выходной JSON от Gemini

```json
{
    "is_receipt": true,
    "vendor": "название магазина/компании",
    "total_amount": 0.00,
    "currency": "AED",
    "date": "YYYY-MM-DD",
    "items": [{"name": "item", "qty": 1, "price": 0.00}],
    "payment_method": "cash | card | transfer",
    "reference": "номер чека/транзакции",
    "tax_amount": null,
    "category_hint": "fuel|maintenance|carwash|insurance|parking|tolls|office|food|communication|transport|other"
}
```

### Валидация (_validate_receipt)

| Шаг | Описание |
|-----|----------|
| Нормализация суммы | Конвертация в float |
| Валидация валюты | Проверка по EXCHANGE_RATES |
| Парсинг даты | 4 формата: `%Y-%m-%d`, `%d/%m/%Y`, `%d.%m.%Y`, `%m/%d/%Y` |
| Fallback даты | Dubai timezone текущая дата |
| Валидация категории | Проверка по VALID_EXPENSE_CATEGORIES |
| Автодетекция категории | По ключевым словам vendor |
| Конвертация в AED | Если валюта не AED |

### Важные правила промпта

- Для чеков АЗС (ENOC, ADNOC): использовать TOTAL (с VAT), не SUBTOTAL
- Salik -- это дорожный сбор (tolls), НЕ парковка
- Валюта в ОАЭ обычно AED

### Инъекция уроков

Типы уроков, инжектируемые в промпт:
- `receipt_amount` -- правильная сумма
- `receipt_vendor` -- правильное название продавца
- `receipt_category` -- правильная категория
- `receipt_date` -- правильная дата
- `receipt_currency` -- правильная валюта

---

## 7 обменных курсов (EXCHANGE_RATES)

| Валюта | Курс к AED | Код |
|--------|-----------|-----|
| AED | 1.0 | AED |
| USD | 3.67 | USD |
| EUR | 4.00 | EUR |
| RUB | 0.038 | RUB |
| GBP | 4.65 | GBP |
| SAR | 0.98 | SAR |
| KWD | 12.0 | KWD |

Курсы фиксированные (hardcoded), не обновляются автоматически.

### Конвертация

```python
amount_aed = amount * EXCHANGE_RATES.get(currency, 1.0)
```

---

## 11 категорий расходов (expense_categories.py)

**Файл:** `core/expense_categories.py`

| # | ID | Название (RU) | Emoji | Ключевые слова |
|---|-----|--------------|-------|----------------|
| 1 | `fuel` | Топливо | fuel | бензин, fuel, gas, adnoc, enoc, emarat, заправка, petrol, diesel |
| 2 | `maintenance` | Обслуживание авто | wrench | ремонт, repair, maintenance, сервис, шина, tire, масло, oil change |
| 3 | `carwash` | Мойка | sponge | мойка, car wash, полировка, химчистка, детейлинг |
| 4 | `insurance` | Страховка | shield | страховка, insurance, полис, policy, oman insurance, axa |
| 5 | `parking` | Парковка | parking | парковка, parking, mawaqif, стоянка |
| 6 | `tolls` | Дорожные сборы | road | salik, салик, toll, штраф, fine, rta, нарушение |
| 7 | `office` | Офис | building | офис, office, канцелярия, бумага, принтер, мебель |
| 8 | `food` | Еда | plate | еда, food, обед, lunch, dinner, кофе, ресторан, доставка |
| 9 | `communication` | Связь | phone | sim, интернет, etisalat, du, телефон, mobile, роуминг |
| 10 | `transport` | Транспорт | taxi | такси, taxi, uber, careem, metro, nol, автобус |
| 11 | `other` | Прочее | package | *(default fallback -- без ключевых слов)* |

### Логика категоризации

```python
def categorize_expense(description: str) -> str:
```

- Первое совпадение ключевого слова побеждает
- Итерация по категориям в порядке (1-10)
- Категория "other" пропускается при сканировании
- Если нет совпадений -> `"other"`

---

## Duplicate Detection (детекция дубликатов)

MD5 хеш от строки `"amount|date|vendor|reference"`:

```python
hash_str = f"{amount}|{date}|{vendor}|{reference}"
dup_hash = hashlib.md5(hash_str.encode()).hexdigest()[:12]
```

Первые 12 символов hex-digest. Сравнивается с существующими записями для предотвращения повторного добавления одного чека.

---

## PDF Export (fpdf2)

**Файл:** `core/export_expenses.py`

### Функция

```python
async def export_expenses_pdf(
    db, user_id, period="week", output_dir="temp"
) -> str:
```

### Библиотека

`fpdf2 >= 2.8.0` -- поддержка Cyrillic через DejaVuSans шрифт (`data/fonts/`).

### Секции отчёта

1. **Заголовок:** "Отчёт по расходам"
2. **Дата:** Период отчёта
3. **Summary:** Итого AED + количество записей
4. **Разбивка по категориям:** Таблица, отсортированная по сумме (убывание), с процентами
5. **Детальная таблица:** Столбцы: #, Date, Category, Description, Amount, Currency, Payment method

### Выходной файл

```
temp/expenses_YYYY-MM-DD_HHMM.pdf
```

---

## Excel Export (openpyxl)

### Функция

```python
async def export_expenses_xlsx(
    db, user_id, period="week", output_dir="temp"
) -> str:
```

### Библиотека

`openpyxl >= 3.1.0`

### 2 листа

#### Sheet 1: "Expenses" (Расходы)

| Столбец | Описание |
|---------|----------|
| ID | Номер записи |
| Date | Дата расхода |
| Category | Категория |
| Vendor | Продавец |
| Description | Описание |
| Amount | Сумма |
| Currency | Валюта |
| AED | Сумма в AED |
| Payment method | Способ оплаты |
| Source | Источник (OCR/manual) |

#### Sheet 2: "Summary" (Итоги)

| Столбец | Описание |
|---------|----------|
| Category | Категория |
| Total AED | Итого в AED |
| Count | Количество записей |
| % | Процент от общего |

Grand total row в конце.

### Стили

- Header: синий фон (#4472C4), белый текст
- Строки: чередующийся серый (#F0F0F0)
- Авто-ширина столбцов

### Выходной файл

```
temp/expenses_YYYY-MM-DD_HHMM.xlsx
```

---

## Финансовый отчёт (format)

Формат отчёта включает:

| Секция | Описание |
|--------|----------|
| Header | Период, дата генерации |
| Summary | Итого AED, количество расходов, средний расход |
| Category breakdown | Таблица по категориям (сумма, количество, %) |
| Top expenses | Топ-5 крупнейших расходов |
| Trend | Сравнение с предыдущим периодом |

---

## Ручное добавление расхода

### Команда

```
/add_expense 150 бензин ADNOC
```

### Обработка

1. Парсинг суммы из первого токена (поддерживает запятую как десятичную)
2. Автокатегоризация через `categorize_expense()`
3. Сохранение с валютой AED, timezone Dubai (UTC+4)
4. Подтверждение: сумма, описание, категория, дата

---

## Коррекция расходов

### Команда /fix

```
/fix EID amount 47.25
/fix EID vendor ADNOC
/fix EID category fuel
```

### Допустимые поля

- `amount` -- сумма (числовая)
- `vendor` -- продавец (текст)
- `category` -- категория (валидация по VALID_EXPENSE_CATEGORIES)

### Автоурок

При каждой коррекции автоматически записывается урок:

```python
services.lessons.record_lesson(
    type=f"receipt_{field}",
    context=vendor_name,
    wrong=old_value,
    correct=new_value,
    ...
)
```

---

## Таблица expenses в БД

```sql
CREATE TABLE expenses (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL,
    amount            REAL NOT NULL,
    currency          TEXT DEFAULT 'AED',
    amount_aed        REAL,
    vendor            TEXT,
    category          TEXT NOT NULL,
    subcategory       TEXT,
    expense_date      TEXT NOT NULL,
    payment_method    TEXT,
    description       TEXT,
    ocr_text          TEXT,
    receipt_source    TEXT,
    receipt_confidence REAL,
    transcription_id  INTEGER,
    items_json        TEXT,
    reference         TEXT,
    notes             TEXT,
    tags              TEXT,
    is_business       INTEGER DEFAULT 1,
    is_deleted        INTEGER DEFAULT 0,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### CRUD операции

| Метод | Описание |
|-------|----------|
| `save_expense()` | Создать расход (16 параметров) |
| `get_expenses()` | Фильтрованный список (soft-delete aware) |
| `get_expense()` | Одна запись по ID |
| `delete_expense()` | Soft delete (is_deleted=1) |
| `update_expense()` | Частичное обновление |
| `get_expense_stats()` | total_aed, count, by_category, by_vendor |
