# EXP-010: AI Model Architecture v6.1.0 -- Миграция deprecated моделей + LLMClient + TaskType

> **Дата:** 2026-02-28
> **Версия:** v6.1.0
> **Теги:** #architecture #ai-models #llm #refactoring #deprecated #migration
> **Влияние:** Высокое (затронуты все 14 LLM-модулей)

---

## Контекст

При подготовке к v6.1.0 обнаружено, что 6 файлов (8 мест) используют deprecated модели Gemini:
- `gemini-2.0-flash` -- sunset 31 марта 2026
- `gemini-2.0-flash-lite` -- sunset 31 марта 2026

Также 5 модулей (translator, ocr, accounting, key_facts, suggester) создавали собственные `genai.Client()` в обход DI-контейнера, что приводило к дублированию model ID, невозможности централизованной смены модели и отсутствию rate limiting.

Решение: трёхфазная миграция с нулевым простоем и сохранением всех тестов зелёными.

---

## Ключевые уроки

### 1. Deprecated модели -- проверяй даты sunset

**Проблема:** `gemini-2.0-flash` и `gemini-2.0-flash-lite` имели sunset 31 марта 2026. Без проверки бот перестал бы работать через месяц.

**Где обнаружено:** 6 файлов, 8 мест в коде:
- `core/llm_client.py` -- основной каскад
- `core/corrector.py` -- автоисправление
- `core/sentiment.py` -- анализ настроения
- `core/summarizer.py` -- резюме
- `core/categories.py` -- категоризация
- `bot/transcriber.py` -- распознавание речи (Groq model string)

**Замена:**
- `gemini-2.0-flash` -> `gemini-2.5-flash`
- `gemini-2.0-flash-lite` -> `gemini-2.5-flash-lite`

**Правило:** ВСЕГДА проверять актуальность моделей при начале новой сессии работы с проектом. Добавить проверку sunset дат в `core/validators.py` или документацию.

---

### 2. DRY для AI-клиентов -- единый LLMClient

**Проблема:** 5 модулей создавали собственные `genai.Client()`:
- `core/translator.py`
- `core/ocr.py`
- `core/accounting.py`
- `core/key_facts.py`
- `admin/suggester.py`

**Последствия:**
- Дублирование model ID в 5+ местах
- Невозможность централизованной смены модели (нужно менять в каждом файле)
- Отсутствие rate limiting для отдельных клиентов
- Лишний расход памяти (5 HTTP-клиентов вместо 1)

**Решение:** Единый `core/llm_client.py` с методами:
- `generate(prompt, ...)` -- текстовая генерация
- `generate_with_image(prompt, image_data, ...)` -- генерация с изображением
- `generate_for_task(prompt, TaskType)` -- маршрутизация по типу задачи

Все 14 модулей теперь используют LLMClient через DI-контейнер (`services.llm`).

**Антипаттерн:** НИКОГДА не создавать `genai.Client()` или прямые HTTP-клиенты в модулях. Всё через LLMClient.

---

### 3. TaskType маршрутизация экономит деньги

**Идея:** Не все AI-задачи требуют одинаковой мощности модели и температуры.

**6 типов задач:**

| TaskType | Модель | Temperature | Примеры |
|----------|--------|-------------|---------|
| CLASSIFICATION | flash-lite (~3x дешевле) | 0.1 | sentiment, categories |
| ANALYSIS | flash | 0.3 | summarizer, key_facts, corrector |
| CREATIVE | flash | 0.7 | improver, suggester |
| TRANSFORMATION | flash | 0.3 | translator, formatter_tour |
| VISION | flash + image | 0.3 | OCR, receipt parsing |
| PLANNING | flash | 0.2 | calculator, router (precise JSON) |

**Экономия:**
- CLASSIFICATION на flash-lite вместо flash: ~10x дешевле при том же качестве
- Общая экономия: $15/мес -> $5-7/мес (оценка)

**Правило:** При добавлении нового LLM-модуля -- определи TaskType, не хардкодь модель.

---

### 4. Phased backward-compatible рефакторинг

**Подход:** 3 фазы (A -> B -> C) с тестами после каждой. Ни один тест не ломался навсегда.

**Фаза A -- замена строк (zero risk):**
- Только замена deprecated model ID на актуальные
- 6 файлов, 8 замен
- Тесты: все 2138 зелёные

**Фаза B -- добавление нового API (low risk):**
- Добавление `generate_for_task()` и `TaskType` enum в LLMClient
- Старое API (`generate()`, `generate_with_image()`) НЕ удаляется
- 7 файлов затронуто
- Тесты: все 2138 зелёные

**Фаза C -- миграция потребителей (medium risk):**
- 13 модулей переведены на `generate_for_task()` или `services.llm.generate()`
- Удалены прямые `genai.Client()` из 5 модулей
- Тесты: все 2138 зелёные

**Правило:** НИКОГДА не делать big-bang рефакторинг. Фазы с промежуточными тестами -- обязательно.

---

### 5. Coroutine leak bug в LLMClient

**Проблема:** В `LLMClient.generate()` при falsy timeout (например, `timeout=0` или `timeout=None`) код создавал корутину через `asyncio.to_thread()`, но не await'ил её, а затем создавал вторую. Первая корутина утекала.

**Плохой код (упрощённо):**
```python
coro = asyncio.to_thread(sync_call)
if timeout:
    result = await asyncio.wait_for(coro, timeout=timeout)
else:
    result = await asyncio.to_thread(sync_call)  # вторая корутина!
# первая coro -- leaked
```

**Исправление -- чистый if/else:**
```python
if timeout:
    coro = asyncio.to_thread(sync_call)
    result = await asyncio.wait_for(coro, timeout=timeout)
else:
    result = await asyncio.to_thread(sync_call)
```

**Правило:** Корутина должна быть создана И await'нута в одном месте. Не создавай корутину "про запас".

---

### 6. accounting.py threading bug

**Проблема:** `accounting.py` использовал синхронные вызовы `client.files.upload()` и `client.models.generate_content()` прямо в async-функции, блокируя event loop.

**Последствия:**
- Бот "подвисал" на 5-10 секунд при обработке чека
- Другие пользователи не получали ответов
- На сервере с одним ядром -- полный блок

**Решение:** Маршрутизация через LLMClient, который автоматически оборачивает синхронные вызовы в `asyncio.to_thread()`.

**Правило:** Любой вызов внешнего API из async-кода -- через `asyncio.to_thread()` или нативный async-клиент. НИКОГДА не вызывать синхронный API напрямую из async.

---

### 7. Масштаб обновления документации

**Проблема:** Архитектурное изменение (LLMClient + TaskType) затронуло ~20 файлов документации:
- `CLAUDE.md` (основная документация)
- `CHANGELOG.md`
- `docs/ARCHITECTURE.md`
- `experience/_index.md`
- Комментарии в коде
- `.env.example`
- И другие

**Решение:** Параллельные субагенты (4-6 штук) обновляют документацию за 10 минут вместо часа.

**Правило:** При архитектурном изменении -- составь список ВСЕХ файлов документации заранее, делегируй параллельным субагентам.

---

## Метрики

| Параметр | Значение |
|----------|----------|
| Файлов в фазе A | 6 |
| Файлов в фазе B | 7 |
| Файлов в фазе C | 13 |
| Тесты (после каждой фазы) | 2138, все зелёные |
| Документация обновлена | 20+ файлов |
| Стоимость API до | ~$15/мес |
| Стоимость API после | ~$5-7/мес |
| Модулей на LLMClient | 14 |
| Удалённых отдельных клиентов | 5 |

---

## Чеклист для будущих AI-миграций

- [ ] Проверить sunset даты текущих моделей
- [ ] Составить список всех файлов с прямыми model ID
- [ ] Определить TaskType для каждого модуля
- [ ] Фазы: A (строки) -> B (новый API) -> C (миграция) с тестами
- [ ] Обновить все файлы документации
- [ ] Проверить корутины на leaks
- [ ] Проверить синхронные вызовы в async-коде
- [ ] Запустить все тесты после каждой фазы

---

## Связанные файлы

| Файл | Роль |
|------|------|
| `core/llm_client.py` | Единый LLM-клиент с TaskType routing |
| `core/services.py` | DI-контейнер (services.llm) |
| `core/corrector.py` | Автоисправление (ANALYSIS) |
| `core/sentiment.py` | Анализ настроения (CLASSIFICATION) |
| `core/summarizer.py` | Резюме (ANALYSIS) |
| `core/categories.py` | Категоризация (CLASSIFICATION) |
| `core/translator.py` | Переводчик (TRANSFORMATION) |
| `core/ocr.py` | Распознавание текста (VISION) |
| `core/accounting.py` | Парсер чеков (VISION) |
| `core/key_facts.py` | Ключевые факты (ANALYSIS) |
| `core/improver.py` | Улучшение текста (CREATIVE) |
| `core/calculator.py` | Калькулятор (PLANNING) |
| `core/router.py` | Маршруты (PLANNING) |
| `admin/suggester.py` | AI-суфлёр (CREATIVE) |
