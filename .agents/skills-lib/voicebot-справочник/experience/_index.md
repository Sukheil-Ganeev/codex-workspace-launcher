# Критические уроки VoiceTranscriptionBot

> experience/_index.md -- ЧИТАТЬ ПРИ АКТИВАЦИИ СКИЛЛА
> Проект: `D:/Downloads/VoiceTranscriptionBot/`
> Версия: v1.0 -> v6.1.0

---

## Топ-10 критических уроков

### 1. Fallback каскады спасают от API outages

**Урок:** НИКОГДА не полагайся на один API провайдер. Каскадная архитектура -- основа надёжности.

**Реализация в проекте:**
- STT: faster-whisper GPU -> Groq Whisper API -> RuntimeError
- LLM: gemini-2.5-flash -> Groq Llama -> safe fallback (через LLMClient)
- OCR: Google Vision -> Gemini Vision
- Все 14 LLM-модулей используют единый LLMClient с автоматическим каскадом

**Почему это работает:**
- Gemini rate limits случаются регулярно (особенно gemini-2.5-flash)
- Groq иногда недоступен на 5-10 минут
- С каскадом пользователь НИКОГДА не видит ошибку, просто используется другая модель

**Правило:** Pipeline `process_voice()` НИКОГДА не крашится. Всегда возвращает `PipelineResult`, даже при ошибках (с `result.error` set).

---

### 2. Unified LLMClient Pattern

**Урок:** Все LLM-модули ДОЛЖНЫ использовать единый `core/llm_client.py`, а не создавать свои клиенты.

**Реализация (v6.1.0):**
```
core/llm_client.py:
  GEMINI_MODELS = [("gemini-2.5-flash", client), ("gemini-2.5-flash-lite", client)]

  generate_for_task(prompt, TaskType.CLASSIFICATION)  → flash-lite, temp 0.1
  generate_for_task(prompt, TaskType.ANALYSIS)         → flash, temp 0.3
  generate_for_task(prompt, TaskType.CREATIVE)         → flash, temp 0.7
  generate_for_task(prompt, TaskType.TRANSFORMATION)   → flash, temp 0.3
  generate_for_task(prompt, TaskType.VISION)            → flash + image
  generate_for_task(prompt, TaskType.PLANNING)          → flash, temp 0.2
```

- Все 14 модулей используют LLMClient: corrector, sentiment, summarizer, translator, key_facts, categories, accounting, ocr, digest, improver, suggester, formatter_tour, calculator, router
- Единая точка инициализации и конфигурации
- Экономия памяти (один HTTP клиент)
- Изменение модели = 1 строка в `GEMINI_MODELS`

**Антипаттерн:** НЕ создавать отдельные LLM клиенты в модулях -- всё консолидировано в LLMClient (v6.1.0).

---

### 3. FTS5 auto-sync через triggers (не manual)

**Урок:** Полнотекстовый индекс ДОЛЖЕН синхронизироваться через SQL triggers, а не через ручные вызовы.

**Реализация:**
```sql
-- AFTER INSERT
CREATE TRIGGER transcriptions_ai AFTER INSERT ON transcriptions BEGIN
    INSERT INTO transcriptions_fts(rowid, transcription, summary) VALUES (...);
END;

-- AFTER DELETE
CREATE TRIGGER transcriptions_ad AFTER DELETE ON transcriptions BEGIN
    INSERT INTO transcriptions_fts(transcriptions_fts, ...) VALUES ('delete', ...);
END;

-- AFTER UPDATE
CREATE TRIGGER transcriptions_au AFTER UPDATE ON transcriptions BEGIN
    -- delete old + insert new
END;
```

**Почему:**
- Гарантированная консистентность (triggers -- atomic с основной операцией)
- Архивация (`DELETE FROM transcriptions`) автоматически чистит FTS
- Невозможно "забыть" обновить индекс

**Ошибка v1.0:** Ручная FTS-вставка после `save()` -- при краше между save и FTS-вставкой индекс рассинхронизировался.

---

### 4. Auto-delete сервисных сообщений улучшает UX

**Урок:** Подтверждения, ошибки и подсказки должны удаляться автоматически.

**Реализация:** `bot/auto_delete.py`
- `DELAY_CONFIRM = 15 сек` -- подтверждения
- `DELAY_ERROR = 20 сек` -- ошибки
- `DELAY_HINT = 25 сек` -- подсказки

**Почему:**
- Чат не засоряется служебными сообщениями
- Пользователь видит результат, но через 15-25 секунд чат чистый
- Silent failure: если удаление не удалось -- логирование на DEBUG, без ошибки

**Важно:** `send_temp()` -- fire-and-forget. Никогда не await результат удаления.

---

### 5. FORCE_GROQ_STT для serverless/ARM deployment

**Урок:** Локальная STT модель НЕВОЗМОЖНА на ARM серверах. ВСЕГДА используй `FORCE_GROQ_STT=true` для серверного развёртывания.

**Контекст:**
- Oracle Cloud Always Free -- ARM Ampere A1, нет GPU
- faster-whisper `large-v3` на CPU: 30-60 секунд на минуту аудио (неприемлемо)
- Groq API: ~1-3 секунды на минуту аудио (отлично)
- Groq бесплатный tier: достаточно для бизнеса

**Реализация:**
- `requirements-server.txt` -- без faster-whisper
- `.env`: `FORCE_GROQ_STT=true`
- Код в `transcriber.py`: если флаг True, `transcribe_local()` полностью пропускается

---

### 6. 2-уровневый approval для деструктивных операций

**Урок:** Любое необратимое действие ДОЛЖНО проходить через approval system.

**Реализация:**
- Level A (24h): удаление одного элемента, DB VACUUM
- Level B (48h): массовые операции (архивация, merge lessons)

**Защищённые операции:**
- Удаление клиента, расхода, урока
- Архивация транскрипций (>180 дней)
- Архивация уроков (>90 дней)
- Объединение уроков
- DB VACUUM

**Почему:**
- Случайное удаление клиента -- критично для бизнеса
- Массовая архивация -- может удалить нужные данные
- Auto-expire (24-48h) предотвращает "зависшие" запросы

---

### 7. Lesson injection в промпты для обучения

**Урок:** Бот должен учиться на коррекциях пользователя через инъекцию уроков в LLM промпты.

**Поток:**
1. Пользователь исправляет ошибку бота (категория, сумма чека, sentiment)
2. `record_lesson()` создаёт/усиливает урок
3. При следующей обработке: `get_relevant_lessons()` находит уроки
4. `format_lessons_for_prompt()` добавляет блок "УРОКИ ИЗ ПРОШЛОГО ОПЫТА" в промпт
5. LLM учитывает уроки

**Ключевые числа:**
- Max 7 уроков на промпт
- Релевантность: context overlap * 2.0 + times_applied * 0.5 + substring match + recency
- Stale после 90 дней без использования
- Purge архивированных после 180 дней

**Пример:** Бот категоризировал чек ADNOC как "parking". Урок: "ADNOC -- это fuel, не parking". При следующем чеке ADNOC -- урок инжектируется и бот правильно определяет "fuel".

---

### 8. Navigation stack для поддержки кнопки "назад"

**Урок:** Интерактивные боты НУЖДАЮТСЯ в навигационном стеке для back-button.

**Реализация:** `core/navigation.py`
```python
_nav_stacks: dict[int, list[tuple[str, dict]]] = {}

push_screen(user_id, screen_name, params)
pop_screen(user_id) -> tuple | None
clear_stack(user_id)
is_back_command(text) -> bool  # "назад", "back", стрелки
```

**Constraints:**
- MAX_STACK_SIZE = 20 (drop oldest)
- Каждый top-level command вызывает `clear_stack()`
- Screens: 'stats', 'history', 'client_card', 'merge', 'export', 'settings', etc.

**Почему:**
- Пользователи ожидают навигацию "назад" как в мобильных приложениях
- Без стека: невозможно вернуться из карточки клиента к списку клиентов
- Работает одинаково в Telegram (callback buttons) и WhatsApp (text "назад")

---

### 9. TaskType routing для оптимальной стоимости

**Урок:** Разные задачи требуют разных моделей и температур. TaskType routing через LLMClient позволяет оптимизировать стоимость и качество.

**Реализация:** `core/llm_client.py`
- `CLASSIFICATION` (sentiment, categories) -> cheapest model (flash-lite, ~$0.10/1M tokens), temperature 0.1
- `ANALYSIS` (summarization, key_facts, correction) -> primary model, temperature 0.3
- `CREATIVE` (improver, suggester) -> best model + high temperature 0.7 для разнообразия
- `TRANSFORMATION` (translator, formatter_tour) -> primary model, temperature 0.3
- `VISION` (OCR, receipt parsing) -> primary model with image support
- `PLANNING` (calculator, router) -> low temperature 0.2 для precise JSON parsing

**Почему:**
- Sentiment -- простая классификация, не нужна дорогая модель
- Улучшение текста -- нужна креативность, высокая temperature
- Маршруты -- нужен точный JSON, низкая temperature
- Менять модели = 1 строка в `core/llm_client.py`

**Экономия:** CLASSIFICATION на flash-lite вместо flash -- ~10x дешевле при том же качестве для простых задач.

---

### 10. AI Model Architecture v6.1.0 -- миграция deprecated моделей + LLMClient + TaskType

**Урок:** Архитектурные миграции AI-моделей требуют: (1) проверки sunset дат, (2) консолидации клиентов через DI, (3) TaskType маршрутизации для экономии, (4) фазированного рефакторинга с тестами.

**Ключевые находки:**
- `gemini-2.0-flash` / `gemini-2.0-flash-lite` deprecated (sunset 31.03.2026) -- обнаружено в 6 файлах (8 мест)
- 5 модулей создавали собственные `genai.Client()` в обход DI -- консолидировано в единый LLMClient
- TaskType routing (6 типов) снижает стоимость с $15/мес до $5-7/мес
- Coroutine leak bug: создание корутины без await при falsy timeout
- accounting.py блокировал event loop синхронными вызовами
- 3 фазы (A->B->C): 2138 тестов зелёные после каждой

**Подробно:** `experience/EXP-010-ai-model-architecture-v6.1.md`

---

## Дополнительные уроки

### Per-Step Error Handling

Каждый шаг pipeline обёрнут индивидуально. Если упал sentiment -- используется default "neutral". Если упала коррекция -- используется оригинальный текст. Pipeline НИКОГДА не останавливается целиком из-за одного упавшего шага.

### Smart Model Selection (now via TaskType)

TaskType автоматически выбирает оптимальную модель и температуру:
- CLASSIFICATION -> lightest model
- CREATIVE -> best model + high temperature
- PLANNING -> best model + low temperature
- Все задачи -> единый каскад с Groq fallback

### Keyword Categorization vs Smart Categorization

Основной pipeline использует regex `categorize()`, не LLM `categorize_smart()`. Regex быстрее, бесплатный, предсказуемый. Smart -- только для сложных случаев.

### Dictation Mode

Аудио > 3 минут -> `is_dictation=True` -> пропускается суммаризация. Длинные диктовки не нуждаются в резюме, пользователь хочет полный текст.

### Graceful Import

Опциональные модули (`key_facts`, `client_detector`) импортируются через try/except. Если модуль недоступен -- pipeline продолжает без него.

### Split Handlers Pattern (v6.0.0)

Монолитный `handlers.py` (6325 строк) разбит на 12 доменных модулей + хаб-маршрутизатор (258 строк). Каждый модуль регистрирует свой router, хаб собирает все через `include_router()`. Упрощает навигацию, тестирование и параллельную разработку.

---

## Антипаттерны (что НЕ делать)

1. **НЕ** создавать отдельный LLM клиент в модулях -- используй LLMClient (всё консолидировано в v6.1.0)
2. **НЕ** синхронизировать FTS вручную -- используй triggers
3. **НЕ** разворачивать faster-whisper на ARM -- используй FORCE_GROQ_STT
4. **НЕ** удалять данные без approval -- всегда через ApprovalManager
5. **НЕ** оставлять служебные сообщения в чате -- используй auto_delete
6. **НЕ** полагаться на один LLM провайдер -- всегда каскад с fallback
7. **НЕ** блокировать event loop STT/LLM вызовами -- используй asyncio.to_thread()
8. **НЕ** хардкодить температуру/модель в модулях -- используй TaskType routing в LLMClient
