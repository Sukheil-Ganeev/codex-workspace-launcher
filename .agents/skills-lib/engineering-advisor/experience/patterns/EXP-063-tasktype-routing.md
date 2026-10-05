# EXP-063: TaskType Routing — маршрутизация AI-задач по сложности

**Тип:** pattern
**Severity:** high
**Проект:** VoiceTranscriptionBot
**Дата:** 2026-02-28

## Проблема

Все AI-задачи использовали одинаковый model cascade независимо от сложности. Sentiment analysis (50 токенов вывода) шёл через тот же дорогой pipeline, что и creative writing (4000 токенов).

## Решение

**Phase C** — `TaskType` enum (6 типов) с `TASK_CONFIG` маппингом на оптимальные параметры.

```python
class TaskType(Enum):
    CLASSIFICATION = "classification"   # sentiment, categories → cheapest model, temp 0.1
    EXTRACTION = "extraction"           # key_facts, dates → cheap model, temp 0.0
    CORRECTION = "correction"           # text correction → mid model, temp 0.3
    SUMMARIZATION = "summarization"     # summaries → mid model, temp 0.5
    CREATIVE = "creative"               # formatting, improving → best model, temp 0.7
    TRANSLATION = "translation"         # translation → mid model, temp 0.3

TASK_CONFIG = {
    TaskType.CLASSIFICATION: {"model": "lite", "temperature": 0.1, "max_tokens": 100},
    TaskType.EXTRACTION: {"model": "lite", "temperature": 0.0, "max_tokens": 500},
    TaskType.CORRECTION: {"model": "primary", "temperature": 0.3, "max_tokens": 2000},
    # ...
}

# Использование
result = await services.llm.generate_for_task(prompt, TaskType.CLASSIFICATION)
```

## Ключевой инсайт

**CLASSIFICATION задачи (sentiment, categories) отлично работают на самой дешёвой модели (flash-lite, $0.10/1M токенов) при temperature 0.1.** Для 1-словных выводов ("positive", "transport") качество не падает. Экономия ~3x на лёгких задачах.

## Паттерн

**Task-based routing** вместо one-size-fits-all:
- Лёгкие задачи (classification, extraction) → дешёвая модель, низкая temperature
- Средние задачи (correction, summarization) → основная модель
- Тяжёлые задачи (creative, formatting) → лучшая модель, высокая temperature

## Экономия

| Тип задачи | До (модель) | После (модель) | Экономия |
|------------|-------------|----------------|----------|
| Sentiment | 2.5-flash ($0.30/1M) | 2.0-flash ($0.10/1M) | 3x |
| Categories | 2.5-flash ($0.30/1M) | 2.0-flash ($0.10/1M) | 3x |
| Key facts | 2.5-flash ($0.30/1M) | 2.0-flash ($0.10/1M) | 3x |
| Formatting | 2.5-flash | 2.5-flash (без изменений) | 0% |

## Чек-лист

- [ ] Каждый AI-вызов имеет явный TaskType
- [ ] TASK_CONFIG содержит параметры для каждого TaskType
- [ ] Новые AI-функции начинаются с выбора TaskType
- [ ] Мониторинг: трекинг стоимости по TaskType (api_monitor.py)

## Связанные уроки

- EXP-061: Deprecated model migration (Phase A)
- EXP-062: LLMClient consolidation (Phase B)
- PAT-031: Phased backward-compatible refactoring
