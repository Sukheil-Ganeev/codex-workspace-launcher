---
id: EXP-044
date: 2026-02-21
type: fix
severity: high
tags: [function-signature, missing-argument, TypeError, detect_client_in_text]
project: VoiceTranscriptionBot v4.5.0
---

## Проблема

`detect_client_in_text(text, clients)` требует 2 аргумента, но вызывалась с одним:
```python
# БЫЛО:
client_phone = await detect_client_in_text(text_for_analysis)
# TypeError: missing 1 required positional argument: 'clients'

# СТАЛО:
from core.clients import list_clients
all_clients = list_clients()
clients_list = [{"name": info.get("name", ""), "phone": phone} for phone, info in all_clients.items()]
client_phone = detect_client_in_text(text_for_analysis, clients_list)
```

Ошибка повторялась в 2 местах pipeline.py (process_voice и process_voice_fast).

## Контекст

При интеграции `detect_client_in_text` в pipeline забыли передать второй аргумент `clients`. Широкий `except Exception` перехватывал ошибку и логировал как warning — функционал молча не работал.

## Решение

1. Проверять ВСЕ аргументы функции при вызове
2. Не использовать широкий `except Exception` без re-raise в dev-режиме
3. IDE/линтер подсвечивают missing arguments — не игнорировать

## Урок

**Каждый вызов — проверь сигнатуру.** Особенно когда функция из другого модуля. Широкий except — враг отладки.
