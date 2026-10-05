# EXP-061: Миграция с deprecated моделей Gemini

**Тип:** fix
**Severity:** high
**Проект:** VoiceTranscriptionBot
**Дата:** 2026-02-28

## Проблема

gemini-2.0-flash и gemini-2.0-flash-lite запланированы на shutdown 31 марта 2026. Использовались в 8 местах в 6 файлах. Модели были захардкожены как строки в каждом модуле.

## Корневая причина

Отсутствие единого источника истины для model ID. Каждый модуль (`summarizer.py`, `corrector.py`, `sentiment.py`, `categories.py`, `accounting.py`, `llm_client.py`) содержал свои строковые литералы `"gemini-2.0-flash"` / `"gemini-2.0-flash-lite"`.

## Решение

**Phase A** — простая замена строк model ID. 8 строк изменено в 6 файлах. Все 2138 тестов прошли.

Замены:
- `gemini-2.0-flash` -> `gemini-2.5-flash`
- `gemini-2.0-flash-lite` -> `gemini-2.0-flash` (вместо удалённого lite)

## Правило

**Централизуй model ID как константы в одном файле.** Паттерн: `GEMINI_MODELS` dict в `llm_client.py` или `config.py`. При следующей миграции — изменение 1 строки вместо 8.

```python
# ПРАВИЛЬНО: единый источник
GEMINI_MODELS = {
    "primary": "gemini-2.5-flash",
    "secondary": "gemini-2.0-flash",
    "lite": "gemini-2.0-flash",
}

# НЕПРАВИЛЬНО: строки разбросаны по файлам
model = "gemini-2.0-flash"  # в summarizer.py
model = "gemini-2.0-flash"  # в corrector.py (копипаста)
```

## Чек-лист

- [ ] Все model ID определены в одном месте (config/constants)
- [ ] Модули импортируют константы, не содержат строковых литералов model ID
- [ ] При добавлении нового модуля с AI — использовать импорт константы
- [ ] Grep по проекту на строку model ID после миграции (проверка полноты)

## Связанные уроки

- EXP-062: LLMClient consolidation (Phase B)
- EXP-063: TaskType routing (Phase C)
