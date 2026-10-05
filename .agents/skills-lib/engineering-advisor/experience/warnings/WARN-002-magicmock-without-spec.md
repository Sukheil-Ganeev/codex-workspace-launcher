---
id: EXP-041
date: 2026-02-21
type: warning
severity: high
tags: [testing, MagicMock, spec, mocking, pytest]
project: VoiceTranscriptionBot
---

## Проблема

`MagicMock()` без параметра `spec=` автоматически создаёт ЛЮБОЙ запрошенный атрибут. Это значит:
- `mock_result.text` → возвращает MagicMock (даже если `.text` не существует)
- `mock_result.nonexistent_field` → тоже возвращает MagicMock
- Тесты проходят зелёные, а реальный код падает с AttributeError

## Контекст

В VoiceTranscriptionBot тесты video callback использовали `MagicMock()` для `PipelineResult`. Код обращался к `result.text` (несуществующий атрибут), но тесты проходили потому что mock не проверяет реальные атрибуты.

## Решение

Всегда использовать `spec=` или `spec_set=`:
```python
# ПЛОХО — скрывает баги
mock_result = MagicMock()
mock_result.text  # молча возвращает MagicMock

# ХОРОШО — ловит баги
mock_result = MagicMock(spec=PipelineResult)
mock_result.text  # AttributeError! Нет такого поля!
```

## Урок

**MagicMock без spec — лжец.** Он говорит "всё работает", пока продакшн падает. Каждый MagicMock в тестах ДОЛЖЕН иметь `spec=RealClass`.

## Правило предотвращения

При code review: `grep -n "MagicMock()" tests/` — если находится без spec= → требовать исправления.
