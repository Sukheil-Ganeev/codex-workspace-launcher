---
id: EXP-043
date: 2026-02-21
type: fix
severity: medium
tags: [async, await, sync, TypeError, detect_client_in_text]
project: VoiceTranscriptionBot v4.5.0
---

## Проблема

В `core/pipeline.py` синхронная функция `detect_client_in_text()` вызывалась через `await`:
```python
# БЫЛО (неправильно):
client_phone = await detect_client_in_text(text_for_analysis)

# СТАЛО (правильно):
client_phone = detect_client_in_text(text_for_analysis, clients_list)
```

Python не выбрасывает ошибку на `await sync_function()` если функция возвращает не-awaitable — TypeError происходит тихо и ловится generic except.

## Контекст

Функция была синхронной (`def detect_client_in_text`), но вызывалась с `await`. Ошибка скрывалась за широким `except Exception` и логировалась как warning, не ломая основной flow.

## Решение

1. Проверить сигнатуру перед `await`: функция должна быть `async def`
2. Если функция синхронная — вызывать без `await`

## Урок

**Перед `await` — проверь `async def`.** Линтер (pylint, pyright) ловит это, но если его нет — проверяй вручную.
